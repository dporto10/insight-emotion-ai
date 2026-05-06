import streamlit as st

def render_hero_score(score_integrado, label, pct, cor):
    st.markdown(f"""
    <div class="hero-score-card">
        <div class="hero-score-title">PONTUAÇÃO GERAL</div>
        <div class="hero-score-value">{str(score_integrado).replace(".", ",")}</div>
        <div class="hero-score-label {cor}">{label}</div>
        <div class="hero-score-bar">
            <div class="hero-score-fill" style="width:{pct}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
