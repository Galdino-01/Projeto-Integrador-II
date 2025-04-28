import streamlit as st
import os
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="Projeto Integrador II",
    page_icon="📄",
    layout="wide"
)

# Obtém o caminho absoluto do diretório do script atual
current_dir = Path(__file__).parent.parent.parent
report_path = current_dir / "relatorio_dataViz.md"

with open(report_path, "r", encoding="utf-8") as file:
    content = file.read()

st.markdown(content)
