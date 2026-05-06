import json
import os
import wave
import numpy as np


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def analyze_speech(audio_path: str, output_json: str) -> dict:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio nao encontrado: {audio_path}")

    with wave.open(audio_path, "rb") as wf:
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    if sample_width != 2:
        raise RuntimeError("Audio precisa estar em PCM 16-bit para analise vocal.")

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)

    if n_channels > 1:
        samples = samples.reshape(-1, n_channels).mean(axis=1)

    if len(samples) == 0:
        result = {
            "duracao_segundos": 0.0,
            "energia_vocal": 0.0,
            "energia_pico": 0.0,
            "fluidez": 0.0,
            "estabilidade_vocal": 0.0,
            "pausas_total_segundos": 0.0,
            "quantidade_pausas": 0,
            "taxa_fala_percentual": 0.0
        }
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        return result

    duration = len(samples) / float(framerate)

    norm = samples / 32768.0

    frame_size = int(framerate * 0.25)
    hop = frame_size

    rms_values = []
    for i in range(0, len(norm), hop):
        chunk = norm[i:i + frame_size]
        if len(chunk) == 0:
            continue
        rms = float(np.sqrt(np.mean(np.square(chunk))))
        rms_values.append(rms)

    if not rms_values:
        rms_values = [0.0]

    rms_values = np.array(rms_values, dtype=np.float32)

    mean_rms = float(np.mean(rms_values))
    peak_rms = float(np.max(rms_values))
    std_rms = float(np.std(rms_values))

    silence_threshold = max(0.01, mean_rms * 0.45)

    pause_count = 0
    pause_total_frames = 0
    in_pause = False
    current_pause = 0

    voiced_frames = 0

    for v in rms_values:
        if v < silence_threshold:
            current_pause += 1
            in_pause = True
        else:
            voiced_frames += 1
            if in_pause and current_pause >= 2:
                pause_count += 1
                pause_total_frames += current_pause
            in_pause = False
            current_pause = 0

    if in_pause and current_pause >= 2:
        pause_count += 1
        pause_total_frames += current_pause

    frame_duration = 0.25
    pause_total_seconds = round(pause_total_frames * frame_duration, 2)
    speech_ratio_percent = round((voiced_frames / max(1, len(rms_values))) * 100.0, 2)

    energia_vocal = round(_clamp(mean_rms * 1400.0), 2)
    energia_pico = round(_clamp(peak_rms * 1200.0), 2)

    estabilidade_vocal = round(_clamp(100.0 - (std_rms * 900.0)), 2)

    fluidez = round(
        _clamp(
            35.0
            + (speech_ratio_percent * 0.55)
            - min(22.0, pause_count * 2.0)
            - min(18.0, pause_total_seconds * 1.5)
        ),
        2
    )

    result = {
        "duracao_segundos": round(duration, 2),
        "energia_vocal": energia_vocal,
        "energia_pico": energia_pico,
        "fluidez": fluidez,
        "estabilidade_vocal": estabilidade_vocal,
        "pausas_total_segundos": pause_total_seconds,
        "quantidade_pausas": int(pause_count),
        "taxa_fala_percentual": speech_ratio_percent
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    return result
