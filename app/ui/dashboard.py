import streamlit as st
import json
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px

from app.analysis.pipeline import processar_video
from app.analysis.diagnostico_comercial import gerar_diagnostico_comercial


st.set_page_config(
    page_title="Insight Emotion AI",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
:root{
    --bg:#071226;
    --bg2:#0b1730;
    --card:#18263f;
    --card2:#1c2b46;
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
[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#08111f 0%, #050b16 100%);
    border-right:1px solid rgba(255,255,255,.06);
}
[data-testid="stSidebar"] *{
    color:#d9e5ff !important;
}
.main-title{
    font-size:2.45rem;
    font-weight:900;
    color:var(--text);
    letter-spacing:-0.02em;
    margin-bottom:.25rem;
}
.sub-title{
    color:var(--muted);
    font-size:1rem;
    margin-bottom:1.35rem;
}
.section-title{
    color:var(--text);
    font-size:1.45rem;
    font-weight:800;
    margin-top:1.1rem;
    margin-bottom:.9rem;
}
.card, .kpi-card, .big-card, .panel-card, .bench-card, .score-card, .frases-box, .strategy-box {
    background: linear-gradient(180deg, rgba(29,43,70,.96) 0%, rgba(24,38,63,.96) 100%);
    border:1px solid rgba(144,166,203,.16);
    border-radius:22px;
    box-shadow: 0 18px 45px rgba(0,0,0,.35);
    color:var(--text);
}
.big-card{ padding:22px; }
.card{ padding:18px; }
.kpi-card{ padding:18px; min-height:118px; }
.panel-card{ padding:20px; min-height:230px; }
.bench-card{ padding:18px; min-height:300px; }
.score-card{ padding:18px; min-height:180px; margin-bottom:18px; overflow:hidden; }
.frases-box, .strategy-box{ padding:18px; }
.kpi-title, .small-label, .metric-title{
    color:var(--muted);
    font-size:.95rem;
    font-weight:600;
    margin-bottom:8px;
}
.kpi-value, .metric-value{
    color:var(--text);
    font-size:2rem;
    font-weight:900;
    line-height:1.05;
}
.kpi-sub, .metric-sub{
    color:var(--muted);
    font-size:.92rem;
    margin-top:10px;
}
.diag-title{
    font-size:2.1rem;
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
    color:var(--muted);
    font-size:.9rem;
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
.pill-blue{ background:rgba(100,168,255,.16); color:#9ec8ff; }
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
.blue{ color:var(--blue) !important; }
.purple{ color:var(--purple) !important; }

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
    height:10px;
    background:rgba(255,255,255,.10);
    border-radius:999px;
    overflow:hidden;
    margin-top:12px;
}
.progress-fill{
    height:100%;
    border-radius:999px;
    background: linear-gradient(90deg,#ff5f62 0%, #ff9f43 35%, #ffd166 65%, #39d98a 100%);
}
.list-card-title{
    color:var(--text);
    font-size:1rem;
    font-weight:800;
    margin-bottom:12px;
}
.list-card ul{
    padding-left:1.1rem;
    margin:0;
}
.list-card li{
    color:#e8f0ff;
    margin-bottom:11px;
    line-height:1.6;
}
.bench-table{
    width:100%;
    border-collapse:collapse;
    margin-top:6px;
}
.bench-table th{
    text-align:left;
    color:#d9e5ff;
    font-size:.95rem;
    padding:10px 8px;
    border-bottom:1px solid rgba(255,255,255,.08);
}
.bench-table td{
    padding:10px 8px;
    color:#d3def3;
    border-bottom:1px solid rgba(255,255,255,.06);
}
.bench-legend{
    margin-top:12px;
    color:var(--muted);
    font-size:.9rem;
}
.score-main{
    color:#ff8b8f;
    font-size:3rem;
    font-weight:900;
    line-height:1;
}
.score-ideal{
    color:#ffd78a;
    font-size:2rem;
    font-weight:900;
}
.scale-row{
    display:flex;
    justify-content:space-between;
    gap:10px;
    margin-top:12px;
    color:#d3def3;
    font-size:.9rem;
    font-weight:700;
}
.frases-box ul, .strategy-box ul{
    margin:.25rem 0 0 1.2rem;
    padding:0;
}
.frases-box li, .strategy-box li{
    color:#e7efff;
    margin-bottom:9px;
    line-height:1.6;
}
.group-title{
    color:#b8c7e3;
    font-size:.92rem;
    font-weight:800;
    text-transform:uppercase;
    margin-top:12px;
    margin-bottom:8px;
}
.stButton button{
    background:linear-gradient(90deg,#6674ff 0%, #7b61ff 100%);
    color:white;
    border:none;
    border-radius:14px;
    font-weight:800;
    padding:.72rem 1.25rem;
}
.stButton button:hover{
    color:white;
    border:none;
}
.small-muted{
    color:var(--muted);
    font-size:.92rem;
}
</style>
""", unsafe_allow_html=True)

MAPA_Y = {
    "Interesse": 6,
    "Curiosidade": 5,
    "Neutro": 4,
    "Desconexao": 3,
    "Resistencia": 2,
    "Apreensao": 1,
    "Rejeicao": 0,
    "Indefinido": 0,
    "Tristeza": 3,
    "Raiva": 2,
    "Medo": 1,
    "Repulsa": 0
}

def formatar_tempo(seg):
    if seg is None:
        return "—"
    try:
        return f"{float(seg):.1f}".replace(".", ",") + "s"
    except:
        return "—"

def pill_html(texto):
    chave = str(texto).strip().lower()
    mapa = {
        "fraco": "pill-red",
        "medio": "pill-orange",
        "médio": "pill-orange",
        "bom": "pill-yellow",
        "forte": "pill-green",
        "negativa": "pill-red",
        "positiva": "pill-green",
        "nao identificado": "pill-gray",
        "não identificado": "pill-gray",
    }
    cls = mapa.get(chave, "pill-gray")
    return f'<span class="pill {cls}">{texto}</span>'

def score_to_percent(v):
    try:
        v = float(v)
    except:
        return 0
    if v < 0:
        return 0
    if v > 100:
        return 100
    return int(v)

def score_bar(value):
    pct = score_to_percent(value)
    return f'<div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>'

def score_scale():
    return '<div class="scale-row"><span>Fraco</span><span>Médio</span><span>Bom</span><span>Excelente</span></div>'

st.sidebar.markdown("## Insight Emotion AI")
st.sidebar.markdown("### Inteligência de reação do consumidor")
st.sidebar.markdown("---")
st.sidebar.write("**Pipeline**")
st.sidebar.write("✔ Vídeo")
st.sidebar.write("✔ Transcrição")
st.sidebar.write("✔ Análise facial")
st.sidebar.write("✔ Análise vocal")
st.sidebar.write("✔ Discurso")
st.sidebar.write("✔ Negociação")

st.markdown('<div class="main-title">Inteligência Emocional Insight</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Plataforma de inteligência emocional e comercial para vídeos de vendas e pitch</div>', unsafe_allow_html=True)

if "analysis_id" not in st.session_state:
    st.session_state["analysis_id"] = None

uploaded_file = st.file_uploader(
    "Faça upload do vídeo da campanha",
    type=["mp4", "mov", "avi", "mkv"]
)

if uploaded_file:
    os.makedirs("data/uploads", exist_ok=True)
    saved_video = os.path.join("data", "uploads", uploaded_file.name)

    with open(saved_video, "wb") as f:
        f.write(uploaded_file.read())

    st.success("Vídeo carregado com sucesso.")

    if st.button("Analisar Campanha"):
        with st.spinner("Processando vídeo e gerando dashboard..."):
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
        st.error("Arquivos da análise não encontrados. Gere uma nova análise.")
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
            "Neutro": "Neutro",
            "Tristeza": "Desconexao",
            "Raiva": "Resistencia",
            "Medo": "Apreensao",
            "Repulsa": "Rejeicao",
            "Indefinido": "Indefinido",
            "happy": "Interesse",
            "surprise": "Curiosidade",
            "neutral": "Neutro",
            "sad": "Desconexao",
            "angry": "Resistencia",
            "fear": "Apreensao",
            "disgust": "Rejeicao",
            "unknown": "Indefinido"
        }
        df["emocao_negocio"] = df["emocao"].map(mapa).fillna("Indefinido")

    diagnostico = gerar_diagnostico_comercial(metrics, vocal, discurso, multimodal, momentos)

    duracao = round(float(df["tempo_segundos"].max()), 2) if not df.empty else 0.0
    amostras = int(metrics.get("total_amostras", len(df)))

    st.markdown('<div class="section-title">Diagnóstico Comercial</div>', unsafe_allow_html=True)

    top_left, top_right = st.columns([3.2, 1.8])

    with top_left:
        st.markdown(f'''
        <div class="big-card">
            <div class="diag-title">{diagnostico["pitch_label"]}</div>
            <div class="diag-grid">
                <div class="diag-item">
                    <div class="diag-item-label">Conexão inicial</div>
                    <div class="diag-item-value red">{diagnostico["conexao_inicial"]}</div>
                </div>
                <div class="diag-item">
                    <div class="diag-item-label">Apresentação de valor</div>
                    <div class="diag-item-value orange">{diagnostico["apresentacao_valor"]}</div>
                </div>
                <div class="diag-item">
                    <div class="diag-item-label">Reação ao preço</div>
                    <div class="diag-item-value red">{diagnostico["reacao_preco"]}</div>
                </div>
                <div class="diag-item">
                    <div class="diag-item-label">Fechamento</div>
                    <div class="diag-item-value red">{diagnostico["fechamento"]}</div>
                </div>
            </div>
            <div class="diag-bottom">
                <span class="pill-score">Potencial comercial</span>
                <span class="red" style="font-size:1.4rem;font-weight:900;">{diagnostico["potencial_comercial"]}</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                '<div class="panel-card list-card"><div class="list-card-title">O Que Funcionou</div><ul>' +
                ''.join([f'<li>{x}</li>' for x in diagnostico["o_que_funcionou"]]) +
                '</ul></div>',
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                '<div class="panel-card list-card"><div class="list-card-title">O Que Prejudicou a Venda</div><ul>' +
                ''.join([f'<li>{x}</li>' for x in diagnostico["o_que_prejudicou"]]) +
                '</ul></div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div class="panel-card list-card" style="margin-top:14px;"><div class="list-card-title">O Que Melhorar</div><ul>' +
            ''.join([f'<li>{x}</li>' for x in diagnostico["o_que_melhorar"]]) +
            '</ul></div>',
            unsafe_allow_html=True
        )

    with top_right:
        score_cards = [
            ("Energia Vocal", vocal.get("energia_vocal", 0), diagnostico["energia_vocal_label"]),
            ("Fluidez", vocal.get("fluidez", 0), diagnostico["fluidez_label"]),
            ("Clareza da Oferta", discurso.get("clareza", 0), diagnostico["clareza_label"]),
            ("Fechamento", discurso.get("forca_fechamento", 0), diagnostico["fechamento_label"]),
            ("Pontuação Integrada", multimodal.get("score_integrado", 0), diagnostico["pontuacao_integrada_label"]),
        ]

        for titulo, valor, label in score_cards:
            cor = "red"
            if str(label).lower() in ["medio", "médio"]:
                cor = "orange"
            elif str(label).lower() == "bom":
                cor = "yellow"
            elif str(label).lower() == "forte":
                cor = "green"

            html_score = f'''
            <div class="score-card">
                <div class="side-score-title">{titulo}</div>
                <div class="side-score-value {cor}">{str(valor).replace(".", ",")}</div>
                <div class="side-score-row">
                    {pill_html(label)}
                    <span class="{cor}" style="font-weight:800;">{label}</span>
                </div>
                {score_bar(valor)}
            </div>
            '''
            st.markdown(html_score, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Parâmetros de Avaliação</div>', unsafe_allow_html=True)

    bench_left, bench_right = st.columns([3.1, 1.6])

    with bench_left:
        st.markdown('''
        <div class="bench-card">
            <table class="bench-table">
                <thead>
                    <tr>
                        <th>Métrica</th>
                        <th>Fraco</th>
                        <th>Médio</th>
                        <th>Bom</th>
                        <th>Excelente</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Energia vocal</td><td>0 - 20</td><td>20 - 40</td><td>40 - 70</td><td>70 - 100</td></tr>
                    <tr><td>Fluidez</td><td>0 - 25</td><td>25 - 50</td><td>50 - 75</td><td>75 - 100</td></tr>
                    <tr><td>Clareza</td><td>0 - 40</td><td>40 - 60</td><td>60 - 80</td><td>80 - 100</td></tr>
                    <tr><td>Persuasão</td><td>0 - 40</td><td>40 - 60</td><td>60 - 80</td><td>80 - 100</td></tr>
                    <tr><td>Fechamento</td><td>0 - 40</td><td>40 - 60</td><td>60 - 80</td><td>80 - 100</td></tr>
                </tbody>
            </table>
            <div class="bench-legend">Fraco · Médio · Bom · Excelente</div>
        </div>
        ''', unsafe_allow_html=True)

    with bench_right:
        score_atual = multimodal.get("score_integrado", 0)
        ideal = 60
        html_bench = f'''
        <div class="score-card">
            <div class="small-label">Sua Pontuação:</div>
            <div class="score-main">{str(score_atual).replace(".", ",")}</div>
            <div class="small-label" style="margin-top:12px;">Ideal mínimo:</div>
            <div class="score-ideal">{ideal}</div>
            {score_bar(score_atual)}
            {score_scale()}
        </div>
        '''
        st.markdown(html_bench, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Linha do Tempo Emocional</div>', unsafe_allow_html=True)

    gleft, gright = st.columns([3.0, 1.45])

    with gleft:
        df_plot = df.copy()
        df_plot["y"] = df_plot["emocao_negocio"].map(MAPA_Y).fillna(0)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_plot["tempo_segundos"],
                y=df_plot["y"],
                mode="lines+markers",
                text=df_plot["emocao_negocio"],
                hovertemplate="Tempo: %{x}s<br>Emoção: %{text}<extra></extra>"
            )
        )

        pico = metrics.get("pico_emocional_segundos")
        queda = metrics.get("queda_interesse_segundos")

        if pico is not None:
            fig.add_vline(x=pico, line_dash="dash", line_color="#9b7bff", annotation_text=f"Pico {formatar_tempo(pico)}", annotation_position="top left")
        if queda is not None:
            fig.add_vline(x=queda, line_dash="dash", line_color="#ff5f62", annotation_text=f"Queda {formatar_tempo(queda)}", annotation_position="top left")

        fig.update_layout(
            height=410,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis_title="Tempo",
            yaxis_title="Resposta",
            yaxis=dict(
                tickmode="array",
                tickvals=list(MAPA_Y.values()),
                ticktext=list(MAPA_Y.keys())
            )
        )
        st.plotly_chart(fig, width="stretch")

    with gright:
        st.markdown(f'''
        <div class="score-card" style="margin-bottom:14px;">
            <div class="small-label">Frames processados</div>
            <div class="metric-value">{amostras}</div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Momentos de Maior Impacto</div>', unsafe_allow_html=True)
        html_m = '<div class="frases-box">'
        momentos_impacto = metrics.get("momentos_impacto", [])
        if momentos_impacto:
            html_m += '<ul>'
            for i, momento in enumerate(momentos_impacto, start=1):
                html_m += f"<li>{i}. {formatar_tempo(momento['inicio_segundos'])} - {formatar_tempo(momento['fim_segundos'])} | {momento['emocao']}</li>"
            html_m += '</ul>'
        else:
            html_m += '<div class="small-muted">Nenhum momento identificado.</div>'
        html_m += '</div>'
        st.markdown(html_m, unsafe_allow_html=True)

        st.markdown('<div class="section-title">Distribuição Emocional</div>', unsafe_allow_html=True)
        dist = pd.DataFrame(list(metrics.get("distribuicao_emocional", {}).items()), columns=["emocao", "percentual"])
        if not dist.empty:
            fig2 = px.pie(dist, names="emocao", values="percentual", hole=0.55)
            fig2.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig2, width="stretch")

    st.markdown('<div class="section-title">Análise da Negociação</div>', unsafe_allow_html=True)

    n1, n2, n3 = st.columns(3)

    with n1:
        st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">Preço mencionado</div>
            <div class="kpi-value blue">{len(momentos.get("preco", []))}</div>
            <div class="kpi-sub">Ocorrências</div>
        </div>
        ''', unsafe_allow_html=True)

    with n2:
        st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">Momentos de interesse</div>
            <div class="kpi-value green">{len(momentos.get("interesse", []))}</div>
            <div class="kpi-sub">Sinais positivos de compra</div>
        </div>
        ''', unsafe_allow_html=True)

    with n3:
        st.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">Tentativas de fechamento</div>
            <div class="kpi-value purple">{len(momentos.get("fechamento", []))}</div>
            <div class="kpi-sub">Chamadas para decisão</div>
        </div>
        ''', unsafe_allow_html=True)

    if momentos.get("desconto"):
        st.info("Desconto detectado na negociação.")
    if momentos.get("duvida"):
        st.warning("Momentos de dúvida do cliente detectados.")

    st.markdown('<div class="section-title">Frases da Negociação</div>', unsafe_allow_html=True)

    html_frases = '<div class="frases-box">'
    ordem = ["interesse", "preco", "desconto", "duvida", "fechamento"]
    nomes = {
        "interesse": "Interesse",
        "preco": "Preço",
        "desconto": "Desconto",
        "duvida": "Dúvida",
        "fechamento": "Fechamento"
    }

    for categoria in ordem:
        frases = momentos.get(categoria, [])
        if frases:
            html_frases += f'<div class="group-title">{nomes.get(categoria, categoria)}</div><ul>'
            for frase in frases[:5]:
                html_frases += f'<li>{frase}</li>'
            html_frases += '</ul>'

    if html_frases == '<div class="frases-box">':
        html_frases += '<div class="small-muted">Nenhuma frase comercial relevante foi detectada.</div>'

    html_frases += '</div>'
    st.markdown(html_frases, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Painel Analítico</div>', unsafe_allow_html=True)
    p1, p2 = st.columns([1.2, 1.1])

    with p1:
        a1, a2, a3 = st.columns(3)
        with a1:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">Energia vocal</div>
                <div class="kpi-value blue">{str(vocal.get("energia_vocal", "—")).replace(".", ",")}</div>
                <div class="kpi-sub">Intensidade média da voz</div>
            </div>
            ''', unsafe_allow_html=True)
        with a2:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">Fluidez</div>
                <div class="kpi-value green">{str(vocal.get("fluidez", "—")).replace(".", ",")}</div>
                <div class="kpi-sub">Continuidade da fala</div>
            </div>
            ''', unsafe_allow_html=True)
        with a3:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">Pausas</div>
                <div class="kpi-value purple">{vocal.get("quantidade_pausas", "—")}</div>
                <div class="kpi-sub">Pausas longas detectadas</div>
            </div>
            ''', unsafe_allow_html=True)

        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">Clareza</div>
                <div class="kpi-value blue">{str(discurso.get("clareza", "—")).replace(".", ",")}</div>
                <div class="kpi-sub">Organização da mensagem</div>
            </div>
            ''', unsafe_allow_html=True)
        with b2:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">Confiança verbal</div>
                <div class="kpi-value green">{str(discurso.get("confianca_verbal", "—")).replace(".", ",")}</div>
                <div class="kpi-sub">Segurança na linguagem</div>
            </div>
            ''', unsafe_allow_html=True)
        with b3:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">Persuasão</div>
                <div class="kpi-value purple">{str(discurso.get("persuasao", "—")).replace(".", ",")}</div>
                <div class="kpi-sub">Força argumentativa</div>
            </div>
            ''', unsafe_allow_html=True)
        with b4:
            st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">Fechamento</div>
                <div class="kpi-value red">{str(discurso.get("forca_fechamento", "—")).replace(".", ",")}</div>
                <div class="kpi-sub">Força da chamada final</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Visão Estratégica</div>', unsafe_allow_html=True)
        html_rec = '<div class="strategy-box"><ul>'
        recs = insights.get("recomendacoes", [])
        if recs:
            for rec in recs:
                html_rec += f'<li>{rec}</li>'
        else:
            html_rec += '<li>Nenhuma recomendação disponível.</li>'
        html_rec += '</ul></div>'
        st.markdown(html_rec, unsafe_allow_html=True)

    with p2:
        st.markdown('<div class="section-title">Dados Detalhados</div>', unsafe_allow_html=True)
        st.dataframe(df, width="stretch", height=430)

    if os.path.exists(transcription_path):
        with open(transcription_path, "r", encoding="utf-8") as f:
            transcricao = f.read()

        st.markdown('<div class="section-title">Transcrição</div>', unsafe_allow_html=True)
        st.text_area("Texto transcrito", transcricao, height=220)
