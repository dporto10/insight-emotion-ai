
import os
import whisper

_WHISPER_MODEL = None
_MODEL_NAME = os.getenv("WHISPER_MODEL", "small")


def _get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        print(f"Carregando modelo Whisper: {_MODEL_NAME}")
        _WHISPER_MODEL = whisper.load_model(_MODEL_NAME)
    return _WHISPER_MODEL


def _limpar_texto(texto: str) -> str:
    texto = (texto or "").strip()
    texto = " ".join(texto.split())
    return texto



def _corrigir_transcricao_comercial(texto: str) -> str:
    """
    Correção leve pós-Whisper para termos frequentes em conversas de vendas.
    Não tenta reescrever tudo; apenas corrige termos que prejudicam a leitura comercial.
    """
    import re

    texto = texto or ""

    substituicoes_simples = {
        "Albuticário": "O Boticário",
        "Albuticario": "O Boticário",
        "Boticario": "Boticário",
        "Botícario": "Boticário",
        "O Rodiciário": "O Boticário",
        "Rodiciário": "Boticário",
        "Rodiçário": "Boticário",
        "Ruby Cário": "Ruby Rose",
        "Rúgio Cário": "Ruby Rose",
        "marcos": "marcas",
        "fragança": "fragrância",
        "fraganças": "fragrâncias",
        "fragrância de natureza": "fragrância da Natura",
        "Body Splash": "body splash",
        "Day of Waris Flash": "body splash",
        "diálogo de body splash": "body splash",
        "necessaire": "nécessaire",
        "PIX": "Pix",
        "pix": "Pix",
        "cartao": "cartão",
        "preco": "preço",
        "desconto no Pix": "desconto no Pix",
    }

    for errado, certo in substituicoes_simples.items():
        texto = texto.replace(errado, certo)

    padroes = [
        (r"\bR\$ ?(\d+)\b", r"R$ \1"),
        (r"\b(\d+)\s*reais\b", r"R$ \1"),
        (r"\bbody\s+spl[a-zçãéíóú]*\b", "body splash"),
        (r"\bO\s+Botic[aá]rio\b", "O Boticário"),
        (r"\bBotic[aá]rio\b", "Boticário"),
        (r"\bNatura\b", "Natura"),
        (r"\bRuby\s+Rose\b", "Ruby Rose"),
    ]

    for padrao, repl in padroes:
        texto = re.sub(padrao, repl, texto, flags=re.IGNORECASE)

    texto = " ".join(texto.split())
    return texto.strip()


def transcribe_audio(audio_path: str, transcription_output: str) -> str:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Áudio não encontrado: {audio_path}")

    model = _get_whisper_model()

    prompt_vendas = (
        "Transcrição em português do Brasil de uma conversa real de vendas no varejo. "
        "O diálogo pode envolver cliente e vendedor em loja, produtos de beleza, perfume, body splash, "
        "creme, cosméticos, O Boticário, Natura, Ruby Rose, fragrância, cheiro doce, cheiro leve, "
        "bolsa, necessaire, faculdade, academia, trabalho, preço, desconto, Pix, cartão, pagamento, "
        "valor, compra, levar, fechamento e objeção. "
        "Preserve o sentido comercial da fala. Não traduza nomes para inglês. "
        "Evite inventar palavras sem sentido. Priorize frases naturais em português do Brasil."
    )

    result = model.transcribe(
        audio_path,
        language="pt",
        task="transcribe",
        fp16=False,
        verbose=False,
        temperature=0,
        initial_prompt=prompt_vendas,
        condition_on_previous_text=False,
        no_speech_threshold=0.55,
        logprob_threshold=-1.0,
        compression_ratio_threshold=2.4,
    )

    texto_bruto = _limpar_texto(result.get("text", ""))
    texto = _corrigir_transcricao_comercial(texto_bruto)

    bruto_output = transcription_output.replace(".txt", "_bruta.txt")
    with open(bruto_output, "w", encoding="utf-8") as f:
        f.write(texto_bruto)

    with open(transcription_output, "w", encoding="utf-8") as f:
        f.write(texto)

    # Salva segmentos com tempo para auditoria e futura análise mais precisa
    segments_output = transcription_output.replace(".txt", "_segmentos.txt")
    with open(segments_output, "w", encoding="utf-8") as f:
        for seg in result.get("segments", []):
            inicio = seg.get("start", 0)
            fim = seg.get("end", 0)
            trecho = _corrigir_transcricao_comercial(_limpar_texto(seg.get("text", "")))
            if trecho:
                f.write(f"[{inicio:.2f}s - {fim:.2f}s] {trecho}\n")

    return transcription_output
