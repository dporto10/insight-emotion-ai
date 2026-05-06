import json
import os


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def build_multimodal_analysis(metricas: dict, vocal: dict, discurso: dict, output_json: str) -> dict:
    engagement = float(metricas.get("engagement_score", 0.0))
    energia = float(vocal.get("energia_vocal", 0.0))
    fluidez = float(vocal.get("fluidez", 0.0))
    estabilidade = float(vocal.get("estabilidade_vocal", 0.0))
    clareza = float(discurso.get("clareza", 0.0))
    confianca_verbal = float(discurso.get("confianca_verbal", 0.0))
    persuasao = float(discurso.get("persuasao", 0.0))
    fechamento = float(discurso.get("forca_fechamento", 0.0))

    score_integrado = _clamp(
        (engagement * 0.35)
        + (energia * 0.10)
        + (fluidez * 0.12)
        + (estabilidade * 0.08)
        + (clareza * 0.12)
        + (confianca_verbal * 0.12)
        + (persuasao * 0.08)
        + (fechamento * 0.03)
    )

    if score_integrado >= 75:
        diagnostico = "Comunicacao comercial forte"
    elif score_integrado >= 55:
        diagnostico = "Comunicacao comercial consistente"
    else:
        diagnostico = "Comunicacao comercial com pontos de melhoria"

    if engagement < 45 and confianca_verbal >= 65:
        leitura = "Baixa expressividade facial, mas boa sustentacao verbal."
    elif engagement >= 55 and confianca_verbal < 50:
        leitura = "Boa resposta visual, mas discurso pouco convincente."
    elif energia < 35 and fluidez < 45:
        leitura = "Voz com baixa energia e fluidez limitada."
    else:
        leitura = "Sinais faciais, vocais e discursivos relativamente alinhados."

    recomendacoes = []

    if energia < 40:
        recomendacoes.append("Elevar energia vocal nos trechos centrais da apresentacao.")
    if fluidez < 45:
        recomendacoes.append("Reduzir pausas longas e melhorar continuidade da fala.")
    if clareza < 55:
        recomendacoes.append("Simplificar o discurso e deixar a proposta mais direta.")
    if confianca_verbal < 55:
        recomendacoes.append("Reforcar linguagem de seguranca, beneficio e resultado.")
    if fechamento < 45:
        recomendacoes.append("Fortalecer chamada para acao e encerramento comercial.")

    if not recomendacoes:
        recomendacoes.append("Manter a estrutura atual e testar pequenas melhorias nos pontos de maior impacto.")

    result = {
        "score_integrado": round(score_integrado, 2),
        "diagnostico": diagnostico,
        "leitura_integrada": leitura,
        "recomendacoes": recomendacoes
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    return result
