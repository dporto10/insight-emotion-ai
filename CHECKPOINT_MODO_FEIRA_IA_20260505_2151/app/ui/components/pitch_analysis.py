import streamlit as st

def render_pitch_lists(diagnostico):

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
            '<div class="panel-card list-card"><div class="list-card-title">O Que Prejudicou</div><ul>' +
            ''.join([f'<li>{x}</li>' for x in diagnostico["o_que_prejudicou"]]) +
            '</ul></div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="panel-card list-card"><div class="list-card-title">O Que Melhorar</div><ul>' +
        ''.join([f'<li>{x}</li>' for x in diagnostico["o_que_melhorar"]]) +
        '</ul></div>',
        unsafe_allow_html=True
    )
