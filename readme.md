# Projeto Integrador II

## Descrição do Projeto

Este projeto tem como objetivo a extração e análise de dados relacionados aos deputados federais e seus gastos no ano de 2022.

O projeto está dividido em três partes principais:
1. **Extração de Dados**: Coleta e armazenamento dos dados dos deputados e seus gastos.
2. **Análise de Dados**: Processamento e geração de insights a partir dos dados coletados.
3. **Visualização de Dados**: Dashboard interativo para exploração e análise dos dados.

## Configuração do Ambiente

### Banco de Dados

O projeto suporta dois tipos de bancos de dados:
- **MySQL**: Configurável através do arquivo `.env`.
- **SQLite**: Utilizado como padrão caso o arquivo `.env` não seja configurado corretamente.

### Arquivo de Configuração (.env)

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```plaintext
DB_HOST=seu_host
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=nome_do_banco
LOGS_PATH=caminho/para/logs
```

## Instalando bibliotecas

Para instalar as dependências necessárias para rodar o projeto, siga os passos abaixo:

#### Pré-requisitos
- Python 3.x instalado.
- Gerenciador de pacotes `pip` (já vem instalado com o Python 3.4+).

#### Passo a Passo:

**Crie um ambiente virtual** (recomendado para isolar as dependências do projeto):
  ```bash
  python -m venv venv
  ```
  - **Linux/Mac**:
  ```bash
  source venv/bin/activate
  ```
  - **Windows**:
  ```bash
  venv\Scripts\activate
  ```

  ```bash
  pip install -r requirements.txt
  ```

## Executando o Projeto

### 1. Extração de Dados (ETL)
Para executar o processo de extração e carregamento dos dados:
  - **Linux/Mac**:
  ```bash
  python3 etl.py
  ```
  - **Windows**:
  ```bash
  python etl.py
  ```

### 2. Dashboard Interativo
Para acessar o dashboard de visualização:
1. Navegue até a pasta `dashboard`
2. Execute o comando:
  ```bash
  streamlit run 1_📄_Homepage.py
  ```
3. O dashboard será aberto automaticamente no seu navegador padrão

## Funcionalidades do Dashboard

O dashboard oferece as seguintes funcionalidades:
- Visualização geral dos gastos dos deputados
- Análise detalhada por deputado
- Comparativos entre diferentes períodos
- Filtros por tipo de despesa
- Exportação de dados e relatórios

## Estrutura do projeto
```
projeto-integrador-ii/
│
├── .env.example              # Exemplo de arquivo de configuração
├── requirements.txt          # Lista de dependências
├── logs/                     # Pasta de logs
├── jupyter/                  # Notebooks usados na construção dos scripts
├── dashboard/               # Aplicação Streamlit para visualização
│   ├── Pages/              # Páginas adicionais do dashboard
│   ├── get_deputados.py    # Script para obtenção de dados dos deputados
│   ├── get_despesas.py     # Script para obtenção de dados de despesas
│   └── 1_📄_Homepage.py    # Página principal do dashboard
├── etl.py                   # Script principal de extração de dados
├── relatorio_etl.md         # Documentação do processo ETL
├── relatorio_dataViz.md     # Documentação da visualização de dados
└── README.md                # Documentação do projeto
```

## Documentação Adicional

Para mais detalhes sobre cada componente do projeto, consulte:
- `relatorio_etl.md`: Documentação detalhada do processo de extração de dados
- `relatorio_dataViz.md`: Documentação das análises e visualizações implementadas