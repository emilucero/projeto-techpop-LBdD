"""
TECHPOP BI - CONSULTAS DO DASHBOARD
=====================================
Consultas SQL parametrizadas para o dashboard Streamlit.
Todas retornam DataFrames do Pandas.
"""

import pandas as pd
from sqlalchemy import text


def _build_time_filter(ano=None, trimestre=None, mes=None) -> str:
    """Constrói cláusula WHERE para filtros temporais."""
    conditions = []
    if ano and ano != "TODOS":
        conditions.append(f"t.ano = {ano}")
    if trimestre and trimestre != "TODOS":
        conditions.append(f"t.trimestre = {trimestre}")
    if mes and mes != "TODOS":
        conditions.append(f"t.mes = {mes}")
    
    if conditions:
        return "WHERE " + " AND ".join(conditions)
    return ""


def get_kpis(engine, ano=None, trimestre=None, mes=None) -> dict:
    """Retorna KPIs principais."""
    where = _build_time_filter(ano, trimestre, mes)
    
    query = text(f"""
        SELECT 
            COALESCE(SUM(f.subtotal), 0) AS faturamento_total,
            COALESCE(SUM(f.quantidade), 0) AS qtd_itens_vendidos,
            COUNT(DISTINCT f.sk_produto) AS qtd_produtos,
            COALESCE(SUM(f.valor_comissao), 0) AS comissoes_pagas
        FROM fato_vendas f
        JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
        {where}
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query)
        row = result.fetchone()
    
    return {
        "faturamento_total": float(row[0]),
        "qtd_itens_vendidos": int(row[1]),
        "qtd_produtos": int(row[2]),
        "comissoes_pagas": float(row[3]),
    }


def get_produtos_mais_vendidos(engine, ano=None, trimestre=None, mes=None) -> pd.DataFrame:
    """Retorna produtos mais vendidos por quantidade."""
    where = _build_time_filter(ano, trimestre, mes)
    
    query = text(f"""
        SELECT 
            p.nome_produto AS "PRODUTO",
            SUM(f.quantidade) AS "QUANTIDADE"
        FROM fato_vendas f
        JOIN dim_produto p ON f.sk_produto = p.sk_produto
        JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
        {where}
        GROUP BY p.nome_produto
        ORDER BY SUM(f.quantidade) DESC
    """)
    
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_faturamento_temporal(engine, granularidade="ANO", ano=None, trimestre=None, mes=None) -> pd.DataFrame:
    """Retorna faturamento por período (ano, trimestre ou mês)."""
    where = _build_time_filter(ano, trimestre, mes)
    
    if granularidade == "MÊS":
        group_cols = "t.ano, t.mes, t.nome_mes"
        select_cols = "t.ano || '-' || LPAD(t.mes::text, 2, '0') AS \"PERÍODO\", t.nome_mes AS \"MÊS\""
        order_cols = "t.ano, t.mes"
    elif granularidade == "TRIMESTRE":
        group_cols = "t.ano, t.trimestre"
        select_cols = "t.ano || '-T' || t.trimestre AS \"PERÍODO\""
        order_cols = "t.ano, t.trimestre"
    else:
        group_cols = "t.ano"
        select_cols = "t.ano::text AS \"PERÍODO\""
        order_cols = "t.ano"
    
    query = text(f"""
        SELECT 
            {select_cols},
            SUM(f.subtotal) AS "FATURAMENTO"
        FROM fato_vendas f
        JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
        {where}
        GROUP BY {group_cols}
        ORDER BY {order_cols}
    """)
    
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_faturamento_categoria(engine, ano=None, trimestre=None, mes=None) -> pd.DataFrame:
    """Retorna faturamento por categoria."""
    where = _build_time_filter(ano, trimestre, mes)
    
    query = text(f"""
        SELECT 
            p.categoria AS "CATEGORIA",
            SUM(f.subtotal) AS "FATURAMENTO"
        FROM fato_vendas f
        JOIN dim_produto p ON f.sk_produto = p.sk_produto
        JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
        {where}
        GROUP BY p.categoria
        ORDER BY SUM(f.subtotal) DESC
    """)
    
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_faturamento_produto(engine, ano=None, trimestre=None, mes=None) -> pd.DataFrame:
    """Retorna faturamento por produto."""
    where = _build_time_filter(ano, trimestre, mes)
    
    query = text(f"""
        SELECT 
            p.nome_produto AS "PRODUTO",
            p.categoria AS "CATEGORIA",
            SUM(f.subtotal) AS "FATURAMENTO"
        FROM fato_vendas f
        JOIN dim_produto p ON f.sk_produto = p.sk_produto
        JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
        {where}
        GROUP BY p.nome_produto, p.categoria
        ORDER BY SUM(f.subtotal) DESC
    """)
    
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_comissoes_vendedor(engine, ano=None, trimestre=None, mes=None) -> pd.DataFrame:
    """Retorna comissões por vendedor."""
    where = _build_time_filter(ano, trimestre, mes)
    
    query = text(f"""
        SELECT 
            v.nome AS "VENDEDOR",
            v.comissao_percentual AS "PERCENTUAL",
            SUM(f.valor_comissao) AS "TOTAL COMISSÃO"
        FROM fato_vendas f
        JOIN dim_vendedor v ON f.sk_vendedor = v.sk_vendedor
        JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
        {where}
        GROUP BY v.nome, v.comissao_percentual
        ORDER BY SUM(f.valor_comissao) DESC
    """)
    
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_fornecedores_por_estado(engine, ano=None, trimestre=None, mes=None) -> pd.DataFrame:
    """
    Retorna quantidade de fornecedores por estado.
    Considera fornecedores associados aos itens de vendas no período.
    """
    where = _build_time_filter(ano, trimestre, mes)
    
    query = text(f"""
        SELECT 
            fo.estado AS "ESTADO",
            fo.region AS "REGIÃO",
            COUNT(DISTINCT fo.supplier_id) AS "QTD FORNECEDORES"
        FROM fato_vendas f
        JOIN dim_fornecedor fo ON f.sk_fornecedor = fo.sk_fornecedor
        JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
        {where}
        GROUP BY fo.estado, fo.region
        ORDER BY COUNT(DISTINCT fo.supplier_id) DESC
    """)
    
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_clientes_por_estado(engine, ano=None, trimestre=None, mes=None) -> pd.DataFrame:
    """
    Retorna quantidade de clientes por estado.
    Considera clientes envolvidos nas vendas do período.
    """
    where = _build_time_filter(ano, trimestre, mes)
    
    query = text(f"""
        SELECT 
            c.estado AS "ESTADO",
            c.region AS "REGIÃO",
            COUNT(DISTINCT c.customer_id) AS "QTD CLIENTES"
        FROM fato_vendas f
        JOIN dim_cliente c ON f.sk_cliente = c.sk_cliente
        JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
        {where}
        GROUP BY c.estado, c.region
        ORDER BY COUNT(DISTINCT c.customer_id) DESC
    """)
    
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_filtros_tempo(engine) -> dict:
    """Retorna valores disponíveis para os filtros temporais."""
    with engine.connect() as conn:
        anos = pd.read_sql(text("SELECT DISTINCT ano FROM dim_tempo ORDER BY ano"), conn)
        trimestres = pd.read_sql(text("SELECT DISTINCT trimestre FROM dim_tempo ORDER BY trimestre"), conn)
        meses = pd.read_sql(text(
            "SELECT DISTINCT mes, nome_mes FROM dim_tempo ORDER BY mes"
        ), conn)
    
    return {
        "anos": ["TODOS"] + anos["ano"].tolist(),
        "trimestres": ["TODOS"] + trimestres["trimestre"].tolist(),
        "meses": ["TODOS"] + meses["mes"].tolist(),
        "nomes_meses": {row["mes"]: row["nome_mes"] for _, row in meses.iterrows()},
    }
