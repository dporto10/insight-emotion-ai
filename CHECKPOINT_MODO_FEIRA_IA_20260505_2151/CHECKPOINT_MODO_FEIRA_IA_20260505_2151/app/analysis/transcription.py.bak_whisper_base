import whisper
import os

_WHISPER_MODEL = None


def _get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        _WHISPER_MODEL = whisper.load_model("base")
    return _WHISPER_MODEL


def transcribe_audio(audio_path: str, transcription_output: str) -> str:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Áudio não encontrado: {audio_path}")

    model = _get_whisper_model()

    result = model.transcribe(audio_path, fp16=False)
    texto = result.get("text", "").strip()

    with open(transcription_output, "w", encoding="utf-8") as f:
        f.write(texto)

    return transcription_output
