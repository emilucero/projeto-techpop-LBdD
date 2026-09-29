"""
TECHPOP BI - ETL MAIN
=======================
Orquestra o pipeline ETL: Extract → Transform → Load.
"""

import sys
import os
import logging

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_oltp_engine, get_dw_engine, test_connection
from etl.extract import extract_sales_data, extract_validation_data
from etl.transform import run_all_transforms, validate_consistency
from etl.load import load_all

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_etl():
    """Executa o pipeline ETL completo."""
    logger.info("=" * 60)
    logger.info("TECHPOP BI - PIPELINE ETL")
    logger.info("=" * 60)
    
    # 1. Verificar conexões
    logger.info("ETAPA 1: VERIFICANDO CONEXÕES...")
    oltp_engine = get_oltp_engine()
    dw_engine = get_dw_engine()
    
    if not test_connection(oltp_engine, "OLTP"):
        logger.error("NÃO FOI POSSÍVEL CONECTAR AO OLTP. ABORTANDO.")
        return False
    
    if not test_connection(dw_engine, "DW"):
        logger.error("NÃO FOI POSSÍVEL CONECTAR AO DW. ABORTANDO.")
        return False
    
    # 2. EXTRACT
    logger.info("")
    logger.info("ETAPA 2: EXTRAÇÃO (EXTRACT)...")
    df_raw = extract_sales_data(oltp_engine)
    
    if df_raw.empty:
        logger.error("NENHUM DADO EXTRAÍDO DO OLTP. ABORTANDO.")
        return False
    
    # 3. TRANSFORM
    logger.info("")
    logger.info("ETAPA 3: TRANSFORMAÇÃO (TRANSFORM)...")
    (
        df_transformed, dim_tempo, dim_cliente, dim_vendedor,
        dim_fornecedor, dim_produto, fato_data, validation
    ) = run_all_transforms(df_raw)
    
    # Exibir validação de consistência
    logger.info("")
    logger.info("RELATÓRIO DE CONSISTÊNCIA (TOTAL_PRICE VS SOMA DOS ITENS):")
    logger.info("-" * 70)
    for _, row in validation.iterrows():
        status = "✓ OK" if row["consistente"] else "✗ INCONSISTENTE"
        logger.info(
            f"  VENDA {int(row['sales_id'])}: "
            f"TOTAL_PRICE={row['total_price_oltp']:>10.2f} | "
            f"SOMA ITENS={row['total_calculado']:>10.2f} | "
            f"DIF={row['diferenca']:>10.2f} | {status}"
        )
    logger.info("-" * 70)
    
    # 4. LOAD
    logger.info("")
    logger.info("ETAPA 4: CARGA (LOAD)...")
    results = load_all(
        dw_engine,
        dim_tempo, dim_cliente, dim_vendedor,
        dim_fornecedor, dim_produto, df_transformed
    )
    
    # Resumo final
    logger.info("")
    logger.info("=" * 60)
    logger.info("RESUMO DA CARGA:")
    logger.info("=" * 60)
    logger.info(f"  DIM_TEMPO:       {results['dim_tempo']} REGISTROS")
    logger.info(f"  DIM_CLIENTE:     {results['dim_cliente']} REGISTROS")
    logger.info(f"  DIM_VENDEDOR:    {results['dim_vendedor']} REGISTROS")
    logger.info(f"  DIM_FORNECEDOR:  {results['dim_fornecedor']} REGISTROS")
    logger.info(f"  DIM_PRODUTO:     {results['dim_produto']} REGISTROS")
    logger.info(f"  FATO_VENDAS:     {results['fato_vendas']} REGISTROS")
    logger.info("=" * 60)
    logger.info("ETL CONCLUÍDO COM SUCESSO!")
    logger.info("=" * 60)
    
    return True


if __name__ == "__main__":
    success = run_etl()
    sys.exit(0 if success else 1)
