import streamlit as st

def render_diagnostico(diagnostico):
    st.markdown('<div class="section-title">Diagnóstico Comercial</div>', unsafe_allow_html=True)

    st.markdown(f"""
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
    """, unsafe_allow_html=True)
