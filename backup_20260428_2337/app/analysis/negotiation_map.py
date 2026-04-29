import json
import os
import pandas as pd

def gerar_mapa_negociacao(emotions_csv_path, topicos, output_json):

    if not os.path.exists(emotions_csv_path):
        raise FileNotFoundError(f"CSV de emoções não encontrado: {emotions_csv_path}")

    df = pd.read_csv(emotions_csv_path)

    if df.empty:
        resultado = {
            "topicos_detectados": topicos,
            "emocao_predominante": "Indefinido",
            "timeline": []
        }

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)

        return resultado

    df["tempo_segundos"] = pd.to_numeric(df["tempo_segundos"], errors="coerce").fillna(0)

    emocao_col = "emocao"

    if "emocao_negocio" in df.columns:
        emocao_col = "emocao_negocio"

    emocao_predominante = df[emocao_col].mode()[0]

    timeline = []

    for _, row in df.iterrows():
        timeline.append({
            "tempo": float(row["tempo_segundos"]),
            "emocao": str(row[emocao_col])
        })

    resultado = {
        "topicos_detectados": topicos,
        "emocao_predominante": emocao_predominante,
        "timeline": timeline
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)

    return resultado
