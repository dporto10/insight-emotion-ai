import cv2
import pandas as pd

MAPA_EMOCOES = {
    "happy": "Felicidade",
    "sad": "Tristeza",
    "angry": "Raiva",
    "fear": "Medo",
    "disgust": "Repulsa",
    "surprise": "Surpresa",
    "neutral": "Neutro",
    "unknown": "Indefinido"
}


def analyze_video_emotions(video_path: str, output_csv: str):
    from deepface import DeepFace

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Nao foi possivel abrir o video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps is None or fps <= 0:
        fps = 30.0

    # amostragem adaptativa leve:
    # tenta 2 amostras por segundo, mas sem exagerar
    frame_interval = max(1, int(round(fps / 2.0)))

    frame_count = 0
    results = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        if frame_count % frame_interval != 0:
            continue

        tempo = round(frame_count / fps, 2)

        try:
            h, w = frame.shape[:2]
            max_width = 960

            if w > max_width:
                new_height = int((max_width / w) * h)
                frame = cv2.resize(frame, (max_width, new_height), interpolation=cv2.INTER_AREA)

            analysis = DeepFace.analyze(
                frame,
                actions=["emotion"],
                enforce_detection=False,
                detector_backend="opencv",
                silent=True
            )

            if isinstance(analysis, list):
                analysis = analysis[0]

            emotion_raw = analysis.get("dominant_emotion", "unknown")
            emotion_pt = MAPA_EMOCOES.get(emotion_raw, emotion_raw)
            confidence = float(analysis.get("emotion", {}).get(emotion_raw, 0.0))

        except Exception:
            emotion_raw = "unknown"
            emotion_pt = "Indefinido"
            confidence = 0.0

        results.append({
            "tempo_segundos": tempo,
            "emocao_raw": emotion_raw,
            "emocao": emotion_pt,
            "confianca": round(confidence, 2)
        })

    cap.release()

    if not results:
        results = [{
            "tempo_segundos": 0,
            "emocao_raw": "unknown",
            "emocao": "Indefinido",
            "confianca": 0.0
        }]

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)

    return output_csv
