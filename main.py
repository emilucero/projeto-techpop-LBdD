"""
TECHPOP BI - PIPELINE PRINCIPAL
=================================
Executa todo o pipeline do projeto:
1. Verificar conexão OLTP
2. Verificar conexão DW
3. Criar tabelas do DW (se não existirem)
4. Executar ETL (Extract → Transform → Load)
5. Executar validações
6. Informar sucesso/erro
"""

import sys
import os
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Adicionar diretório raiz ao path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.database import (
    get_oltp_engine, get_dw_engine, 
    test_connection, get_postgres_admin_url
)
from sqlalchemy import text, create_engine


def create_databases():
    """Cria os bancos techpop_oltp e techpop_dw se não existirem."""
    logger.info("VERIFICANDO/CRIANDO BANCOS DE DADOS...")
    
    oltp_db = os.getenv("OLTP_DATABASE", "techpop_oltp")
    dw_db = os.getenv("DW_DATABASE", "techpop_dw")
    if oltp_db == "postgres" and dw_db == "postgres":
        logger.info("UTILIZANDO BANCO UNIFICADO 'postgres' (SUPABASE/CLOUD). PULANDO CRIAÇÃO DE BANCOS.")
        return True

    try:
        admin_engine = create_engine(get_postgres_admin_url(), isolation_level="AUTOCOMMIT")
        
        with admin_engine.connect() as conn:
            for db_name in ["techpop_oltp", "techpop_dw"]:
                result = conn.execute(
                    text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
                )
                if result.fetchone() is None:
                    conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                    logger.info(f"BANCO '{db_name}' CRIADO COM SUCESSO.")
                else:
                    logger.info(f"BANCO '{db_name}' JÁ EXISTE.")
        
        admin_engine.dispose()
        return True
    except Exception as e:
        logger.error(f"ERRO AO CRIAR BANCOS: {e}")
        return False


def execute_sql_file(conn, file_path: Path):
    """Executa um arquivo SQL tratando comentários e delimitadores."""
    sql_text = file_path.read_text(encoding="utf-8")
    clean_lines = []
    for line in sql_text.splitlines():
        line_clean = line.strip()
        if not line_clean.startswith("--"):
            clean_lines.append(line)
    clean_sql = "\n".join(clean_lines)
    for statement in clean_sql.split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(text(statement))


def setup_oltp():
    """Cria tabelas e insere dados no OLTP."""
    logger.info("CONFIGURANDO OLTP...")
    
    oltp_engine = get_oltp_engine()
    sql_dir = PROJECT_ROOT / "sql" / "oltp"
    
    try:
        with oltp_engine.begin() as conn:
            # Verificar se as tabelas já existem e têm dados
            result = conn.execute(text(
                "SELECT EXISTS ("
                "  SELECT FROM information_schema.tables "
                "  WHERE table_schema = 'public' AND table_name = 'categories'"
                ")"
            ))
            tables_exist = result.scalar()
            
            if tables_exist:
                result = conn.execute(text("SELECT COUNT(*) FROM categories"))
                count = result.scalar()
                if count > 0:
                    logger.info("OLTP JÁ CONFIGURADO. PULANDO CRIAÇÃO.")
                    return True
            
            # Executar DDL
            ddl_file = sql_dir / "01_create_oltp.sql"
            execute_sql_file(conn, ddl_file)
            logger.info("DDL DO OLTP EXECUTADO.")
            
            # Executar DML
            dml_file = sql_dir / "02_insert_oltp.sql"
            execute_sql_file(conn, dml_file)
            logger.info("DML DO OLTP EXECUTADO.")
        
        oltp_engine.dispose()
        return True
    except Exception as e:
        logger.error(f"ERRO AO CONFIGURAR OLTP: {e}")
        return False


def setup_dw():
    """Cria tabelas do DW."""
    logger.info("CONFIGURANDO DW...")
    
    dw_engine = get_dw_engine()
    sql_dir = PROJECT_ROOT / "sql" / "dw"
    
    try:
        with dw_engine.begin() as conn:
            # Executar DDL
            ddl_file = sql_dir / "01_create_dw.sql"
            execute_sql_file(conn, ddl_file)
            logger.info("DDL DO DW EXECUTADO.")
            
            # Executar índices
            idx_file = sql_dir / "02_indexes.sql"
            execute_sql_file(conn, idx_file)
            logger.info("ÍNDICES DO DW CRIADOS.")
        
        dw_engine.dispose()
        return True
    except Exception as e:
        logger.error(f"ERRO AO CONFIGURAR DW: {e}")
        return False


def run_pipeline():
    """Executa o pipeline completo."""
    logger.info("=" * 60)
    logger.info("TECHPOP BI - PIPELINE PRINCIPAL")
    logger.info("=" * 60)
    
    # 1. Criar bancos
    logger.info("")
    logger.info("PASSO 1: CRIANDO BANCOS DE DADOS...")
    if not create_databases():
        logger.error("FALHA AO CRIAR BANCOS. ABORTANDO.")
        return False
    
    # 2. Setup OLTP
    logger.info("")
    logger.info("PASSO 2: CONFIGURANDO OLTP...")
    if not setup_oltp():
        logger.error("FALHA AO CONFIGURAR OLTP. ABORTANDO.")
        return False
    
    # 3. Setup DW
    logger.info("")
    logger.info("PASSO 3: CONFIGURANDO DW...")
    if not setup_dw():
        logger.error("FALHA AO CONFIGURAR DW. ABORTANDO.")
        return False
    
    # 4. Executar ETL
    logger.info("")
    logger.info("PASSO 4: EXECUTANDO ETL...")
    from etl.main import run_etl
    if not run_etl():
        logger.error("FALHA NO ETL. ABORTANDO.")
        return False
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("PIPELINE CONCLUÍDO COM SUCESSO!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("PRÓXIMOS PASSOS:")
    logger.info("  1. GERAR GRÁFICOS: python reports/gerar_graficos.py")
    logger.info("  2. INICIAR DASHBOARD: streamlit run dashboard/app.py")
    logger.info("=" * 60)
    
    return True


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
