import streamlit as st

def render_insights_cards(diagnostico):
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown(
            '<div class="panel-card success-card"><div class="list-card-title">O Que Funcionou</div><div class="check-list">' +
            ''.join([f'<div class="check-item"><span class="check-icon">✓</span><span>{x}</span></div>' for x in diagnostico["o_que_funcionou"]]) +
            '</div></div>',
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            '<div class="panel-card danger-card"><div class="list-card-title">O Que Prejudicou a Venda</div><div class="check-list">' +
            ''.join([f'<div class="check-item"><span class="warn-icon">⚠️</span><span>{x}</span></div>' for x in diagnostico["o_que_prejudicou"]]) +
            '</div></div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="panel-card advice-card" style="margin-top:20px;"><div class="list-card-title">O Que Melhorar</div><div class="check-list">' +
        ''.join([f'<div class="check-item"><span class="action-icon">⚡</span><span>{x}</span></div>' for x in diagnostico["o_que_melhorar"]]) +
        '</div></div>',
        unsafe_allow_html=True
    )
