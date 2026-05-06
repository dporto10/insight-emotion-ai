from pyannote.audio import Pipeline
import pandas as pd

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

def identificar_falantes(audio_path):
    diarization = pipeline(audio_path)

    segmentos = []

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segmentos.append({
            "inicio": turn.start,
            "fim": turn.end,
            "falante": speaker
        })

    return pd.DataFrame(segmentos)