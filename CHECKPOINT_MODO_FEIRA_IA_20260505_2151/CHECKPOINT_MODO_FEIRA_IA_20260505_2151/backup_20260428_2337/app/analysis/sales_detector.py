import json
import os
import re


def _normalizar_frase(frase: str) -> str:
    frase = (frase or "").strip().lower()

    frase = re.sub(r"\s+", " ", frase)
    frase = re.sub(r"[\"“”]", "", frase)

    palavras = frase.split()
    limpas = []
    anterior = None

    for p in palavras:
        if p != anterior:
            limpas.append(p)
        anterior = p

    frase = " ".join(limpas).strip(" .,-;:")

    if not frase:
        return ""

    frase = frase[0].upper() + frase[1:]

    if not frase.endswith("."):
        frase += "."

    return frase


def _filtrar_frases(frases):
    resultado = []
    vistas = set()

    for frase in frases:
        f = _normalizar_frase(frase)

        if len(f) < 12:
            continue

        chave = f.lower()
        if chave in vistas:
            continue

        vistas.add(chave)
        resultado.append(f)

    return resultado[:6]


def detectar_momentos_venda(transcricao_path, output_json):
    if not os.path.exists(transcricao_path):
        raise FileNotFoundError("Transcricao nao encontrada")

    with open(transcricao_path, "r", encoding="utf-8") as f:
        texto = f.read().lower()

    texto = re.sub(r"\s+", " ", texto)

    momentos = {
        "interesse": [],
        "duvida": [],
        "preco": [],
        "desconto": [],
        "fechamento": []
    }

    palavras = {
        "interesse": ["gostei", "interesse", "quero", "legal", "bom", "otimo", "fica bom"],
        "duvida": ["talvez", "nao sei", "vou pensar", "depois", "vou olhar", "um pouco menor"],
        "preco": ["preco", "valor", "custa", "quanto", "reais"],
        "desconto": ["desconto", "promocao", "mais barato", "menor", "7,50"],
        "fechamento": ["vou levar", "vou comprar", "fechado", "ok vou", "pix", "passa la", "vamos vender"]
    }

    frases = re.split(r'[.!?]', texto)

    for frase in frases:
        frase = frase.strip()
        if not frase:
            continue

        for categoria, lista in palavras.items():
            if any(palavra in frase for palavra in lista):
                momentos[categoria].append(frase)

    for categoria in list(momentos.keys()):
        momentos[categoria] = _filtrar_frases(momentos[categoria])

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(momentos, f, ensure_ascii=False, indent=4)

    return momentos
