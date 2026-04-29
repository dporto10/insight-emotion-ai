import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")


def ensure_directories() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_analysis_id(prefix: str = "analysis") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}"


def get_analysis_dir(analysis_id: str) -> str:
    return os.path.join(PROCESSED_DIR, analysis_id)


def create_analysis_dir(analysis_id: str) -> str:
    analysis_dir = get_analysis_dir(analysis_id)
    os.makedirs(analysis_dir, exist_ok=True)
    return analysis_dir


def get_upload_path(filename: str) -> str:
    return os.path.join(UPLOADS_DIR, filename)


def get_analysis_paths(analysis_id: str, video_filename: str) -> dict:
    analysis_dir = get_analysis_dir(analysis_id)

    return {
        "analysis_id": analysis_id,
        "analysis_dir": analysis_dir,
        "video_input": os.path.join(analysis_dir, video_filename),
        "audio_path": os.path.join(analysis_dir, "audio.wav"),
        "transcription_path": os.path.join(analysis_dir, "transcricao.txt"),
        "emotions_csv": os.path.join(analysis_dir, "emocoes_detalhadas.csv"),
        "emotions_summary": os.path.join(analysis_dir, "resumo_emocoes.txt"),
        "timeline_txt": os.path.join(analysis_dir, "timeline_emocao.txt"),
        "timeline_png": os.path.join(analysis_dir, "timeline_emocao.png"),
        "final_report_txt": os.path.join(analysis_dir, "relatorio_final.txt"),
        "metrics_json": os.path.join(analysis_dir, "metricas.json"),
        "insights_json": os.path.join(analysis_dir, "insights.json"),
    }
