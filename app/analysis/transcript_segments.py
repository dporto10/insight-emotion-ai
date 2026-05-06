
import re
from pathlib import Path
import unicodedata
from typing import List, Dict, Any


def _normalize(text: str) -> str:
    text = (text or "").lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def carregar_segmentos_transcricao(transcription_path: str) -> List[Dict[str, Any]]:
    """
    Carrega transcricao_segmentos.txt gerado pelo Whisper.
    Funciona para qualquer vídeo, desde que o arquivo siga o padrão:
    [0.00s - 2.50s] texto
    """
    if not transcription_path:
        return []

    segmentos_path = transcription_path.replace(".txt", "_segmentos.txt")
    path = Path(segmentos_path)

    if not path.exists():
        return []

    segmentos = []

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue

        match = re.match(r"\[(\d+(?:\.\d+)?)s\s*-\s*(\d+(?:\.\d+)?)s\]\s*(.*)", line)

        if not match:
            continue

        inicio = float(match.group(1))
        fim = float(match.group(2))
        texto = _clean(match.group(3))

        if texto:
            segmentos.append({
                "inicio": inicio,
                "fim": fim,
                "texto": texto,
            })

    return segmentos


def _score_comercial(texto: str, contexto: str, emocao: str) -> int:
    """
    Score genérico de relevância comercial.
    Não depende de produto específico.
    Serve para venda de cosmético, caneta, roupa, serviço, tecnologia etc.
    """
    t = _normalize(texto)
    score = 0

    termos_pesos = {
        # necessidade / descoberta
        "preciso": 5,
        "precisa": 5,
        "necessidade": 6,
        "procurando": 5,
        "queria": 4,
        "quero": 4,
        "prefiro": 4,
        "preferencia": 5,
        "uso": 4,
        "usar": 4,

        # valor / solução
        "beneficio": 6,
        "vantagem": 5,
        "melhor": 4,
        "produto": 4,
        "solucao": 6,
        "resolve": 5,
        "ajuda": 4,
        "qualidade": 4,
        "durabilidade": 4,
        "conforto": 4,
        "estabilidade": 4,

        # preço / negociação
        "preco": 7,
        "valor": 6,
        "quanto": 5,
        "desconto": 7,
        "menor": 5,
        "barato": 5,
        "caro": 5,
        "pagamento": 5,
        "pix": 6,
        "cartao": 5,
        "dinheiro": 5,

        # fechamento
        "comprar": 8,
        "levar": 8,
        "fechar": 8,
        "quero": 6,
        "gostei": 6,
        "fica bom": 7,
        "pode passar": 8,
        "vou querer": 8,
        "vou levar": 8,
    }

    for termo, peso in termos_pesos.items():
        if termo in t:
            score += peso

    if "?" in texto:
        score += 3

    if contexto == "abertura" and any(x in t for x in ["preciso", "procurando", "queria", "necessidade", "preferencia"]):
        score += 4

    if contexto == "fechamento" and any(x in t for x in ["comprar", "levar", "gostei", "pix", "cartao", "fechar", "pode passar"]):
        score += 6

    if emocao in ["Perda de interesse", "Resistência comercial"] and any(x in t for x in ["preco", "valor", "desconto", "caro", "menor"]):
        score += 5

    return score


def escolher_trecho_por_tempo(
    segmentos: List[Dict[str, Any]],
    inicio: float,
    fim: float,
    contexto: str,
    emocao: str,
    fallback: str = "",
) -> str:
    """
    Escolhe o trecho mais relevante usando tempo real + relevância comercial.
    Se não houver segmentos, usa fallback.
    """
    if not segmentos:
        return _clean(fallback)

    inicio = float(inicio or 0)
    fim = float(fim or inicio)
    centro = (inicio + fim) / 2

    candidatos = []

    for seg in segmentos:
        seg_inicio = float(seg.get("inicio", 0))
        seg_fim = float(seg.get("fim", seg_inicio))
        texto = seg.get("texto", "")

        # pega segmentos próximos ao momento detectado
        distancia = min(abs(seg_inicio - centro), abs(seg_fim - centro))

        # janela flexível: até 12s de distância
        if distancia <= 12:
            comercial = _score_comercial(texto, contexto, emocao)
            proximidade = max(0, 12 - distancia)
            score_final = comercial + proximidade

            candidatos.append((score_final, texto))

    if not candidatos:
        return _clean(fallback)

    candidatos.sort(key=lambda x: x[0], reverse=True)
    return _clean(candidatos[0][1] or fallback)
