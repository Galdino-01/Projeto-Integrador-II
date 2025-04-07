import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Projeto Integrador II",
    page_icon="📄",
    layout="wide"
)

with open("relatorio_dataViz.md", "r", encoding="utf-8") as file:
    content = file.read()

st.markdown(content)
