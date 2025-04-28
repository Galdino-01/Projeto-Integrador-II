import streamlit as st
import os
from pathlib import Path
import base64

# Configuração da página
st.set_page_config(
    page_title="Projeto Integrador II",
    page_icon="📄",
    layout="wide"
)

# Obtém o caminho absoluto do diretório do script atual
current_dir = Path(__file__).parent.parent
pdf_path = current_dir / "tcc.pdf"

# Verifica se o arquivo existe
if pdf_path.exists():
    # Lê o conteúdo do PDF como bytes
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Usa HTML para embutir o PDF
    pdf_display = f"""
        <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)
else:
    st.error("Arquivo tcc.pdf não encontrado.")
