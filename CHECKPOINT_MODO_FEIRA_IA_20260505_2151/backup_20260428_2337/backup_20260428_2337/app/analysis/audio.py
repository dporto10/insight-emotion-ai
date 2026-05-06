import os
import subprocess


def extract_audio(video_path: str, audio_output: str) -> str:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")

    output_dir = os.path.dirname(audio_output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    ffmpeg_path = "ffmpeg"

    command = [
        ffmpeg_path,
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_output,
    ]

    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "FFmpeg não encontrado no terminal atual. Feche e reabra o VS Code/PowerShell e teste 'ffmpeg -version'."
        ) from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Erro ao extrair áudio com FFmpeg: {e}") from e

    if not os.path.exists(audio_output):
        raise RuntimeError("O FFmpeg terminou, mas o arquivo de áudio não foi gerado.")

    return audio_output
