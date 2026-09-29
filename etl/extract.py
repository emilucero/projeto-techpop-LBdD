"""
TECHPOP BI - EXTRACT (EXTRAÇÃO)
=================================
Extrai dados do banco OLTP (PostgreSQL) usando SQLAlchemy.
Realiza os JOINs necessários para obter todos os dados
em um único dataset para o ETL.
"""

import logging
import pandas as pd
from sqlalchemy import text

logger = logging.getLogger(__name__)


def extract_sales_data(engine) -> pd.DataFrame:
    """
    Extrai todos os dados de vendas do OLTP com JOINs entre as tabelas.
    
    Retorna um DataFrame com:
    - Dados de sales_items (item_id, sales_id, quantity, price)
    - Dados de sales (date, customer_id, seller_id, total_price)
    - Dados de customers (customer_name, email, state)
    - Dados de sellers (seller_name, email, state, tx_commission)
    - Dados de products (product_name, price, category_id, supplier_id)
    - Dados de categories (category_name)
    - Dados de suppliers (supplier_name, email, state)
    """
    query = text("""
        SELECT 
            si.item_id,
            si.sales_id,
            si.product_id,
            si.quantity,
            si.price AS item_price,
            
            s."date" AS sale_date,
            s.customer_id,
            s.seller_id,
            s.total_price,
            
            c.customer_name,
            c.email AS customer_email,
            c.state AS customer_state,
            
            se.seller_name,
            se.email AS seller_email,
            se.state AS seller_state,
            se.tx_commission,
            
            p.product_name,
            p.price AS product_price,
            p.category_id,
            p.supplier_id,
            
            cat.category_name,
            
            sup.supplier_name,
            sup.email AS supplier_email,
            sup.state AS supplier_state
            
        FROM public.sales_items si
        JOIN public.sales s ON si.sales_id = s.sales_id
        JOIN public.customers c ON s.customer_id = c.customer_id
        JOIN public.sellers se ON s.seller_id = se.seller_id
        JOIN public.products p ON si.product_id = p.product_id
        JOIN public.categories cat ON p.category_id = cat.category_id
        JOIN public.suppliers sup ON p.supplier_id = sup.supplier_id
        ORDER BY si.sales_id, si.item_id
    """)

    logger.info("EXTRAINDO DADOS DO OLTP...")
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    logger.info(f"EXTRAÇÃO CONCLUÍDA: {len(df)} REGISTROS EXTRAÍDOS.")
    return df


def extract_validation_data(engine) -> pd.DataFrame:
    """
    Extrai dados para validação de inconsistência entre
    sales.total_price e a soma real dos itens.
    """
    query = text("""
        SELECT 
            s.sales_id,
            s.total_price AS total_price_oltp,
            COALESCE(SUM(si.quantity * si.price), 0) AS total_calculado
        FROM public.sales s
        LEFT JOIN public.sales_items si ON s.sales_id = si.sales_id
        GROUP BY s.sales_id, s.total_price
        ORDER BY s.sales_id
    """)

    logger.info("EXTRAINDO DADOS PARA VALIDAÇÃO DE CONSISTÊNCIA...")
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    logger.info(f"VALIDAÇÃO EXTRAÍDA: {len(df)} VENDAS.")
    return df
