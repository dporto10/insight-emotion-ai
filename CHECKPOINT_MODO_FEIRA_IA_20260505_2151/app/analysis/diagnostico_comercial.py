
def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def _count_momento(momentos, chave):
    if isinstance(momentos, dict):
        return len(momentos.get(chave, []) or [])
    return 0


def classificar_score(valor, minimo_evidencia=True):
    try:
        valor = float(valor)
    except Exception:
        return "Não identificado"

    # Evita transformar ausência de dado em avaliação negativa
    if minimo_evidencia and valor <= 0:
        return "Não identificado"

    # Faixas mais justas para não classificar tudo como fraco
    if valor < 25:
        return "Fraco"
    elif valor < 50:
        return "Médio"
    elif valor < 75:
        return "Bom"
    return "Forte"


def nivel_confianca(*valores):
    validos = [v for v in valores if v is not None]
    validos = [v for v in validos if _safe_float(v, 0) > 0]

    if len(validos) >= 4:
        return "Alta"
    if len(validos) >= 2:
        return "Média"
    return "Baixa"


def classificar_reacao_preco(momentos, metrics, discurso):
    preco_count = _count_momento(momentos, "preco")
    desconto_count = _count_momento(momentos, "desconto")
    duvida_count = _count_momento(momentos, "duvida")
    emocao_pred = str(metrics.get("emocao_predominante", "")).lower()
    persuasao = _safe_float(discurso.get("persuasao", 0))

    if preco_count == 0:
        return "Não identificado"

    if desconto_count > 0 or duvida_count > 0 or "desconexao" in emocao_pred or "resistencia" in emocao_pred:
        return "Negativa"

    if persuasao >= 60:
        return "Positiva"

    return "Média"


def gerar_diagnostico_comercial(metrics, vocal, discurso, multimodal, momentos):
    engagement = _safe_float(metrics.get("engagement_score", 0))
    queda = metrics.get("queda_interesse_segundos")
    clareza = _safe_float(discurso.get("clareza", 0))
    persuasao = _safe_float(discurso.get("persuasao", 0))
    fechamento_score = _safe_float(discurso.get("forca_fechamento", 0))
    energia = _safe_float(vocal.get("energia_vocal", 0))
    fluidez = _safe_float(vocal.get("fluidez", 0))
    score_integrado = _safe_float(multimodal.get("score_integrado", 0))

    try:
        queda = float(queda) if queda is not None else None
    except Exception:
        queda = None

    # Não transformar ausência de sinal em crítica automática
    confianca_geral = nivel_confianca(engagement, clareza, persuasao, fechamento_score, energia, fluidez, score_integrado)

    conexao_base = engagement
    if queda is not None and queda <= 5 and engagement > 0:
        conexao_base = min(conexao_base, 25)
    elif queda is not None and queda <= 12 and engagement > 0:
        conexao_base = min(conexao_base, 45)

    conexao_inicial = classificar_score(conexao_base)
    apresentacao_valor_score = (clareza + persuasao) / 2 if (clareza > 0 or persuasao > 0) else 0
    apresentacao_valor = classificar_score(apresentacao_valor_score)
    reacao_preco = classificar_reacao_preco(momentos, metrics, discurso)
    fechamento = classificar_score(fechamento_score)

    # Potencial comercial calibrado:
    # não deixa engagement zerado destruir toda a avaliação quando existem outros sinais úteis.
    valores_potencial = []

    if engagement > 0:
        valores_potencial.append(engagement * 0.20)
    if clareza > 0:
        valores_potencial.append(clareza * 0.22)
    if persuasao > 0:
        valores_potencial.append(persuasao * 0.22)
    if fechamento_score > 0:
        valores_potencial.append(fechamento_score * 0.18)
    if score_integrado > 0:
        valores_potencial.append(score_integrado * 0.18)

    peso_total = 0
    if engagement > 0:
        peso_total += 0.20
    if clareza > 0:
        peso_total += 0.22
    if persuasao > 0:
        peso_total += 0.22
    if fechamento_score > 0:
        peso_total += 0.18
    if score_integrado > 0:
        peso_total += 0.18

    potencial_score = sum(valores_potencial) / peso_total if peso_total > 0 else 0
    potencial_comercial = classificar_score(potencial_score)

    if potencial_score >= 75:
        pitch_label = "Pitch Forte"
    elif potencial_score >= 55:
        pitch_label = "Pitch Promissor"
    elif potencial_score > 0:
        pitch_label = "Pitch com Pontos Críticos"
    else:
        pitch_label = "Análise Inconclusiva"

    o_que_funcionou = []
    o_que_prejudicou = []
    o_que_melhorar = []

    if _count_momento(momentos, "interesse") > 0:
        o_que_funcionou.append("Houve sinais de interesse em momentos específicos da conversa.")
    if _count_momento(momentos, "fechamento") > 0:
        o_que_funcionou.append("Houve algum sinal de abertura para avanço ou fechamento.")
    if persuasao >= 60:
        o_que_funcionou.append("A fala apresentou bons sinais de persuasão comercial.")

    if queda is not None and queda <= 5 and engagement > 0:
        o_que_prejudicou.append("Há evidência de perda de atenção logo no início da conversa.")
        o_que_melhorar.append("Reforce a abertura com uma dor clara, promessa de valor ou pergunta consultiva.")
    elif queda is not None and queda <= 12 and engagement > 0:
        o_que_prejudicou.append("Existe um possível sinal de queda de atenção ainda no começo do pitch.")
        o_que_melhorar.append("Fortaleça os primeiros segundos antes de entrar na explicação comercial.")

    if energia > 0 and energia < 25:
        o_que_prejudicou.append("A energia vocal ficou baixa para uma abordagem comercial.")
        o_que_melhorar.append("Aumente a energia nos trechos de valor, preço e fechamento.")
    if fluidez > 0 and fluidez < 35:
        o_que_prejudicou.append("A fluidez da fala pode ter prejudicado a continuidade da mensagem.")
        o_que_melhorar.append("Reduza pausas longas e deixe a fala mais contínua.")
    if reacao_preco == "Negativa":
        o_que_prejudicou.append("O preço parece ter gerado resistência ou dúvida.")
        o_que_melhorar.append("Apresente valor, prova ou benefício antes de falar de preço.")
    if fechamento_score > 0 and fechamento_score < 40:
        o_que_prejudicou.append("O fechamento não mostrou força suficiente para conduzir o próximo passo.")
        o_que_melhorar.append("Use um fechamento mais direto, com convite claro para ação.")
    if clareza > 0 and clareza < 55:
        o_que_melhorar.append("Simplifique a proposta de valor e deixe o benefício principal mais explícito.")

    if not o_que_funcionou:
        o_que_funcionou.append("Não houve evidência forte de resposta comercial positiva. Esse ponto deve ser validado com mais dados do vídeo.")
    if not o_que_prejudicou:
        o_que_prejudicou.append("Não foram encontrados pontos críticos confirmados com alta evidência.")
    if not o_que_melhorar:
        o_que_melhorar.append("Manter a estrutura geral e testar ajustes pontuais nos trechos de maior impacto.")

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
        "nivel_confianca_geral": confianca_geral,
        "potencial_score": round(potencial_score, 2),
        "o_que_funcionou": o_que_funcionou[:4],
        "o_que_prejudicou": o_que_prejudicou[:4],
        "o_que_melhorar": o_que_melhorar[:4],
    }
