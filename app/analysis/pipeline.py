import os
import shutil

from app.utils.files import (
    ensure_directories,
    generate_analysis_id,
    create_analysis_dir,
    get_analysis_paths
)

from app.analysis.audio import extract_audio
from app.analysis.transcription import transcribe_audio
from app.analysis.emotion import analyze_video_emotions
from app.analysis.metrics import calcular_metricas, gerar_insights, salvar_json
from app.analysis.speech_analysis import analyze_speech
from app.analysis.discourse_analysis import analyze_discourse
from app.analysis.multimodal_analysis import build_multimodal_analysis
from app.analysis.topics import detectar_topicos
from app.analysis.negotiation_map import gerar_mapa_negociacao
from app.analysis.sales_detector import detectar_momentos_venda


def limpar_arquivos_temporarios(video_path: str, base_dir: str, video_name: str, paths: dict):
    candidatos_arquivo = [
        video_path,
        os.path.join(base_dir, video_name),
        paths.get("audio_path"),
    ]

    for arquivo in candidatos_arquivo:
        try:
            if arquivo and os.path.exists(arquivo):
                os.remove(arquivo)
        except Exception:
            pass

    candidatos_pasta = [
        os.path.join(base_dir, "frames"),
        os.path.join(base_dir, "temp"),
        os.path.join(base_dir, "extracted_frames"),
        os.path.join(base_dir, "screenshots"),
    ]

    for pasta in candidatos_pasta:
        try:
            if os.path.exists(pasta):
                shutil.rmtree(pasta, ignore_errors=True)
        except Exception:
            pass



def processar_video(video_path: str):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video nao encontrado: {video_path}")

    ensure_directories()

    analysis_id = generate_analysis_id()
    create_analysis_dir(analysis_id)

    video_name = os.path.basename(video_path)
    paths = get_analysis_paths(analysis_id, video_name)

    base_dir = os.path.dirname(paths["metrics_json"])

    vocal_json = os.path.join(base_dir, "analise_vocal.json")
    discurso_json = os.path.join(base_dir, "analise_discurso.json")
    multimodal_json = os.path.join(base_dir, "analise_multimodal.json")
    topicos_json = os.path.join(base_dir, "topicos_negociacao.json")
    mapa_negociacao_json = os.path.join(base_dir, "mapa_negociacao.json")
    momentos_venda_json = os.path.join(base_dir, "momentos_venda.json")

    print("\n===== INICIANDO ANALISE =====")

    video_input = video_path
    print("Video pronto para processamento")

    extract_audio(video_input, paths["audio_path"])
    print("Audio extraido")

    transcribe_audio(paths["audio_path"], paths["transcription_path"])
    print("Transcricao criada")

    with open(paths["transcription_path"], "r", encoding="utf-8") as f:
        transcription_text = f.read().strip()

    analyze_video_emotions(video_input, paths["emotions_csv"])
    print("Emocoes analisadas")

    metricas = calcular_metricas(paths["emotions_csv"])
    insights = gerar_insights(metricas)

    vocal = analyze_speech(paths["audio_path"], vocal_json)
    print("Analise vocal concluida")

    discurso = analyze_discourse(paths["transcription_path"], vocal_json, discurso_json)
    print("Analise de discurso concluida")

    multimodal = build_multimodal_analysis(metricas, vocal, discurso, multimodal_json)
    print("Analise multimodal concluida")

    topicos = detectar_topicos(transcription_text)
    salvar_json({"topicos_detectados": topicos}, topicos_json)
    print("Topicos detectados")

    mapa_negociacao = gerar_mapa_negociacao(paths["emotions_csv"], topicos, mapa_negociacao_json)
    print("Mapa da negociacao gerado")

    momentos_venda = detectar_momentos_venda(paths["transcription_path"], momentos_venda_json)
    print("Momentos de venda detectados")

    if topicos:
        insights["resumo_executivo"] += " " + (
            "Topicos detectados na conversa: " + ", ".join(topicos) + "."
        )

    if mapa_negociacao.get("emocao_predominante"):
        insights["resumo_executivo"] += " " + (
            f"No mapa da negociacao, a emocao predominante foi {mapa_negociacao['emocao_predominante']}."
        )

    if momentos_venda.get("preco"):
        insights["recomendacoes"].append("Observe a reacao do cliente no momento em que o preco e apresentado.")
    if momentos_venda.get("desconto"):
        insights["recomendacoes"].append("Avalie se o desconto aumentou o interesse e acelerou a decisao.")
    if momentos_venda.get("fechamento"):
        insights["recomendacoes"].append("Revise se o fechamento foi introduzido no momento de maior interesse.")
    if momentos_venda.get("duvida"):
        insights["recomendacoes"].append("Identifique trechos de duvida para reforcar clareza e seguranca na oferta.")

    insights["resumo_executivo"] += " " + (
        f"Na camada vocal, a energia foi {vocal['energia_vocal']}, a fluidez foi {vocal['fluidez']} "
        f"e a estabilidade vocal foi {vocal['estabilidade_vocal']}. "
        f"Na camada discursiva, a clareza foi {discurso['clareza']}, a confianca verbal foi {discurso['confianca_verbal']} "
        f"e a forca de fechamento foi {discurso['forca_fechamento']}. "
        f"Na leitura integrada, o score multimodal foi {multimodal['score_integrado']} e o diagnostico foi: {multimodal['diagnostico']}."
    )

    insights["recomendacoes"].extend(multimodal.get("recomendacoes", []))

    salvar_json(metricas, paths["metrics_json"])
    salvar_json(insights, paths["insights_json"])

    print("\n===== RESULTADO =====")
    print("Engagement Score:", metricas["engagement_score"])
    print("Emocao predominante:", metricas["emocao_predominante"])
    print("Pico emocional:", metricas["pico_emocional_segundos"])
    print("Queda de interesse:", metricas["queda_interesse_segundos"])
    print("Score multimodal:", multimodal["score_integrado"])
    print("Topicos:", topicos)

    print("\nArquivos gerados:")
    print(paths["metrics_json"])
    print(paths["insights_json"])
    print(vocal_json)
    print(discurso_json)
    print(multimodal_json)
    print(topicos_json)
    print(mapa_negociacao_json)

    limpar_arquivos_temporarios(video_path, base_dir, video_name, paths)
    print("Arquivos temporarios removidos")

    return analysis_id
