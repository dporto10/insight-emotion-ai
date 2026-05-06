import os
import json
import pandas as pd

def load_analysis(analysis_id: str, base_dir="data/processed"):
    base = os.path.join(base_dir, analysis_id)

    paths = {
        "metrics": os.path.join(base, "metricas.json"),
        "insights": os.path.join(base, "insights.json"),
        "emotions": os.path.join(base, "emocoes_detalhadas.csv"),
        "transcription": os.path.join(base, "transcricao.txt"),
        "vocal": os.path.join(base, "analise_vocal.json"),
        "discurso": os.path.join(base, "analise_discurso.json"),
        "multimodal": os.path.join(base, "analise_multimodal.json"),
        "momentos": os.path.join(base, "momentos_venda.json"),
    }

    data = {}

    if os.path.exists(paths["metrics"]):
        with open(paths["metrics"], "r", encoding="utf-8") as f:
            data["metrics"] = json.load(f)

    if os.path.exists(paths["insights"]):
        with open(paths["insights"], "r", encoding="utf-8") as f:
            data["insights"] = json.load(f)

    if os.path.exists(paths["emotions"]):
        data["emotions_df"] = pd.read_csv(paths["emotions"])

    if os.path.exists(paths["transcription"]):
        with open(paths["transcription"], "r", encoding="utf-8") as f:
            data["transcription"] = f.read()

    for key in ["vocal", "discurso", "multimodal", "momentos"]:
        if os.path.exists(paths[key]):
            with open(paths[key], "r", encoding="utf-8") as f:
                data[key] = json.load(f)
        else:
            data[key] = {}

    return data
