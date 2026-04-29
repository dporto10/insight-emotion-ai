import json
import os
import pandas as pd


MAPA_NEGOCIO = {
    "Felicidade": "Interesse",
    "Surpresa": "Curiosidade",
    "Neutro": "Neutro",
    "Tristeza": "Desconexao",
    "Raiva": "Resistencia",
    "Medo": "Apreensao",
    "Repulsa": "Rejeicao",
    "Indefinido": "Indefinido",
    "happy": "Interesse",
    "surprise": "Curiosidade",
    "neutral": "Neutro",
    "sad": "Desconexao",
    "angry": "Resistencia",
    "fear": "Apreensao",
    "disgust": "Rejeicao",
    "unknown": "Indefinido"
}


def mapear_emocao_negocio(emocao: str) -> str:
    return MAPA_NEGOCIO.get(str(emocao).strip(), "Indefinido")


def suavizar_emocoes(lista):
    if len(lista) < 3:
        return lista

    suavizada = lista.copy()

    for i in range(1, len(lista) - 1):
        prev_e = lista[i - 1]
        curr_e = lista[i]
        next_e = lista[i + 1]

        if prev_e == next_e and curr_e != prev_e:
            suavizada[i] = prev_e

    return suavizada


def detectar_momentos_impacto(df: pd.DataFrame, top_n: int = 3, janela_segundos: float = 2.0, distancia_minima_segundos: float = 5.0):
    if df.empty:
        return []

    candidatos = df.copy()
    candidatos["score_impacto"] = candidatos["confianca"].rolling(window=3, min_periods=1).mean()

    candidatos = candidatos.sort_values("score_impacto", ascending=False).reset_index(drop=True)

    momentos = []

    for _, row in candidatos.iterrows():
        pico = float(row["tempo_segundos"])

        conflita = False
        for m in momentos:
            if abs(pico - m["pico_segundos"]) < distancia_minima_segundos:
                conflita = True
                break

        if conflita:
            continue

        inicio = max(0.0, round(pico - janela_segundos / 2.0, 2))
        fim = round(pico + janela_segundos / 2.0, 2)

        momentos.append({
            "inicio_segundos": inicio,
            "pico_segundos": round(pico, 2),
            "fim_segundos": fim,
            "emocao": str(row["emocao_negocio"]),
            "score": round(float(row["score_impacto"]), 2)
        })

        if len(momentos) >= top_n:
            break

    momentos = sorted(momentos, key=lambda x: x["pico_segundos"])
    return momentos


def calcular_metricas(csv_path: str) -> dict:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV de emocoes nao encontrado: {csv_path}")

    df = pd.read_csv(csv_path)

    if df.empty:
        raise ValueError("CSV de emocoes esta vazio")

    df["emocao_negocio"] = df["emocao"].apply(mapear_emocao_negocio)
    df["emocao_negocio"] = suavizar_emocoes(df["emocao_negocio"].tolist())
    df["confianca"] = pd.to_numeric(df["confianca"], errors="coerce").fillna(0.0)
    df["tempo_segundos"] = pd.to_numeric(df["tempo_segundos"], errors="coerce").fillna(0.0)

    total = len(df)

    positivas = ["Interesse", "Curiosidade"]
    negativas = ["Desconexao", "Resistencia", "Rejeicao", "Apreensao"]

    total_positivas = int(df["emocao_negocio"].isin(positivas).sum())
    total_negativas = int(df["emocao_negocio"].isin(negativas).sum())

    engagement_score = round((total_positivas / total) * 100, 2)
    positive_ratio = round((total_positivas / total) * 100, 2)
    negative_ratio = round((total_negativas / total) * 100, 2)

    emocao_predominante = df["emocao_negocio"].value_counts().idxmax()

    df["confianca_suavizada"] = df["confianca"].rolling(window=3, min_periods=1).mean()
    pico_row = df.loc[df["confianca_suavizada"].idxmax()]
    pico_emocional_segundos = round(float(pico_row["tempo_segundos"]), 2)
    pico_emocional_tipo = str(pico_row["emocao_negocio"])

    emocoes_queda = {"Neutro", "Desconexao", "Resistencia", "Rejeicao"}
    sequencia_minima = 3

    queda_interesse_segundos = None
    contador = 0
    inicio_queda = None

    for _, row in df.iterrows():
        emocao = row["emocao_negocio"]
        tempo = float(row["tempo_segundos"])

        if emocao in emocoes_queda:
            contador += 1
            if inicio_queda is None:
                inicio_queda = tempo
            if contador >= sequencia_minima:
                queda_interesse_segundos = round(inicio_queda, 2)
                break
        else:
            contador = 0
            inicio_queda = None

    distribuicao = (
        df["emocao_negocio"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
        .to_dict()
    )

    momentos_impacto = detectar_momentos_impacto(df, top_n=3, janela_segundos=2.0, distancia_minima_segundos=5.0)

    return {
        "total_amostras": total,
        "engagement_score": engagement_score,
        "positive_ratio": positive_ratio,
        "negative_ratio": negative_ratio,
        "emocao_predominante": emocao_predominante,
        "pico_emocional_segundos": pico_emocional_segundos,
        "pico_emocional_tipo": pico_emocional_tipo,
        "queda_interesse_segundos": queda_interesse_segundos,
        "distribuicao_emocional": distribuicao,
        "momentos_impacto": momentos_impacto
    }


def gerar_insights(metricas: dict) -> dict:
    textos = []
    recomendacoes = []

    engagement = metricas["engagement_score"]
    predominante = metricas["emocao_predominante"]
    pico_tempo = metricas["pico_emocional_segundos"]
    queda_tempo = metricas["queda_interesse_segundos"]
    momentos_impacto = metricas.get("momentos_impacto", [])

    if engagement >= 70:
        textos.append("A campanha demonstra forte capacidade de engajamento inicial.")
        recomendacoes.append("Preservar a abertura da campanha, pois ela esta capturando bem a atencao.")
    elif engagement >= 50:
        textos.append("A campanha apresenta engajamento moderado.")
        recomendacoes.append("Reforcar gatilhos criativos nos trechos centrais para elevar o envolvimento.")
    else:
        textos.append("A campanha apresenta baixo engajamento emocional.")
        recomendacoes.append("Rever a proposta visual e narrativa da campanha para aumentar conexao com o publico.")

    textos.append(f"A reacao predominante observada foi {predominante}.")
    textos.append(f"O maior pico emocional ocorreu em {pico_tempo} segundos, com predominancia de {metricas['pico_emocional_tipo']}.")

    if queda_tempo is not None:
        textos.append(f"Foi identificada uma queda de interesse em {queda_tempo} segundos.")
        recomendacoes.append(f"Revisar o trecho proximo de {queda_tempo}s para reduzir perda de interesse.")
    else:
        textos.append("Nao foi identificada queda relevante de interesse ao longo da campanha.")
        recomendacoes.append("Manter a estrutura atual, pois nao houve queda critica de interesse.")

    if momentos_impacto:
        primeiro = momentos_impacto[0]
        textos.append(
            f"O trecho de maior impacto ocorreu entre {primeiro['inicio_segundos']}s e {primeiro['fim_segundos']}s, com destaque para {primeiro['emocao']}."
        )

    if predominante in ["Desconexao", "Resistencia", "Rejeicao"]:
        recomendacoes.append("Testar uma nova abordagem criativa para reduzir reacoes negativas.")
    elif predominante == "Neutro":
        recomendacoes.append("Aumentar contraste emocional e estimulos narrativos para reduzir neutralidade.")
    else:
        recomendacoes.append("Explorar mais o gatilho criativo presente nos momentos de maior resposta positiva.")

    if momentos_impacto:
        recomendacoes.append("Considere reaproveitar os momentos de maior impacto em cortes, anuncios e aberturas de video.")

    return {
        "resumo_executivo": " ".join(textos),
        "recomendacoes": recomendacoes
    }


def salvar_json(dados: dict, caminho_saida: str) -> str:
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    return caminho_saida
