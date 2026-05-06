def classificar_score(valor):
    try:
        valor = float(valor)
    except:
        return "Indefinido"

    if valor < 40:
        return "Fraco"
    elif valor < 60:
        return "Médio"
    elif valor < 80:
        return "Bom"
    return "Forte"


def classificar_reacao_preco(momentos, metrics, discurso):
    preco_count = len(momentos.get("preco", []))
    desconto_count = len(momentos.get("desconto", []))
    duvida_count = len(momentos.get("duvida", []))
    emocao_pred = str(metrics.get("emocao_predominante", "")).lower()
    persuasao = float(discurso.get("persuasao", 0) or 0)

    if preco_count == 0:
        return "Não identificado"

    if desconto_count > 0 or duvida_count > 0 or "desconexao" in emocao_pred or "resistencia" in emocao_pred:
        return "Negativa"

    if persuasao >= 60:
        return "Positiva"

    return "Média"


def gerar_diagnostico_comercial(metrics, vocal, discurso, multimodal, momentos):
    engagement = float(metrics.get("engagement_score", 0) or 0)
    queda = metrics.get("queda_interesse_segundos")
    clareza = float(discurso.get("clareza", 0) or 0)
    persuasao = float(discurso.get("persuasao", 0) or 0)
    fechamento_score = float(discurso.get("forca_fechamento", 0) or 0)
    energia = float(vocal.get("energia_vocal", 0) or 0)
    fluidez = float(vocal.get("fluidez", 0) or 0)
    score_integrado = float(multimodal.get("score_integrado", 0) or 0)

    if queda is not None:
        try:
            queda = float(queda)
        except:
            queda = None

    # conexão inicial
    conexao_base = engagement
    if queda is not None and queda <= 5:
        conexao_base = min(conexao_base, 25)
    elif queda is not None and queda <= 12:
        conexao_base = min(conexao_base, 45)

    conexao_inicial = classificar_score(conexao_base)

    # apresentação de valor
    apresentacao_valor_score = (clareza + persuasao) / 2 if (clareza or persuasao) else 0
    apresentacao_valor = classificar_score(apresentacao_valor_score)

    # reação ao preço
    reacao_preco = classificar_reacao_preco(momentos, metrics, discurso)

    # fechamento
    fechamento = classificar_score(fechamento_score)

    # potencial comercial
    potencial_score = (
        engagement * 0.20
        + clareza * 0.20
        + persuasao * 0.20
        + fechamento_score * 0.20
        + score_integrado * 0.20
    )
    potencial_comercial = classificar_score(potencial_score)

    pitch_label = "Pitch Fraco"
    if potencial_score >= 60:
        pitch_label = "Pitch Promissor"
    if potencial_score >= 75:
        pitch_label = "Pitch Forte"

    o_que_funcionou = []
    o_que_prejudicou = []
    o_que_melhorar = []

    if len(momentos.get("interesse", [])) > 0:
        o_que_funcionou.append("Houve interesse ao falar do produto.")
    if len(momentos.get("desconto", [])) > 0:
        o_que_funcionou.append("O desconto aumentou a atenção.")
    if len(momentos.get("fechamento", [])) > 0:
        o_que_funcionou.append("Houve abertura para fechamento.")

    if queda is not None and queda <= 5:
        o_que_prejudicou.append("Queda de interesse logo no inicio.")
        o_que_melhorar.append("Melhorar a abertura nos primeiros 5 segundos.")
    elif queda is not None and queda <= 12:
        o_que_prejudicou.append("A atencao cai cedo demais.")
        o_que_melhorar.append("Fortalecer a abertura antes do primeiro bloco comercial.")

    if energia < 20:
        o_que_prejudicou.append("Voz com baixa energia.")
        o_que_melhorar.append("Elevar energia vocal nos trechos principais.")
    if fluidez < 30:
        o_que_prejudicou.append("Fluidez baixa na fala.")
        o_que_melhorar.append("Reduzir pausas longas e deixar a fala mais continua.")
    if reacao_preco == "Negativa":
        o_que_prejudicou.append("O preco gerou resistencia.")
        o_que_melhorar.append("Apresentar beneficios antes do preco.")
    if fechamento_score < 40:
        o_que_prejudicou.append("Fechamento pouco forte.")
        o_que_melhorar.append("Usar um fechamento mais direto e objetivo.")
    if clareza < 55:
        o_que_melhorar.append("Simplificar a mensagem e reforcar a proposta de valor.")
    if len(momentos.get("desconto", [])) > 0:
        o_que_melhorar.append("Reforcar valor antes de oferecer desconto.")

    if not o_que_funcionou:
        o_que_funcionou.append("Nao houve sinais claros de resposta comercial forte.")
    if not o_que_prejudicou:
        o_que_prejudicou.append("Nao foram detectados pontos criticos relevantes.")
    if not o_que_melhorar:
        o_que_melhorar.append("Manter a estrutura atual e testar pequenos ajustes.")

    return {
        "pitch_label": pitch_label,
        "conexao_inicial": conexao_inicial,
        "apresentacao_valor": apresentacao_valor,
        "reacao_preco": reacao_preco,
        "fechamento": fechamento,
        "potencial_comercial": potencial_comercial,
        "energia_vocal_label": classificar_score(energia),
        "fluidez_label": classificar_score(fluidez),
        "clareza_label": classificar_score(clareza),
        "fechamento_label": classificar_score(fechamento_score),
        "pontuacao_integrada_label": classificar_score(score_integrado),
        "o_que_funcionou": o_que_funcionou[:4],
        "o_que_prejudicou": o_que_prejudicou[:4],
        "o_que_melhorar": o_que_melhorar[:4],
    }
