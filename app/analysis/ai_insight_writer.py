
import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List


def _load_local_env():
    """
    Carrega variáveis do .env automaticamente.
    Procura o .env na pasta atual e nas pastas acima.
    """
    from pathlib import Path as _Path
    import os as _os

    candidates = [
        _Path.cwd() / ".env",
        _Path(__file__).resolve().parents[2] / ".env",
        _Path(__file__).resolve().parents[3] / ".env" if len(_Path(__file__).resolve().parents) > 3 else None,
    ]

    for env_path in candidates:
        if env_path is None or not env_path.exists():
            continue

        try:
            for line in env_path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
                line = line.strip()

                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip().replace("\ufeff", "")
                value = value.strip().strip('"').strip("'")

                if key and value and not _os.getenv(key):
                    _os.environ[key] = value

            return str(env_path)
        except Exception as e:
            print(f"Aviso: falha ao carregar .env em {env_path}: {e}")

    return None



def _safe_list(value):
    if isinstance(value, list):
        return value
    if value:
        return [str(value)]
    return []


def _cortar(texto: str, limite: int = 4500) -> str:
    texto = (texto or "").strip()
    if len(texto) <= limite:
        return texto
    return texto[:limite] + "\n[TRANSCRIÇÃO CORTADA PARA CABER NO CONTEXTO]"


def _build_payload(
    diagnostico: Dict[str, Any],
    texto: str,
    metrics: Dict[str, Any],
    vocal: Dict[str, Any],
    discurso: Dict[str, Any],
    multimodal: Dict[str, Any],
    momentos: Any,
) -> Dict[str, Any]:
    return {
        "diagnostico_atual": diagnostico,
        "transcricao": _cortar(texto),
        "metricas_emocionais": metrics,
        "analise_vocal": vocal,
        "analise_discurso": discurso,
        "analise_multimodal": multimodal,
        "momentos_venda": momentos,
        "instrucao": (
            "Gere uma análise consultiva de vendas fiel ao vídeo. "
            "Não use frases genéricas. Use evidências da transcrição. "
            "Diferencie venda ruim, venda concluída, venda subaproveitada e análise inconclusiva. "
            "Considere resultado real da venda, preço, objeção, pagamento, fechamento, emoção facial e voz. "
            "Se a evidência for fraca, diga que é inconclusivo em vez de inventar conclusão."
        ),
    }


def _fallback_consultivo(
    diagnostico: Dict[str, Any],
    texto: str,
    metrics: Dict[str, Any],
    vocal: Dict[str, Any],
    discurso: Dict[str, Any],
    multimodal: Dict[str, Any],
    momentos: Any,
) -> Dict[str, Any]:
    resultado = diagnostico.get("resultado_venda", "Não identificado")
    fechamento_real = diagnostico.get("fechamento_real", "Não identificado")
    analise_real = diagnostico.get("analise_comercial_real", {}) or {}

    preco = analise_real.get("preco", {}) or {}
    necessidade = analise_real.get("necessidade", {}) or {}

    energia = float(vocal.get("energia_vocal", 0) or 0)
    fluidez = float(vocal.get("fluidez", 0) or 0)
    clareza = float(discurso.get("clareza", 0) or 0)
    score = float(multimodal.get("score_integrado", 0) or 0)
    predominante = metrics.get("emocao_predominante", "Indefinido")

    funcionou = []
    prejudicou = []
    melhorar = []

    if resultado == "Venda concluída":
        funcionou.append(
            "Venda concluída: há sinal de decisão do cliente na conversa. A leitura correta é de venda funcional, não de fracasso comercial."
        )
        if fechamento_real == "Positivo":
            funcionou.append(
                "O fechamento foi positivo no resultado, embora pareça mais passivo do que conduzido pelo vendedor."
            )
    else:
        funcionou.append(
            "Não há evidência forte de venda concluída. A análise deve priorizar intenção do cliente, objeção e avanço de conversa."
        )

    if necessidade.get("nivel") in ["Baixa", "Superficial"]:
        prejudicou.append(
            f"Exploração de necessidade {str(necessidade.get('nivel', 'baixa')).lower()}: a conversa poderia investigar melhor uso, preferência, urgência ou motivo de compra."
        )
        melhorar.append(
            "Faça uma pergunta consultiva antes de apresentar opções: para qual uso, preferência principal, limite de preço ou problema que o cliente quer resolver."
        )

    if preco.get("houve_preco"):
        prejudicou.append(
            f"{preco.get('tipo', 'Preço identificado')}: {preco.get('impacto', 'o preço apareceu como parte relevante da decisão.')}"
        )
        melhorar.append(
            "Antes de negociar preço, conecte a oferta a um benefício concreto para reduzir comparação apenas por valor."
        )

    if energia > 0 and energia < 45:
        prejudicou.append(
            "A energia vocal ficou baixa para uma abordagem comercial; isso pode reduzir entusiasmo e percepção de segurança."
        )
        melhorar.append(
            "Aumente variação de tom nos momentos de valor, preço e fechamento."
        )

    if clareza > 0 and clareza < 58:
        melhorar.append(
            "Simplifique a explicação: diga primeiro o benefício principal, depois detalhe produto, preço e forma de pagamento."
        )

    if predominante == "Neutro":
        melhorar.append(
            "A predominância neutra não significa rejeição; trate como venda racional e compense com perguntas e benefícios mais objetivos."
        )

    leitura = (
        f"Leitura consultiva: resultado={resultado}, fechamento={fechamento_real}, "
        f"emoção predominante={predominante}, energia={energia:.1f}, fluidez={fluidez:.1f}, "
        f"clareza={clareza:.1f}, score integrado={score:.1f}. "
        "A análise deve considerar o resultado real da conversa antes de rotular o pitch como fraco."
    )

    return {
        "pitch_label": diagnostico.get("pitch_label", "Análise comercial"),
        "leitura_consultiva": leitura,
        "o_que_funcionou": funcionou[:4],
        "o_que_prejudicou": prejudicou[:4] if prejudicou else ["Não houve evidência forte o suficiente para afirmar um ponto crítico com segurança."],
        "o_que_melhorar": melhorar[:4] if melhorar else ["Revisar manualmente os principais trechos para identificar oportunidades específicas de melhoria."],
    }


def _parse_json(texto: str) -> Dict[str, Any]:
    texto = (texto or "").strip()

    if texto.startswith("```"):
        texto = texto.strip("`")
        texto = texto.replace("json", "", 1).strip()

    inicio = texto.find("{")
    fim = texto.rfind("}")

    if inicio >= 0 and fim > inicio:
        texto = texto[inicio:fim + 1]

    return json.loads(texto)



def _chamar_openai(payload: Dict[str, Any]) -> Dict[str, Any]:
    _load_local_env()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não configurada.")

    model = os.getenv("INSIGHT_LLM_MODEL", "gpt-4.1-mini").strip()

    system_prompt = """
Você é uma IA especialista em análise comercial de vídeos de venda.

Sua tarefa é gerar insights consultivos, sinceros e específicos para o vídeo analisado.

Regras obrigatórias:
1. Não use frases genéricas como "melhore a comunicação" sem explicar com base no vídeo.
2. Use evidências reais da transcrição.
3. Se houve venda concluída, nunca trate como fracasso. Classifique como venda concluída, venda funcional ou venda subaproveitada.
4. Diferencie erro crítico, ponto de otimização, estilo de venda e evidência inconclusiva.
5. Use emoção facial e voz como apoio, não como sentença absoluta.
6. Neutralidade facial não significa automaticamente desinteresse.
7. Explique o impacto comercial: conversão, margem, confiança, objeção, preço ou fechamento.
8. Responda apenas JSON válido, sem markdown.
9. Todos os textos devem ser específicos do vídeo analisado.
10. O plano estratégico deve mudar conforme o produto, necessidade do cliente, preço, forma de pagamento, voz e emoção. Mantenha cada prioridade objetiva e com no máximo duas linhas.
11. As evidências da conversa devem usar trechos reais ou bem próximos da transcrição.
12. Não repita sempre as mesmas recomendações. Varie conforme o contexto comercial.
13. O campo evidencias_conversa é obrigatório.
14. Em evidencias_conversa, cada item deve ter trecho, interpretação e sugestão conectados entre si. Se a transcrição estiver confusa, indique baixa clareza em vez de forçar conclusão.
15. Não use interpretação de fechamento em trecho de abertura.
16. Não use sugestão genérica. A sugestão deve responder ao problema daquele trecho específico.
17. Se a transcrição estiver confusa, diga isso na interpretação em vez de inventar.
13. Se a venda foi concluída, explique se foi uma venda conduzida, passiva, negociada ou subaproveitada.
14. Se houve preço/desconto/Pix/cartão, explique o impacto disso na margem, conversão ou decisão.

Formato obrigatório:
{
  "pitch_label": "...",
  "resumo_executivo": "Resumo curto, direto e específico da venda analisada.",
  "leitura_consultiva": "...",
  "resultado_detectado": "...",
  "preco_negociacao": "...",
  "diagnostico_cards": {
    "conexao_inicial": "Status + frase curta, exemplo: Médio — abertura útil, mas superficial.",
    "apresentacao_valor": "...",
    "reacao_preco": "...",
    "fechamento": "...",
    "potencial_comercial": "..."
  },
  "o_que_funcionou": ["...", "..."],
  "o_que_prejudicou": ["...", "..."],
  "o_que_melhorar": ["...", "..."],
  "plano_estrategico": {
    "prioridades": ["...", "...", "..."],
    "complementares": ["...", "...", "..."]
  },
  "evidencias_conversa": [
    {
      "titulo": "...",
      "trecho": "...",
      "interpretacao": "...",
      "sugestao": "..."
    }
  ]
}

"""

    user_prompt = (
        "Analise os dados abaixo como um consultor comercial. "
        "Gere insights específicos para este vídeo, evitando frases padrão.\n\n"
        + json.dumps(payload, ensure_ascii=False)
    )

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.35,
        "max_tokens": 1500,
        "response_format": {"type": "json_object"}
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        erro = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Erro OpenAI HTTP {e.code}: {erro}") from e

    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    if not content:
        raise RuntimeError("Resposta vazia da OpenAI.")

    return _parse_json(content)




def _norm_local(texto: str) -> str:
    import unicodedata
    texto = (texto or "").lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def _classificar_trecho_evidencia(frase: str) -> str:
    f = _norm_local(frase)

    if any(x in f for x in ["quanto", "preco", "preço", "valor", "r$", "reais", "desconto", "pix", "cartao", "cartão", "dinheiro"]):
        return "Preço e decisão"

    if any(x in f for x in ["vou pagar", "pagar no pix", "vou levar", "vou comprar", "gostei", "fica bom", "ta bom", "tá bom", "vou querer"]):
        return "Fechamento"

    if any(x in f for x in ["preciso", "precisa", "queria", "quero", "necessidade", "procurando", "bolsa", "trabalho", "faculdade", "academia", "dia a dia", "preferencia", "preferência"]):
        return "Necessidade do cliente"

    if any(x in f for x in ["produto", "marca", "fragrancia", "fragrância", "cheiro", "leve", "doce", "compacto", "duracao", "duração", "beneficio", "benefício"]):
        return "Apresentação de valor"

    return "Condução da conversa"


def _interpretar_trecho_evidencia(frase: str, titulo: str) -> str:
    f = _norm_local(frase)

    if titulo == "Necessidade do cliente":
        if any(x in f for x in ["faculdade", "academia", "trabalho", "bolsa", "dia a dia"]):
            return "O cliente apresentou uma rotina clara de uso. Esse é um bom sinal comercial, porque permite adaptar a oferta à necessidade real, não apenas ao produto."
        if any(x in f for x in ["preferencia", "preferência", "marca"]):
            return "O vendedor buscou entender preferência de marca, o que ajuda a filtrar opções e aumenta a chance de aderência da oferta."
        return "O cliente demonstrou uma necessidade ou intenção de compra, mas ainda havia espaço para aprofundar melhor o motivo da escolha."

    if titulo == "Apresentação de valor":
        if any(x in f for x in ["leve", "compacto", "bolsa", "duracao", "duração", "cheiro"]):
            return "O trecho conecta características do produto com critérios importantes para o cliente. A oportunidade é transformar essa característica em benefício direto."
        return "O produto foi apresentado, mas o valor poderia ficar mais claro se fosse ligado a um ganho prático para o cliente."

    if titulo == "Preço e decisão":
        if any(x in f for x in ["desconto", "pix", "menor"]):
            return "Houve negociação de preço ou condição de pagamento. Isso indica avanço na decisão, mas também risco de perda de margem se o valor não for reforçado antes."
        if any(x in f for x in ["r$", "reais", "preco", "preço", "valor"]):
            return "O preço entrou como parte importante da decisão. Nesse momento, o vendedor precisa sustentar o valor para evitar comparação apenas por custo."
        return "O trecho mostra sensibilidade a preço ou busca por condição de compra."

    if titulo == "Fechamento":
        return "O cliente sinalizou avanço para compra ou pagamento. Esse é um sinal positivo de conversão, mesmo que o fechamento possa ter sido mais passivo do que conduzido."

    if any(x in f for x in ["boa noite", "oi", "olá", "ola"]):
        return "A abertura foi educada, mas ainda precisa criar rapidamente contexto comercial para prender mais atenção."

    return "O trecho ajuda a entender a condução da venda, mas não traz sozinho uma conclusão comercial forte."


def _sugerir_por_evidencia(frase: str, titulo: str) -> str:
    f = _norm_local(frase)

    if titulo == "Necessidade do cliente":
        if any(x in f for x in ["faculdade", "academia", "trabalho", "bolsa", "dia a dia"]):
            return "Aprofunde com uma pergunta prática: onde o cliente mais usaria o produto, qual característica é indispensável e qual limite de preço faz sentido."
        return "Faça uma pergunta de aprofundamento antes de apresentar a solução, para entender uso, preferência e prioridade do cliente."

    if titulo == "Apresentação de valor":
        return "Converta característica em benefício. Em vez de apenas descrever o produto, explique como ele facilita a rotina ou resolve a necessidade citada."

    if titulo == "Preço e decisão":
        return "Antes de conceder desconto ou reforçar preço, retome o benefício principal e mostre por que a opção vale o investimento."

    if titulo == "Fechamento":
        return "Conduza o próximo passo com clareza: confirme forma de pagamento, quantidade e decisão final, sem deixar o fechamento depender apenas do cliente."

    return "Use esse ponto para tornar a fala mais objetiva e conectada à intenção do cliente."


def _gerar_evidencias_fallback(texto: str, diagnostico: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Gera evidências consultivas locais sem misturar insight de um trecho com outro.
    Cada interpretação é criada a partir do próprio trecho.
    """
    import re

    texto = (texto or "").strip()
    frases = [f.strip() for f in re.split(r"(?<=[.!?])\s+", texto) if len(f.strip()) > 25]

    if not frases:
        return [{
            "titulo": "Evidência indisponível",
            "trecho": "A transcrição não trouxe trecho suficiente para evidência textual confiável.",
            "interpretacao": "A análise deve ser considerada inconclusiva nesse ponto.",
            "sugestao": "Teste com áudio mais claro ou vídeo mais curto para melhorar a leitura da IA.",
        }]

    # Escolhe trechos variados por importância comercial
    selecionadas = []
    categorias_usadas = set()

    def score(frase):
        f = _norm_local(frase)
        pontos = 0
        for termo in ["preciso", "queria", "necessidade", "preço", "preco", "valor", "desconto", "pix", "gostei", "vou pagar", "vou levar", "marca", "produto", "benefício", "beneficio"]:
            if termo in f:
                pontos += 3
        if "?" in frase:
            pontos += 2
        return pontos

    frases_ordenadas = sorted(frases, key=score, reverse=True)

    for frase in frases_ordenadas:
        titulo = _classificar_trecho_evidencia(frase)

        # evita quatro cards do mesmo tipo
        if titulo in categorias_usadas and len(categorias_usadas) < 3:
            continue

        categorias_usadas.add(titulo)
        selecionadas.append((titulo, frase))

        if len(selecionadas) >= 4:
            break

    # se faltou evidência, completa com primeiras frases úteis
    for frase in frases:
        if len(selecionadas) >= 4:
            break
        if not any(frase == s[1] for s in selecionadas):
            selecionadas.append((_classificar_trecho_evidencia(frase), frase))

    evidencias = []
    for titulo, frase in selecionadas[:4]:
        evidencias.append({
            "titulo": titulo,
            "trecho": frase[:280],
            "interpretacao": _interpretar_trecho_evidencia(frase, titulo),
            "sugestao": _sugerir_por_evidencia(frase, titulo),
        })

    return evidencias[:4]


def _validar_evidencias_ia(evidencias: Any, texto: str, diagnostico: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Se a IA devolver evidências genéricas ou sem nexo, substitui por evidências locais melhores.
    """
    if not isinstance(evidencias, list) or not evidencias:
        return _gerar_evidencias_fallback(texto, diagnostico)

    ruins = 0
    limpas = []

    frases_genericas = [
        "use esse trecho como evidência",
        "ajustar abordagem, valor, preço ou fechamento",
        "conforme o contexto da venda",
    ]

    for ev in evidencias:
        if not isinstance(ev, dict):
            ruins += 1
            continue

        titulo = str(ev.get("titulo", "")).strip()
        trecho = str(ev.get("trecho", "")).strip()
        interpretacao = str(ev.get("interpretacao", "")).strip()
        sugestao = str(ev.get("sugestao", "")).strip()

        combinado = _norm_local(" ".join([titulo, trecho, interpretacao, sugestao]))

        if len(trecho) < 15 or len(interpretacao) < 20 or len(sugestao) < 20:
            ruins += 1
            continue

        if any(g in combinado for g in frases_genericas):
            ruins += 1
            continue

        limpas.append({
            "titulo": titulo or _classificar_trecho_evidencia(trecho),
            "trecho": trecho[:280],
            "interpretacao": interpretacao[:420],
            "sugestao": sugestao[:420],
        })

    if ruins >= 2 or len(limpas) < 2:
        return _gerar_evidencias_fallback(texto, diagnostico)

    return limpas[:4]


def gerar_insights_consultivos(
    diagnostico: Dict[str, Any],
    texto: str,
    metrics: Dict[str, Any],
    vocal: Dict[str, Any],
    discurso: Dict[str, Any],
    multimodal: Dict[str, Any],
    momentos: Any,
) -> Dict[str, Any]:
    _load_local_env()
    diagnostico = dict(diagnostico or {})
    payload = _build_payload(diagnostico, texto, metrics, vocal, discurso, multimodal, momentos)

    try:
        gerado = _chamar_openai(payload)
        origem = "llm"
    except Exception as e:
        print(f"Aviso: LLM indisponível. Usando fallback local. Motivo: {e}")
        gerado = _fallback_consultivo(diagnostico, texto, metrics, vocal, discurso, multimodal, momentos)
        origem = "fallback"

    for campo in ["pitch_label", "leitura_consultiva"]:
        if gerado.get(campo):
            diagnostico[campo] = gerado[campo]

    for campo in ["o_que_funcionou", "o_que_prejudicou", "o_que_melhorar"]:
        lista = _safe_list(gerado.get(campo))
        if lista:
            diagnostico[campo] = lista[:4]

    # Campos consultivos extras gerados pela IA
    if gerado.get("resumo_executivo"):
        diagnostico["resumo_executivo_ia"] = gerado.get("resumo_executivo")
        diagnostico["leitura_consultiva"] = gerado.get("resumo_executivo")

    if gerado.get("resultado_detectado"):
        diagnostico["resultado_venda"] = gerado.get("resultado_detectado")

    if gerado.get("preco_negociacao"):
        diagnostico["preco_negociacao_ia"] = gerado.get("preco_negociacao")

    cards = gerado.get("diagnostico_cards")
    if isinstance(cards, dict):
        if cards.get("conexao_inicial"):
            diagnostico["conexao_inicial"] = cards.get("conexao_inicial")
        if cards.get("apresentacao_valor"):
            diagnostico["apresentacao_valor"] = cards.get("apresentacao_valor")
        if cards.get("reacao_preco"):
            diagnostico["reacao_preco"] = cards.get("reacao_preco")
        if cards.get("fechamento"):
            diagnostico["fechamento"] = cards.get("fechamento")
        if cards.get("potencial_comercial"):
            diagnostico["potencial_comercial"] = cards.get("potencial_comercial")
        diagnostico["diagnostico_cards_ia"] = cards

    plano = gerado.get("plano_estrategico")
    if isinstance(plano, dict):
        diagnostico["plano_estrategico_ia"] = {
            "prioridades": _safe_list(plano.get("prioridades"))[:3],
            "complementares": _safe_list(plano.get("complementares"))[:4],
        }

    evidencias = gerado.get("evidencias_conversa")
    diagnostico["evidencias_conversa_ia"] = _validar_evidencias_ia(evidencias, texto, diagnostico)

    # Garantia: se a IA não devolver plano_estrategico,
    # monta o plano a partir dos próprios insights gerados pela IA.
    if "plano_estrategico_ia" not in diagnostico:
        prioridades_base = diagnostico.get("o_que_melhorar", []) or []
        complementares_base = diagnostico.get("o_que_prejudicou", []) or []

        diagnostico["plano_estrategico_ia"] = {
            "prioridades": prioridades_base[:3],
            "complementares": complementares_base[:3],
        }

    # Garantia: Evidências da Conversa sempre devem vir da camada consultiva.
    if not diagnostico.get("evidencias_conversa_ia"):
        diagnostico["evidencias_conversa_ia"] = _gerar_evidencias_fallback(texto, diagnostico)

    diagnostico["origem_insights_consultivos"] = origem
    return diagnostico
