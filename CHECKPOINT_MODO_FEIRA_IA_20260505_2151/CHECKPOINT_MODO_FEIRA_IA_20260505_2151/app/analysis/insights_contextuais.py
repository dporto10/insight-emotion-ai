
import os
import re
import unicodedata
from typing import Dict, List, Any
from app.analysis.ai_insight_writer import gerar_insights_consultivos
from app.analysis.transcript_segments import carregar_segmentos_transcricao, escolher_trecho_por_tempo
from app.analysis.commercial_intelligence import analisar_inteligencia_comercial


def _safe_float(value, default=0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _normalize(text: str) -> str:
    text = (text or "").lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def _split_sentences(text: str) -> List[str]:
    text = _clean_text(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [_clean_text(p) for p in parts if _clean_text(p)]


def _extract_keywords(segment: str) -> List[str]:
    words = re.findall(r"[a-z0-9]+", _normalize(segment))
    stop = {
        "de", "da", "do", "das", "dos", "e", "o", "a", "os", "as",
        "um", "uma", "para", "por", "com", "sem", "que", "na", "no",
        "nas", "nos", "em", "ser", "foi", "vai", "tem", "ta", "mais",
        "menos", "muito", "isso", "essa", "esse", "ela", "ele", "eu",
        "voce", "voces", "nos", "meu", "minha", "seu", "sua", "ja",
        "tudo", "bem", "boa", "noite", "entao", "exatamente"
    }

    freq = {}
    for w in words:
        if len(w) < 4 or w in stop:
            continue
        freq[w] = freq.get(w, 0) + 1

    return [k for k, _ in sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:5]]


def _contexto_por_tempo(inicio: float, fim: float, total: float) -> str:
    if total <= 0:
        return "desenvolvimento"
    ratio = ((inicio + fim) / 2) / total
    if ratio <= 0.20:
        return "abertura"
    if ratio >= 0.75:
        return "fechamento"
    return "desenvolvimento"


def _rotulo_negocio(emocao_raw: str) -> str:
    e = _normalize(emocao_raw)
    mapa = {
        "desconexao": "Perda de interesse",
        "neutro": "Atenção moderada",
        "interesse": "Alto engajamento",
        "curiosidade": "Alto engajamento",
        "resistencia": "Resistência comercial",
        "apreensao": "Atenção moderada",
        "rejeicao": "Resistência comercial",
    }
    return mapa.get(e, emocao_raw or "Indefinido")


def _detectar_tema(segment: str) -> str:
    s = _normalize(segment)

    if any(x in s for x in ["preco", "valor", "menor", "desconto", "pagamento", "parcel"]):
        return "preço"

    if any(x in s for x in ["beneficio", "vantagem", "solucao", "produto", "resultado", "melhor"]):
        return "valor"

    if any(x in s for x in ["procurando", "precisa", "quer", "dor", "problema", "necessidade", "serve", "pra que"]):
        return "necessidade"

    if any(x in s for x in ["fechar", "comprar", "pedido", "codigo", "code", "olhar", "levar", "vamos"]):
        return "fechamento"

    if any(x in s for x in ["boa noite", "tudo bem", "oi", "ola"]):
        return "abertura"

    return "condução"


def _detectar_intencao(segment: str, contexto: str) -> str:
    s = _normalize(segment)

    if "?" in segment or any(x in s for x in ["procurando", "precisa", "pra que", "para que", "qual", "como", "quando"]):
        return "diagnóstico de necessidade"

    if any(x in s for x in ["beneficio", "vantagem", "melhor", "serve", "produto", "solucao", "valor"]):
        return "apresentação de valor"

    if any(x in s for x in ["preco", "valor", "desconto", "pagamento", "menor"]):
        return "negociação de preço"

    if any(x in s for x in ["fechar", "comprar", "pedido", "olhar", "codigo", "code", "levar"]):
        return "tentativa de fechamento"

    if contexto == "abertura":
        return "abertura comercial"

    return "condução da conversa"


def _peso_impacto(contexto: str, tema: str, intencao: str, emocao: str) -> int:
    peso = 1

    if contexto == "abertura":
        peso += 1
    if contexto == "fechamento":
        peso += 3

    if tema == "preço":
        peso += 3
    elif tema == "fechamento":
        peso += 3
    elif tema == "necessidade":
        peso += 2
    elif tema == "valor":
        peso += 2

    if intencao == "negociação de preço":
        peso += 3
    elif intencao == "tentativa de fechamento":
        peso += 3
    elif intencao == "diagnóstico de necessidade":
        peso += 2

    if emocao in ["Perda de interesse", "Resistência comercial"]:
        peso += 2

    return min(peso, 10)


def _score_frase(sentence: str, contexto: str, emocao: str) -> int:
    s = _normalize(sentence)
    score = 0

    pesos = {
        "preco": 7,
        "valor": 6,
        "beneficio": 6,
        "desconto": 5,
        "pagamento": 5,
        "produto": 4,
        "procurando": 6,
        "precisa": 6,
        "problema": 6,
        "solucao": 6,
        "duvida": 5,
        "comprar": 6,
        "fechar": 7,
        "pedido": 5,
        "oferta": 6,
        "copo": 4,
        "menor": 4,
    }

    for termo, peso in pesos.items():
        if termo in s:
            score += peso

    if "?" in sentence:
        score += 4

    if contexto == "abertura" and any(x in s for x in ["procurando", "precisa", "problema", "boa noite", "tudo bem"]):
        score += 4

    if contexto == "fechamento" and any(x in s for x in ["comprar", "fechar", "codigo", "code", "pedido", "olhar"]):
        score += 5

    if emocao in ["Perda de interesse", "Resistência comercial"] and any(x in s for x in ["preco", "desconto", "pagamento", "menor"]):
        score += 5

    return score


def _pick_segment_by_ratio(sentences: List[str], inicio: float, fim: float, total: float, contexto: str, emocao: str) -> str:
    if not sentences:
        return ""
    if len(sentences) == 1:
        return sentences[0]

    total = max(float(total or 1), 1)
    meio = (float(inicio or 0) + float(fim or 0)) / 2
    ratio = max(0.0, min(1.0, meio / total))

    n = len(sentences)
    centro = max(0, min(n - 1, int(ratio * (n - 1))))

    janela_ini = max(0, centro - 4)
    janela_fim = min(n, centro + 5)
    candidatos = sentences[janela_ini:janela_fim]

    return _clean_text(max(candidatos, key=lambda s: _score_frase(s, contexto, emocao)))


def _nivel_confianca(trecho: str, emocao: str, contexto: str, inicio: float, fim: float, vocal: Dict[str, Any], discurso: Dict[str, Any]) -> Dict[str, Any]:
    score = 0
    motivos = []

    if trecho and len(trecho) >= 20:
        score += 25
        motivos.append("trecho real identificado")

    if emocao and emocao != "Indefinido":
        score += 20
        motivos.append("emoção comercial detectada")

    if contexto in ["abertura", "desenvolvimento", "fechamento"]:
        score += 10
        motivos.append("contexto temporal identificado")

    if _extract_keywords(trecho):
        score += 15
        motivos.append("palavras-chave comerciais no trecho")

    if _safe_float(vocal.get("energia_vocal", 0)) > 0:
        score += 10
        motivos.append("sinal vocal disponível")

    if _safe_float(discurso.get("clareza", 0)) > 0 or _safe_float(discurso.get("persuasao", 0)) > 0:
        score += 10
        motivos.append("sinal discursivo disponível")

    if fim > inicio:
        score += 10
        motivos.append("intervalo temporal válido")

    if score >= 75:
        nivel = "Alta"
    elif score >= 50:
        nivel = "Média"
    else:
        nivel = "Baixa"

    return {"score": score, "nivel": nivel, "motivos": motivos}


def _causa_especifica(segment: str, contexto: str, emocao: str, vocal: Dict[str, Any], discurso: Dict[str, Any]) -> str:
    tema = _detectar_tema(segment)
    intencao = _detectar_intencao(segment, contexto)
    s = _normalize(segment)

    clareza = _safe_float(discurso.get("clareza", 0))
    energia = _safe_float(vocal.get("energia_vocal", 0))
    fluidez = _safe_float(vocal.get("fluidez", 0))

    if emocao == "Perda de interesse":
        if intencao == "diagnóstico de necessidade":
            return "a necessidade apareceu no diálogo, mas não foi aprofundada com uma pergunta que revelasse uso, urgência ou motivação de compra"

        if intencao == "negociação de preço":
            return "a conversa entrou em preço sem sustentar claramente o valor percebido antes da objeção"

        if intencao == "tentativa de fechamento":
            return "houve tentativa de avanço, mas sem reforçar benefício ou reduzir risco antes de conduzir o próximo passo"

        if contexto == "abertura":
            return "a abertura não apresentou rapidamente uma promessa de valor, dor do cliente ou motivo forte para continuar ouvindo"

        if tema == "valor":
            return "o valor foi mencionado, mas sem prova, exemplo ou consequência prática para o cliente"

        if clareza > 0 and clareza < 55:
            return "a mensagem ficou pouco clara e dificultou a compreensão do benefício"

        if fluidez > 0 and fluidez < 45:
            return "a fala perdeu continuidade, reduzindo o ritmo comercial"

        if energia > 0 and energia < 45:
            return "a baixa energia vocal reduziu autoridade e impacto"

        return "o trecho perdeu força comercial por falta de objetividade ou progressão clara"

    if emocao == "Atenção moderada":
        if intencao == "diagnóstico de necessidade":
            return "o cliente acompanhou a conversa, mas ainda faltou transformar a resposta dele em diagnóstico comercial"

        if intencao == "apresentação de valor":
            return "a proposta foi acompanhada, mas faltou prova concreta ou exemplo para tornar o valor mais evidente"

        if intencao == "negociação de preço":
            return "o preço foi compreendido, mas ainda precisava ser ancorado em benefício percebido"

        return "houve atenção, mas sem elemento forte o suficiente para elevar o engajamento"

    if emocao == "Alto engajamento":
        if intencao == "diagnóstico de necessidade":
            return "a fala se conectou com uma necessidade real do cliente"
        if intencao == "apresentação de valor":
            return "o trecho aproximou valor percebido e interesse do cliente"
        if intencao == "tentativa de fechamento":
            return "o momento criou boa oportunidade para avançar a conversa"
        return "houve boa conexão entre fala e interesse percebido"

    if emocao == "Resistência comercial":
        if tema == "preço":
            return "o preço pode ter gerado objeção porque o valor ainda não estava forte o suficiente"
        return "o trecho pode ter aumentado dúvida, risco percebido ou insegurança"

    return "o trecho trouxe um sinal relevante da dinâmica comercial"


def _acao_especifica(contexto: str, emocao: str, segment: str) -> str:
    tema = _detectar_tema(segment)
    intencao = _detectar_intencao(segment, contexto)
    trecho_curto = _clean_text(segment)[:90]

    if emocao == "Perda de interesse":
        if intencao == "diagnóstico de necessidade":
            return f"aprofunde a resposta do cliente no trecho \"{trecho_curto}\" perguntando uso, urgência ou motivo da compra"

        if intencao == "negociação de preço":
            return "antes de falar preço, apresente benefício, prova e percepção de valor"

        if intencao == "tentativa de fechamento":
            return "antes de avançar para o próximo passo, reforce o principal benefício e reduza o risco percebido"

        if contexto == "abertura":
            return "substitua a abertura genérica por uma pergunta ligada à dor, objetivo ou intenção do cliente"

        if tema == "valor":
            return "transforme o benefício em exemplo prático para o cliente visualizar ganho real"

        return "encurte a explicação e destaque o ponto de valor mais importante"

    if emocao == "Atenção moderada":
        if intencao == "diagnóstico de necessidade":
            return f"use o trecho \"{trecho_curto}\" como gancho para uma pergunta consultiva"
        if intencao == "negociação de preço":
            return "reforce valor percebido antes de defender ou repetir preço"
        if intencao == "apresentação de valor":
            return "adicione exemplo concreto, prova ou comparação para tornar o valor mais evidente"
        return "adicione prova, comparação ou exemplo prático para aumentar engajamento"

    if emocao == "Alto engajamento":
        return "repita esse padrão de fala nos próximos momentos e use como ponte para o fechamento"

    if emocao == "Resistência comercial":
        return "valide a objeção, reduza risco percebido e retome o valor principal antes de avançar"

    return "torne a fala mais específica para a situação do cliente"


def _contraste(item: Dict[str, Any], momentos_contextuais: List[Dict[str, Any]]) -> str:
    contexto = item["contexto"]
    emocao = item["emocao_negocio"]

    houve_alto = any(m.get("emocao_negocio") == "Alto engajamento" for m in momentos_contextuais)

    if emocao in ["Perda de interesse", "Resistência comercial"] and houve_alto:
        return "Havia sinal anterior de interesse, mas ele não foi convertido em avanço comercial."

    if contexto == "abertura" and emocao == "Perda de interesse":
        return "O problema aparece logo no início, antes de o cliente receber uma proposta de valor clara."

    if contexto == "fechamento" and emocao == "Perda de interesse":
        return "O ponto crítico ocorre em um momento de alto impacto, quando a conversa deveria caminhar para decisão."

    return ""


def _formatar_insight(tipo: str, item: Dict[str, Any], todos: List[Dict[str, Any]]) -> str:
    contexto = item["contexto"]
    causa = item["causa"]
    acao = item["acao"]
    trecho = item["trecho"]
    confianca = item["confianca"]["nivel"]
    intencao = item["intencao"]
    impacto = item["impacto"]
    contraste = _contraste(item, todos)

    if len(trecho) > 130:
        trecho = trecho[:130] + "..."

    prefixo = {
        "Alta": "Ponto confirmado",
        "Média": "Sinal provável",
        "Baixa": "Sinal inconclusivo",
    }.get(confianca, "Sinal observado")

    impacto_txt = "alto impacto" if impacto >= 7 else "impacto moderado" if impacto >= 4 else "baixo impacto"

    if tipo == "funcionou":
        return f"{prefixo} ({impacto_txt}): no {contexto}, a intenção foi {intencao} e houve sinal positivo porque {causa}. Trecho: \"{trecho}\"."

    if tipo == "prejudicou":
        extra = f" {contraste}" if contraste else ""
        return f"{prefixo} ({impacto_txt}): no {contexto}, a intenção foi {intencao}, mas o vídeo perdeu força porque {causa}. Trecho: \"{trecho}\".{extra}"

    if confianca == "Baixa":
        return f"Sinal inconclusivo: há pouca evidência para afirmar uma falha clara. Mesmo assim, revise o trecho \"{trecho}\" antes de concluir."

    return f"{prefixo} ({impacto_txt}): no {contexto}, {acao}."


def _dedup_por_intencao(items: List[str]) -> List[str]:
    resultado = []
    vistos = set()

    for item in items:
        chave = _normalize(item)
        chave = re.sub(r'"[^"]+"', '"TRECHO"', chave)
        chave = chave[:120]

        if chave in vistos:
            continue
        vistos.add(chave)
        resultado.append(item)

    return resultado


def enriquecer_diagnostico_contextual(
    diagnostico: Dict[str, Any],
    transcription_path: str,
    metrics: Dict[str, Any],
    vocal: Dict[str, Any],
    discurso: Dict[str, Any],
    multimodal: Dict[str, Any],
    momentos: List[Dict[str, Any]],
) -> Dict[str, Any]:
    diagnostico = dict(diagnostico or {})

    texto = ""
    if transcription_path and os.path.exists(transcription_path):
        try:
            texto = open(transcription_path, "r", encoding="utf-8").read()
        except Exception:
            texto = ""

    sentences = _split_sentences(texto)
    segmentos_transcricao = carregar_segmentos_transcricao(transcription_path)

    total_seg = _safe_float(metrics.get("duracao_total_segundos", 0), 0)
    if total_seg <= 0:
        try:
            total_seg = max(_safe_float(m.get("fim_segundos", 0), 0) for m in (metrics.get("momentos_impacto") or []))
        except Exception:
            total_seg = 60.0

    momentos_contextuais = []

    for m in (metrics.get("momentos_impacto") or []):
        inicio = _safe_float(m.get("inicio_segundos", 0), 0)
        fim = _safe_float(m.get("fim_segundos", inicio + 3), inicio + 3)
        emocao_negocio = _rotulo_negocio(str(m.get("emocao", "")))
        contexto = _contexto_por_tempo(inicio, fim, total_seg)
        trecho_fallback = _pick_segment_by_ratio(sentences, inicio, fim, total_seg, contexto, emocao_negocio)
        trecho = escolher_trecho_por_tempo(
            segmentos_transcricao,
            inicio,
            fim,
            contexto,
            emocao_negocio,
            trecho_fallback,
        )
        tema = _detectar_tema(trecho)
        intencao = _detectar_intencao(trecho, contexto)
        confianca = _nivel_confianca(trecho, emocao_negocio, contexto, inicio, fim, vocal, discurso)
        impacto = _peso_impacto(contexto, tema, intencao, emocao_negocio)

        item = {
            "inicio_segundos": inicio,
            "fim_segundos": fim,
            "contexto": contexto,
            "emocao_negocio": emocao_negocio,
            "trecho": trecho,
            "tema": tema,
            "intencao": intencao,
            "impacto": impacto,
            "causa": _causa_especifica(trecho, contexto, emocao_negocio, vocal, discurso),
            "acao": _acao_especifica(contexto, emocao_negocio, trecho),
            "palavras_chave": _extract_keywords(trecho),
            "confianca": confianca,
        }

        momentos_contextuais.append(item)

    momentos_contextuais = sorted(momentos_contextuais, key=lambda x: (x["impacto"], x["confianca"]["score"]), reverse=True)

    funcionou = []
    prejudicou = []
    melhorar = []

    for item in momentos_contextuais:
        nivel = item["confianca"]["nivel"]

        if item["emocao_negocio"] == "Alto engajamento" and nivel in ["Alta", "Média"]:
            funcionou.append(_formatar_insight("funcionou", item, momentos_contextuais))

        elif item["emocao_negocio"] in ["Perda de interesse", "Resistência comercial"]:
            if nivel in ["Alta", "Média"]:
                prejudicou.append(_formatar_insight("prejudicou", item, momentos_contextuais))
                melhorar.append(_formatar_insight("melhorar", item, momentos_contextuais))
            else:
                melhorar.append(_formatar_insight("melhorar", item, momentos_contextuais))

        elif item["emocao_negocio"] == "Atenção moderada" and nivel in ["Alta", "Média"]:
            melhorar.append(_formatar_insight("melhorar", item, momentos_contextuais))

    if funcionou:
        diagnostico["o_que_funcionou"] = _dedup_por_intencao(funcionou)[:3]
    else:
        diagnostico["o_que_funcionou"] = [
            "Não houve evidência suficiente de um ponto comercial forte. Isso não significa que o pitch foi ruim, apenas que o vídeo não apresentou um sinal positivo claro."
        ]

    if prejudicou:
        diagnostico["o_que_prejudicou"] = _dedup_por_intencao(prejudicou)[:3]
    else:
        diagnostico["o_que_prejudicou"] = [
            "Não houve evidência forte o suficiente para afirmar um ponto crítico com segurança."
        ]

    if melhorar:
        diagnostico["o_que_melhorar"] = _dedup_por_intencao(melhorar)[:4]
    else:
        diagnostico["o_que_melhorar"] = [
            "A análise não encontrou um ponto específico de correção com confiança alta. Recomenda-se revisar manualmente os principais trechos do pitch."
        ]

    diagnostico["momentos_contextuais"] = momentos_contextuais[:5]

    diagnostico = analisar_inteligencia_comercial(
        texto,
        diagnostico,
        metrics,
        vocal,
        discurso,
        multimodal,
        momentos,
    )

    diagnostico = gerar_insights_consultivos(
        diagnostico,
        texto,
        metrics,
        vocal,
        discurso,
        multimodal,
        momentos,
    )

    return diagnostico
