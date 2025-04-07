import pandas as pd
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging

# Carregar variáveis de ambiente do .env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

def carregar_lista_despesas():
    # Conectando no banco de dados
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
        except Exception as e:
            logging.error(f"Erro ao conectar ao MySQL: {e}")
            raise

    except ValueError as e:
        # Conexão SQLite
        try:
            engine = create_engine("sqlite://../database.db")
        except Exception as e:
            logging.error(f"Erro ao conectar ao SQLite: {e}")
            raise

    # Importando dados
    lista_despesas = pd.read_sql("SELECT * FROM deputados_despesas", engine)
    return lista_despesas