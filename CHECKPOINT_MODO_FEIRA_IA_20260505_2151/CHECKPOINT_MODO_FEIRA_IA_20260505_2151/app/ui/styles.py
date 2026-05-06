import streamlit as st

def apply_styles():
    st.markdown("""
<style>
:root{
    --bg:#050914;
    --bg-soft:#0a1120;
    --panel:#0f1728;
    --panel-2:#121c31;
    --panel-3:#16223c;
    --border:rgba(151,172,214,.12);
    --border-strong:rgba(151,172,214,.18);
    --text:#eef4ff;
    --muted:#9aa9c5;
    --green:#34d399;
    --orange:#ffb45c;
    --red:#ff7a7f;
    --purple:#9b7bff;
    --blue:#7aa2ff;
    --shadow:0 18px 50px rgba(0,0,0,.34);
    --radius:22px;
}

html, body, [class*="css"]{
    font-family: Inter, "Segoe UI", Arial, sans-serif;
}

[data-testid="stAppViewContainer"]{
    background:
        radial-gradient(circle at 12% 0%, rgba(86,109,255,.14) 0%, transparent 26%),
        radial-gradient(circle at 100% 0%, rgba(96,74,255,.10) 0%, transparent 22%),
        linear-gradient(180deg, #070d18 0%, #050914 45%, #03060d 100%);
}

.block-container{
    max-width: 1460px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

section[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #0d1830 0%, #0a1428 100%);
    border-right:1px solid rgba(255,255,255,.05);
}

.main-title{
    font-size:2.7rem;
    line-height:1.03;
    font-weight:900;
    color:var(--text);
    letter-spacing:-.03em;
    margin-bottom:.35rem;
}

.sub-title{
    color:var(--muted);
    font-size:1rem;
    margin-bottom:1.4rem;
}

.section-title{
    color:var(--text);
    font-size:1.42rem;
    font-weight:850;
    letter-spacing:-.02em;
    margin-top:1.35rem;
    margin-bottom:.95rem;
}

.card, .big-card, .panel-card, .score-card, .hero-score-card, .pitch-insight-card, .strategy-box{
    background:linear-gradient(180deg, rgba(18,28,49,.96) 0%, rgba(12,20,36,.98) 100%);
    border:1px solid var(--border);
    border-radius:var(--radius);
    box-shadow:var(--shadow);
    color:var(--text);
    backdrop-filter: blur(8px);
}

.card{ padding:18px; }

.big-card{
    padding:24px;
    margin-bottom:28px;
    overflow:hidden;
}

.panel-card{
    padding:20px;
    min-height:220px;
    margin-top:0;
}

.score-card{
    padding:18px;
    min-height:160px;
    margin-bottom:16px;
}

.score-card:hover,
.card:hover,
.panel-card:hover,
.pitch-insight-card:hover,
.big-card:hover{
    border-color:var(--border-strong);
    box-shadow:0 22px 55px rgba(0,0,0,.38);
}

.hero-score-card{
    position:relative;
    overflow:hidden;
    padding:30px 28px;
    margin-bottom:24px;
}

.hero-score-card::before{
    content:"";
    position:absolute;
    inset:-30% auto auto -10%;
    width:280px;
    height:280px;
    background:radial-gradient(circle, rgba(88,124,255,.18) 0%, transparent 68%);
    pointer-events:none;
}

.hero-score-card::after{
    content:"";
    position:absolute;
    inset:auto -5% -35% auto;
    width:260px;
    height:260px;
    background:radial-gradient(circle, rgba(155,123,255,.14) 0%, transparent 68%);
    pointer-events:none;
}

.hero-score-title{
    position:relative;
    z-index:1;
    font-size:.82rem;
    letter-spacing:.18em;
    color:#9fb1cf;
    font-weight:800;
    margin-bottom:12px;
}

.hero-score-value{
    position:relative;
    z-index:1;
    font-size:4.1rem;
    font-weight:900;
    line-height:1;
    letter-spacing:-.04em;
    color:#ffffff;
}

.hero-score-label{
    position:relative;
    z-index:1;
    margin-top:10px;
    font-size:1.08rem;
    font-weight:850;
}

.hero-score-bar{
    position:relative;
    z-index:1;
    width:100%;
    height:12px;
    margin-top:18px;
    background:#22314f;
    border-radius:999px;
    overflow:hidden;
    box-shadow: inset 0 1px 2px rgba(0,0,0,.28);
}

.hero-score-fill{
    height:100%;
    background:linear-gradient(90deg,#ff6b72 0%, #ffb45c 38%, #ffd76a 68%, #34d399 100%);
    border-radius:999px;
}

.diag-title{
    font-size:2rem;
    font-weight:900;
    line-height:1.05;
    color:#ffffff;
    margin-bottom:18px;
    letter-spacing:-.03em;
}

.diag-grid{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:16px;
    margin-top:8px;
}

.diag-item{
    background:linear-gradient(180deg, rgba(255,255,255,.04) 0%, rgba(255,255,255,.02) 100%);
    border:1px solid rgba(255,255,255,.06);
    border-radius:18px;
    padding:14px 15px;
}

.diag-item-label{
    color:#c9d8f4;
    font-size:.9rem;
    font-weight:750;
    margin-bottom:8px;
}

.diag-item-value{
    font-size:1.08rem;
    font-weight:850;
    letter-spacing:-.01em;
}

.diag-bottom{
    margin-top:18px;
    display:flex;
    align-items:center;
    gap:12px;
}

.pill, .pill-score{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    padding:7px 12px;
    border-radius:12px;
    font-size:.88rem;
    font-weight:800;
}

.pill-red{ background:rgba(255,107,114,.14); color:#ff9aa0; }
.pill-orange{ background:rgba(255,180,92,.14); color:#ffc983; }
.pill-yellow{ background:rgba(255,215,106,.14); color:#ffe08d; }
.pill-green{ background:rgba(52,211,153,.14); color:#86ebc0; }
.pill-gray{ background:rgba(255,255,255,.07); color:#d8e4fa; }

.pill-score{
    background:rgba(255,255,255,.07);
    color:#dce8ff;
}

.red{ color:var(--red) !important; }
.orange{ color:var(--orange) !important; }
.yellow{ color:var(--yellow) !important; }
.green{ color:var(--green) !important; }

.side-score-title,
.list-card-title{
    color:var(--text);
    font-size:1rem;
    font-weight:800;
    margin-bottom:10px;
}

.side-score-value{
    color:#ffffff;
    font-size:2rem;
    font-weight:900;
    line-height:1.02;
    letter-spacing:-.03em;
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
    gap:4px;
    width:100%;
    height:8px;
}

.progress-seg{
    flex:1;
    height:6px;
    border-radius:4px;
    background:#3d4c68;
}

.progress-seg.active{
    background:linear-gradient(90deg,#ff6b72 0%, #ff9657 42%, #ffcf5b 70%, #34d399 100%);
}

.small-label{
    color:#b9c8e8;
    font-size:.88rem;
    font-weight:700;
    margin-bottom:10px;
    text-transform:uppercase;
    letter-spacing:.04em;
}

.metric-value{
    color:#ffffff;
    font-size:2.3rem;
    font-weight:900;
    line-height:1.02;
    letter-spacing:-.03em;
}

.metric-sub{
    color:#c7d5ee;
    font-size:.92rem;
    line-height:1.55;
    margin-top:10px;
}

.heatmap-shell{
    background:linear-gradient(180deg, rgba(15,25,48,.72) 0%, rgba(10,18,36,.45) 100%);
    border:1px solid rgba(151,172,214,.12);
    border-radius:24px;
    padding:22px;
    box-shadow:0 18px 45px rgba(0,0,0,.25);
}

.heatmap-top{
    display:grid;
    grid-template-columns:repeat(3,1fr);
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
    background:rgba(255,255,255,.03);
}

.heatmap-kpi-title{
    color:#eef4ff;
    font-size:.96rem;
    font-weight:800;
    margin-bottom:4px;
}

.heatmap-kpi-value{
    color:#ffffff;
    font-size:1.8rem;
    font-weight:900;
    line-height:1.05;
    margin-bottom:4px;
    letter-spacing:-.03em;
}

.heatmap-kpi-sub{
    color:#9aabc6;
    font-size:.82rem;
}

.heatmap-stage{ margin-top: 14px; }

.heatmap-bar{
    display:flex;
    width:100%;
    height:64px;
    border-radius:16px;
    overflow:hidden;
    background:#13213a;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.05), 0 12px 28px rgba(0,0,0,.24);
}

.hm-seg{
    flex:1;
    min-width:8px;
    position:relative;
}

.hm-seg + .hm-seg{
    box-shadow: inset 1px 0 0 rgba(9,18,36,.45);
}

.hm-green{ background:linear-gradient(180deg,#3ce19a 0%, #159e63 100%); }
.hm-yellow{ background:linear-gradient(180deg,#ffe57a 0%, #d9b326 100%); }
.hm-orange{ background:linear-gradient(180deg,#ffb86b 0%, #ee7f27 100%); }
.hm-red{ background:linear-gradient(180deg,#ff6e79 0%, #df3b52 100%); }

.heatmap-scale{
    display:flex;
    justify-content:space-between;
    margin-top:10px;
    color:#9aabc6;
    font-size:.82rem;
    padding:0 2px;
}

.heatmap-legend{
    display:flex;
    flex-wrap:wrap;
    gap:16px;
    margin-top:16px;
    color:#d3def4;
    font-size:.87rem;
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
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:16px;
    margin-top:14px;
    margin-bottom:18px;
}

.pitch-insight-card{
    border-radius:20px;
    padding:18px;
}

.pitch-insight-title,
.strategy-title{
    color:#eef4ff;
    font-size:1.02rem;
    font-weight:850;
    margin-bottom:12px;
}

.strategy-box{
    border-radius:22px;
    padding:20px;
    margin-top:18px;
}

.strategy-priority-list{
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:16px;
    margin-top:14px;
    margin-bottom:18px;
}

.strategy-priority-card{
    background:linear-gradient(180deg, rgba(255,255,255,.045) 0%, rgba(255,255,255,.02) 100%);
    border:1px solid rgba(151,172,214,.12);
    border-radius:18px;
    padding:16px;
    box-shadow:0 10px 26px rgba(0,0,0,.18);
}

.strategy-priority-label{
    color:#b9c8e8;
    font-size:.78rem;
    font-weight:800;
    letter-spacing:.08em;
    text-transform:uppercase;
    margin-bottom:10px;
}

.strategy-priority-text{
    color:#eef4ff;
    font-size:.98rem;
    line-height:1.68;
    font-weight:500;
}

.strategy-extra-title{
    color:#dbe6ff;
    font-size:.96rem;
    font-weight:800;
    margin-top:6px;
    margin-bottom:12px;
}

.success-card{
    background:linear-gradient(180deg, rgba(16,34,43,.96) 0%, rgba(12,25,33,.98) 100%);
    border:1px solid rgba(52,211,153,.14);
}

.danger-card{
    background:linear-gradient(180deg, rgba(38,24,31,.96) 0%, rgba(28,17,23,.98) 100%);
    border:1px solid rgba(255,122,127,.14);
}

.advice-card{
    background:linear-gradient(180deg, rgba(28,24,39,.96) 0%, rgba(21,17,31,.98) 100%);
    border:1px solid rgba(155,123,255,.16);
}

.success-card .list-card-title{ color:#dcfff1; }
.danger-card .list-card-title{ color:#ffe3e5; }
.advice-card .list-card-title{ color:#efe4ff; }

.check-list{
    display:flex;
    flex-direction:column;
    gap:14px;
    margin-top:10px;
}

.check-item{
    display:flex;
    align-items:flex-start;
    gap:14px;
    color:#eef4ff;
    line-height:1.7;
    font-size:1rem;
    font-weight:500;
}

.check-icon,
.warn-icon,
.action-icon{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    width:28px;
    min-width:28px;
    height:28px;
    line-height:1;
    transform: translateY(1px);
}

.check-icon{
    color:var(--green);
    font-size:22px;
    font-weight:900;
}

.warn-icon{
    color:var(--orange);
    font-size:22px;
}

.action-icon{
    color:var(--purple);
    font-size:22px;
}

.panel-card ul,
.pitch-insight-card ul,
.strategy-box ul{
    padding-left:1.05rem;
    margin:0;
}

.panel-card li,
.pitch-insight-card li,
.strategy-box li{
    color:#e5eeff;
    margin-bottom:10px;
    line-height:1.58;
}

[data-testid="stFileUploaderDropzone"]{
    background:linear-gradient(180deg, rgba(17,28,49,.94) 0%, rgba(20,33,57,.98) 100%);
    border:1px dashed rgba(151,172,214,.28);
    border-radius:20px;
    box-shadow:0 14px 35px rgba(0,0,0,.20);
}

[data-testid="stFileUploaderDropzone"]:hover{
    border-color:rgba(110,168,255,.45);
    background:linear-gradient(180deg, rgba(20,33,57,.98) 0%, rgba(24,39,67,1) 100%);
}

.stButton > button{
    border:none;
    border-radius:14px;
    padding:.72rem 1.2rem;
    font-weight:800;
    color:white;
    background:linear-gradient(135deg, #4f7cff 0%, #6b8dff 55%, #7b61ff 100%);
    box-shadow:0 10px 28px rgba(79,124,255,.26);
}

.stButton > button:hover{
    transform:translateY(-1px);
    box-shadow:0 16px 34px rgba(79,124,255,.34);
}

.stButton > button:focus{
    outline:none;
    box-shadow:0 0 0 3px rgba(110,168,255,.20);
}

.stTextArea textarea{
    border-radius:16px !important;
    background:#0f1b31 !important;
    color:#eef4ff !important;
    border:1px solid rgba(151,172,214,.14) !important;
}

@media (max-width: 1100px){
    .pitch-insights-grid,
    .heatmap-top,
    .diag-grid,
    .strategy-priority-list{
        grid-template-columns:1fr !important;
    }

    .hero-score-value{
        font-size:3.2rem;
    }
}
</style>
""", unsafe_allow_html=True)


.score-card.compact-insight{
    min-height: 132px !important;
    padding: 18px 20px !important;
    border-radius: 20px !important;
}

.score-card.compact-insight .small-label{
    font-size: .92rem;
    margin-bottom: 10px;
}

.score-card.compact-insight .metric-value{
    font-size: 2.1rem !important;
    line-height: 1.05;
    margin-bottom: 8px;
}

.score-card.compact-insight .metric-sub{
    font-size: .92rem;
    line-height: 1.45;
    margin-top: 0;
}


/* ===== Refino de layout: plano + momentos ===== */
.strategy-box{
    padding:24px !important;
    min-height:100%;
}

.strategy-title{
    font-size:1.08rem !important;
    font-weight:900 !important;
    margin-bottom:14px !important;
}

.strategy-box ul{
    margin-top:8px !important;
}

.strategy-box li{
    margin-bottom:12px !important;
}

.score-card.compact-insight{
    min-height:124px !important;
}

.section-title{
    margin-top:1.5rem !important;
    margin-bottom:1rem !important;
}

.block-container .element-container:has(.strategy-box){
    margin-bottom:8px;
}

/* momentos detectados mais elegantes */
.momentos-shell{
    background:linear-gradient(180deg, rgba(18,28,49,.96) 0%, rgba(12,20,36,.98) 100%);
    border:1px solid rgba(151,172,214,.12);
    border-radius:22px;
    box-shadow:0 18px 50px rgba(0,0,0,.34);
    padding:20px;
}

.momentos-title{
    color:#eef4ff;
    font-size:1.02rem;
    font-weight:850;
    margin-bottom:12px;
}


/* ===== Polimento premium da seção final ===== */
.score-card.compact-insight{
    min-height: 138px !important;
    padding: 20px 22px !important;
    border-radius: 22px !important;
    border: 1px solid rgba(151,172,214,.10) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,.22) !important;
}

.score-card.compact-insight .small-label{
    font-size: .88rem !important;
    color: #b8c7e6 !important;
    margin-bottom: 10px !important;
    text-transform: uppercase;
    letter-spacing: .04em;
}

.score-card.compact-insight .metric-value{
    font-size: 2.15rem !important;
    line-height: 1.02 !important;
    margin-bottom: 8px !important;
}

.score-card.compact-insight .metric-sub{
    font-size: .90rem !important;
    line-height: 1.5 !important;
    color: #c9d7f2 !important;
    margin-top: 0 !important;
}

.card{
    border-radius: 22px !important;
}

.section-title{
    margin-top: 1.6rem !important;
    margin-bottom: 1rem !important;
}

.strategy-box{
    border-radius: 24px !important;
}

@media (max-width: 1100px){
    .score-card.compact-insight{
        min-height: auto !important;
    }
}


/* ===== Upgrade premium leitura da conversa ===== */

.score-card.compact-insight {
    background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
    border: 1px solid rgba(151,172,214,0.08) !important;
    box-shadow: 0 12px 32px rgba(0,0,0,0.28) !important;
    backdrop-filter: blur(8px);
}

.score-card.compact-insight .metric-value {
    font-size: 2.3rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}

.score-card.compact-insight .small-label {
    opacity: 0.9;
}

.score-card.compact-insight .metric-sub {
    opacity: 0.85;
}



/* ===== Upgrade premium leitura da conversa v2 ===== */
.score-card{
    background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
    border: 1px solid rgba(151,172,214,0.08) !important;
    box-shadow: 0 12px 32px rgba(0,0,0,0.28) !important;
    backdrop-filter: blur(8px);
}

.score-card .metric-value{
    font-size: 2.3rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}

.score-card .small-label{
    opacity: 0.9;
}

.score-card .metric-sub{
    opacity: 0.85;
}


/* ===== refinamento premium dos score-cards ===== */
.score-card{
    background:linear-gradient(180deg, rgba(28,42,72,.96) 0%, rgba(22,34,58,.98) 100%) !important;
    border:1px solid rgba(151,172,214,.10) !important;
    border-radius:22px !important;
    box-shadow:0 14px 34px rgba(0,0,0,.24) !important;
    backdrop-filter:blur(8px);
}

.score-card:hover{
    transform:translateY(-1px);
    box-shadow:0 18px 40px rgba(0,0,0,.28) !important;
    border-color:rgba(151,172,214,.16) !important;
}


/* ===== upgrade premium leitura da conversa (correto) ===== */

.side-score-title{
    font-size:0.9rem !important;
    color:#c7d5ee !important;
    letter-spacing:.04em;
    margin-bottom:12px !important;
}

.side-score-value{
    font-size:2.4rem !important;
    font-weight:900 !important;
    letter-spacing:-.03em;
    margin-bottom:6px;
}

.side-score-row{
    margin-top:12px !important;
}

.side-score-box{
    background:linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
    border:1px solid rgba(151,172,214,.08) !important;
    border-radius:20px !important;
    box-shadow:0 14px 34px rgba(0,0,0,.28) !important;
    backdrop-filter:blur(8px);
    padding:18px 20px !important;
    margin-bottom:14px;
}



/* ===== ajuste definitivo leitura da conversa ===== */

/* força visual premium nos cards da direita */
div[data-testid="column"] div.score-card{
    background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
    border: 1px solid rgba(151,172,214,0.08) !important;
    border-radius: 20px !important;
    box-shadow: 0 14px 34px rgba(0,0,0,0.28) !important;
    backdrop-filter: blur(8px);
}

/* números maiores */
div[data-testid="column"] .metric-value{
    font-size: 2.4rem !important;
    font-weight: 900 !important;
}

/* título mais elegante */
div[data-testid="column"] .small-label{
    color: #c7d5ee !important;
    letter-spacing: .04em;
}



/* ===== micro-polimento final da seção de evidências ===== */

div[data-testid="column"] div.score-card{
    margin-bottom: 18px !important;
    padding: 22px 22px !important;
}

div[data-testid="column"] .metric-sub{
    margin-top: 12px !important;
    line-height: 1.6 !important;
}

div[data-testid="column"] .metric-value{
    margin-top: 2px;
    margin-bottom: 10px;
}

.card{
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}

.card:hover{
    transform: translateY(-1px);
    box-shadow: 0 16px 38px rgba(0,0,0,.24);
    border-color: rgba(151,172,214,.16);
}



/* ===== DASHBOARD POLISH FINAL ===== */

/* layout geral */
.block-container{
    max-width: 1500px !important;
    padding-top: 1.35rem !important;
    padding-bottom: 2.4rem !important;
}

.section-title{
    font-size: 1.48rem !important;
    font-weight: 900 !important;
    letter-spacing: -.025em !important;
    margin-top: 1.55rem !important;
    margin-bottom: 1.05rem !important;
    color: #f2f6ff !important;
}

/* base visual premium */
.card, .big-card, .panel-card, .score-card, .hero-score-card, .strategy-box{
    border: 1px solid rgba(151,172,214,.10) !important;
    box-shadow: 0 18px 48px rgba(0,0,0,.30) !important;
    backdrop-filter: blur(10px) !important;
}

.card:hover, .big-card:hover, .panel-card:hover, .score-card:hover, .strategy-box:hover{
    border-color: rgba(151,172,214,.16) !important;
    box-shadow: 0 22px 56px rgba(0,0,0,.34) !important;
}

/* hero principal */
.hero-score-card{
    padding: 34px 34px !important;
    border-radius: 26px !important;
    margin-bottom: 28px !important;
    background:
        linear-gradient(180deg, rgba(28,42,72,.98) 0%, rgba(16,26,46,.98) 100%) !important;
}

.hero-score-title{
    font-size: .84rem !important;
    letter-spacing: .22em !important;
    margin-bottom: 14px !important;
    color: #a9bbda !important;
}

.hero-score-value{
    font-size: 4.45rem !important;
    font-weight: 900 !important;
    line-height: .95 !important;
    letter-spacing: -.05em !important;
}

.hero-score-label{
    margin-top: 12px !important;
    font-size: 1.08rem !important;
    font-weight: 900 !important;
}

.hero-score-bar{
    margin-top: 22px !important;
    height: 14px !important;
    border-radius: 999px !important;
    background: rgba(255,255,255,.10) !important;
}

.hero-score-fill{
    box-shadow: 0 0 18px rgba(255,180,92,.18) !important;
}

/* diagnostico principal */
.big-card{
    padding: 28px !important;
    margin-bottom: 30px !important;
    border-radius: 26px !important;
    background:
        linear-gradient(180deg, rgba(28,42,72,.98) 0%, rgba(17,28,49,.98) 100%) !important;
}

.diag-title{
    font-size: 2.2rem !important;
    line-height: 1.02 !important;
    margin-bottom: 22px !important;
}

.diag-grid{
    gap: 18px !important;
    margin-top: 10px !important;
}

.diag-item{
    padding: 16px 16px !important;
    border-radius: 18px !important;
    border: 1px solid rgba(255,255,255,.07) !important;
    background:
        linear-gradient(180deg, rgba(255,255,255,.045) 0%, rgba(255,255,255,.02) 100%) !important;
}

.diag-item-label{
    font-size: .9rem !important;
    font-weight: 800 !important;
    color: #c8d6f1 !important;
    margin-bottom: 10px !important;
}

.diag-item-value{
    font-size: 1.12rem !important;
    font-weight: 900 !important;
}

.diag-bottom{
    margin-top: 22px !important;
    gap: 14px !important;
}

/* cards de listas */
.panel-card{
    padding: 22px !important;
    min-height: 228px !important;
    border-radius: 24px !important;
    box-shadow: 0 16px 38px rgba(0,0,0,.26) !important;
}

.list-card-title{
    font-size: 1.06rem !important;
    font-weight: 900 !important;
    margin-bottom: 14px !important;
}

.check-list{
    gap: 12px !important;
    margin-top: 10px !important;
}

.check-item{
    gap: 14px !important;
    line-height: 1.68 !important;
    font-size: 1rem !important;
    font-weight: 520 !important;
}

.check-icon, .warn-icon, .action-icon{
    transform: translateY(1px);
}

/* coluna direita superior */
.score-card.compact-insight{
    min-height: 170px !important;
    padding: 20px 20px !important;
    border-radius: 22px !important;
    background:
        linear-gradient(180deg, rgba(28,42,72,.96) 0%, rgba(17,28,49,.98) 100%) !important;
}

.side-score-title{
    font-size: .98rem !important;
    font-weight: 850 !important;
    margin-bottom: 12px !important;
    color: #eef4ff !important;
}

.side-score-value{
    font-size: 2.15rem !important;
    font-weight: 900 !important;
    line-height: 1 !important;
    margin-bottom: 2px !important;
}

.side-score-row{
    margin-top: 12px !important;
    gap: 10px !important;
}

.progress-track{
    margin-top: 14px !important;
}

.progress-seg{
    height: 7px !important;
    border-radius: 999px !important;
}

/* metric cards gerais */
.small-label{
    color: #b9c8e8 !important;
    font-size: .86rem !important;
    font-weight: 800 !important;
    margin-bottom: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: .05em !important;
}

.metric-value{
    color: #ffffff !important;
    font-size: 2.32rem !important;
    font-weight: 900 !important;
    line-height: 1.01 !important;
    letter-spacing: -.03em !important;
}

.metric-sub{
    color: #c7d5ee !important;
    font-size: .92rem !important;
    line-height: 1.58 !important;
    margin-top: 10px !important;
}

/* score-cards da leitura da conversa */
div[data-testid="column"] div.score-card{
    border-radius: 22px !important;
    padding: 22px 22px !important;
    margin-bottom: 18px !important;
    background:
        linear-gradient(180deg, rgba(28,42,72,.98) 0%, rgba(18,30,52,.98) 100%) !important;
    border: 1px solid rgba(151,172,214,.10) !important;
    box-shadow: 0 14px 34px rgba(0,0,0,.28) !important;
}

div[data-testid="column"] .metric-value{
    font-size: 2.42rem !important;
    font-weight: 900 !important;
}

div[data-testid="column"] .metric-sub{
    margin-top: 12px !important;
}

/* strategy box */
.strategy-box{
    padding: 24px !important;
    border-radius: 26px !important;
    background:
        linear-gradient(180deg, rgba(28,42,72,.98) 0%, rgba(17,28,49,.98) 100%) !important;
}

.strategy-title{
    font-size: 1.08rem !important;
    font-weight: 900 !important;
    margin-bottom: 14px !important;
    color: #eef4ff !important;
}

/* mobile */
@media (max-width: 1100px){
    .hero-score-value{
        font-size: 3.45rem !important;
    }

    .diag-grid{
        grid-template-columns: 1fr 1fr !important;
    }

    .score-card.compact-insight{
        min-height: auto !important;
    }
}

@media (max-width: 720px){
    .diag-grid{
        grid-template-columns: 1fr !important;
    }

    .hero-score-card,
    .big-card,
    .panel-card,
    .score-card,
    .strategy-box{
        padding: 18px !important;
    }
}


/* ===== FINAL REFINEMENT DASHBOARD ===== */

/* HERO MAIS IMPACTANTE */
.hero-score-card{
    padding: 38px 40px !important;
    border-radius: 28px !important;
}

.hero-score-value{
    font-size: 4.8rem !important;
}

.hero-score-bar{
    height: 16px !important;
}

/* DIAGNÓSTICO MAIS RESPIRADO */
.big-card{
    padding: 32px !important;
}

.diag-grid{
    gap: 22px !important;
}

.diag-item{
    padding: 18px 18px !important;
}

/* LISTAS MAIS ELEGANTES */
.panel-card{
    padding: 24px !important;
    border-radius: 26px !important;
}

/* COLUNA DIREITA MAIS FORTE */
div[data-testid="column"] div.score-card{
    padding: 24px 24px !important;
    border-radius: 24px !important;
}

div[data-testid="column"] .metric-value{
    font-size: 2.5rem !important;
}

/* MELHOR ALINHAMENTO VISUAL GLOBAL */
.block-container{
    padding-top: 1.2rem !important;
}

/* MICRO CONTRASTE */
.card, .big-card, .panel-card, .score-card{
    border: 1px solid rgba(151,172,214,.12) !important;
}



/* ===== NOVO MAPA DE ENGAJAMENTO ===== */

.engagement-bar{
    height: 12px !important;
    border-radius: 999px !important;
    background: rgba(255,255,255,.08) !important;
    position: relative;
    overflow: hidden;
    margin-top: 18px;
}

/* linha base */
.engagement-line{
    height: 4px;
    background: linear-gradient(90deg, #ff5a5a, #ffb347, #6ee7b7);
    border-radius: 999px;
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 100%;
    opacity: .5;
}

/* pontos importantes */
.engagement-point{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%);
    box-shadow: 0 0 8px rgba(0,0,0,.4);
}

/* cores por tipo */
.engagement-high{
    background: #6ee7b7;
}

.engagement-medium{
    background: #fbbf24;
}

.engagement-low{
    background: #ff5a5a;
}

/* labels abaixo */
.engagement-label{
    font-size: .72rem;
    color: #9fb6ff;
    margin-top: 8px;
}

/* cards de insight abaixo */
.engagement-insight{
    margin-top: 14px;
    padding: 12px 14px;
    border-radius: 14px;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(151,172,214,.10);
    font-size: .85rem;
    color: #c7d5ee;
}

.engagement-insight strong{
    color: #eef4ff;
}



/* ===== POLIMENTO FINAL MAPA ===== */

/* linha mais forte */
.engagement-line,
[style*="linear-gradient(90deg,#ff6b72"]{
    height: 5px !important;
    opacity: .9 !important;
}

/* pontos mais vivos */
div[style*="#ffd76a"]{
    box-shadow: 0 0 22px rgba(255,215,106,.55) !important;
}

div[style*="#ff6b72"]{
    box-shadow: 0 0 22px rgba(255,107,114,.55) !important;
}

/* callouts mais alinhados */
div[style*="transform:translate(-50%, -92px)"]{
    transform: translate(-50%, -78px) !important;
}

div[style*="transform:translate(-50%, -62px)"]{
    transform: translate(-50%, -52px) !important;
}

/* insights mais premium */
.engagement-insight{
    background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.02)) !important;
    border: 1px solid rgba(151,172,214,.14) !important;
    padding: 14px 16px !important;
    border-radius: 14px !important;
    font-size: .9rem !important;
}

/* espaçamento geral */
.engagement-insight + .engagement-insight{
    margin-top: 6px;
}

