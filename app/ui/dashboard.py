import os
import json
import math
import re
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from app.analysis.pipeline import processar_video
from app.analysis.diagnostico_comercial import gerar_diagnostico_comercial
from app.analysis.insights_contextuais import enriquecer_diagnostico_contextual


st.set_page_config(page_title="Insight Emotion AI", page_icon="📊", layout="wide")

MAPA_Y = {
    "Interesse": 6,
    "Curiosidade": 5,
    "Atenção moderada": 4,
    "Perda de interesse": 3,
    "Resistencia": 2,
    "Apreensao": 1,
    "Rejeicao": 0,
    "Indefinido": 0,
}

def formatar_tempo(seg):
    try:
        return f"{float(seg):.1f}".replace(".", ",") + "s"
    except Exception:
        return "—"

def pill_html(texto):
    chave = str(texto).strip().lower()
    if chave in ["fraco", "negativa"]:
        cls = "pill-red"
    elif chave in ["medio", "médio"]:
        cls = "pill-orange"
    elif chave == "bom":
        cls = "pill-yellow"
    elif chave in ["forte", "excelente"]:
        cls = "pill-green"
    else:
        cls = "pill-gray"
    return f'<span class="pill {cls}">{texto}</span>'

def score_to_percent(v):
    try:
        v = float(v)
    except Exception:
        return 0
    return max(0, min(100, int(v)))

def score_bar(value):
    pct = score_to_percent(value)
    segmentos = 12
    ativos = int(round((pct / 100) * segmentos))
    if pct > 0 and ativos == 0:
        ativos = 1
    ativos = max(0, min(segmentos, ativos))
    partes = []
    for i in range(segmentos):
        cls = "progress-seg active" if i < ativos else "progress-seg"
        partes.append(f'<span class="{cls}"></span>')
    return '<div class="progress-track"><div class="progress-segments">' + ''.join(partes) + '</div></div>'

def classe_cor(label):
    chave = str(label).lower()
    if chave in ["medio", "médio"]:
        return "orange"
    if chave == "bom":
        return "yellow"
    if chave in ["forte", "excelente"]:
        return "green"
    return "red"


def compactar_texto_card(texto, limite=240):
    texto = str(texto or "").replace("\n", " ").strip()
    texto = " ".join(texto.split())
    if len(texto) <= limite:
        return texto
    corte = texto[:limite].rsplit(" ", 1)[0]
    return corte + "..."

def extrair_status_descricao(valor):
    texto = str(valor or "Não identificado").strip()
    texto = " ".join(texto.split())

    status_possiveis = [
        "Não identificado", "Inconclusivo", "Fraco", "Médio", "Medio",
        "Bom", "Forte", "Excelente", "Negociada", "Negativa", "Positiva"
    ]

    for status in status_possiveis:
        if texto.lower().startswith(status.lower()):
            desc = texto[len(status):].strip(" -—:,.")
            return status.replace("Medio", "Médio"), desc

    if "—" in texto:
        a, b = texto.split("—", 1)
        return a.strip(), b.strip()

    if " - " in texto:
        a, b = texto.split(" - ", 1)
        return a.strip(), b.strip()

    if "," in texto and len(texto.split(",", 1)[0]) <= 18:
        a, b = texto.split(",", 1)
        return a.strip(), b.strip()

    return texto, ""

def cor_por_status(status):
    chave = str(status).strip().lower()
    if chave in ["forte", "excelente", "positivo", "positiva", "bom"]:
        return "green" if chave in ["forte", "excelente", "positivo", "positiva"] else "yellow"
    if chave in ["médio", "medio", "negociada"]:
        return "orange"
    if chave in ["não identificado", "inconclusivo"]:
        return "yellow"
    return "red"

def render_diag_value(valor):
    status, desc = extrair_status_descricao(valor)
    cor = cor_por_status(status)
    desc = compactar_texto_card(desc, 115)

    if desc:
        return (
            f'<div class="diag-status {cor}">{status}</div>'
            f'<div class="diag-desc">{desc}</div>'
        )

    return f'<div class="diag-status {cor}">{compactar_texto_card(status, 90)}</div>'

def interpretar_score_lateral(titulo, valor, label, diagnostico=None):
    titulo_norm = str(titulo).lower()
    label_norm = str(label).lower()

    if "energia" in titulo_norm:
        if label_norm in ["forte", "excelente", "bom"]:
            return "Boa presença vocal para sustentar a abordagem."
        if label_norm in ["médio", "medio"]:
            return "Energia suficiente, mas ainda pode variar mais o tom."
        return "Pode reduzir entusiasmo e segurança percebida."

    if "ritmo" in titulo_norm or "fluidez" in titulo_norm:
        if label_norm in ["forte", "excelente", "bom"]:
            return "Ritmo favorece compreensão da mensagem."
        if label_norm in ["médio", "medio"]:
            return "Ritmo aceitável, mas pode reduzir pausas."
        return "Pode prejudicar continuidade e confiança."

    if "clareza" in titulo_norm:
        if label_norm in ["forte", "excelente", "bom"]:
            return "Oferta compreensível para o cliente."
        if label_norm in ["médio", "medio"]:
            return "Mensagem clara em partes, mas ainda pode simplificar."
        return "Benefício principal precisa ficar mais evidente."

    if "fechamento" in titulo_norm:
        fechamento_real = ""
        try:
            fechamento_real = str((diagnostico or {}).get("fechamento_real", "")).lower()
        except Exception:
            fechamento_real = ""

        if "positivo" in fechamento_real:
            return "Venda avançou, mas avalie se foi conduzida ou passiva."
        if label_norm in ["forte", "excelente", "bom"]:
            return "Boa condução para o próximo passo."
        if label_norm in ["médio", "medio"]:
            return "Há avanço, mas pode confirmar decisão com mais clareza."
        return "Cliente pode decidir, mas o vendedor conduziu pouco."

    return "Indicador usado como apoio à leitura comercial."

def trecho_parece_confuso(texto):
    texto = str(texto or "").strip()
    if not texto:
        return True

    palavras = texto.split()
    if len(palavras) < 4:
        return True

    muito_longas = [p for p in palavras if len(p) > 22]
    sem_vogais = [p for p in palavras if len(p) > 5 and not re.search(r"[aeiouáéíóúãõâêô]", p.lower())]

    if len(muito_longas) >= 2 or len(sem_vogais) >= 2:
        return True

    return False


def render_heatmap(df_plot, metrics):
    if df_plot.empty or "emocao_negocio" not in df_plot.columns:
        st.markdown('<div class="card">Sem dados para gerar o mapa de engajamento.</div>', unsafe_allow_html=True)
        return

    pico = metrics.get("pico_emocional_segundos")
    queda = metrics.get("queda_interesse_segundos")
    momentos_impacto = metrics.get("momentos_impacto", [])

    try:
        total_seg = float(df_plot["tempo_segundos"].max())
        if total_seg <= 0:
            total_seg = 50.0
    except Exception:
        total_seg = 50.0

    melhor_fechamento = None
    for momento in momentos_impacto:
        emocao = str(momento.get("emocao", "")).strip().lower()
        if melhor_fechamento is None and emocao in ["interesse", "curiosidade", "neutro"]:
            melhor_fechamento = momento.get("fim_segundos")

    queda_posterior = None
    for momento in momentos_impacto:
        try:
            inicio = float(momento.get("inicio_segundos", 0) or 0)
        except Exception:
            inicio = 0
        emocao = str(momento.get("emocao", "")).strip().lower()
        if inicio >= 30 and emocao in ["desconexao", "desconexão", "perda de interesse", "sad", "fear", "tristeza", "medo", "resistencia", "resistência"]:
            queda_posterior = inicio
            break

    def pos(seg):
        try:
            if seg is None:
                return None
            s = float(seg)
            return max(1, min(98, (s / total_seg) * 100))
        except Exception:
            return None

    top_cards = (
        '<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-bottom:24px;">'
            '<div style="background:linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));border:1px solid rgba(151,172,214,.10);border-radius:18px;padding:18px 18px;">'
                '<div style="color:#eef4ff;font-weight:800;font-size:1rem;margin-bottom:8px;">⭐ Maior conexão</div>'
                f'<div style="color:#ffffff;font-size:2rem;font-weight:900;line-height:1;">{formatar_tempo(pico)}</div>'
                '<div style="color:#b9c8e8;font-size:.92rem;margin-top:10px;">Ponto de maior conexão</div>'
            '</div>'
            '<div style="background:linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));border:1px solid rgba(151,172,214,.10);border-radius:18px;padding:18px 18px;">'
                '<div style="color:#eef4ff;font-weight:800;font-size:1rem;margin-bottom:8px;">▲ Atenção inicial</div>'
                f'<div style="color:#ffffff;font-size:2rem;font-weight:900;line-height:1;">{formatar_tempo(queda)}</div>'
                '<div style="color:#b9c8e8;font-size:.92rem;margin-top:10px;">Início com menor ativação</div>'
            '</div>'
            '<div style="background:linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));border:1px solid rgba(151,172,214,.10);border-radius:18px;padding:18px 18px;">'
                '<div style="color:#eef4ff;font-weight:800;font-size:1rem;margin-bottom:8px;">● Leitura do pitch</div>'
                '<div style="color:#ffffff;font-size:2rem;font-weight:900;line-height:1;">Fluxo</div>'
                '<div style="color:#b9c8e8;font-size:.92rem;margin-top:10px;">Jornada emocional da conversa</div>'
            '</div>'
        '</div>'
    )

    line = '<div style="position:absolute;left:0;right:0;top:58%;height:4px;background:linear-gradient(90deg,#ff6b72 0%, #ff8a62 25%, #ffd76a 50%, #6ee7b7 72%, #8ea7d8 100%);border-radius:999px;transform:translateY(-50%);opacity:.68;"></div>'

    markers = []
    for s in [0, 10, 20, 30, 40, total_seg]:
        l = pos(s)
        if l is not None:
            markers.append(
                f'<div style="position:absolute;left:{l:.2f}%;top:58%;transform:translate(-50%,-50%);width:8px;height:8px;border-radius:999px;background:#8ea7d8;border:1px solid rgba(255,255,255,.28);z-index:3;"></div>'
            )

    if queda is not None:
        markers.append(
            f'<div style="position:absolute;left:{pos(queda):.2f}%;top:58%;transform:translate(-50%,-50%);width:16px;height:16px;border-radius:999px;background:#ff6b72;box-shadow:0 0 18px rgba(255,107,114,.28);border:1px solid rgba(255,255,255,.28);z-index:4;"></div>'
        )
        markers.append(
            f'<div style="position:absolute;left:{max(pos(queda), 8):.2f}%;top:58%;transform:translate(0,-36px);background:linear-gradient(180deg, rgba(25,36,60,.98) 0%, rgba(18,27,46,.98) 100%);border:1px solid rgba(255,107,114,.26);border-radius:16px;padding:10px 12px;min-width:120px;box-shadow:0 12px 30px rgba(0,0,0,.28);z-index:4;"><div style="color:#eef4ff;font-size:.82rem;font-weight:800;margin-bottom:4px;">⚠ Atenção inicial baixa</div><div style="color:#b9c8e8;font-size:.78rem;line-height:1.35;">início da conversa</div></div>'
        )

    if melhor_fechamento is not None:
        markers.append(
            f'<div style="position:absolute;left:{pos(melhor_fechamento):.2f}%;top:58%;transform:translate(-50%,-50%);width:16px;height:16px;border-radius:999px;background:#ffd76a;box-shadow:0 0 18px rgba(255,215,106,.28);border:1px solid rgba(255,255,255,.28);z-index:4;"></div>'
        )
        markers.append(
            f'<div style="position:absolute;left:{max(pos(melhor_fechamento), 18):.2f}%;top:58%;transform:translate(-50%,-78px);background:linear-gradient(180deg, rgba(25,36,60,.98) 0%, rgba(18,27,46,.98) 100%);border:1px solid rgba(255,215,106,.22);border-radius:16px;padding:10px 12px;min-width:150px;box-shadow:0 12px 30px rgba(0,0,0,.28);z-index:4;"><div style="color:#eef4ff;font-size:.82rem;font-weight:800;margin-bottom:4px;">⭐ Nível máximo</div><div style="color:#b9c8e8;font-size:.78rem;line-height:1.35;">{formatar_tempo(melhor_fechamento)} | Momento favorável</div></div>'
        )

    if queda_posterior is not None:
        markers.append(
            f'<div style="position:absolute;left:{pos(queda_posterior):.2f}%;top:58%;transform:translate(-50%,-50%);width:14px;height:14px;border-radius:999px;background:#ff8a62;box-shadow:0 0 18px rgba(255,138,98,.28);border:1px solid rgba(255,255,255,.28);z-index:4;"></div>'
        )

    scale = []
    for s in [0, 10, 20, 30, 40, 50]:
        real = min(s, total_seg)
        l = pos(real if total_seg >= 50 else (s / 50) * total_seg)
        scale.append(f'<span style="position:absolute;left:{l:.2f}%;transform:translateX(-50%);color:#9fb6ff;font-size:.78rem;">{s}s</span>')

    insight_1 = f'⚠️ <strong>Atenção inicial baixa</strong> logo no início, baixa ativação emocional aos <strong>{formatar_tempo(queda)}</strong>' if queda is not None else '⚠️ <strong>Atenção inicial baixa</strong> não identificada'
    insight_2 = f'⭐ <strong>Melhor momento</strong> aos {formatar_tempo(melhor_fechamento)}: máximo interesse foi alcançado' if melhor_fechamento is not None else '⭐ <strong>Melhor momento</strong> não identificado'
    insight_3 = f'➚ <strong>Queda rápida</strong> após {formatar_tempo(queda_posterior)}: explicação longa causou desatenção' if queda_posterior is not None else '➚ <strong>Queda rápida</strong> não foi observada no final da conversa'

    html = (
        '<div class="card" style="padding:24px;border-radius:22px;">'
        + top_cards +
        '<div style="position:relative;height:156px;margin:12px 0 12px 0;">'
        + ''.join(markers)
        + line
        + '</div>'
        + '<div style="position:relative;height:18px;margin-top:2px;margin-bottom:18px;">'
        + ''.join(scale)
        + '</div>'
        + '<div style="display:flex;gap:22px;flex-wrap:wrap;font-size:.92rem;margin-bottom:18px;">'
            + '<span style="color:#6ee7b7;">● Alto engajamento</span>'
            + '<span style="color:#ffd76a;">● Atenção moderada</span>'
            + '<span style="color:#ff6b72;">● Objeção detectada / desconexão</span>'
        + '</div>'
        + '<div style="display:flex;flex-direction:column;gap:10px;">'
            + f'<div class="engagement-insight">{insight_1}</div>'
            + f'<div class="engagement-insight">{insight_2}</div>'
            + f'<div class="engagement-insight">{insight_3}</div>'
        + '</div>'
        + '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


st.markdown("""
<style>
:root{
    --bg:#071226;
    --card:#18263f;
    --border:#31435f;
    --text:#eef4ff;
    --muted:#9aabc6;
    --red:#ff5f62;
    --orange:#ffb347;
    --yellow:#ffd166;
    --green:#39d98a;
    --blue:#64a8ff;
    --purple:#9b7bff;
}
[data-testid="stAppViewContainer"]{
    background: radial-gradient(circle at top left, #0b1730 0%, #071226 55%, #050d1d 100%);
}
.block-container{
    max-width: 1500px;
    padding-top: 1rem;
    padding-bottom: 1rem;
}
.main-title{
    font-size:2.45rem;
    font-weight:900;
    color:var(--text);
    margin-bottom:.25rem;
}
.sub-title{
    color:var(--muted);
    margin-bottom:1.35rem;
}
.section-title{
    color:var(--text);
    font-size:1.45rem;
    font-weight:800;
    margin-top:1.1rem;
    margin-bottom:.9rem;
}
.card, .big-card, .panel-card, .score-card{
    background: linear-gradient(180deg, rgba(29,43,70,.96) 0%, rgba(24,38,63,.96) 100%);
    border:1px solid rgba(144,166,203,.16);
    border-radius:22px;
    box-shadow: 0 18px 45px rgba(0,0,0,.35);
    color:var(--text);
}
.big-card{ padding:22px; }
.card{ padding:18px; }
.panel-card{ padding:20px; min-height:220px; }
.score-card{ padding:18px; min-height:160px; margin-bottom:18px; }
.hero-score-card{
    background:linear-gradient(180deg, rgba(29,43,70,.98) 0%, rgba(24,38,63,.98) 100%);
    border:1px solid rgba(144,166,203,.16);
    border-radius:24px;
    padding:28px;
    text-align:center;
    margin-bottom:22px;
    box-shadow:0 20px 50px rgba(0,0,0,.32);
}
.hero-score-title{
    font-size:.85rem;
    letter-spacing:.14em;
    color:#9CA3AF;
    font-weight:800;
    margin-bottom:10px;
}
.hero-score-value{
    font-size:4rem;
    font-weight:900;
    line-height:1;
    color:#ffffff;
}
.hero-score-label{
    margin-top:10px;
    font-size:1.1rem;
    font-weight:800;
}
.hero-score-bar{
    width:100%;
    height:12px;
    margin-top:18px;
    background:#2a3a58;
    border-radius:999px;
    overflow:hidden;
}
.hero-score-fill{
    height:100%;
    background:linear-gradient(90deg,#ff6a63 0%, #ffb347 45%, #ffd166 70%, #39d98a 100%);
    border-radius:999px;
}
.diag-title{
    font-size:2rem;
    font-weight:900;
    color:var(--red);
    margin-bottom:18px;
}
.diag-grid{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:12px;
}
.diag-item{
    background: rgba(255,255,255,.03);
    border:1px solid rgba(255,255,255,.08);
    border-radius:16px;
    padding:14px;
}
.diag-item-label{
    color:#ffffff;
    font-size:.95rem;
    font-weight:800;
    margin-bottom:8px;
}
.diag-item-value{
    font-size:1.05rem;
    font-weight:800;
}
.diag-bottom{
    margin-top:18px;
    display:flex;
    align-items:center;
    gap:12px;
}
.pill{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    padding:6px 12px;
    border-radius:12px;
    font-size:.92rem;
    font-weight:800;
}
.pill-red{ background:rgba(255,95,98,.16); color:#ff8e91; }
.pill-orange{ background:rgba(255,179,71,.16); color:#ffc979; }
.pill-yellow{ background:rgba(255,209,102,.16); color:#ffe199; }
.pill-green{ background:rgba(57,217,138,.16); color:#7ef0b1; }
.pill-gray{ background:rgba(255,255,255,.07); color:#c9d6ef; }
.pill-score{
    background:rgba(255,255,255,.08);
    color:#d7e3ff;
    padding:6px 12px;
    border-radius:10px;
    font-size:.85rem;
    font-weight:700;
}
.red{ color:var(--red) !important; }
.orange{ color:var(--orange) !important; }
.yellow{ color:var(--yellow) !important; }
.green{ color:var(--green) !important; }

.side-score-title{
    color:var(--text);
    font-size:1rem;
    font-weight:700;
    margin-bottom:10px;
}
.side-score-value{
    color:#ffd7c5;
    font-size:2rem;
    font-weight:900;
    line-height:1.05;
}
.side-score-row{
    display:flex;
    align-items:center;
    gap:10px;
    margin-top:10px;
}
.progress-track{
    width:100%;
    height:8px;
    margin-top:12px;
}
.progress-segments{
    display:flex;
    gap:3px;
    width:100%;
    height:8px;
}
.progress-seg{
    flex:1;
    height:6px;
    border-radius:2px;
    background:#4b5a78;
}
.progress-seg.active{
    background: linear-gradient(90deg,#ff6a63 0%, #ff835b 45%, #ff4f59 100%);
}
.list-card-title{
    color:var(--text);
    font-size:1rem;
    font-weight:800;
    margin-bottom:12px;
}
.panel-card ul{
    padding-left:1.1rem;
    margin:0;
}
.panel-card li{
    color:#e8f0ff;
    margin-bottom:11px;
    line-height:1.6;
}
.small-label{
    color:var(--muted);
    font-size:.95rem;
    font-weight:600;
    margin-bottom:8px;
}
.metric-value{
    color:var(--text);
    font-size:2rem;
    font-weight:900;
    line-height:1.05;
}
.metric-sub{
    color:var(--muted);
    font-size:.92rem;
    margin-top:10px;
}

.heatmap-shell{
    background: linear-gradient(180deg, rgba(13,22,45,.52) 0%, rgba(10,18,38,.30) 100%);
    border:1px solid rgba(120,150,210,.12);
    border-radius:22px;
    padding:22px;
    box-shadow:0 18px 45px rgba(0,0,0,.20);
}
.heatmap-top{
    display:grid;
    grid-template-columns:repeat(3, 1fr);
    gap:14px;
    margin-bottom:18px;
}
.heatmap-kpi{
    display:flex;
    align-items:flex-start;
    gap:10px;
    padding:14px 16px;
    border-radius:16px;
    border:1px solid rgba(255,255,255,.06);
    background:rgba(255,255,255,.02);
}
.heatmap-kpi-icon{
    font-size:1rem;
    line-height:1.2;
    margin-top:2px;
}
.heatmap-kpi-title{
    color:#eef4ff;
    font-size:1rem;
    font-weight:800;
    margin-bottom:4px;
}
.heatmap-kpi-value{
    color:#ffffff;
    font-size:1.9rem;
    font-weight:900;
    line-height:1.05;
    margin-bottom:4px;
}
.heatmap-kpi-sub{
    color:#9aabc6;
    font-size:.84rem;
}
.heatmap-kpi-green .heatmap-kpi-icon{ color:#ffd166; }
.heatmap-kpi-red .heatmap-kpi-icon{ color:#ff6b72; }
.heatmap-kpi-blue .heatmap-kpi-icon{ color:#9bb0ff; }

.heatmap-stage{ margin-top:8px; }
.heatmap-bar{
    display:flex;
    width:100%;
    height:62px;
    border-radius:14px;
    overflow:hidden;
    background:#14233f;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.05), 0 10px 24px rgba(0,0,0,.22);
}
.hm-seg{
    flex:1;
    min-width:8px;
    position:relative;
}
.hm-seg + .hm-seg{
    box-shadow: inset 1px 0 0 rgba(9,18,36,.42);
}
.hm-green{ background:linear-gradient(180deg,#33e08a 0%, #10995b 100%); }
.hm-yellow{ background:linear-gradient(180deg,#ffe56f 0%, #e0ba28 100%); }
.hm-orange{ background:linear-gradient(180deg,#ffb15f 0%, #f07d1f 100%); }
.hm-red{ background:linear-gradient(180deg,#ff6873 0%, #e3364a 100%); }
.heatmap-scale{
    display:flex;
    justify-content:space-between;
    margin-top:10px;
    color:#9aabc6;
    font-size:.84rem;
    padding:0 2px;
}
.heatmap-legend{
    display:flex;
    flex-wrap:wrap;
    gap:16px;
    margin-top:16px;
    color:#cbd7f0;
    font-size:.88rem;
}
.hm-dot{
    display:inline-block;
    width:10px;
    height:10px;
    border-radius:999px;
    margin-right:7px;
    vertical-align:middle;
}


.pitch-insights-grid{
    display:grid;
    grid-template-columns:repeat(3, minmax(0,1fr));
    gap:16px;
    margin-top:14px;
    margin-bottom:18px;
}
.pitch-insight-card{
    background: linear-gradient(180deg, rgba(29,43,70,.96) 0%, rgba(24,38,63,.96) 100%);
    border:1px solid rgba(144,166,203,.16);
    border-radius:18px;
    padding:18px;
    box-shadow: 0 14px 30px rgba(0,0,0,.22);
}
.pitch-insight-title{
    color:#eef4ff;
    font-size:1rem;
    font-weight:800;
    margin-bottom:10px;
}
.pitch-insight-card ul{
    margin:0;
    padding-left:1rem;
}
.pitch-insight-card li{
    color:#dfe9ff;
    margin-bottom:10px;
    line-height:1.55;
}
@media (max-width: 1100px){
    .pitch-insights-grid{
        grid-template-columns:1fr;
    }
}



.strategy-box{
    background: linear-gradient(180deg, rgba(29,43,70,.96) 0%, rgba(24,38,63,.96) 100%);
    border:1px solid rgba(144,166,203,.16);
    border-radius:20px;
    padding:20px;
    box-shadow:0 16px 40px rgba(0,0,0,.28);
    margin-top:18px;
}
.strategy-title{
    color:#eef4ff;
    font-size:1.1rem;
    font-weight:900;
    margin-bottom:12px;
}
.strategy-box ul{
    margin:0;
    padding-left:1.1rem;
}
.strategy-box li{
    color:#dfe9ff;
    margin-bottom:10px;
    line-height:1.6;
}


.executive-summary{
    background:linear-gradient(180deg, rgba(28,42,72,.98) 0%, rgba(17,28,49,.98) 100%);
    border:1px solid rgba(151,172,214,.16);
    border-radius:26px;
    padding:24px 26px;
    margin-bottom:24px;
    box-shadow:0 18px 45px rgba(0,0,0,.30);
}
.executive-summary-grid{
    display:grid;
    grid-template-columns:1.2fr 1fr 1fr;
    gap:16px;
}
.executive-summary-title{
    color:#eef4ff;
    font-size:1.25rem;
    font-weight:900;
    margin-bottom:10px;
}
.executive-summary-text{
    color:#dbe6ff;
    font-size:.98rem;
    line-height:1.65;
}
.executive-kpi{
    background:rgba(255,255,255,.035);
    border:1px solid rgba(255,255,255,.08);
    border-radius:18px;
    padding:16px;
}
.executive-kpi-label{
    color:#9fb6ff;
    font-size:.78rem;
    font-weight:900;
    text-transform:uppercase;
    letter-spacing:.08em;
    margin-bottom:8px;
}
.executive-kpi-value{
    color:#ffffff;
    font-size:1.25rem;
    font-weight:900;
    line-height:1.25;
}
.executive-kpi-sub{
    color:#b9c8e8;
    font-size:.86rem;
    line-height:1.45;
    margin-top:8px;
}
@media (max-width: 1100px){
    .executive-summary-grid{
        grid-template-columns:1fr;
    }
}


.diag-status{
    font-size:1.05rem;
    font-weight:900;
    line-height:1.2;
    margin-bottom:6px;
}
.diag-desc{
    color:#cdd9f3;
    font-size:.82rem;
    line-height:1.42;
    font-weight:600;
}
.executive-summary-text{
    font-size:.94rem !important;
    line-height:1.58 !important;
}
.executive-kpi-value{
    font-size:1.08rem !important;
    line-height:1.32 !important;
}
.executive-kpi-sub{
    font-size:.82rem !important;
}
.card strong{
    color:#eef4ff;
}


/* ===== MODO FEIRA - VISUAL CLEAN ===== */

.main-title{
    font-size:2.15rem !important;
    letter-spacing:-.04em;
}

.sub-title{
    font-size:.98rem !important;
    color:#b9c8e8 !important;
}

.section-title{
    font-size:1.26rem !important;
    margin-top:1.35rem !important;
    margin-bottom:.75rem !important;
}

.hero-score-card{
    padding:30px 32px !important;
    border-radius:24px !important;
    margin-bottom:24px !important;
}

.hero-score-title{
    font-size:.76rem !important;
    letter-spacing:.20em !important;
    color:#aebfe0 !important;
}

.hero-score-value{
    font-size:3.7rem !important;
}

.hero-score-label{
    font-size:1rem !important;
}

.executive-summary{
    padding:22px 24px !important;
    border-radius:24px !important;
}

.executive-summary-title{
    font-size:1.16rem !important;
    line-height:1.35 !important;
}

.executive-summary-text{
    max-width:720px;
}

.executive-kpi{
    padding:15px 16px !important;
    border-radius:16px !important;
}

.big-card{
    padding:24px !important;
    border-radius:24px !important;
}

.diag-title{
    color:#f3f7ff !important;
    font-size:1.55rem !important;
    letter-spacing:-.03em;
    margin-bottom:16px !important;
}

.diag-grid{
    gap:10px !important;
}

.diag-item{
    padding:13px !important;
    border-radius:15px !important;
}

.diag-item-label{
    font-size:.82rem !important;
    color:#dfe8ff !important;
    margin-bottom:7px !important;
}

.diag-status{
    font-size:.98rem !important;
}

.diag-desc{
    font-size:.78rem !important;
    line-height:1.38 !important;
    color:#c5d2ed !important;
}

.panel-card{
    padding:18px 20px !important;
    border-radius:20px !important;
    min-height:auto !important;
}

.list-card-title{
    font-size:.94rem !important;
    margin-bottom:10px !important;
}

.check-item{
    font-size:.86rem !important;
    line-height:1.48 !important;
    margin-bottom:8px !important;
}

.score-card{
    padding:18px !important;
    border-radius:20px !important;
    min-height:auto !important;
    margin-bottom:14px !important;
}

.side-score-title{
    font-size:.9rem !important;
}

.side-score-value{
    font-size:1.85rem !important;
}

.metric-sub{
    font-size:.8rem !important;
    line-height:1.45 !important;
}

.strategy-box{
    padding:22px !important;
    border-radius:24px !important;
}

.strategy-title{
    font-size:1rem !important;
}

.strategy-box li{
    font-size:.88rem !important;
    line-height:1.5 !important;
}

.card{
    border-radius:20px !important;
    padding:17px !important;
}

.card div{
    line-height:1.5;
}

.progress-seg.active{
    background:linear-gradient(90deg,#ff8a62 0%, #ffd166 55%, #6ee7b7 100%) !important;
}

/* Menos aparência de erro quando a análise é de venda concluída */
.red{
    color:#ff7f87 !important;
}

.orange{
    color:#ffc46b !important;
}

.yellow{
    color:#ffe08a !important;
}

.green{
    color:#6ee7b7 !important;
}

/* Oculta elementos padrão que deixam a apresentação com cara de app cru */
#MainMenu{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}

/* Melhor leitura em telas menores de notebook */
@media (max-width: 1200px){
    .diag-grid{
        grid-template-columns:repeat(2,minmax(0,1fr)) !important;
    }

    .hero-score-value{
        font-size:3.1rem !important;
    }

    .executive-summary-grid{
        grid-template-columns:1fr !important;
    }
}


/* === PADRONIZACAO_VISUAL_CLEAN === */

/* paleta mais suave */
:root{
    --soft-red:#f29a9f;
    --soft-orange:#e8b978;
    --soft-yellow:#e4cb89;
    --soft-green:#97c9ac;
    --soft-text:#d9e4f7;
    --soft-muted:#9fb1d1;
    --soft-line:#3a4b69;
}

/* títulos */
.main-title,
.sub-title,
.section-title,
.hero-score-title,
.diag-title,
.diag-item-label,
.list-card-title,
.side-score-title,
.strategy-title,
.pitch-insight-title,
.small-label,
.heatmap-kpi-title{
    font-weight:800 !important;
}

/* textos gerais */
.card,
.big-card,
.panel-card,
.score-card,
.strategy-box,
.pitch-insight-card,
.heatmap-shell,
.hero-score-card{
    color:var(--soft-text) !important;
}

.card p,
.big-card p,
.panel-card p,
.score-card p,
.strategy-box p,
.pitch-insight-card p,
.heatmap-shell p,
.hero-score-card p,
.card li,
.big-card li,
.panel-card li,
.score-card li,
.strategy-box li,
.pitch-insight-card li,
.heatmap-shell li,
.hero-score-card li,
.check-item,
.metric-sub,
.heatmap-kpi-sub,
.sub-title{
    font-weight:400 !important;
    color:var(--soft-text) !important;
    line-height:1.55 !important;
}

/* strong mais leve dentro do conteúdo */
.card strong,
.big-card strong,
.panel-card strong,
.score-card strong,
.strategy-box strong,
.pitch-insight-card strong,
.heatmap-shell strong,
.hero-score-card strong{
    font-weight:500 !important;
    color:inherit !important;
}

/* valores e números */
.hero-score-value,
.side-score-value,
.metric-value,
.heatmap-kpi-value{
    font-weight:700 !important;
    color:#ffffff !important;
}

/* labels de status mais discretas */
.red{ color:var(--soft-red) !important; }
.orange{ color:var(--soft-orange) !important; }
.yellow{ color:var(--soft-yellow) !important; }
.green{ color:var(--soft-green) !important; }

.diag-item-value{
    font-weight:700 !important;
}

.diag-bottom span:last-child{
    font-weight:700 !important;
}

.check-item span:last-child{
    font-weight:400 !important;
    color:var(--soft-text) !important;
}

/* pills mais discretas */
.pill-red{ background:rgba(242,154,159,.10) !important; color:var(--soft-red) !important; }
.pill-orange{ background:rgba(232,185,120,.10) !important; color:var(--soft-orange) !important; }
.pill-yellow{ background:rgba(228,203,137,.10) !important; color:var(--soft-yellow) !important; }
.pill-green{ background:rgba(151,201,172,.10) !important; color:var(--soft-green) !important; }
.pill-gray{ background:rgba(255,255,255,.05) !important; color:#c7d4ee !important; }

/* barras e progresso menos chamativos */
.hero-score-fill{
    background:linear-gradient(90deg,#d98b84 0%, #d7b06e 45%, #9bc5a8 100%) !important;
}
.progress-seg.active{
    background:linear-gradient(90deg,#d98b84 0%, #d7b06e 50%, #9bc5a8 100%) !important;
}

/* heatmap/legendas menos coloridos */
.heatmap-legend span,
.heatmap-scale span,
.engagement-insight{
    color:var(--soft-text) !important;
    font-weight:400 !important;
}
.engagement-insight strong{
    font-weight:500 !important;
}

/* bordas e contraste mais limpos */
.card, .big-card, .panel-card, .score-card, .strategy-box, .pitch-insight-card, .hero-score-card, .heatmap-shell{
    border-color:rgba(144,166,203,.12) !important;
    box-shadow:0 12px 28px rgba(0,0,0,.22) !important;
}

/* markdown do streamlit dentro dos cards */
div[data-testid="stMarkdownContainer"] p{
    font-weight:400;
}
div[data-testid="stMarkdownContainer"] strong{
    font-weight:500;
}

/* evita exagero visual em títulos muito vermelhos */
.diag-title{
    color:#ff8f97 !important;
}

/* === FIM_PADRONIZACAO_VISUAL_CLEAN === */


/* === LAYOUT_DASHBOARD_CLEAN_V2 === */

/* ===== ESPAÇAMENTO GERAL ===== */
.section-title{
    margin-top: 30px !important;
    margin-bottom: 14px !important;
    font-size: 1.65rem !important;
    line-height: 1.2 !important;
}

.main-title{
    margin-bottom: 8px !important;
}

.sub-title{
    margin-bottom: 26px !important;
    max-width: 900px !important;
}

/* ===== HERO ===== */
.hero-score-card{
    padding: 28px 30px !important;
    border-radius: 22px !important;
    margin-top: 12px !important;
    margin-bottom: 26px !important;
}

.hero-score-title{
    font-size: .82rem !important;
    letter-spacing: .16em !important;
    text-transform: uppercase !important;
    margin-bottom: 10px !important;
}

.hero-score-value{
    font-size: 3rem !important;
    line-height: 1 !important;
    margin-bottom: 10px !important;
}

.hero-score-label{
    font-size: 1rem !important;
    margin-bottom: 18px !important;
}

.hero-score-bar{
    height: 8px !important;
    border-radius: 999px !important;
    overflow: hidden !important;
}

/* ===== RESUMO / CARDS GERAIS ===== */
.card,
.big-card,
.panel-card,
.score-card,
.strategy-box,
.pitch-insight-card,
.heatmap-shell{
    border-radius: 20px !important;
    padding: 18px 18px !important;
    margin-bottom: 14px !important;
}

.card h1, .card h2, .card h3,
.big-card h1, .big-card h2, .big-card h3,
.panel-card h1, .panel-card h2, .panel-card h3,
.score-card h1, .score-card h2, .score-card h3{
    margin-top: 0 !important;
    margin-bottom: 10px !important;
}

/* ===== BLOCOS DO RESUMO EXECUTIVO ===== */
.executive-grid,
.summary-grid{
    display: grid !important;
    grid-template-columns: 1.4fr 1fr 1fr !important;
    gap: 14px !important;
    align-items: stretch !important;
}

.executive-card,
.summary-card,
.summary-kpi-card{
    min-height: 145px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    padding: 18px !important;
    border-radius: 18px !important;
}

.executive-card p,
.summary-card p,
.summary-kpi-card p{
    margin: 0 !important;
}

/* ===== DIAGNÓSTICO ===== */
.big-card{
    padding: 20px !important;
}

.diag-title{
    font-size: 1.05rem !important;
    line-height: 1.25 !important;
    margin-bottom: 16px !important;
}

.diag-grid{
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0,1fr)) !important;
    gap: 12px !important;
    margin-bottom: 14px !important;
    align-items: stretch !important;
}

.diag-item{
    min-height: 120px !important;
    padding: 14px 14px !important;
    border-radius: 16px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
}

.diag-item-label{
    font-size: .86rem !important;
    line-height: 1.25 !important;
    margin-bottom: 10px !important;
}

.diag-item-value{
    font-size: .98rem !important;
    line-height: 1.45 !important;
    word-break: break-word !important;
}

.diag-bottom{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    flex-wrap: wrap !important;
    margin-top: 4px !important;
}

.pill-score{
    padding: 6px 10px !important;
    border-radius: 10px !important;
    font-size: .78rem !important;
}

.diag-bottom span:last-child{
    font-size: 1.02rem !important;
}

/* ===== BLOCOS "PONTOS FORTES / RISCOS / AÇÕES" ===== */
.panel-card{
    min-height: 170px !important;
}

.list-card-title{
    font-size: .98rem !important;
    margin-bottom: 12px !important;
}

.check-list{
    display: flex !important;
    flex-direction: column !important;
    gap: 10px !important;
}

.check-item{
    display: flex !important;
    align-items: flex-start !important;
    gap: 8px !important;
    line-height: 1.55 !important;
}

.check-item span:last-child{
    display: block !important;
    flex: 1 !important;
}

/* ===== CARDS LATERAIS DAS MÉTRICAS ===== */
.score-card{
    min-height: 138px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
}

.side-score-title{
    font-size: .96rem !important;
    margin-bottom: 8px !important;
}

.side-score-value{
    font-size: 1.28rem !important;
    line-height: 1.1 !important;
    margin-bottom: 6px !important;
}

.metric-sub{
    font-size: .84rem !important;
    line-height: 1.45 !important;
    margin-top: 8px !important;
}

/* ===== SINAIS / JORNADA / MAPA ===== */
.heatmap-shell{
    padding: 20px !important;
}

.heatmap-kpi-grid{
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0,1fr)) !important;
    gap: 12px !important;
    margin-bottom: 18px !important;
}

.heatmap-kpi-card{
    min-height: 104px !important;
    border-radius: 16px !important;
    padding: 14px !important;
}

.heatmap-kpi-title{
    font-size: .9rem !important;
    margin-bottom: 8px !important;
}

.heatmap-kpi-value{
    font-size: 1.15rem !important;
    margin-bottom: 6px !important;
}

.heatmap-kpi-sub{
    font-size: .84rem !important;
}

/* ===== PRIORIDADES ===== */
.strategy-box{
    padding: 22px !important;
}

.strategy-title{
    margin-bottom: 16px !important;
    font-size: 1.05rem !important;
}

.priority-grid{
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0,1fr)) !important;
    gap: 14px !important;
    align-items: stretch !important;
}

.priority-card{
    min-height: 150px !important;
    padding: 16px !important;
    border-radius: 16px !important;
}

.priority-card p{
    margin: 0 !important;
    line-height: 1.6 !important;
}

/* ===== EVIDÊNCIAS ===== */
.evidence-card{
    padding: 18px !important;
    border-radius: 18px !important;
    margin-bottom: 14px !important;
}

.evidence-title{
    font-size: .82rem !important;
    margin-bottom: 10px !important;
    letter-spacing: .12em !important;
    text-transform: uppercase !important;
}

.evidence-card p{
    margin-top: 0 !important;
    margin-bottom: 8px !important;
    line-height: 1.6 !important;
}

.evidence-card blockquote{
    margin: 10px 0 !important;
}

/* ===== TEXTOS ===== */
p, li, span{
    word-break: break-word !important;
}

.card p,
.big-card p,
.panel-card p,
.score-card p,
.strategy-box p,
.pitch-insight-card p,
.heatmap-shell p{
    font-size: .95rem !important;
}

/* ===== RESPONSIVIDADE ===== */
@media (max-width: 1200px){
    .executive-grid,
    .summary-grid,
    .diag-grid,
    .priority-grid,
    .heatmap-kpi-grid{
        grid-template-columns: 1fr !important;
    }

    .diag-item,
    .executive-card,
    .summary-card,
    .summary-kpi-card,
    .priority-card{
        min-height: auto !important;
    }
}

/* === FIM_LAYOUT_DASHBOARD_CLEAN_V2 === */


/* === RESUMO_EXECUTIVO_NEGRITO_CLEAN === */

/* Somente títulos em destaque */
.executive-summary-title{
    font-weight:800 !important;
    color:#eef4ff !important;
}

/* Rótulos pequenos podem ser seminegrito, mas discretos */
.executive-kpi-label{
    font-weight:700 !important;
    color:#9fb6ff !important;
}

/* Conteúdo do resumo sem negrito excessivo */
.executive-summary-text,
.executive-kpi-value,
.executive-kpi-sub{
    font-weight:400 !important;
    color:#d9e4f7 !important;
}

/* Valor principal dos cards do resumo: legível, mas não pesado */
.executive-kpi-value{
    font-size:1rem !important;
    line-height:1.45 !important;
}

/* Subtexto mais discreto */
.executive-kpi-sub{
    font-size:.82rem !important;
    color:#aebcda !important;
    line-height:1.45 !important;
}

/* Remove força de negrito caso algum strong apareça dentro do resumo */
.executive-summary strong,
.executive-kpi strong{
    font-weight:400 !important;
    color:inherit !important;
}

/* === FIM_RESUMO_EXECUTIVO_NEGRITO_CLEAN === */


/* === PADRAO_VISUAL_GERAL_V3 === */

/* ===== BASE GERAL ===== */
:root{
    --ui-bg-card:rgba(28,42,72,.96);
    --ui-bg-card-2:rgba(20,33,57,.98);
    --ui-border:rgba(144,166,203,.14);
    --ui-text:#dbe6f8;
    --ui-title:#f3f7ff;
    --ui-muted:#a9b9d6;
    --ui-soft-red:#e99aa0;
    --ui-soft-orange:#dfb979;
    --ui-soft-yellow:#d9c98a;
    --ui-soft-green:#9cc9ad;
}

/* ===== RESET DE PESO DOS TEXTOS ===== */
.card,
.big-card,
.panel-card,
.score-card,
.strategy-box,
.hero-score-card,
.executive-summary,
.executive-kpi{
    font-weight:400 !important;
    color:var(--ui-text) !important;
}

/* Todo texto interno fica normal por padrão */
.card div,
.big-card div,
.panel-card div,
.score-card div,
.strategy-box div,
.hero-score-card div,
.executive-summary div,
.executive-kpi div,
.card span,
.big-card span,
.panel-card span,
.score-card span,
.strategy-box span,
.hero-score-card span,
.executive-summary span,
.executive-kpi span,
.card li,
.big-card li,
.panel-card li,
.score-card li,
.strategy-box li{
    font-weight:400 !important;
}

/* ===== SOMENTE TÍTULOS EM NEGRITO ===== */
.main-title,
.section-title,
.hero-score-title,
.diag-title,
.diag-item-label,
.list-card-title,
.side-score-title,
.small-label,
.strategy-title,
.executive-summary-title,
.executive-kpi-label{
    font-weight:800 !important;
    color:var(--ui-title) !important;
}

/* Rótulos pequenos mais discretos */
.hero-score-title,
.executive-kpi-label,
.small-label{
    color:#9fb6ff !important;
    letter-spacing:.10em !important;
    text-transform:uppercase !important;
    font-size:.74rem !important;
}

/* ===== VALORES PRINCIPAIS SEM EXAGERO ===== */
.hero-score-value{
    font-weight:700 !important;
    font-size:3.35rem !important;
    color:#ffffff !important;
}

.side-score-value,
.metric-value{
    font-weight:700 !important;
    color:#ffffff !important;
}

.hero-score-label,
.diag-status,
.pill,
.pill-score{
    font-weight:600 !important;
}

/* ===== CORES MAIS SUAVES E PADRONIZADAS ===== */
.red{ color:var(--ui-soft-red) !important; }
.orange{ color:var(--ui-soft-orange) !important; }
.yellow{ color:var(--ui-soft-yellow) !important; }
.green{ color:var(--ui-soft-green) !important; }

.pill-red{
    background:rgba(233,154,160,.10) !important;
    color:var(--ui-soft-red) !important;
}
.pill-orange{
    background:rgba(223,185,121,.10) !important;
    color:var(--ui-soft-orange) !important;
}
.pill-yellow{
    background:rgba(217,201,138,.10) !important;
    color:var(--ui-soft-yellow) !important;
}
.pill-green{
    background:rgba(156,201,173,.10) !important;
    color:var(--ui-soft-green) !important;
}
.pill-gray{
    background:rgba(255,255,255,.055) !important;
    color:#c8d5ee !important;
}

/* ===== CARDS PADRONIZADOS ===== */
.card,
.big-card,
.panel-card,
.score-card,
.strategy-box,
.hero-score-card,
.executive-summary,
.executive-kpi{
    background:linear-gradient(180deg, var(--ui-bg-card) 0%, var(--ui-bg-card-2) 100%) !important;
    border:1px solid var(--ui-border) !important;
    box-shadow:0 12px 28px rgba(0,0,0,.22) !important;
    border-radius:20px !important;
}

/* ===== RESUMO EXECUTIVO ===== */
.executive-summary{
    padding:22px !important;
}

.executive-summary-grid{
    display:grid !important;
    grid-template-columns:1.35fr 1fr 1fr !important;
    gap:14px !important;
    align-items:stretch !important;
}

.executive-summary-title{
    font-size:1rem !important;
    line-height:1.35 !important;
    margin-bottom:10px !important;
}

.executive-summary-text{
    font-size:.88rem !important;
    line-height:1.58 !important;
    color:var(--ui-text) !important;
    font-weight:400 !important;
}

.executive-kpi{
    padding:16px !important;
    min-height:140px !important;
}

.executive-kpi-value{
    font-size:.96rem !important;
    line-height:1.46 !important;
    color:var(--ui-text) !important;
    font-weight:400 !important;
}

.executive-kpi-sub{
    font-size:.78rem !important;
    line-height:1.45 !important;
    color:var(--ui-muted) !important;
    font-weight:400 !important;
    margin-top:8px !important;
}

/* ===== DIAGNÓSTICO ===== */
.diag-title{
    font-size:1.18rem !important;
    line-height:1.3 !important;
    margin-bottom:16px !important;
}

.diag-grid{
    gap:12px !important;
}

.diag-item{
    min-height:120px !important;
    padding:14px !important;
    border-radius:16px !important;
}

.diag-item-label{
    font-size:.78rem !important;
    line-height:1.3 !important;
    margin-bottom:10px !important;
}

.diag-item-value,
.diag-desc{
    font-size:.78rem !important;
    line-height:1.45 !important;
    color:var(--ui-text) !important;
}

.diag-status{
    font-size:.88rem !important;
    margin-bottom:4px !important;
}

/* ===== PONTOS FORTES / RISCOS / AÇÕES ===== */
.panel-card{
    padding:18px !important;
    min-height:auto !important;
}

.list-card-title{
    font-size:.9rem !important;
    margin-bottom:12px !important;
}

.check-item{
    font-size:.82rem !important;
    line-height:1.52 !important;
    color:var(--ui-text) !important;
}

.check-icon,
.warn-icon,
.action-icon{
    opacity:.85 !important;
}

/* ===== CARDS LATERAIS ===== */
.score-card{
    padding:18px !important;
    min-height:135px !important;
}

.side-score-title{
    font-size:.86rem !important;
    margin-bottom:8px !important;
}

.side-score-value{
    font-size:1.32rem !important;
}

.side-score-row{
    margin-top:8px !important;
}

.metric-sub{
    font-size:.78rem !important;
    color:var(--ui-muted) !important;
    line-height:1.42 !important;
}

/* ===== BARRAS MENOS COLORIDAS ===== */
.hero-score-fill{
    background:linear-gradient(90deg,#d9908b 0%, #d8b371 50%, #a3c7ad 100%) !important;
}

.progress-seg.active{
    background:linear-gradient(90deg,#d9908b 0%, #d8b371 50%, #a3c7ad 100%) !important;
}

/* ===== PLANO E PRIORIDADES ===== */
.strategy-box{
    padding:22px !important;
}

.strategy-box li{
    font-size:.84rem !important;
    line-height:1.55 !important;
    color:var(--ui-text) !important;
}

.strategy-title{
    font-size:.95rem !important;
}

/* Mantém Prioridade 1, 2 e 3 em destaque, mas sem exagero */
.strategy-box [style*="Prioridade"]{
    font-weight:800 !important;
}

/* ===== EVIDÊNCIAS ===== */
.card div[style*="text-transform:uppercase"]{
    font-weight:800 !important;
    color:#dbe6ff !important;
}

.card div[style*="color:#eef4ff"]{
    font-weight:400 !important;
    color:var(--ui-text) !important;
}

.card div[style*="color:#b9c8e8"]{
    font-weight:400 !important;
    color:var(--ui-muted) !important;
}

.card div[style*="color:#6ee7b7"]{
    font-weight:400 !important;
    color:#9cc9ad !important;
}

/* Remove negrito interno de Interpretação/Sugestão */
.card strong{
    font-weight:500 !important;
    color:#dce7fb !important;
}

/* ===== SINAIS EMOCIONAIS ===== */
.engagement-insight{
    font-size:.82rem !important;
    line-height:1.5 !important;
    color:var(--ui-text) !important;
    background:rgba(255,255,255,.035) !important;
}

.engagement-insight strong{
    font-weight:500 !important;
}

/* ===== RESPONSIVO ===== */
@media (max-width:1200px){
    .executive-summary-grid{
        grid-template-columns:1fr !important;
    }
}

/* === FIM_PADRAO_VISUAL_GERAL_V3 === */


/* === FONT_SIZE_GERAL_14 === */

/* Fonte base geral */
html, body, [data-testid="stAppViewContainer"]{
    font-size:14px !important;
}

/* Textos comuns */
.card,
.big-card,
.panel-card,
.score-card,
.strategy-box,
.hero-score-card,
.executive-summary,
.executive-kpi,
.check-item,
.metric-sub,
.diag-desc,
.diag-item-value,
.executive-summary-text,
.executive-kpi-value,
.executive-kpi-sub,
.strategy-box li{
    font-size:14px !important;
}

/* Labels e pequenos títulos internos */
.diag-item-label,
.list-card-title,
.side-score-title,
.small-label,
.executive-kpi-label{
    font-size:14px !important;
}

/* Títulos principais continuam maiores */
.section-title{
    font-size:20px !important;
}

.diag-title,
.executive-summary-title{
    font-size:18px !important;
}

.main-title{
    font-size:32px !important;
}

.sub-title{
    font-size:14px !important;
}

/* Números principais */
.hero-score-value{
    font-size:48px !important;
}

.side-score-value,
.metric-value{
    font-size:24px !important;
}

/* Prioridades */
.strategy-box [style*="Prioridade"]{
    font-size:13px !important;
}

/* Evidências */
.card div[style*="text-transform:uppercase"]{
    font-size:13px !important;
}

.card div{
    font-size:14px !important;
}

/* === FIM_FONT_SIZE_GERAL_14 === */


/* === LEITURA_EMOCIONAL_CLIENTE_SEGURA === */

.emotion-clean-grid{
    display:grid;
    grid-template-columns:2fr 1fr;
    gap:18px;
    align-items:stretch;
}

.emotion-clean-card{
    background:linear-gradient(180deg, rgba(28,42,72,.96) 0%, rgba(20,33,57,.98) 100%);
    border:1px solid rgba(144,166,203,.14);
    border-radius:20px;
    padding:20px;
    box-shadow:0 12px 28px rgba(0,0,0,.22);
}

.emotion-kpis{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:12px;
    margin-bottom:18px;
}

.emotion-mini{
    background:rgba(255,255,255,.035);
    border:1px solid rgba(255,255,255,.08);
    border-radius:16px;
    padding:14px;
    min-height:96px;
}

.emotion-mini-label,
.voice-mini-label{
    color:#9fb6ff;
    font-size:13px;
    text-transform:uppercase;
    letter-spacing:.08em;
    font-weight:800;
    margin-bottom:8px;
}

.emotion-mini-value,
.voice-mini-value{
    color:#f3f7ff;
    font-size:18px;
    font-weight:700;
    line-height:1.25;
}

.emotion-mini-sub,
.voice-mini-sub{
    color:#a9b9d6;
    font-size:14px;
    line-height:1.45;
    margin-top:6px;
}

.emotion-dist-title{
    color:#f3f7ff;
    font-size:15px;
    font-weight:800;
    margin-bottom:12px;
}

.emotion-dist{
    display:flex;
    flex-direction:column;
    gap:10px;
}

.emotion-row{
    display:grid;
    grid-template-columns:150px 1fr 56px;
    gap:10px;
    align-items:center;
}

.emotion-name{
    color:#dbe6f8;
    font-size:14px;
}

.emotion-track{
    height:9px;
    background:rgba(255,255,255,.08);
    border-radius:999px;
    overflow:hidden;
}

.emotion-fill{
    height:100%;
    background:linear-gradient(90deg,#d9908b 0%, #d8b371 55%, #a3c7ad 100%);
    border-radius:999px;
}

.emotion-percent{
    color:#a9b9d6;
    font-size:14px;
    text-align:right;
}

.emotion-reading{
    margin-top:18px;
    background:rgba(255,255,255,.03);
    border:1px solid rgba(255,255,255,.08);
    border-radius:16px;
    padding:16px;
}

.emotion-reading-title{
    color:#f3f7ff;
    font-size:15px;
    font-weight:800;
    margin-bottom:10px;
}

.emotion-reading-line{
    color:#dbe6f8;
    font-size:14px;
    line-height:1.55;
    margin-bottom:8px;
}

.voice-mini{
    background:rgba(255,255,255,.035);
    border:1px solid rgba(255,255,255,.08);
    border-radius:16px;
    padding:14px;
    margin-bottom:12px;
}

@media (max-width:1200px){
    .emotion-clean-grid{
        grid-template-columns:1fr;
    }
    .emotion-kpis{
        grid-template-columns:1fr 1fr;
    }
    .emotion-row{
        grid-template-columns:120px 1fr 48px;
    }
}

/* === FIM_LEITURA_EMOCIONAL_CLIENTE_SEGURA === */

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Inteligência Emocional Insight</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Plataforma de inteligência emocional e comercial para vídeos de vendas e pitch</div>', unsafe_allow_html=True)

if "analysis_id" not in st.session_state:
    st.session_state["analysis_id"] = None

uploaded_file = st.file_uploader("Faça upload do vídeo da campanha", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file:
    os.makedirs("data/uploads", exist_ok=True)
    saved_video = os.path.join("data", "uploads", uploaded_file.name)
    with open(saved_video, "wb") as f:
        f.write(uploaded_file.read())
    st.success("Vídeo carregado com sucesso.")

    if st.button("Analisar Campanha"):
        with st.spinner("Processando vídeo..."):
            analysis_id = processar_video(saved_video)
            st.session_state["analysis_id"] = analysis_id

analysis_id = st.session_state.get("analysis_id")

if analysis_id:
    base = os.path.join("data", "processed", analysis_id)

    metrics_path = os.path.join(base, "metricas.json")
    insights_path = os.path.join(base, "insights.json")
    emotions_csv = os.path.join(base, "emocoes_detalhadas.csv")
    transcription_path = os.path.join(base, "transcricao.txt")
    vocal_json = os.path.join(base, "analise_vocal.json")
    discurso_json = os.path.join(base, "analise_discurso.json")
    multimodal_json = os.path.join(base, "analise_multimodal.json")
    momentos_path = os.path.join(base, "momentos_venda.json")

    if not (os.path.exists(metrics_path) and os.path.exists(insights_path) and os.path.exists(emotions_csv)):
        st.error("Arquivos da análise não encontrados.")
        st.stop()

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    with open(insights_path, "r", encoding="utf-8") as f:
        insights = json.load(f)

    vocal, discurso, multimodal, momentos = {}, {}, {}, {}
    if os.path.exists(vocal_json):
        with open(vocal_json, "r", encoding="utf-8") as f:
            vocal = json.load(f)
    if os.path.exists(discurso_json):
        with open(discurso_json, "r", encoding="utf-8") as f:
            discurso = json.load(f)
    if os.path.exists(multimodal_json):
        with open(multimodal_json, "r", encoding="utf-8") as f:
            multimodal = json.load(f)
    if os.path.exists(momentos_path):
        with open(momentos_path, "r", encoding="utf-8") as f:
            momentos = json.load(f)

    df = pd.read_csv(emotions_csv)

    if "emocao_negocio" not in df.columns:
        mapa = {
            "Felicidade": "Interesse",
            "Surpresa": "Curiosidade",
            "Atenção moderada": "Atenção moderada",
            "Tristeza": "Perda de interesse",
            "Raiva": "Resistencia",
            "Medo": "Apreensao",
            "Repulsa": "Rejeicao",
            "Indefinido": "Indefinido",
            "happy": "Interesse",
            "surprise": "Curiosidade",
            "neutral": "Atenção moderada",
            "sad": "Perda de interesse",
            "angry": "Resistencia",
            "fear": "Apreensao",
            "disgust": "Rejeicao",
            "unknown": "Indefinido"
        }
        df["emocao_negocio"] = df["emocao"].map(mapa).fillna("Indefinido")

    diagnostico = gerar_diagnostico_comercial(metrics, vocal, discurso, multimodal, momentos)
    diagnostico = enriquecer_diagnostico_contextual(
        diagnostico,
        transcription_path,
        metrics,
        vocal,
        discurso,
        multimodal,
        momentos,
    )

    score_integrado = multimodal.get("score_integrado", 0)
    label = diagnostico.get("pontuacao_integrada_label", "Fraco")
    cor = classe_cor(label)
    pct = score_to_percent(score_integrado)

    st.markdown(f"""
    <div class="hero-score-card">
        <div class="hero-score-title">ÍNDICE COMERCIAL DA VENDA</div>
        <div class="hero-score-value">{str(score_integrado).replace(".", ",")}</div>
        <div class="hero-score-label {cor}">{label}</div>
        <div class="hero-score-bar"><div class="hero-score-fill" style="width:{pct}%"></div></div>
    </div>
    """, unsafe_allow_html=True)


    resultado_venda = diagnostico.get("resultado_venda", "Não identificado")
    fechamento_real = diagnostico.get("fechamento_real", diagnostico.get("fechamento", "Não identificado"))
    leitura_consultiva = diagnostico.get("leitura_consultiva", "")

    if not leitura_consultiva:
        leitura_consultiva = (
            "A análise cruza sinais de fala, emoção facial, voz e transcrição para identificar "
            "pontos fortes, riscos comerciais e oportunidades de melhoria na abordagem de venda."
        )

    preco_info = diagnostico.get("analise_comercial_real", {}).get("preco", {})
    tipo_preco = diagnostico.get("preco_negociacao_ia") or preco_info.get("tipo", diagnostico.get("reacao_preco", "Não identificado"))
    impacto_preco = preco_info.get("impacto", "Preço analisado conforme os sinais da conversa.")

    leitura_consultiva_ui = compactar_texto_card(leitura_consultiva, 430)
    tipo_preco_ui = compactar_texto_card(tipo_preco, 150)
    impacto_preco_ui = compactar_texto_card(impacto_preco, 190)

    st.markdown(f"""
    <div class="section-title">Resumo Executivo da Venda</div>
    <div class="executive-summary">
        <div class="executive-summary-grid">
            <div>
                <div class="executive-summary-title">{diagnostico.get("pitch_label", "Análise comercial")}</div>
                <div class="executive-summary-text">{str(leitura_consultiva_ui).replace('**','')}</div>
            </div>
            <div class="executive-kpi">
                <div class="executive-kpi-label">Resultado detectado</div>
                <div class="executive-kpi-value">{str(resultado_venda).replace('**','')}</div>
                <div class="executive-kpi-sub">Fechamento real: {str(fechamento_real).replace('**','')}</div>
            </div>
            <div class="executive-kpi">
                <div class="executive-kpi-label">Preço e negociação</div>
                <div class="executive-kpi-value">{str(tipo_preco_ui).replace('**','')}</div>
                <div class="executive-kpi-sub">{str(impacto_preco_ui).replace('**','')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    st.markdown('<div class="section-title">Diagnóstico Comercial</div>', unsafe_allow_html=True)

    top_left, top_right = st.columns([3.2, 1.8])

    with top_left:
        st.markdown(f"""
        <div class="big-card">
            <div class="diag-title">{diagnostico["pitch_label"]}</div>
            <div class="diag-grid">
                <div class="diag-item">
                    <div class="diag-item-label">Abertura da conversa</div>
                    <div class="diag-item-value">{render_diag_value(diagnostico.get("conexao_inicial", "Não identificado"))}</div>
                </div>
                <div class="diag-item">
                    <div class="diag-item-label">Clareza da oferta</div>
                    <div class="diag-item-value">{render_diag_value(diagnostico.get("apresentacao_valor", "Não identificado"))}</div>
                </div>
                <div class="diag-item">
                    <div class="diag-item-label">Reação ao preço</div>
                    <div class="diag-item-value">{render_diag_value(diagnostico.get("reacao_preco", "Não identificado"))}</div>
                </div>
                <div class="diag-item">
                    <div class="diag-item-label">Fechamento da venda</div>
                    <div class="diag-item-value">{render_diag_value(diagnostico.get("fechamento", "Não identificado"))}</div>
                </div>
            </div>
            <div class="diag-bottom">
                <span class="pill-score">Potencial de conversão</span>
                <span style="font-size:1.15rem;font-weight:900;">{render_diag_value(diagnostico.get("potencial_comercial", "Não identificado"))}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2, gap="large")

        with c1:
            st.markdown(
                '<div class="panel-card success-card"><div class="list-card-title">Pontos fortes</div><div class="check-list">' +
                ''.join([f'<div class="check-item"><span class="check-icon">✓</span><span>{compactar_texto_card(x, 260)}</span></div>' for x in diagnostico["o_que_funcionou"]]) +
                '</div></div>',
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                '<div class="panel-card danger-card"><div class="list-card-title">Riscos comerciais</div><div class="check-list">' +
                ''.join([f'<div class="check-item"><span class="warn-icon">⚠️</span><span>{compactar_texto_card(x, 260)}</span></div>' for x in diagnostico["o_que_prejudicou"]]) +
                '</div></div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div class="panel-card advice-card" style="margin-top:20px;"><div class="list-card-title">Ações recomendadas</div><div class="check-list">' +
            ''.join([f'<div class="check-item"><span class="action-icon">⚡</span><span>{compactar_texto_card(x, 260)}</span></div>' for x in diagnostico["o_que_melhorar"]]) +
            '</div></div>',
            unsafe_allow_html=True
        )

    with top_right:
        score_cards = [
            ("Energia da fala", vocal.get("energia_vocal", 0), diagnostico["energia_vocal_label"]),
            ("Ritmo da conversa", vocal.get("fluidez", 0), diagnostico["fluidez_label"]),
            ("Clareza da Oferta", discurso.get("clareza", 0), diagnostico["clareza_label"]),
            ("Condução do fechamento", discurso.get("forca_fechamento", 0), diagnostico["fechamento_label"]),
        ]

        for titulo, valor, item_label in score_cards:
            item_cor = classe_cor(item_label)
            score_insight = interpretar_score_lateral(titulo, valor, item_label, diagnostico)
            html_score = f"""
            <div class="score-card compact-insight">
                <div class="side-score-title">{titulo}</div>
                <div class="side-score-value {item_cor}">{str(valor).replace(".", ",")}</div>
                <div class="side-score-row">
                    {pill_html(item_label)}
                    <span class="{item_cor}" style="font-weight:800;">{item_label}</span>
                </div>
                {score_bar(valor)}
                <div class="metric-sub">{score_insight}</div>
            </div>
            """
            st.markdown(html_score, unsafe_allow_html=True)




    st.markdown('<div class="section-title">Leitura Emocional do Cliente</div>', unsafe_allow_html=True)

    def _etapa_video(seg, total):
        try:
            seg = float(seg or 0)
            total = float(total or 0)
        except Exception:
            return "Não identificado"

        if total <= 0:
            return "Não identificado"

        pct_video = seg / total

        if pct_video <= 0.25:
            return "Início"
        if pct_video <= 0.70:
            return "Desenvolvimento"
        return "Final"

    def _label_vocal_simples(valor):
        try:
            v = float(valor or 0)
        except Exception:
            v = 0

        if v >= 70:
            return "Alta", "Boa sustentação para a abordagem comercial."
        if v >= 45:
            return "Média", "Suficiente, mas pode ganhar mais consistência."
        return "Baixa", "Pode reduzir segurança percebida e força comercial."

    df_emocional = df.copy()

    if "emocao_negocio" in df_emocional.columns and not df_emocional.empty:
        serie_emocional = df_emocional["emocao_negocio"].fillna("Indefinido").astype(str)
    elif "emocao" in df_emocional.columns and not df_emocional.empty:
        serie_emocional = df_emocional["emocao"].fillna("Indefinido").astype(str)
    else:
        serie_emocional = pd.Series(["Indefinido"])

    dist = serie_emocional.value_counts(normalize=True).mul(100).round(1).to_dict()

    ordem_emocional = [
        "Interesse",
        "Curiosidade",
        "Atenção moderada",
        "Perda de interesse",
        "Resistencia",
        "Apreensao",
        "Rejeicao",
        "Indefinido",
    ]

    dist_final = []
    usados = set()

    for ref in ordem_emocional:
        for nome, valor in dist.items():
            if str(nome).strip().lower() == ref.strip().lower():
                dist_final.append((ref, valor))
                usados.add(nome)

    for nome, valor in dist.items():
        if nome not in usados:
            dist_final.append((nome, valor))

    dist_final = dist_final[:6]

    if dist_final:
        emocao_top = dist_final[0][0]
        emocao_top_pct = dist_final[0][1]
    else:
        emocao_top = "Indefinido"
        emocao_top_pct = 0

    receptividade = 0
    sensibilidade = 0

    for nome, valor in dist_final:
        n = str(nome).lower()

        if n in ["interesse", "curiosidade", "atenção moderada", "atencao moderada"]:
            receptividade += float(valor or 0)

        if n in ["perda de interesse", "resistencia", "resistência", "apreensao", "apreensão", "rejeicao", "rejeição"]:
            sensibilidade += float(valor or 0)

    try:
        total_seg = float(df_emocional["tempo_segundos"].max()) if "tempo_segundos" in df_emocional.columns and not df_emocional.empty else 0
    except Exception:
        total_seg = 0

    etapa_pico = _etapa_video(metrics.get("pico_emocional_segundos"), total_seg)
    etapa_queda = _etapa_video(metrics.get("queda_interesse_segundos"), total_seg)

    if receptividade >= 60:
        leitura_geral = "A leitura facial indica boa abertura emocional durante a conversa."
    elif sensibilidade >= 35:
        leitura_geral = "A leitura facial mostra oscilação relevante, possivelmente ligada a dúvida, preço ou comparação de valor."
    else:
        leitura_geral = "A leitura facial sugere comportamento mais racional e moderado, comum em vendas rápidas."

    if sensibilidade >= 25:
        leitura_sensibilidade = "Atenção especial aos momentos de preço, dúvida ou sustentação de valor."
    else:
        leitura_sensibilidade = "Não houve predominância forte de resistência emocional."

    energia_label, energia_txt = _label_vocal_simples(vocal.get("energia_vocal", 0))
    ritmo_label, ritmo_txt = _label_vocal_simples(vocal.get("fluidez", 0))
    clareza_label = diagnostico.get("clareza_label", "Não identificado")
    fechamento_label = diagnostico.get("fechamento_label", "Não identificado")

    emo_left, emo_right = st.columns([2, 1], gap="large")

    with emo_left:
        e1, e2, e3, e4 = st.columns(4, gap="small")

        with e1:
            st.markdown(f"""
            <div class="card" style="min-height:120px;">
                <div class="small-label">Emoção predominante</div>
                <div class="metric-value">{emocao_top}</div>
                <div class="metric-sub">{str(emocao_top_pct).replace(".", ",")}% dos sinais detectados</div>
            </div>
            """, unsafe_allow_html=True)

        with e2:
            st.markdown(f"""
            <div class="card" style="min-height:120px;">
                <div class="small-label">Receptividade</div>
                <div class="metric-value">{str(round(receptividade, 1)).replace(".", ",")}%</div>
                <div class="metric-sub">Interesse, curiosidade ou atenção moderada</div>
            </div>
            """, unsafe_allow_html=True)

        with e3:
            st.markdown(f"""
            <div class="card" style="min-height:120px;">
                <div class="small-label">Sensibilidade</div>
                <div class="metric-value">{str(round(sensibilidade, 1)).replace(".", ",")}%</div>
                <div class="metric-sub">Dúvida, queda ou resistência emocional</div>
            </div>
            """, unsafe_allow_html=True)

        with e4:
            st.markdown(f"""
            <div class="card" style="min-height:120px;">
                <div class="small-label">Momento crítico</div>
                <div class="metric-value">{etapa_queda}</div>
                <div class="metric-sub">Etapa com menor ativação emocional</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card">
            <div class="list-card-title">Distribuição emocional detectada</div>
        """, unsafe_allow_html=True)

        for nome, valor in dist_final:
            try:
                pct = max(0, min(100, float(valor or 0)))
            except Exception:
                pct = 0

            label_pct = str(round(pct, 1)).replace(".", ",")

            col_nome, col_barra, col_valor = st.columns([1.4, 3, .7], gap="small")

            with col_nome:
                st.markdown(f"<div style='font-size:14px;color:#dbe6f8;'>{nome}</div>", unsafe_allow_html=True)

            with col_barra:
                st.progress(pct / 100)

            with col_valor:
                st.markdown(f"<div style='font-size:14px;color:#a9b9d6;text-align:right;'>{label_pct}%</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card">
            <div class="list-card-title">Interpretação da IA</div>
            <div style="font-size:14px;line-height:1.6;color:#dbe6f8;margin-bottom:8px;">{leitura_geral}</div>
            <div style="font-size:14px;line-height:1.6;color:#dbe6f8;margin-bottom:8px;">O maior ponto de conexão apareceu na etapa: {etapa_pico}.</div>
            <div style="font-size:14px;line-height:1.6;color:#dbe6f8;">{leitura_sensibilidade}</div>
        </div>
        """, unsafe_allow_html=True)

    with emo_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="list-card-title">Resumo vocal do vendedor</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="score-card" style="min-height:auto;margin-bottom:12px;">
            <div class="small-label">Energia da fala</div>
            <div class="metric-value">{energia_label}</div>
            <div class="metric-sub">{energia_txt}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="score-card" style="min-height:auto;margin-bottom:12px;">
            <div class="small-label">Ritmo da conversa</div>
            <div class="metric-value">{ritmo_label}</div>
            <div class="metric-sub">{ritmo_txt}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="score-card" style="min-height:auto;margin-bottom:12px;">
            <div class="small-label">Clareza da oferta</div>
            <div class="metric-value">{clareza_label}</div>
            <div class="metric-sub">Mostra se a proposta ficou compreensível para o cliente.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="score-card" style="min-height:auto;">
            <div class="small-label">Fechamento</div>
            <div class="metric-value">{fechamento_label}</div>
            <div class="metric-sub">Indica se o vendedor conduziu o cliente para o próximo passo.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


    estrategia = []

    # 1) abertura
    conexao_inicial = str(diagnostico.get("conexao_inicial", "")).strip().lower()
    if conexao_inicial in ["fraco", "baixo", "negativo"]:
        estrategia.append("A abertura do pitch precisa ser mais forte. Tente começar com uma dor clara do cliente, uma promessa objetiva de resultado ou uma pergunta que gere curiosidade imediata.")
    elif conexao_inicial in ["medio", "médio"]:
        estrategia.append("A abertura teve conexão parcial. Vale testar uma introdução mais direta, com mais impacto nos primeiros segundos para aumentar retenção logo no início.")
    else:
        estrategia.append("A abertura gerou conexão razoável. Preserve a estrutura inicial e use esse trecho como base para padronizar futuras abordagens.")

    # 2) valor / clareza
    apresentacao_valor = str(diagnostico.get("apresentacao_valor", "")).strip().lower()
    clareza = float(discurso.get("clareza", 0) or 0)
    if apresentacao_valor in ["fraco", "baixo", "negativo"] or clareza < 50:
        estrategia.append("A proposta de valor ainda não está clara o suficiente. Antes de falar de preço, reforce benefício, transformação e motivo pelo qual a solução vale a atenção do cliente.")
    elif clareza < 70:
        estrategia.append("A clareza da oferta pode melhorar. Simplifique a explicação e destaque com mais objetividade o principal benefício percebido pelo cliente.")
    else:
        estrategia.append("A proposta de valor está relativamente compreensível. O próximo passo é torná-la mais memorável, usando linguagem simples e foco no resultado final.")

    # 3) preço
    reacao_preco = str(diagnostico.get("reacao_preco", "")).strip().lower()
    if reacao_preco in ["fraco", "negativo", "resistencia", "resistência"]:
        estrategia.append("O momento do preço exige mais preparação. Reforce valor, prova, benefício e redução de risco antes de mencionar investimento, para diminuir resistência nessa etapa.")
    else:
        estrategia.append("A reação ao preço não foi o maior problema, mas ainda vale preparar melhor a transição para esse momento, conectando preço a valor percebido.")

    # 4) fechamento
    fechamento = str(diagnostico.get("fechamento", "")).strip().lower()
    forca_fechamento = float(discurso.get("forca_fechamento", 0) or 0)
    if fechamento in ["fraco", "baixo", "negativo"] or forca_fechamento < 50:
        estrategia.append("O fechamento precisa ser mais direto. Termine a conversa com chamada clara para ação, próximo passo objetivo e menos espaço para dispersão do cliente.")
    elif forca_fechamento < 70:
        estrategia.append("Há espaço para fortalecer o fechamento. Vale testar perguntas de avanço, convite para decisão e fechamento com mais segurança verbal.")
    else:
        estrategia.append("O fechamento está relativamente funcional. A melhoria agora está em reduzir fricção e conduzir o cliente com mais naturalidade até a decisão.")

    # 5) voz / ritmo
    energia_vocal = float(vocal.get("energia_vocal", 0) or 0)
    fluidez = float(vocal.get("fluidez", 0) or 0)
    pausas = float(vocal.get("quantidade_pausas", 0) or 0)
    if energia_vocal < 40:
        estrategia.append("A energia vocal está baixa para um pitch comercial. Trabalhe mais variação de tom, presença e intenção, especialmente nos momentos de proposta de valor e fechamento.")
    if fluidez < 50:
        estrategia.append("A fluidez da fala pode estar prejudicando a percepção de confiança. Treinar ritmo, continuidade e transições mais limpas tende a melhorar a autoridade do pitch.")
    if pausas >= 4:
        estrategia.append("Foram detectadas pausas longas ou frequentes. Isso pode reduzir impacto e segurança. Vale ensaiar trechos críticos para tornar a fala mais contínua.")

    # 6) momentos emocionais
    pico_seg = metrics.get("pico_emocional_segundos")
    queda_seg = metrics.get("queda_interesse_segundos")
    if pico_seg is not None:
        estrategia.append(f"O trecho em {formatar_tempo(pico_seg)} merece atenção: ali houve maior conexão emocional. Use esse ponto como referência para entender o que mais engaja no seu discurso.")
    if queda_seg is not None:
        estrategia.append(f"A atenção começa a cair em {formatar_tempo(queda_seg)}. Reveja o que está sendo dito nesse momento e considere encurtar, simplificar ou mudar a abordagem.")

    # 7) recomendações do diagnóstico, sem repetir demais
    for item in diagnostico.get("o_que_melhorar", []):
        if item not in estrategia and len(estrategia) < 8:
            estrategia.append(item)

    # Plano estratégico: prioridade máxima para textos gerados pela IA.
    plano_ia = diagnostico.get("plano_estrategico_ia", {})

    prioridades = []
    complementares = []

    if isinstance(plano_ia, dict):
        prioridades = list(plano_ia.get("prioridades", []) or [])
        complementares = list(plano_ia.get("complementares", []) or [])

    # Completa prioridades usando insights da IA, sem voltar para textos antigos fixos.
    fontes_para_completar = []
    fontes_para_completar += list(diagnostico.get("o_que_melhorar", []) or [])
    fontes_para_completar += list(diagnostico.get("o_que_prejudicou", []) or [])
    fontes_para_completar += list(diagnostico.get("o_que_funcionou", []) or [])

    for item in fontes_para_completar:
        item = str(item).strip()
        if item and item not in prioridades and len(prioridades) < 3:
            prioridades.append(item)

    if not prioridades:
        prioridades = [
            "A análise não encontrou evidência suficiente para montar prioridades específicas. Revise os principais trechos da venda antes de tomar decisão."
        ]

    prioridades = prioridades[:3]

    # Se a IA não trouxe complementares, usa os demais insights gerados por ela.
    if not complementares:
        for item in fontes_para_completar:
            item = str(item).strip()
            if item and item not in prioridades and item not in complementares:
                complementares.append(item)

    complementares = complementares[:4]

    cards_html = ''.join([
        f'<div style="background:linear-gradient(180deg, rgba(255,255,255,.045) 0%, rgba(255,255,255,.02) 100%);'
        f'border:1px solid rgba(151,172,214,.12);border-radius:18px;padding:16px;box-shadow:0 10px 26px rgba(0,0,0,.18);">'
        f'<div style="color:#b9c8e8;font-size:.78rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin-bottom:10px;">'
        f'Prioridade {i+1}</div>'
        f'<div style="color:#eef4ff;font-size:.98rem;line-height:1.68;font-weight:500;">{texto}</div>'
        f'</div>'
        for i, texto in enumerate(prioridades)
    ])

    complementares_html = ''
    if complementares:
        complementares_html = (
            '<div style="color:#dbe6ff;font-size:.96rem;font-weight:800;margin-top:6px;margin-bottom:12px;">Ajustes complementares</div>'
            '<ul>'
            + ''.join([f'<li>{x}</li>' for x in complementares]) +
            '</ul>'
        )

    html_strategy = (
        '<div class="strategy-box">'
        ''
        '<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:14px;margin-bottom:18px;">'
        + cards_html +
        '</div>'
        + complementares_html +
        '</div>'
    )

    st.markdown('<div class="section-title">Plano Estratégico de Melhoria</div>', unsafe_allow_html=True)

    plano_col = st.container()

    with plano_col:
        st.markdown(html_strategy, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Evidências da Conversa</div>', unsafe_allow_html=True)

    evidencias_ia = diagnostico.get("evidencias_conversa_ia", [])

    if isinstance(evidencias_ia, list) and evidencias_ia:
        st.markdown('<div class="section-title">Evidências analisadas pela IA</div>', unsafe_allow_html=True)

        for ev in evidencias_ia[:4]:
            if not isinstance(ev, dict):
                continue

            titulo_ev = compactar_texto_card(ev.get("titulo", "Evidência da conversa"), 90)
            trecho_ev = ev.get("trecho", "")
            interpretacao_ev = ev.get("interpretacao", "")
            sugestao_ev = ev.get("sugestao", "")

            if trecho_parece_confuso(trecho_ev):
                trecho_ev = compactar_texto_card(trecho_ev, 210)
                interpretacao_ev = "Trecho com baixa clareza na transcrição. A análise considera apenas os sinais comerciais identificáveis nesse ponto."
                sugestao_ev = "Use esse trecho com cautela e valide manualmente caso ele seja decisivo para a apresentação."
            else:
                trecho_ev = compactar_texto_card(trecho_ev, 260)
                interpretacao_ev = compactar_texto_card(interpretacao_ev, 330)
                sugestao_ev = compactar_texto_card(sugestao_ev, 300)

            st.markdown(f"""
            <div class="card" style="margin-bottom:12px;position:relative;">
                <div style="font-size:0.78rem;color:#dbe6ff;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;font-weight:800;">
                    {titulo_ev}
                </div>
                <div style="color:#eef4ff;line-height:1.55;">"{trecho_ev}"</div>
                <div style="margin-top:10px;color:#b9c8e8;font-size:.9rem;line-height:1.55;">
                    <strong>Interpretação:</strong> {interpretacao_ev}
                </div>
                <div style="margin-top:8px;color:#6ee7b7;font-size:.88rem;line-height:1.55;">
                    <strong>Sugestão:</strong> {sugestao_ev}
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown(
            '<div class="card">A IA não encontrou evidências textuais suficientes para exibir com segurança.</div>',
            unsafe_allow_html=True
        )

