# ### Importando bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from get_deputados import carregar_lista_deputados
from get_despesas import carregar_lista_despesas

# Configuração da página
st.set_page_config(
    page_title="Despesas dos Deputados",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para formatar valores monetários
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para carregar dados
@st.cache_data(ttl=3600)
def carregando_dados():
    # # Carregar dados dos deputados
    lista_deputados = carregar_lista_deputados()
    
    # Carregar dados das despesas
    lista_despesas = carregar_lista_despesas()
    
    # Pré-processamento
    deputados_unicos = lista_deputados.drop_duplicates(subset="id", keep="last")
    
    # Converter data e extrair mês
    lista_despesas['dataDocumento'] = pd.to_datetime(lista_despesas['dataDocumento'], errors='coerce')
    meses_pt = {
        1: 'Janeiro',
        2: 'Fevereiro',
        3: 'Março',
        4: 'Abril',
        5: 'Maio',
        6: 'Junho',
        7: 'Julho',
        8: 'Agosto',
        9: 'Setembro',
        10: 'Outubro',
        11: 'Novembro',
        12: 'Dezembro'
    }
    lista_despesas['mes_nome'] = lista_despesas['mes'].map(meses_pt)
    
    # Adicionar informações de deputados às despesas
    lista_despesas = lista_despesas.merge(
        deputados_unicos[['id', 'nomeCivil', 'siglaPartido', 'siglaUf']], 
        left_on='id_deputado', 
        right_on='id', 
        how='left'
    )
    
    return deputados_unicos, lista_despesas

# Carregar dados
deputados_unicos, lista_despesas = carregando_dados()

# Título e descrição
st.title("💰 Análise de Despesas dos Deputados")
st.caption("Os registros são referentes aos deputados em exercício no ano de 2022")

# Sidebar com filtros
st.header("Filtros")

# Criar um container para os filtros
with st.container(border=True):
    # Primeiro, vamos criar os filtros básicos que não dependem de outros
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtro por partido (independente)
        partido_selecionado = st.selectbox(
            "Escolha um partido",
            options=["Todos"] + sorted(deputados_unicos["siglaPartido"].unique().tolist()),
            index=0
        )
    
    with col2:
        # Filtro por mês (independente)
        meses = ["Todos"] + ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        mes_selecionado = st.selectbox(
            "Escolha um mês", 
            options=meses,
            index=0
        )
    
    # Agora, vamos criar os filtros dependentes
    col3, col4 = st.columns(2)
    
    with col3:
        # Filtrar deputados com base no partido selecionado
        if partido_selecionado != "Todos":
            deputados_filtrados = deputados_unicos[deputados_unicos["siglaPartido"] == partido_selecionado]
            deputados_options = ["Todos"] + sorted(deputados_filtrados["nomeCivil"].unique().tolist())
        else:
            deputados_options = ["Todos"] + sorted(deputados_unicos["nomeCivil"].unique().tolist())
        
        # Filtro por deputado (depende do partido)
        deputado_selecionado = st.selectbox(
            "Escolha um deputado", 
            options=deputados_options,
            index=0
        )
    
    with col4:
        # Filtro por tipo de despesa
        tipo_despesa = st.multiselect(
            "Selecione tipo(s) de despesa",
            options=lista_despesas['tipoDespesa'].unique(),
            placeholder="Escolha uma opção"
        )
    
    # Filtro por valor
    min_valor, max_valor = st.slider(
        "Filtrar por valor (R$)",
        min_value=float(lista_despesas['valorDocumento'].min()),
        max_value=float(lista_despesas['valorDocumento'].max()),
        value=(0.0, float(lista_despesas['valorDocumento'].max()))
    )

# Aplicar filtros
despesas_filtradas = lista_despesas.copy()

# Filtro por deputado
if deputado_selecionado != "Todos":
    id_deputado = deputados_unicos.loc[deputados_unicos['nomeCivil'] == deputado_selecionado, 'id'].values[0]
    despesas_filtradas = despesas_filtradas[despesas_filtradas['id_deputado'] == id_deputado]

# Filtro por mês
if mes_selecionado != "Todos":
    mes_numero = meses.index(mes_selecionado)
    despesas_filtradas = despesas_filtradas[despesas_filtradas['mes'] == mes_numero]

# Filtro de partido
if partido_selecionado != "Todos":
    despesas_filtradas = despesas_filtradas[despesas_filtradas['siglaPartido'] == partido_selecionado]

# Filtro por tipo de despesa
if len(tipo_despesa) > 0:
    despesas_filtradas = despesas_filtradas[despesas_filtradas['tipoDespesa'].isin(tipo_despesa)]

# Filtro por valor
despesas_filtradas = despesas_filtradas[
    (despesas_filtradas['valorDocumento'] >= min_valor) & 
    (despesas_filtradas['valorDocumento'] <= max_valor)
]

# Seção de métricas
st.header("📊 Métricas Principais")
col1, col2, col3, col4 = st.columns([4, 3, 3, 3])

with col1:
    total_gasto = despesas_filtradas["valorDocumento"].sum()
    st.metric(
        "Total Gasto", 
        formatar_moeda(total_gasto), 
        delta=None, 
        help="Total das despesas conforme filtros aplicados", 
        border=True
    )

with col2:
    media_despesa = despesas_filtradas['valorDocumento'].mean()
    st.metric(
        "Média por Despesa", 
        formatar_moeda(media_despesa),
        delta=None,
        border=True
    )

with col3:
    qtd_despesas = len(despesas_filtradas)
    st.metric(
        "Total de Despesas", 
        f"{qtd_despesas:,}",
        delta=None,
        border=True
    )
with col4:
    fornecedores_unicos = despesas_filtradas['cnpjCpfFornecedor'].nunique()
    st.metric(
        "Fornecedores Distintos", 
        fornecedores_unicos,
        delta=None,
        border=True
    )
    
# Abas para diferentes visualizações
tab1, tab2, tab3, tab4 = st.tabs(["📈 Visualizações", "📋 Detalhes das Despesas", "🔍 Análises", "📊 Comparativos"])

with tab1:
    st.header("Visualizações Gráficas")
    
    # Criar abas para diferentes tipos de visualizações
    viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Gastos por Tipo", "Evolução Temporal", "Distribuição"])
    
    with viz_tab1:
        # Gráfico de barras por tipo de despesa
        despesas_por_tipo = despesas_filtradas.groupby('tipoDespesa')['valorDocumento'].sum().reset_index()
        despesas_por_tipo = despesas_por_tipo.sort_values('valorDocumento', ascending=False)
        
        fig = px.bar(
            despesas_por_tipo, 
            x='tipoDespesa', 
            y='valorDocumento',
            title='Gastos por Tipo de Despesa',
            labels={'tipoDespesa': 'Tipo de Despesa', 'valorDocumento': 'Total Gasto (R$)'},
            color='tipoDespesa',
            text=despesas_por_tipo['valorDocumento'].apply(formatar_moeda),
            hover_data={'valorDocumento': ':,.2f'}
        )
        
        fig.update_layout(
            xaxis_title="Tipo de Despesa",
            yaxis_title="Total Gasto (R$)",
            yaxis_tickformat=",.2f",
            yaxis_tickprefix="R$ ",
            showlegend=False,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Adicionar tabela com os dados
        with st.expander("Ver dados em formato de tabela"):
            st.dataframe(
                despesas_por_tipo.rename(columns={
                    'tipoDespesa': 'Tipo de Despesa',
                    'valorDocumento': 'Total Gasto (R$)'
                }).style.format({'Total Gasto (R$)': lambda x: formatar_moeda(x)}),
                use_container_width=True
            )
    
    with viz_tab2:
        # Evolução temporal dos gastos
        if len(despesas_filtradas) > 0:
            # Agrupar por mês
            gastos_por_mes = despesas_filtradas.groupby(['mes', 'mes_nome'])['valorDocumento'].sum().reset_index()
            gastos_por_mes = gastos_por_mes.sort_values('mes')
            
            # Calcular média mensal
            media_mensal = gastos_por_mes['valorDocumento'].mean()
            
            fig = go.Figure()
            
            # Adicionar barras para gastos mensais
            fig.add_trace(go.Bar(
                x=gastos_por_mes['mes_nome'],
                y=gastos_por_mes['valorDocumento'],
                name='Gastos Mensais',
                text=gastos_por_mes['valorDocumento'].apply(formatar_moeda),
                textposition='auto',
                marker_color='#3498db'
            ))
            
            # Adicionar linha para média
            fig.add_trace(go.Scatter(
                x=gastos_por_mes['mes_nome'],
                y=[media_mensal] * len(gastos_por_mes),
                name='Média Mensal',
                line=dict(color='red', dash='dash'),
                text=[formatar_moeda(media_mensal)] * len(gastos_por_mes),
                mode='lines+text',
                textposition='top center'
            ))
            
            fig.update_layout(
                title='Evolução Mensal dos Gastos',
                xaxis_title="Mês",
                yaxis_title="Total Gasto (R$)",
                yaxis_tickformat=",.2f",
                yaxis_tickprefix="R$ ",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Adicionar tabela com os dados
            with st.expander("Ver dados em formato de tabela"):
                st.dataframe(
                    gastos_por_mes.rename(columns={
                        'mes_nome': 'Mês',
                        'valorDocumento': 'Total Gasto (R$)'
                    }).style.format({'Total Gasto (R$)': lambda x: formatar_moeda(x)}),
                    use_container_width=True
                )
        else:
            st.info("Não há dados suficientes para mostrar a evolução temporal.")
    
    with viz_tab3:
        # Distribuição dos gastos
        if len(despesas_filtradas) > 0:
            # Gráfico de pizza com distribuição por tipo
            fig = px.pie(
                despesas_por_tipo,
                names='tipoDespesa',
                values='valorDocumento',
                title='Distribuição por Tipo de Despesa',
                hole=0.4
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=500)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Distribuição por partido (se não estiver filtrado por partido)
            if partido_selecionado == "Todos":
                gastos_por_partido = despesas_filtradas.groupby('siglaPartido')['valorDocumento'].sum().reset_index()
                gastos_por_partido = gastos_por_partido.sort_values('valorDocumento', ascending=False)
                
                fig = px.pie(
                    gastos_por_partido,
                    names='siglaPartido',
                    values='valorDocumento',
                    title='Distribuição por Partido',
                    hole=0.4
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=500)
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados suficientes para mostrar a distribuição.")

with tab2:
    st.header("Detalhes das Despesas")

    # Renomear colunas para exibição
    nomes_colunas = {
        'dataDocumento': 'Data',
        'tipoDespesa': 'Tipo de Despesa',
        'nomeFornecedor': 'Fornecedor',
        'cnpjCpfFornecedor': 'CNPJ/CPF',
        'valorDocumento': 'Valor (R$)',
        'urlDocumento': 'Comprovante',
        'nomeCivil': 'Deputado',
        'siglaPartido': 'Partido',
        'siglaUf': 'UF'
    }


    # Exibir tabela
    st.dataframe(
        despesas_filtradas,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Data": st.column_config.DateColumn(
                "Data",
                help="Data do documento",
                format="DD/MM/YYYY"
            ),
            "Valor (R$)": st.column_config.TextColumn(
                "Valor (R$)",
                help="Valor da despesa"
            ),
            "Comprovante": st.column_config.TextColumn(
                "Comprovante",
                help="Link para o comprovante da despesa"
            )
        }
    )
    
    # Adicionar botão para download
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    
    csv = convert_df_to_csv(despesas_filtradas)
    st.download_button(
        "📥 Baixar dados (CSV)",
        data=csv,
        file_name='despesas.csv',
        mime='text/csv'
    )


with tab3:
    st.header("Análises Detalhadas")
    
    # Criar abas para diferentes tipos de análises
    analise_tab1, analise_tab2, analise_tab3 = st.tabs(["Fornecedores", "Deputados", "Temporal"])
    
    with analise_tab1:
        st.subheader("Análise de Fornecedores")

        # Calcular top fornecedores
        top_fornecedores = (despesas_filtradas.groupby(['nomeFornecedor', 'cnpjCpfFornecedor'])
                        ['valorDocumento']
                        .sum()
                        .reset_index()
                        .sort_values('valorDocumento', ascending=False))

        # Limitar a top 20 para melhor visualização
        top_fornecedores = top_fornecedores.head(20)

        # Salvar uma cópia formatada só para exibição no texto do gráfico
        top_fornecedores['valorDocumentoFormatado'] = top_fornecedores['valorDocumento'].apply(formatar_moeda)

        # Renomear colunas
        top_fornecedores = top_fornecedores.rename(columns={
            'nomeFornecedor': 'Fornecedor',
            'cnpjCpfFornecedor': 'CNPJ/CPF',
            'valorDocumento': 'Total Gasto (R$)'
        })

        # Exibir tabela
        st.dataframe(
            top_fornecedores[['Fornecedor', 'CNPJ/CPF', 'Total Gasto (R$)']].assign(
                **{'Total Gasto (R$)': top_fornecedores['Total Gasto (R$)'].apply(formatar_moeda)}
            ),
            hide_index=True,
            use_container_width=True
        )

        # Gráfico de barras para top fornecedores
        fig = px.bar(
            top_fornecedores,
            x='Fornecedor',
            y='Total Gasto (R$)',
            title='Top 20 Fornecedores por Valor Total',
            text='valorDocumentoFormatado',
            color='Fornecedor'
        )

        fig.update_layout(
            xaxis_tickangle=45,
            showlegend=False,
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)
        
        # Análise de fornecedores por tipo de despesa
        st.subheader("Fornecedores por Tipo de Despesa")
        
        # Selecionar tipo de despesa para análise
        tipo_para_analise = st.selectbox(
            "Selecione um tipo de despesa para análise detalhada",
            options=despesas_filtradas['tipoDespesa'].unique(),
            index=0
        )
        
        # Filtrar despesas pelo tipo selecionado
        despesas_tipo = despesas_filtradas[despesas_filtradas['tipoDespesa'] == tipo_para_analise]
        
        # Calcular top fornecedores para o tipo selecionado
        top_fornecedores_tipo = (despesas_tipo.groupby(['nomeFornecedor', 'cnpjCpfFornecedor'])
                                ['valorDocumento']
                                .sum()
                                .reset_index()
                                .sort_values('valorDocumento', ascending=False)
                                .head(10))
        
        # Formatar valores
        top_fornecedores_tipo['valorDocumento'] = top_fornecedores_tipo['valorDocumento'].apply(formatar_moeda)
        
        # Renomear colunas
        top_fornecedores_tipo = top_fornecedores_tipo.rename(columns={
            'nomeFornecedor': 'Fornecedor',
            'cnpjCpfFornecedor': 'CNPJ/CPF',
            'valorDocumento': 'Total Gasto (R$)'
        })
        
        # Exibir tabela
        st.dataframe(
            top_fornecedores_tipo,
            hide_index=True,
            use_container_width=True
        )
    
    with analise_tab2:
        st.subheader("Análise de Deputados")
        
        # Só mostrar análise de deputados se não tiver deputado selecionado
        if deputado_selecionado == "Todos":
            # Calcular gastos por deputado
            gastos_por_deputado = (despesas_filtradas.groupby(['id_deputado', 'nomeCivil', 'siglaPartido'])
                                  ['valorDocumento']
                                  .sum()
                                  .reset_index()
                                  .sort_values('valorDocumento', ascending=False))
            
            # Formatar valores
            gastos_por_deputado['valorDocumento'] = gastos_por_deputado['valorDocumento'].apply(formatar_moeda)
            
            # Renomear colunas
            gastos_por_deputado = gastos_por_deputado.rename(columns={
                'nomeCivil': 'Deputado',
                'siglaPartido': 'Partido',
                'valorDocumento': 'Total Gasto (R$)'
            })
            
            # Exibir tabela
            st.dataframe(
                gastos_por_deputado,
                hide_index=True,
                use_container_width=True
            )
            
            # Gráfico de barras para top deputados
            # Ordenar os dados em ordem decrescente pelo valor total gasto
            top_deputados = gastos_por_deputado.sort_values('Total Gasto (R$)', ascending=False).head(20)
            
            fig = px.bar(
                top_deputados,
                x='Deputado',
                y='Total Gasto (R$)',
                color='Partido',
                title='Top 20 Deputados por Valor Total Gasto',
                text='Total Gasto (R$)'
            )
            
            fig.update_layout(
                xaxis_tickangle=45,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Análise por partido
            st.subheader("Análise por Partido")
            
            # Calcular gastos por partido
            gastos_por_partido = (despesas_filtradas.groupby('siglaPartido')
                                 ['valorDocumento']
                                 .sum()
                                 .reset_index()
                                 .sort_values('valorDocumento', ascending=False))
            
            # Calcular número de deputados por partido
            deputados_por_partido = deputados_unicos.groupby('siglaPartido').size().reset_index(name='num_deputados')
            
            # Juntar os dados
            analise_partido = gastos_por_partido.merge(deputados_por_partido, on='siglaPartido')
            
            # Calcular gasto médio por deputado
            analise_partido['gasto_medio_por_deputado'] = analise_partido['valorDocumento'] / analise_partido['num_deputados']
            
            # Formatar valores
            analise_partido['valorDocumento'] = analise_partido['valorDocumento'].apply(formatar_moeda)
            analise_partido['gasto_medio_por_deputado'] = analise_partido['gasto_medio_por_deputado'].apply(formatar_moeda)
            
            # Renomear colunas
            analise_partido = analise_partido.rename(columns={
                'siglaPartido': 'Partido',
                'valorDocumento': 'Total Gasto (R$)',
                'num_deputados': 'Número de Deputados',
                'gasto_medio_por_deputado': 'Gasto Médio por Deputado (R$)'
            })
            
            # Exibir tabela
            st.dataframe(
                analise_partido,
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Selecione 'Todos' nos filtros para ver a análise de deputados.")
    
    with analise_tab3:
        st.subheader("Análise Temporal")
        
        # Análise de gastos por dia da semana
        despesas_filtradas['dia_semana'] = pd.to_datetime(despesas_filtradas['dataDocumento']).dt.day_name()
        
        # Mapear dias da semana para português
        dias_pt = {
            'Monday': 'Segunda',
            'Tuesday': 'Terça',
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta',
            'Friday': 'Sexta',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        
        despesas_filtradas['dia_semana_pt'] = despesas_filtradas['dia_semana'].map(dias_pt)
        
        # Ordem dos dias da semana
        ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        # Calcular gastos por dia da semana
        gastos_por_dia = (despesas_filtradas.groupby('dia_semana_pt')
                         ['valorDocumento']
                         .sum()
                         .reindex(ordem_dias)
                         .reset_index())
        
        # Gráfico de barras para gastos por dia da semana
        fig = px.bar(
            gastos_por_dia,
            x='dia_semana_pt',
            y='valorDocumento',
            title='Gastos por Dia da Semana',
            labels={'dia_semana_pt': 'Dia da Semana', 'valorDocumento': 'Total Gasto (R$)'},
            text=gastos_por_dia['valorDocumento'].apply(formatar_moeda)
        )
        
        fig.update_layout(
            xaxis_title="Dia da Semana",
            yaxis_title="Total Gasto (R$)",
            yaxis_tickformat=",.2f",
            yaxis_tickprefix="R$ ",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)


with tab4:
    st.header("Comparativos")
    
    # Comparativo de gastos por deputado vs. média
    if deputado_selecionado != "Todos":
        # Calcular média de gastos por deputado
        # Primeiro, calcular o total gasto por cada deputado
        gastos_por_deputado = lista_despesas.groupby('id_deputado')['valorDocumento'].sum().reset_index()
        # Depois, calcular a média desses totais
        media_geral = gastos_por_deputado['valorDocumento'].mean()
        
        # Calcular gastos do deputado selecionado
        gastos_deputado = despesas_filtradas[despesas_filtradas['id_deputado'] == id_deputado]['valorDocumento'].sum()
        
        # Calcular percentual em relação à média
        percentual = (gastos_deputado / media_geral) * 100
        
        # Criar gráfico de comparação
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=['Média Geral', deputado_selecionado],
            y=[media_geral, gastos_deputado],
            text=[formatar_moeda(media_geral), formatar_moeda(gastos_deputado)],
            textposition='auto',
            marker_color=['#3498db', '#e74c3c']
        ))
        
        fig.update_layout(
            title=f'Comparativo: {deputado_selecionado} vs. Média Geral',
            yaxis_title='Total Gasto (R$)',
            yaxis_tickformat=",.2f",
            yaxis_tickprefix="R$ "
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Exibir percentual
        st.metric(
            "Percentual em relação à média",
            f"{percentual:.1f}%",
            delta=f"{percentual - 100:.1f}%",
            delta_color="inverse"
        )
        
        # Comparativo por tipo de despesa
        st.subheader("Comparativo por Tipo de Despesa")
        
        # Calcular gastos por tipo para o deputado
        gastos_tipo_deputado = (despesas_filtradas[despesas_filtradas['id_deputado'] == id_deputado]
                               .groupby('tipoDespesa')['valorDocumento']
                               .sum()
                               .reset_index())
        
        # Calcular gastos por tipo para todos (média por deputado)
        # Primeiro, calcular o total por deputado e tipo
        gastos_por_deputado_tipo = (lista_despesas.groupby(['id_deputado', 'tipoDespesa'])['valorDocumento']
                                    .sum()
                                    .reset_index())
        
        # Depois, calcular a média por tipo
        gastos_tipo_geral = (gastos_por_deputado_tipo.groupby('tipoDespesa')['valorDocumento']
                            .mean()
                            .reset_index())
        
        # Criar gráfico de barras empilhadas
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=gastos_tipo_deputado['tipoDespesa'],
            y=gastos_tipo_deputado['valorDocumento'],
            name=deputado_selecionado,
            text=gastos_tipo_deputado['valorDocumento'].apply(formatar_moeda),
            textposition='auto',
            marker_color='#e74c3c'
        ))
        
        fig.add_trace(go.Bar(
            x=gastos_tipo_geral['tipoDespesa'],
            y=gastos_tipo_geral['valorDocumento'],
            name='Média Geral',
            text=gastos_tipo_geral['valorDocumento'].apply(formatar_moeda),
            textposition='auto',
            marker_color='#3498db'
        ))
        
        fig.update_layout(
            title=f'Comparativo por Tipo de Despesa: {deputado_selecionado} vs. Média Geral',
            barmode='group',
            yaxis_title='Total Gasto (R$)',
            yaxis_tickformat=",.2f",
            yaxis_tickprefix="R$ "
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Selecione um deputado específico para ver comparativos.")
        
    # Comparativo de gastos por partido
    st.subheader("Comparativo por Partido")
    
    # Calcular média de gastos por deputado por partido
    media_partido = (lista_despesas.groupby(['siglaPartido', 'id_deputado'])['valorDocumento']
                     .sum()
                     .reset_index()
                     .groupby('siglaPartido')['valorDocumento']
                     .mean()
                     .reset_index()
                     .sort_values('valorDocumento', ascending=False))
    
    # Criar gráfico de barras
    fig = px.bar(
        media_partido,
        x='siglaPartido',
        y='valorDocumento',
        title='Média de Gastos por Deputado por Partido',
        labels={'siglaPartido': 'Partido', 'valorDocumento': 'Média de Gastos (R$)'},
        color='siglaPartido'
    )
    
    fig.update_layout(
        xaxis_title="Partido",
        yaxis_title="Média de Gastos por Deputado (R$)",
        yaxis_tickformat=",.2f",
        yaxis_tickprefix="R$ "
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Adicionar gráfico de proporcionalidade de gastos por partido
    st.subheader("Proporcionalidade de Gastos por Partido")
    
    # Calcular total de gastos por partido
    gastos_por_partido = (lista_despesas.groupby('siglaPartido')['valorDocumento']
                          .sum()
                          .reset_index()
                          .sort_values('valorDocumento', ascending=False))
    
    # Calcular número de deputados por partido
    deputados_por_partido = deputados_unicos.groupby('siglaPartido').size().reset_index(name='num_deputados')
    
    # Juntar os dados
    proporcionalidade = gastos_por_partido.merge(deputados_por_partido, on='siglaPartido')
    
    # Calcular gasto médio por deputado
    proporcionalidade['gasto_medio_por_deputado'] = proporcionalidade['valorDocumento'] / proporcionalidade['num_deputados']
    
    # Criar gráfico de barras para proporcionalidade
    fig = px.bar(
        proporcionalidade,
        x='siglaPartido',
        y='gasto_medio_por_deputado',
        title='Gasto Médio por Deputado por Partido',
        labels={'siglaPartido': 'Partido', 'gasto_medio_por_deputado': 'Gasto Médio por Deputado (R$)'},
        color='siglaPartido',
        text=proporcionalidade['num_deputados'].apply(lambda x: f"{x} deputados")
    )
    
    fig.update_layout(
        xaxis_title="Partido",
        yaxis_title="Gasto Médio por Deputado (R$)",
        yaxis_tickformat=",.2f",
        yaxis_tickprefix="R$ "
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Adicionar gráfico de comparação entre gasto total e gasto médio por deputado
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=proporcionalidade['siglaPartido'],
        y=proporcionalidade['valorDocumento'],
        name='Gasto Total',
        text=proporcionalidade['valorDocumento'].apply(formatar_moeda),
        textposition='auto',
        marker_color='#3498db'
    ))
    
    fig.add_trace(go.Bar(
        x=proporcionalidade['siglaPartido'],
        y=proporcionalidade['gasto_medio_por_deputado'],
        name='Gasto Médio por Deputado',
        text=proporcionalidade['gasto_medio_por_deputado'].apply(formatar_moeda),
        textposition='auto',
        marker_color='#e74c3c'
    ))
    
    fig.update_layout(
        title='Comparação: Gasto Total vs. Gasto Médio por Deputado por Partido',
        xaxis_title="Partido",
        yaxis_title="Valor (R$)",
        yaxis_tickformat=",.2f",
        yaxis_tickprefix="R$ ",
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparativo de gastos por mês
    st.subheader("Comparativo Mensal")
    
    # Calcular gastos por mês
    gastos_mes = (despesas_filtradas.groupby(['mes', 'mes_nome'])['valorDocumento']
                  .sum()
                  .reset_index()
                  .sort_values('mes'))
    
    # Calcular média mensal
    media_mensal = gastos_mes['valorDocumento'].mean()
    
    # Adicionar linha de média
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=gastos_mes['mes_nome'],
        y=gastos_mes['valorDocumento'],
        name='Gastos Mensais',
        text=gastos_mes['valorDocumento'].apply(formatar_moeda),
        textposition='auto',
        marker_color='#3498db'
    ))
    
    fig.add_trace(go.Scatter(
        x=gastos_mes['mes_nome'],
        y=[media_mensal] * len(gastos_mes),
        name='Média Mensal',
        line=dict(color='red', dash='dash'),
        text=[formatar_moeda(media_mensal)] * len(gastos_mes),
        mode='lines+text',
        textposition='top center'
    ))
    
    fig.update_layout(
        title='Comparativo de Gastos Mensais vs. Média',
        xaxis_title="Mês",
        yaxis_title="Total Gasto (R$)",
        yaxis_tickformat=",.2f",
        yaxis_tickprefix="R$ "
    )
    
    st.plotly_chart(fig, use_container_width=True)
        
    