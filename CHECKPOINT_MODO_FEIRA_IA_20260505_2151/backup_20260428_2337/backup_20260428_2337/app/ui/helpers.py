import streamlit as st

def load_external_css():
    try:
        with open('app/ui/style.css', encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Erro ao carregar CSS: {e}")
