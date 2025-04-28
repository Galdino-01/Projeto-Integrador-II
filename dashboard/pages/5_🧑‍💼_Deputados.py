# ### Importando bibliotecas
import streamlit as st
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from PIL import Image
import requests
from io import BytesIO
import logging

from get_deputados import carregar_lista_deputados

# Configuração da página
st.set_page_config(
    page_title="Deputados",
    page_icon="🧑",
    layout="wide"
)

st.caption("Os registros são referentes aos deputados em exercício no ano de 2022")

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Definir variáveis globais para faixas etárias
bins = [18, 31, 41, 51, 61, 71, 81, 120]
labels = ["18-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81+"]

### Coletar dados
@st.cache_data(ttl=3600)  # Cache por 1 hora para melhorar performance
def carregar_dados_deputados():
    """Carrega e processa os dados dos deputados."""
    try:
        lista_deputados = carregar_lista_deputados()
        
        # Criar uma cópia explícita para evitar SettingWithCopyWarning
        deputados_unicos = lista_deputados.drop_duplicates(subset="id", keep="last").copy()
        
        # Processar datas com formato explícito
        deputados_unicos["dataNascimento"] = pd.to_datetime(deputados_unicos["dataNascimento"], format="%Y-%m-%d").dt.strftime("%d/%m/%Y")
        
        # Calcular idade
        hoje = datetime.now()
        # Usar .loc para evitar SettingWithCopyWarning
        deputados_unicos.loc[:, "idade"] = (hoje - pd.to_datetime(deputados_unicos["dataNascimento"], format="%d/%m/%Y", dayfirst=True)).dt.days // 365
        
        # Definir faixas etárias
        deputados_unicos.loc[:, "faixa_etaria"] = pd.cut(deputados_unicos["idade"], bins=bins, labels=labels, right=False)
        
        return lista_deputados, deputados_unicos
    except Exception as e:
        logging.error(f"Erro ao carregar dados dos deputados: {e}")
        st.error("Erro ao carregar dados dos deputados. Por favor, tente novamente mais tarde.")
        return pd.DataFrame(), pd.DataFrame()

# Carregar dados
lista_deputados, deputados_unicos = carregar_dados_deputados()

# Verificar se os dados foram carregados corretamente
if deputados_unicos.empty:
    st.stop()

### Funções que constroem graficos
def get_pie_genero():
    """Gera gráfico de pizza para distribuição de gênero."""
    contagem = deputados_unicos["sexo"].value_counts()
    contagem.index = contagem.index.map({"M": "♂ Masculino", "F": "♀ Feminino"})
    total = contagem.sum()
    porcentagens = (contagem/total)*100

    # Configuração do plot
    fig, ax = plt.subplots(figsize=(4, 4), facecolor="none")

    # Cores e estilo
    cores = ["#5542ff", "#ff33cc"]
    wedgeprops = {"width": 0.4, "edgecolor": "white", "linewidth": 3}

    ax.pie(
        contagem,
        colors=cores,
        startangle=90,
        wedgeprops=wedgeprops,
        pctdistance=0.8
    )
    # Informações centrais
    center_text = f"Total Deputados\n{total}\n\n"
    center_text += f"♂ {porcentagens["♂ Masculino"]:.1f}% ({contagem["♂ Masculino"]})\n♀ {porcentagens["♀ Feminino"]:.1f}% ({contagem["♀ Feminino"]})" 
    ax.text(0, 0, center_text,
            ha="center", va="center",
            fontsize=9, fontweight="bold",
            linespacing=1.5)

    # Legenda automática com símbolos
    ax.legend(contagem.index,
            bbox_to_anchor=(0.9, 0.9),
            frameon=True)

    # Remover eixos
    ax.axis("equal")

    # Título integrado
    plt.title("Distribuição de Gênero", 
            fontsize=14)
    return fig

def get_faixa_etaria():
    """Gera gráfico de barras para distribuição por faixa etária."""
    contagem_idade = deputados_unicos["faixa_etaria"].value_counts().reindex(labels)
    colors = plt.cm.plasma(np.linspace(0.2, 0.8, len(labels)))

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    bars = ax2.bar(contagem_idade.index, contagem_idade.values, color=colors)
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f"{int(height)}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax2.set_title("Distribuição por Faixa Etária Detalhada", loc="left", fontsize=14, pad=15)
    ax2.set_xlabel("Faixa Etária", labelpad=10)
    ax2.set_ylabel("Número de Deputados", labelpad=10)
    ax2.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")

    return fig2

def get_escolaridade():
    """Gera gráfico de barras horizontais para distribuição por escolaridade."""
    contagem_escolaridade = deputados_unicos["escolaridade"].value_counts().sort_values(ascending=True)
    cores = plt.cm.Blues(np.linspace(0.3, 0.9, len(contagem_escolaridade)))
    fig, ax = plt.subplots(figsize=(8, 6))
    barras = ax.barh(contagem_escolaridade.index, contagem_escolaridade.values, color=cores)
    for bar in barras:
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                f"{int(width)}",
                va="center", ha="left",
                fontsize=9, fontweight="bold")
        
    ax.set_title("Distribuição por Nível de Escolaridade", fontsize=18, pad=15)
    ax.set_xlabel("Número de Deputados", fontsize=14)
    ax.grid(axis="x", alpha=0.2)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
        
    plt.tight_layout()
    return fig

### Metricas quantitativas - 1 linhas do dash
qtd_deputados = deputados_unicos["id"].nunique()
qtd_partidos = lista_deputados["siglaPartido"].nunique()

deputados_ativos = deputados_unicos.loc[deputados_unicos["situacao"] == "Exercício"]

metricaQtdDeputados, metricaAtivos, metricaQtdPartidos = st.columns(3)
metricaQtdDeputados.metric("Quantidade de deputados", qtd_deputados, border=True)
metricaAtivos.metric("Quantidade de deputados ativos", len(deputados_ativos), border=True, help="Deputados que foram reeleitos e estão em exercício em 2025")
metricaQtdPartidos.metric("Quantidade de partidos", qtd_partidos, border=True)

### Graficos da 2 linha do dash
qtdGenero, qtdFaixaEtaria, qtfGrauEscolaridade = st.columns(3)

# Genero
graficoGenero = get_pie_genero()
qtdGenero.pyplot(graficoGenero, clear_figure=True, use_container_width=True)
graficoFaixaEtaria = get_faixa_etaria()
qtdFaixaEtaria.pyplot(graficoFaixaEtaria, clear_figure=True, use_container_width=True)

graficoEscolaridade = get_escolaridade()
qtfGrauEscolaridade.pyplot(graficoEscolaridade, clear_figure=True, use_container_width=True)

### Tabela de deputados 3 linha do dash
@st.cache_data
def preparar_tabela_deputados(lista_deputados, hoje):
    """Prepara a tabela de deputados para exibição."""
    # Criar uma cópia explícita para evitar SettingWithCopyWarning
    tabela_deputados = lista_deputados.copy()
    
    # Calcular idade com formato explícito
    tabela_deputados.loc[:, "idade"] = (hoje - pd.to_datetime(tabela_deputados["dataNascimento"], format="%Y-%m-%d")).dt.days // 365
    
    # Remover colunas desnecessárias
    colunas_para_remover = ["id", "Unnamed: 0", "urlFoto", "cpf", "dataNascimento", 
                           "dataFalecimento", "ufNascimento", "municipioNascimento", 
                           "escolaridade", "idade", "sexo"]
    tabela_deputados = tabela_deputados.drop(columns=[col for col in colunas_para_remover if col in tabela_deputados.columns])
    
    # Formatar data
    tabela_deputados.loc[:, "ultimoStatus"] = pd.to_datetime(tabela_deputados["ultimoStatus"], format="%Y-%m-%d").dt.strftime("%d/%m/%Y")
    tabela_deputados.loc[:, "ultimoStatus"] = tabela_deputados["ultimoStatus"].fillna("Não informado")
    
    # Renomear colunas
    tabela_deputados = tabela_deputados.rename(columns={
        "nomeCampanha": "Nome de Campanha",
        "siglaPartido": "Partido",
        "siglaUf": "UF",
        "ultimoStatus": "Última Atualização",
        "ultimoPartido": "Último Partido",
        "situacao": "Situação",
        "condicaoEleitoral": "Condição Eleitoral",
        "nomeCivil": "Nome", 
    })
    
    return tabela_deputados

hoje = datetime.now()
tabela_deputados = preparar_tabela_deputados(lista_deputados, hoje)

ordem_colunas = ["Nome", "Nome de Campanha", "UF", "Partido", "Último Partido", "Condição Eleitoral", "Escolaridade", "Situação", "Última Atualização"]
colunas_finais = [col for col in ordem_colunas if col in tabela_deputados.columns]

st.write("Deputados e sua Trajetória Partidária")
st.dataframe(tabela_deputados[colunas_finais], 
             hide_index=True, 
             use_container_width=True)

### Ver mais infos do deputado - linha 4 do dash
with st.container(border=True):
    deputado = st.selectbox("Escolha um deputado para visualizar mais sobre ele", deputados_unicos["nomeCivil"])
    
    if deputado:
        deputado_escolhido = deputados_unicos.loc[deputados_unicos["nomeCivil"] == deputado]
        
        if not deputado_escolhido.empty:
            fotoDeputado, cards = st.columns([2, 8])
            
            # Carregar foto do deputado
            url_foto = deputado_escolhido["urlFoto"].iloc[0]
            headers = {"User-Agent": "Mozilla/5.0"}
            
            try:
                response = requests.get(url_foto, headers=headers, timeout=10)
                if response.status_code == 200 and "image" in response.headers.get("Content-Type", ""):
                    foto_deputado = Image.open(BytesIO(response.content))
                    fotoDeputado.image(foto_deputado, width=170)
                else:
                    fotoDeputado.error("Não foi possível carregar a imagem do deputado")
            except Exception as e:
                logging.error(f"Erro ao carregar imagem do deputado: {e}")
                fotoDeputado.error("Erro ao carregar a imagem do deputado")
            
            with cards:
                linha1 = st.columns([4, 2, 3])
                with linha1[0]:
                    st.metric("Nome de campanha", str(deputado_escolhido["nomeCampanha"].iloc[0]), border=True)
                with linha1[1]:
                    st.metric("Idade", deputado_escolhido["idade"].iloc[0], border=True)
                with linha1[2]:
                    situacao_parlamentar = deputado_escolhido["situacao"].iloc[0]
                    situacao_final = "Não Informado" if pd.isna(situacao_parlamentar) else situacao_parlamentar
                    st.metric("Situação parlamentar", situacao_final, border=True)
            
                linha2 = st.columns([2, 2, 4])
                with linha2[0]:
                    st.metric("Data Nascimento", str(deputado_escolhido["dataNascimento"].iloc[0]), border=True)
                with linha2[1]:
                    genero_deputado = deputado_escolhido["sexo"].iloc[0]
                    genero_final = "Masculino" if genero_deputado == "M" else "Feminino" if genero_deputado == "F" else "Não Informado"
                    st.metric("Gênero", genero_final, border=True)
                with linha2[2]:
                    st.metric("Partido Atual", str(deputado_escolhido["ultimoPartido"].iloc[0]), border=True)
                    
            dadosPessoais = st.columns([2, 3, 3, 4])
            
            with dadosPessoais[0]:
                estado_deputado = deputado_escolhido["siglaUf"].iloc[0]
                st.metric("UF Nascimento", estado_deputado, border=True)
            with dadosPessoais[1]:
                municipio_deputado = deputado_escolhido["municipioNascimento"].iloc[0]
                st.metric("Município Nascimento", municipio_deputado, border=True)
            with dadosPessoais[2]:
                cpf_deputado = deputado_escolhido["cpf"].iloc[0]
                st.metric("CPF", cpf_deputado, border=True)
            with dadosPessoais[3]:
                escolaridade_deputado = deputado_escolhido["escolaridade"].iloc[0]
                st.metric("Escolaridade", escolaridade_deputado, border=True)
            
            deputado_validacao = deputado_escolhido["Sala"].iloc[0]
            verificar_gabinete = False if pd.isna(deputado_validacao) else True
            
            if verificar_gabinete:
                st.write("Dados do gabinete do deputado")
                dadosGabinete = st.columns([1, 1, 1, 2, 6])
                with dadosGabinete[0]:
                    predio_gabinete = deputado_escolhido["Prédio"].iloc[0]
                    predio_final = "-" if (pd.isna(predio_gabinete) or predio_gabinete == "x") else int(predio_gabinete)
                    st.metric("Predio", predio_final, border=True)
                with dadosGabinete[1]:
                    sala_deputado = deputado_escolhido["Sala"].iloc[0]
                    sala_final = "-" if pd.isna(sala_deputado) else int(sala_deputado) 
                    st.metric("Sala", sala_final, border=True)
                with dadosGabinete[2]:
                    andar_deputado = deputado_escolhido["Andar"].iloc[0]
                    andar_final = "-" if pd.isna(andar_deputado) else int(andar_deputado) 
                    st.metric("Andar", andar_final, border=True)
                with dadosGabinete[3]:
                    telefone_deputado = deputado_escolhido["Telefone"].iloc[0]
                    telefone_final = "-" if pd.isna(telefone_deputado) else telefone_deputado 
                    st.metric("Telefone", telefone_final, border=True)
                with dadosGabinete[4]:
                    email_deputado = deputado_escolhido["Email"].iloc[0]
                    email_final = "-" if pd.isna(email_deputado) else email_deputado 
                    st.metric("Email", email_final, border=True)

st.caption("Dados atualizados em " + pd.Timestamp.now().strftime("%d/%m/%Y"))