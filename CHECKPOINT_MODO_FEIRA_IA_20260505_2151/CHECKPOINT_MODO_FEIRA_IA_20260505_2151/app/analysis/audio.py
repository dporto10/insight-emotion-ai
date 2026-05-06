
import os
import subprocess


def _run_ffmpeg(command):
    subprocess.run(
        command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def extract_audio(video_path: str, audio_output: str) -> str:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")

    output_dir = os.path.dirname(audio_output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    ffmpeg_path = "ffmpeg"

    # Versão principal: melhora fala antes do Whisper
    # - converte para mono
    # - padroniza para 16kHz
    # - reduz ruído leve
    # - normaliza volume
    command_clean = [
        ffmpeg_path,
        "-y",
        "-i", video_path,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-af", "highpass=f=80,lowpass=f=7800,afftdn=nf=-25,dynaudnorm=f=150:g=15",
        "-acodec", "pcm_s16le",
        audio_output,
    ]

    # Fallback simples caso algum filtro não esteja disponível no FFmpeg
    command_simple = [
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
        _run_ffmpeg(command_clean)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "FFmpeg não encontrado. Feche e reabra o VS Code/PowerShell e teste: ffmpeg -version"
        ) from e
    except subprocess.CalledProcessError:
        print("Aviso: limpeza de áudio falhou. Usando extração simples.")
        try:
            _run_ffmpeg(command_simple)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erro ao extrair áudio com FFmpeg: {e}") from e

    if not os.path.exists(audio_output):
        raise RuntimeError("O FFmpeg terminou, mas o arquivo de áudio não foi gerado.")

    return audio_output
