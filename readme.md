# Projeto Integrador II

## Descrição do Projeto

Este projeto tem como objetivo a extração e análise de dados relacionados aos deputados federais e seus gastos no ano de 2022.

O projeto está dividido em duas partes principais:
1. **Extração de Dados**: Coleta e armazenamento dos dados dos deputados e seus gastos.
2. **Análise de Dados**: Processamento e geração de insights a partir dos dados coletados.

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
**Rode o script**:
  - **Linux/Mac**:
  ```bash
  python3 etl.py
  ```
  - **Windows**:
  ```bash
  python etl.py
  ```
## Próximos Passos
Esta é apenas a primeira fase do projeto, focada na extração e armazenamento dos dados. As próximas etapas incluirão:

**Análise Exploratória de Dados (EDA)**: Identificação de padrões e anomalias nos gastos.

**Visualização de Dados**: Criação de gráficos e dashboards interativos.

**Relatórios Automatizados**: Geração de relatórios periódicos com insights relevantes.

## Estrutura do projeto
```
projeto-integrador-ii/
│
├── .env.example              # Exemplo de arquivo de configuração
├── requirements.txt          # Lista de dependências
├── logs/                     # Pasta de logs ( se usado o padrão)
├── jupyter/                  # Notebooks usados na construição dos scripts
└── README.md                 # Documentação do projeto
```