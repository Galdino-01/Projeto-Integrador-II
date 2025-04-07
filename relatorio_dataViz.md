# Relatório ETL - Dados de Despesas dos Deputados

## 1. Introdução

Este relatório documenta o processo de Extração, Transformação e Carregamento (ETL) dos dados de despesas dos deputados federais. O objetivo é fornecer uma visão clara e estruturada dos dados financeiros relacionados às atividades parlamentares.

## 2. Fontes de Dados

### 2.1 Dados de Deputados
- **Fonte**: `Banco de dados - View: deputados_completo`
- **Origem**: Câmara dos Deputados
- **Campos Principais**:
  - id: Identificador único do deputado
  - nomeCivil: Nome civil do deputado
  - siglaPartido: Partido político
  - siglaUf: Estado de origem
  - situacao: Situação atual do mandato
  - ultimoStatus: Data do último status

### 2.2 Dados de Despesas
- **Fonte**: `Banco de dados - View: deputados_despesas`
- **Origem**: Portal da Transparência da Câmara dos Deputados
- **Campos Principais**:
  - id_deputado: Referência ao deputado
  - dataDocumento: Data da despesa
  - tipoDespesa: Categoria da despesa
  - valorDocumento: Valor monetário
  - nomeFornecedor: Nome do fornecedor
  - cnpjCpfFornecedor: CNPJ/CPF do fornecedor
  - urlDocumento: Link para o comprovante

## 3. Processo de ETL

### 3.1 Extração (Extract)

#### 3.1.1 Dados de Deputados
```python
# Carregamento dos dados dos deputados do banco de dados
from get_deputados import carregar_lista_deputados
deputados_df = carregar_lista_deputados()
```

#### 3.1.2 Dados de Despesas
```python
# Carregamento dos dados de despesas do banco de dados
from get_despesas import carregar_lista_despesas
despesas_df = carregar_lista_despesas()
```

### 3.2 Transformação (Transform)

#### 3.2.1 Limpeza e Padronização
- Remoção de duplicatas nos dados de deputados
- Conversão de datas para formato padrão
- Padronização de valores monetários
- Tratamento de valores nulos

#### 3.2.2 Enriquecimento de Dados
- Adição de informações de deputados às despesas
- Criação de campos derivados (mês, ano)
- Cálculo de métricas agregadas

#### 3.2.3 Código de Transformação
```python
# Pré-processamento de deputados
deputados_unicos = deputados_df.drop_duplicates(subset="id", keep="last")

# Conversão de datas e extração de mês
despesas_df['dataDocumento'] = pd.to_datetime(despesas_df['dataDocumento'], errors='coerce')
despesas_df['mes'] = despesas_df['dataDocumento'].dt.month

# Mapeamento de meses para nomes em português
meses_pt = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}
despesas_df['mes_nome'] = despesas_df['mes'].map(meses_pt)

# Adição de informações de deputados às despesas
despesas_df = despesas_df.merge(
    deputados_unicos[['id', 'nomeCivil', 'siglaPartido', 'siglaUf']], 
    left_on='id_deputado', 
    right_on='id', 
    how='left'
)
```

### 3.3 Carregamento (Load)

#### 3.3.1 Estrutura Final dos Dados
- Dados carregados em memória para análise no dashboard
- Organização por categorias de análise (deputados, despesas, métricas)
- Relacionamentos mantidos através de chaves (id_deputado)

#### 3.3.2 Métricas e Agregações
- Total de despesas por deputado
- Média de gastos por tipo de despesa
- Distribuição de gastos por partido
- Evolução temporal dos gastos
- Análise comparativa entre deputados
- Proporcionalidade de gastos por partido

## 4. Qualidade dos Dados

### 4.1 Validações
- Verificação de integridade dos dados
- Validação de valores monetários
- Checagem de relacionamentos entre tabelas
- Análise de completude dos dados

### 4.2 Tratamento de Anomalias
- Identificação de valores outliers
- Correção de inconsistências
- Padronização de formatos
- Tratamento de dados ausentes

## 5. Visualizações e Análises

### 5.1 Dashboards
- **Visão Geral das Despesas**
  - Total de gastos
  - Distribuição por tipo de despesa
  - Evolução temporal
  - Filtros interativos por deputado, partido e período

- **Análise por Deputado**
  - Detalhamento individual de gastos
  - Comparativo com média geral
  - Análise por tipo de despesa
  - Informações pessoais e de gabinete

- **Análise por Partido**
  - Total de gastos por partido
  - Média de gastos por deputado
  - Proporcionalidade de gastos
  - Comparativo entre partidos

### 5.2 Relatórios
- **Relatórios de Gastos**
  - Detalhamento por categoria
  - Análise comparativa entre deputados
  - Distribuição geográfica dos gastos
  - Tendências e padrões temporais

- **Métricas de Performance**
  - Gastos médios por deputado
  - Proporção de gastos por tipo
  - Comparativos com médias gerais
  - Indicadores de eficiência

## 6. Conclusão

O processo ETL desenvolvido permite uma análise completa e detalhada das despesas dos deputados federais, fornecendo insights valiosos sobre o uso dos recursos públicos. A estrutura modular e bem documentada facilita a manutenção e evolução do sistema. O dashboard interativo permite aos usuários explorar os dados de forma dinâmica, com filtros e visualizações que facilitam a compreensão dos padrões de gastos.

## 7. Próximos Passos

- **Melhorias no ETL**
  - Implementação de atualizações automáticas dos dados
  - Otimização das consultas ao banco de dados
  - Adição de validações adicionais na extração

- **Aprimoramentos do Dashboard**
  - Adição de mais visualizações interativas
  - Implementação de alertas para anomalias
  - Desenvolvimento de análises preditivas
  - Melhoria na performance das consultas

- **Expansão de Funcionalidades**
  - Inclusão de dados históricos de legislaturas anteriores
  - Adição de comparações entre períodos
  - Implementação de exportação de relatórios personalizados
  - Desenvolvimento de API para acesso aos dados 