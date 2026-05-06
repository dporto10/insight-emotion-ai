import streamlit as st

def render_score_card(titulo, valor, label, pill_html, score_bar):

    cor = "red"

    if str(label).lower() in ["medio","médio"]:
        cor = "orange"
    elif str(label).lower() == "bom":
        cor = "yellow"
    elif str(label).lower() == "forte":
        cor = "green"

    html = f'''
    <div class="score-card">
        <div class="side-score-title">{titulo}</div>
        <div class="side-score-value {cor}">{str(valor).replace(".",",")}</div>
        <div class="side-score-row">
            {pill_html(label)}
            <span class="{cor}" style="font-weight:800;">{label}</span>
        </div>
        {score_bar(valor)}
    </div>
    '''

    st.markdown(html, unsafe_allow_html=True)


import streamlit as st

def render_hero_score(score, label, pct, cor):
    st.markdown(f"""
    <div class="hero-score-card">
        <div class="hero-score-title">PONTUAÇÃO GERAL</div>
        <div class="hero-score-value">{str(score).replace(".", ",")}</div>
        <div class="hero-score-label {cor}">{label}</div>
        <div class="hero-score-bar">
            <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#6ee7b7,#60a5fa);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
