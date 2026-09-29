"""
TECHPOP BI - LOAD (CARGA)
===========================
Carrega as dimensões e a fato no Data Warehouse (PostgreSQL).

Ordem de carga:
1. DIM_TEMPO
2. DIM_CLIENTE
3. DIM_VENDEDOR
4. DIM_FORNECEDOR
5. DIM_PRODUTO
6. FATO_VENDAS

O processo é idempotente: limpa e recarrega sem criar duplicações.
"""

import logging
import pandas as pd
from sqlalchemy import text

logger = logging.getLogger(__name__)


def truncate_dw(engine) -> None:
    """Limpa todas as tabelas do DW para recarga idempotente."""
    logger.info("LIMPANDO TABELAS DO DW PARA RECARGA...")
    
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE fato_vendas RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_tempo RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_cliente RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_vendedor RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_fornecedor RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE dim_produto RESTART IDENTITY CASCADE"))
    
    logger.info("TABELAS DO DW LIMPAS COM SUCESSO.")


def load_dim_tempo(engine, dim_tempo: pd.DataFrame) -> dict:
    """Carrega DIM_TEMPO e retorna mapeamento data -> sk_tempo."""
    logger.info("CARREGANDO DIM_TEMPO...")
    
    dim_tempo.to_sql("dim_tempo", engine, if_exists="append", index=False)
    
    # Buscar surrogate keys geradas
    with engine.connect() as conn:
        result = conn.execute(text("SELECT sk_tempo, data_completa FROM dim_tempo"))
        sk_map = {str(row[1]): row[0] for row in result}
    
    logger.info(f"DIM_TEMPO CARREGADA: {len(dim_tempo)} REGISTROS.")
    return sk_map


def load_dim_cliente(engine, dim_cliente: pd.DataFrame) -> dict:
    """Carrega DIM_CLIENTE e retorna mapeamento customer_id -> sk_cliente."""
    logger.info("CARREGANDO DIM_CLIENTE...")
    
    dim_cliente.to_sql("dim_cliente", engine, if_exists="append", index=False)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT sk_cliente, customer_id FROM dim_cliente"))
        sk_map = {row[1]: row[0] for row in result}
    
    logger.info(f"DIM_CLIENTE CARREGADA: {len(dim_cliente)} REGISTROS.")
    return sk_map


def load_dim_vendedor(engine, dim_vendedor: pd.DataFrame) -> dict:
    """Carrega DIM_VENDEDOR e retorna mapeamento seller_id -> sk_vendedor."""
    logger.info("CARREGANDO DIM_VENDEDOR...")
    
    dim_vendedor.to_sql("dim_vendedor", engine, if_exists="append", index=False)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT sk_vendedor, seller_id FROM dim_vendedor"))
        sk_map = {row[1]: row[0] for row in result}
    
    logger.info(f"DIM_VENDEDOR CARREGADA: {len(dim_vendedor)} REGISTROS.")
    return sk_map


def load_dim_fornecedor(engine, dim_fornecedor: pd.DataFrame) -> dict:
    """Carrega DIM_FORNECEDOR e retorna mapeamento supplier_id -> sk_fornecedor."""
    logger.info("CARREGANDO DIM_FORNECEDOR...")
    
    dim_fornecedor.to_sql("dim_fornecedor", engine, if_exists="append", index=False)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT sk_fornecedor, supplier_id FROM dim_fornecedor"))
        sk_map = {row[1]: row[0] for row in result}
    
    logger.info(f"DIM_FORNECEDOR CARREGADA: {len(dim_fornecedor)} REGISTROS.")
    return sk_map


def load_dim_produto(engine, dim_produto: pd.DataFrame) -> dict:
    """Carrega DIM_PRODUTO e retorna mapeamento product_id -> sk_produto."""
    logger.info("CARREGANDO DIM_PRODUTO...")
    
    dim_produto.to_sql("dim_produto", engine, if_exists="append", index=False)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT sk_produto, product_id FROM dim_produto"))
        sk_map = {row[1]: row[0] for row in result}
    
    logger.info(f"DIM_PRODUTO CARREGADA: {len(dim_produto)} REGISTROS.")
    return sk_map


def load_fato_vendas(
    engine,
    df: pd.DataFrame,
    sk_tempo: dict,
    sk_cliente: dict,
    sk_vendedor: dict,
    sk_produto: dict,
    sk_fornecedor: dict
) -> int:
    """
    Carrega FATO_VENDAS usando as surrogate keys das dimensões.
    
    Retorna a quantidade de registros carregados.
    """
    logger.info("CARREGANDO FATO_VENDAS...")
    
    fato = df.copy()
    
    # Mapear surrogate keys
    fato["sale_date_str"] = fato["sale_date"].dt.date.astype(str)
    fato["sk_tempo"] = fato["sale_date_str"].map(sk_tempo)
    fato["sk_cliente"] = fato["customer_id"].map(sk_cliente)
    fato["sk_vendedor"] = fato["seller_id"].map(sk_vendedor)
    fato["sk_produto"] = fato["product_id"].map(sk_produto)
    fato["sk_fornecedor"] = fato["supplier_id"].map(sk_fornecedor)
    
    # Verificar se todas as SKs foram mapeadas
    sk_cols = ["sk_tempo", "sk_cliente", "sk_vendedor", "sk_produto", "sk_fornecedor"]
    for col in sk_cols:
        nulls = fato[col].isna().sum()
        if nulls > 0:
            logger.error(f"ENCONTRADOS {nulls} REGISTROS SEM {col.upper()} MAPEADA!")
    
    # Selecionar colunas da fato
    fato_final = fato[[
        "sk_tempo", "sk_cliente", "sk_vendedor", "sk_produto", "sk_fornecedor",
        "sales_id", "item_id", "quantity", "item_price",
        "subtotal", "tx_commission", "valor_comissao"
    ]].copy()
    
    fato_final.columns = [
        "sk_tempo", "sk_cliente", "sk_vendedor", "sk_produto", "sk_fornecedor",
        "sales_id", "item_id", "quantidade", "preco_unitario",
        "subtotal", "comissao_percentual", "valor_comissao"
    ]
    
    # Converter SKs para inteiro
    for col in sk_cols:
        fato_final[col] = fato_final[col].astype(int)
    
    fato_final.to_sql("fato_vendas", engine, if_exists="append", index=False)
    
    count = len(fato_final)
    logger.info(f"FATO_VENDAS CARREGADA: {count} REGISTROS.")
    return count


def validate_dw(engine) -> pd.DataFrame:
    """Executa validações no DW carregado."""
    logger.info("EXECUTANDO VALIDAÇÕES NO DW...")
    
    validations = []
    
    with engine.connect() as conn:
        # Contagem de registros
        tables = {
            "DIM_TEMPO": "dim_tempo",
            "DIM_CLIENTE": "dim_cliente",
            "DIM_VENDEDOR": "dim_vendedor",
            "DIM_FORNECEDOR": "dim_fornecedor",
            "DIM_PRODUTO": "dim_produto",
            "FATO_VENDAS": "fato_vendas",
        }
        
        logger.info("-" * 50)
        logger.info("CONTAGEM DE REGISTROS:")
        logger.info("-" * 50)
        for name, table in tables.items():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            logger.info(f"  {name}: {count} REGISTROS")
            validations.append({"TABELA": name, "REGISTROS": count})
        
        # Verificar FKs órfãs
        logger.info("-" * 50)
        logger.info("VERIFICAÇÃO DE CHAVES ESTRANGEIRAS:")
        logger.info("-" * 50)
        
        fk_checks = [
            ("SK_TEMPO", "dim_tempo", "sk_tempo"),
            ("SK_CLIENTE", "dim_cliente", "sk_cliente"),
            ("SK_VENDEDOR", "dim_vendedor", "sk_vendedor"),
            ("SK_PRODUTO", "dim_produto", "sk_produto"),
            ("SK_FORNECEDOR", "dim_fornecedor", "sk_fornecedor"),
        ]
        
        for name, dim_table, sk_col in fk_checks:
            result = conn.execute(text(
                f"SELECT COUNT(*) FROM fato_vendas f "
                f"LEFT JOIN {dim_table} d ON f.{sk_col} = d.{sk_col} "
                f"WHERE d.{sk_col} IS NULL"
            ))
            orphans = result.scalar()
            status = "OK" if orphans == 0 else f"ERRO: {orphans} ÓRFÃOS"
            logger.info(f"  {name}: {status}")
        
        # Verificar duplicidades
        result = conn.execute(text(
            "SELECT COUNT(*) FROM ("
            "  SELECT sales_id, item_id FROM fato_vendas "
            "  GROUP BY sales_id, item_id HAVING COUNT(*) > 1"
            ") sub"
        ))
        dups = result.scalar()
        logger.info(f"  DUPLICIDADES: {'NENHUMA' if dups == 0 else f'{dups} ENCONTRADAS'}")
        
        # Verificar nulos
        result = conn.execute(text(
            "SELECT "
            "  COUNT(*) FILTER (WHERE subtotal IS NULL) AS nulos_subtotal, "
            "  COUNT(*) FILTER (WHERE valor_comissao IS NULL) AS nulos_comissao "
            "FROM fato_vendas"
        ))
        row = result.fetchone()
        logger.info(f"  NULOS SUBTOTAL: {row[0]}")
        logger.info(f"  NULOS COMISSÃO: {row[1]}")
    
    logger.info("-" * 50)
    logger.info("VALIDAÇÕES CONCLUÍDAS.")
    
    return pd.DataFrame(validations)


def load_all(
    engine,
    dim_tempo: pd.DataFrame,
    dim_cliente: pd.DataFrame,
    dim_vendedor: pd.DataFrame,
    dim_fornecedor: pd.DataFrame,
    dim_produto: pd.DataFrame,
    df_transformed: pd.DataFrame
) -> dict:
    """
    Executa a carga completa do DW.
    
    Retorna dicionário com contagens.
    """
    logger.info("=" * 60)
    logger.info("INICIANDO CARGA NO DATA WAREHOUSE...")
    logger.info("=" * 60)
    
    # 1. Limpar DW (idempotência)
    truncate_dw(engine)
    
    # 2. Carregar dimensões (na ordem correta)
    sk_tempo_map = load_dim_tempo(engine, dim_tempo)
    sk_cliente_map = load_dim_cliente(engine, dim_cliente)
    sk_vendedor_map = load_dim_vendedor(engine, dim_vendedor)
    sk_fornecedor_map = load_dim_fornecedor(engine, dim_fornecedor)
    sk_produto_map = load_dim_produto(engine, dim_produto)
    
    # 3. Carregar fato
    fato_count = load_fato_vendas(
        engine, df_transformed,
        sk_tempo_map, sk_cliente_map, sk_vendedor_map,
        sk_produto_map, sk_fornecedor_map
    )
    
    # 4. Validar
    validation_df = validate_dw(engine)
    
    logger.info("=" * 60)
    logger.info("CARGA NO DW CONCLUÍDA COM SUCESSO.")
    logger.info("=" * 60)
    
    return {
        "dim_tempo": len(dim_tempo),
        "dim_cliente": len(dim_cliente),
        "dim_vendedor": len(dim_vendedor),
        "dim_fornecedor": len(dim_fornecedor),
        "dim_produto": len(dim_produto),
        "fato_vendas": fato_count,
        "validation": validation_df,
    }
