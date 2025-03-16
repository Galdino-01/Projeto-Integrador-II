import requests
import os
import pandas as pd
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging

# Carregar variáveis de ambiente do .env
load_dotenv()

# Configuração do logging
path_logs = os.getenv("PATH_LOGS", "./logs")
os.makedirs(path_logs, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"{path_logs}/logs.log"),
        logging.StreamHandler()
    ]
)

def get_env_var(name):
    value = os.getenv(name)
    
    if value is None:
        raise ValueError(f"A variável de ambiente '{name}' não está definida.")
    
    if not value.strip():
        raise ValueError(f"A variável de ambiente '{name}' está vazia.")
    
    return value

try:
    db_host = get_env_var("DB_HOST_ENV")
    db_port = get_env_var("DB_PORT_ENV")
    db_user = get_env_var("DB_USER_ENV")
    db_password = get_env_var("DB_PASS_ENV")
    db_database = get_env_var("DB_NAME_ENV")
    logging.info("Variáveis de ambiente carregadas com sucesso.")

    # Conexão MySQL
    try:
        engine = create_engine(f"mysql+pymysql://{db_user}:%s@{db_host}/{db_database}?charset=utf8mb4" % quote_plus(db_password))
        logging.info("Conexão MySQL estabelecida com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao conectar ao MySQL: {e}")
        raise

except ValueError as e:
    logging.warning(f"Variáveis de ambiente do MySQL não configuradas: {e}")
    logging.info("Criando engine SQLite local...")

    # Conexão SQLite
    try:
        engine = create_engine("sqlite:///database.db")
        logging.info("Conexão SQLite estabelecida com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao conectar ao SQLite: {e}")
        raise

# ### Extração e tratamento de dados - API ( dadosabertos.camara.leg.br )

# Função para verificar se tem uma próxima página para requisição
def verificar_proxima_pagina(data):
    for link in data['links']:
        if link['rel'] == 'next' and link['href']:
            return link['href']
    return False

# Iniciando um dataframe vazio para receber a lista de deputados
df_deputados = pd.DataFrame()

try:
    url_base = "https://dadosabertos.camara.leg.br/api/v2"

    # Buscar lista de deputados no período selecionado
    url_deputados = f"{url_base}/deputados"

    logging.info("Iniciando extração da lista de deputados")

    # Realizando a requisição com a Legislatura 56 ( referente ao periodo de deputados de 2019-02-01 a 2023-01-31 )
    response = requests.get(url_deputados, params={"idLegislatura": 56})
    
    dados_deputados = response.json()

    retorno_dados = pd.DataFrame(dados_deputados["dados"])
    df_deputados = pd.concat([df_deputados, retorno_dados], ignore_index=True)

    # Se tiver mais páginas, adicionar ela na lista de despesas
    nova_pagina = True
    while nova_pagina:
        nova_url = verificar_proxima_pagina(dados_deputados)
        if not nova_url:
            logging.info(f"Não há novas paginas")
            nova_pagina = False
            break

        logging.info(f"Nova pagina de deputados")
        response = requests.get(nova_url)
        dados_deputados = response.json()

        retorno_dados = pd.DataFrame(dados_deputados["dados"])
        df_deputados = pd.concat([df_deputados, retorno_dados], ignore_index=True)

except Exception as e:
    logging.error(f"Ocorreu um erro inesperado: {e}")
    raise

# Salvando a lista de deputados no banco de dados
if len(df_deputados) > 0:
    try:
        df_deputados.to_sql(
            name="deputados",
            con=engine,
            if_exists="replace",
            index=False
        )
        logging.info("Dados dos deputados salvos com sucesso no banco de dados.")
    except Exception as e:
        logging.error(f"Erro ao salvar os dados no banco de dados: {e}")
        raise
else:
    logging.info("Nenhum dado de deputados para salvar.")

df_deputado_final = pd.DataFrame()
df_deputados_ultimo_status_final = pd.DataFrame()
df_deputados_ultimo_gabinete_final = pd.DataFrame()

try:
    # Coletar dados detalhados de cada deputado 
    id_unicos = df_deputados["id"].drop_duplicates()

    for id in id_unicos:

        url = f"{url_base}/deputados/{id}"
        
        # Buscando dados detalhados dos deputados
        logging.info(f"Buscando dados detalhados do deputado com id: {id}")
        response = requests.get(url)

        deputado_detalhado = response.json()
        logging.info("Dados encontrados, seguindo para tratamento dos dados")
        
        # Verifica se a chave "dados" está presente na resposta
        if "dados" not in deputado_detalhado:
            raise KeyError("Item 'dados', não encontrado na resposta JSON")
        
        # Extrair dados do ultimo gabinete
        logging.info("Extraindo dados do último status de gabinete do deputado")
        df_deputados_ultimo_gabinete = deputado_detalhado["dados"]["ultimoStatus"]["gabinete"]
        df_deputados_ultimo_gabinete = pd.DataFrame([df_deputados_ultimo_gabinete])
        df_deputados_ultimo_gabinete["id_deputado"] = deputado_detalhado["dados"]["id"]
        del deputado_detalhado["dados"]["ultimoStatus"]["gabinete"]
        
        # Extrair dados do ultimo status do deputado
        logging.info("Extraindo dados do último status do deputado")
        df_deputados_ultimo_status = deputado_detalhado["dados"]["ultimoStatus"]
        df_deputados_ultimo_status = pd.DataFrame([df_deputados_ultimo_status])
        df_deputados_ultimo_status["id_deputado"] = deputado_detalhado["dados"]["id"]
        del deputado_detalhado["dados"]["ultimoStatus"]
        
        # Dados pessoais do deputado
        logging.info("Extraindo dados pessoais do deputado e excluindo dados que não serão utilizados")
        del deputado_detalhado["dados"]["redeSocial"]
        del deputado_detalhado["dados"]["urlWebsite"]
        df_deputado = pd.DataFrame([deputado_detalhado["dados"]])

        # Concatena os DataFrames temporários aos DataFrames finais
        df_deputado_final = pd.concat([df_deputado_final, df_deputado], ignore_index=True)
        df_deputados_ultimo_status_final = pd.concat([df_deputados_ultimo_status_final, df_deputados_ultimo_status], ignore_index=True)
        df_deputados_ultimo_gabinete_final = pd.concat([df_deputados_ultimo_gabinete_final, df_deputados_ultimo_gabinete], ignore_index=True)
        logging.info(f"Dados do deputado {id} processados com sucesso")

        logging.info("Dados inseridos com sucesso")
except Exception as e:
    logging.error(f"Ocorreu um erro inesperado: {e}")
    raise

try:
    logging.info("Inserindo dados no banco de dados")
    df_deputado_final.to_sql(name="deputados_detalhado", con=engine, if_exists="replace", index=False)
    df_deputados_ultimo_status_final.to_sql(name="deputados_ultimo_status", con=engine, if_exists="replace", index=False)
    df_deputados_ultimo_gabinete_final.to_sql(name="deputados_ultimo_gabinete", con=engine, if_exists="replace", index=False)
except Exception as e:
    logging.error(f"Ocorreu um erro inesperado: {e}")
    raise

df_gastos = pd.DataFrame()
lista_id = df_deputados["id"].drop_duplicates()

for id in lista_id:

    logging.info(f"Buscando despesas do deputado {id}")
    # Buscar lista de deputados no período selecionado
    url = f"{url_base}/deputados/{id}/despesas"
    periodo = 2022
    params = {"ano": periodo, "ordem": "ASC", "ordenarPor": "ano", "idLegislatura": 56}
    response = requests.get(url, params=params)
    dados_despesas = response.json()
    
    if len(dados_despesas["dados"]) == 0:
        logging.info(f"Não há dados para o deputado {id}")

    try:

        df_despesas = pd.DataFrame(dados_despesas["dados"])
        df_despesas["id_deputado"] = id

        # Se tiver mais páginas, adicionar ela na lista de despesas
        nova_pagina = True
        while nova_pagina:
            nova_url = verificar_proxima_pagina(dados_despesas)
            if not nova_url:
                logging.info(f"Não há novas paginas para o deputado {id}")
                nova_pagina = False
                break
                
            logging.info(f"Nova pagina para o deputado {id}")
            response = requests.get(nova_url)
            dados_despesas = response.json()

            nova_despesas = pd.DataFrame(dados_despesas["dados"])
            nova_despesas["id_deputado"] = id
            df_despesas = pd.concat([df_despesas, nova_despesas], ignore_index=True)

        # Juntar todos os dados em 1 dataframe unico
        df_gastos = pd.concat([df_gastos, df_despesas], ignore_index=True)
        logging.info(f"Despesas do deputado {id} processadas com sucesso")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}")

try:
    logging.info("Inserindo dados no banco de dados")
    df_gastos.to_sql(name="deputados_despesas", con=engine, if_exists="replace", index=False)
except Exception as e:
    logging.error(f"Ocorreu um erro inesperado: {e}")
    raise
logging.info("Despesas inseridas com sucesso")
