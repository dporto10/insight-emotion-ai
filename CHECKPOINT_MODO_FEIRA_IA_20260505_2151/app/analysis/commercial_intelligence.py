
import re
import unicodedata
from typing import Dict, Any, List


def _normalize(text: str) -> str:
    text = (text or "").lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _contains_any(text: str, terms: List[str]) -> bool:
    t = _normalize(text)
    return any(term in t for term in terms)


def detectar_venda_concluida(texto: str) -> Dict[str, Any]:
    frases_fechamento = [
        "a gente vai comprar",
        "vou comprar",
        "vou levar",
        "vamos levar",
        "vou ficar com",
        "vamos ficar com",
        "quero uma caixa",
        "quer uma caixa",
        "pode separar",
        "pode passar",
        "fecha pra mim",
        "vamos fechar",
        "vou querer",
        "gostei do preco",
        "gostei do preço",
        "fica bom",
    ]

    texto_norm = _normalize(texto)

    for frase in frases_fechamento:
        if _normalize(frase) in texto_norm:
            return {
                "venda_concluida": True,
                "evidencia": frase,
                "confianca": "Alta",
            }

    sinais_pagamento = ["pix", "cartao", "cartão", "credito", "crédito", "dinheiro", "qr code", "qrcode"]
    sinais_decisao = ["gostei", "fica bom", "ta bom", "tá bom", "pode", "vou", "vamos", "passa", "pagar"]
    sinais_preco = ["7,50", "7.50", "10 reais", "valor", "preco", "preço", "menor"]

    tem_pagamento = _contains_any(texto, sinais_pagamento)
    tem_decisao = _contains_any(texto, sinais_decisao)
    tem_preco = _contains_any(texto, sinais_preco)

    if tem_pagamento and tem_decisao:
        return {
            "venda_concluida": True,
            "evidencia": "sinais de pagamento e aceite do cliente",
            "confianca": "Alta",
        }

    if tem_preco and tem_pagamento:
        return {
            "venda_concluida": True,
            "evidencia": "negociação de preço seguida de forma de pagamento",
            "confianca": "Média",
        }

    if _contains_any(texto, ["comprar", "levar", "pedido", "caixa"]) and _contains_any(texto, ["sim", "quero", "vamos", "pode"]):
        return {
            "venda_concluida": True,
            "evidencia": "sinais combinados de decisão de compra",
            "confianca": "Média",
        }

    return {
        "venda_concluida": False,
        "evidencia": "",
        "confianca": "Baixa",
    }


def detectar_negociacao_preco(texto: str, momentos: Any) -> Dict[str, Any]:
    preco_detectado = False

    if isinstance(momentos, dict):
        preco_detectado = bool(momentos.get("preco"))

    if _contains_any(texto, ["preco", "valor", "quanto", "desconto", "menor", "pagamento"]):
        preco_detectado = True

    if not preco_detectado:
        return {
            "houve_preco": False,
            "tipo": "Não identificado",
            "impacto": "Sem evidência clara de negociação de preço.",
        }

    if _contains_any(texto, ["menor", "desconto", "mais baixo", "baixar"]):
        return {
            "houve_preco": True,
            "tipo": "Preço negociado",
            "impacto": "Houve negociação ou busca por valor mais baixo, indicando sensibilidade a preço.",
        }

    return {
        "houve_preco": True,
        "tipo": "Preço consultado",
        "impacto": "O cliente demonstrou interesse prático ao perguntar ou reagir ao preço.",
    }


def detectar_exploracao_necessidade(texto: str) -> Dict[str, Any]:
    perguntas_consultivas = [
        "para que",
        "pra que",
        "qual uso",
        "como voce usa",
        "voce precisa",
        "o que voce procura",
        "prefere",
        "vai usar",
        "com que frequencia",
    ]

    if _contains_any(texto, perguntas_consultivas):
        return {
            "nivel": "Boa",
            "descricao": "Houve tentativa de entender a necessidade do cliente.",
        }

    if _contains_any(texto, ["procurando", "precisa", "quer"]):
        return {
            "nivel": "Superficial",
            "descricao": "A necessidade apareceu, mas poderia ser explorada com perguntas mais profundas.",
        }

    return {
        "nivel": "Baixa",
        "descricao": "Não houve evidência forte de exploração da necessidade do cliente.",
    }


def analisar_inteligencia_comercial(
    texto: str,
    diagnostico: Dict[str, Any],
    metrics: Dict[str, Any],
    vocal: Dict[str, Any],
    discurso: Dict[str, Any],
    multimodal: Dict[str, Any],
    momentos: Any,
) -> Dict[str, Any]:
    diagnostico = dict(diagnostico or {})
    texto_limpo = _clean(texto)

    venda = detectar_venda_concluida(texto_limpo)
    preco = detectar_negociacao_preco(texto_limpo, momentos)
    necessidade = detectar_exploracao_necessidade(texto_limpo)

    venda_concluida = venda["venda_concluida"]

    if venda_concluida:
        diagnostico["resultado_venda"] = "Venda concluída"
        diagnostico["fechamento_real"] = "Positivo"
        diagnostico["fechamento"] = "Bom"

        # Se a venda aconteceu, o pitch não deve ser tratado como fracasso.
        diagnostico["pitch_label"] = "Venda concluída com pontos de otimização"

        if diagnostico.get("potencial_comercial") in ["Fraco", "Não identificado"]:
            diagnostico["potencial_comercial"] = "Médio"

        if diagnostico.get("pontuacao_integrada_label") in ["Fraco", "Não identificado"]:
            diagnostico["pontuacao_integrada_label"] = "Médio"

        if preco["houve_preco"]:
            diagnostico["reacao_preco"] = "Negociada"

        leitura = (
            "A venda foi concluída, portanto o vídeo não deve ser interpretado como uma falha comercial. "
            "A leitura correta é de uma venda funcional, com oportunidade de melhorar condução, construção de valor e margem."
        )

        funcionou = [
            f"Venda concluída: o cliente indicou decisão de compra com evidência de alta confiança ({venda['evidencia']}).",
            "A conversa foi suficiente para levar o cliente à decisão, mesmo sem uma condução comercial altamente estruturada.",
        ]

        prejudicou = [
            "A venda aconteceu, mas há sinal de subaproveitamento: o cliente decidiu de forma mais passiva do que conduzida pelo vendedor.",
        ]

        if preco["houve_preco"]:
            prejudicou.append(
                f"{preco['tipo']}: {preco['impacto']} Isso pode reduzir margem quando o valor não é reforçado antes do preço."
            )

        melhorar = [
            "Antes de falar preço, reforce valor percebido com benefício, prova ou exemplo prático.",
            "Aprofunde a necessidade do cliente com uma pergunta simples sobre uso, preferência ou objetivo da compra.",
            "No fechamento, conduza o próximo passo com mais clareza em vez de depender apenas da decisão espontânea do cliente.",
        ]

        diagnostico["leitura_consultiva"] = leitura
        diagnostico["o_que_funcionou"] = funcionou[:4]
        diagnostico["o_que_prejudicou"] = prejudicou[:4]
        diagnostico["o_que_melhorar"] = melhorar[:4]

    else:
        diagnostico["resultado_venda"] = "Venda não confirmada"
        diagnostico["fechamento_real"] = "Não identificado"

        diagnostico["leitura_consultiva"] = (
            "Não há evidência suficiente de venda concluída na transcrição. "
            "A análise deve priorizar sinais de intenção, objeção, preço e avanço de conversa."
        )

    diagnostico["analise_comercial_real"] = {
        "resultado_venda": diagnostico.get("resultado_venda"),
        "fechamento_real": diagnostico.get("fechamento_real"),
        "evidencia_fechamento": venda.get("evidencia"),
        "confianca_fechamento": venda.get("confianca"),
        "preco": preco,
        "necessidade": necessidade,
    }

    return diagnostico
