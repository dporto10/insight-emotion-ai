import json
import os
import re


PALAVRAS_CONFIANCA = {
    "resultado", "resultados", "vantagem", "vantagens", "seguranca", "confianca",
    "garantia", "crescimento", "economia", "lucro", "eficiencia", "melhoria",
    "solucao", "solucoes", "beneficio", "beneficios", "valor", "oportunidade",
    "estrategia", "performance", "conversao", "aumento", "reduzir", "otimizar"
}

PALAVRAS_HESITACAO = {
    "talvez", "acho", "mais ou menos", "provavelmente", "quem sabe",
    "tipo", "assim", "hum", "eh", "ne", "nao sei", "pode ser"
}

PALAVRAS_FECHAMENTO = {
    "proximo passo", "vamos avancar", "fechar", "fechamento", "contrato",
    "proposta", "prazo", "entrega", "assinatura", "implementar",
    "comecar", "seguir", "agendar", "alinhamento"
}

PALAVRAS_OBJECAO = {
    "caro", "risco", "duvida", "dificil", "problema", "medo",
    "barreira", "obstaculo", "demora", "incerteza"
}


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def _count_occurrences(text: str, terms) -> int:
    total = 0
    for term in terms:
        total += len(re.findall(r"\b" + re.escape(term) + r"\b", text))
    return total


def analyze_discourse(transcription_path: str, audio_json_path: str, output_json: str) -> dict:
    if not os.path.exists(transcription_path):
        raise FileNotFoundError(f"Transcricao nao encontrada: {transcription_path}")

    with open(transcription_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    text_lower = text.lower()
    clean_words = re.findall(r"\b[\wÀ-ÿ\-]+\b", text_lower, flags=re.UNICODE)
    total_words = len(clean_words)

    total_sentences = max(1, len(re.findall(r"[.!?]+", text)))
    avg_sentence_len = total_words / total_sentences if total_sentences else total_words

    confidence_hits = _count_occurrences(text_lower, PALAVRAS_CONFIANCA)
    hesitation_hits = _count_occurrences(text_lower, PALAVRAS_HESITACAO)
    closing_hits = _count_occurrences(text_lower, PALAVRAS_FECHAMENTO)
    objection_hits = _count_occurrences(text_lower, PALAVRAS_OBJECAO)

    filler_ratio = hesitation_hits / max(1, total_words)
    confidence_ratio = confidence_hits / max(1, total_words)

    structure_bonus = 0.0
    if 8 <= avg_sentence_len <= 22:
        structure_bonus = 18.0
    elif 6 <= avg_sentence_len <= 28:
        structure_bonus = 10.0

    clarity_score = _clamp(
        52.0
        + structure_bonus
        - (filler_ratio * 400.0)
        - min(18.0, abs(avg_sentence_len - 16.0) * 1.2)
    )

    verbal_confidence_score = _clamp(
        40.0
        + (confidence_hits * 7.0)
        + (closing_hits * 5.0)
        - (hesitation_hits * 6.0)
        - (objection_hits * 2.0)
    )

    persuasion_score = _clamp(
        35.0
        + (confidence_hits * 6.0)
        + (closing_hits * 6.0)
        - (hesitation_hits * 4.0)
    )

    closing_strength_score = _clamp(
        25.0
        + (closing_hits * 15.0)
        - (hesitation_hits * 3.0)
    )

    words_per_minute = 0.0
    if os.path.exists(audio_json_path):
        with open(audio_json_path, "r", encoding="utf-8") as f:
            audio_data = json.load(f)
        duration = float(audio_data.get("duracao_segundos", 0.0))
        if duration > 0:
            words_per_minute = round((total_words / duration) * 60.0, 2)

    result = {
        "total_palavras": total_words,
        "palavras_confianca": confidence_hits,
        "palavras_hesitacao": hesitation_hits,
        "palavras_fechamento": closing_hits,
        "palavras_objecao": objection_hits,
        "clareza": round(clarity_score, 2),
        "confianca_verbal": round(verbal_confidence_score, 2),
        "persuasao": round(persuasion_score, 2),
        "forca_fechamento": round(closing_strength_score, 2),
        "palavras_por_minuto": words_per_minute
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    return result
