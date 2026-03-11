import re

TOPICOS = {
    "preco": ["preco", "valor", "custa", "reais", "desconto", "7,50", "10 reais"],
    "beneficio": ["serve para", "beneficio", "vantagem", "funciona", "ajuda", "melhor"],
    "pagamento": ["pix", "cartao", "credito", "debito", "dinheiro", "pagar", "pagamento"],
    "fechamento": ["vai levar", "fechar", "comprar", "interesse", "passar", "qr code"],
    "garantia": ["garantia", "troca", "devolucao"],
    "objecao": ["caro", "duvida", "nao sei", "menor", "desconto"]
}


def detectar_topicos(texto: str):
    texto = (texto or "").lower()
    encontrados = []

    for topico, palavras in TOPICOS.items():
        for palavra in palavras:
            if palavra in texto:
                encontrados.append(topico)
                break

    return sorted(list(set(encontrados)))
