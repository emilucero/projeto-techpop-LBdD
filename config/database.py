"""
TECHPOP BI - CONFIGURAÇÃO DE BANCO DE DADOS
=============================================
Gerencia conexões com PostgreSQL (OLTP e DW)
usando variáveis de ambiente.
"""

import os
import logging
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

logger = logging.getLogger(__name__)


def get_oltp_url() -> str:
    """Retorna a URL de conexão do banco OLTP."""
    host = os.getenv("OLTP_HOST", "localhost")
    port = os.getenv("OLTP_PORT", "5432")
    database = os.getenv("OLTP_DATABASE", "techpop_oltp")
    user = os.getenv("OLTP_USER", "postgres")
    password = quote_plus(os.getenv("OLTP_PASSWORD", "postgres"))
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"


def get_dw_url() -> str:
    """Retorna a URL de conexão do Data Warehouse."""
    host = os.getenv("DW_HOST", "localhost")
    port = os.getenv("DW_PORT", "5432")
    database = os.getenv("DW_DATABASE", "techpop_dw")
    user = os.getenv("DW_USER", "postgres")
    password = quote_plus(os.getenv("DW_PASSWORD", "postgres"))
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"


def get_oltp_engine():
    """Cria e retorna engine SQLAlchemy para o OLTP."""
    return create_engine(get_oltp_url())


def get_dw_engine():
    """Cria e retorna engine SQLAlchemy para o DW."""
    return create_engine(get_dw_url())


def test_connection(engine, db_name: str) -> bool:
    """Testa a conexão com o banco de dados."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info(f"CONEXÃO COM {db_name} ESTABELECIDA COM SUCESSO.")
        return True
    except Exception as e:
        logger.error(f"ERRO AO CONECTAR COM {db_name}: {e}")
        return False


def get_postgres_admin_url() -> str:
    """Retorna URL de conexão com o banco postgres (para criar bancos)."""
    host = os.getenv("OLTP_HOST", "localhost")
    port = os.getenv("OLTP_PORT", "5432")
    user = os.getenv("OLTP_USER", "postgres")
    password = quote_plus(os.getenv("OLTP_PASSWORD", "postgres"))
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/postgres"
