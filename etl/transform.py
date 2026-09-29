"""
TECHPOP BI - TRANSFORM (TRANSFORMAÇÃO)
========================================
Aplica todas as regras de transformação nos dados extraídos do OLTP.

Transformações implementadas:
1.  Conversão de datas
2.  Criação do campo YYYYMMDD
3.  Extração de ano
4.  Extração de trimestre
5.  Extração de mês
6.  Conversão de textos para MAIÚSCULO
7.  Criação de region
8.  Cálculo do subtotal
9.  Cálculo do valor da comissão
10. Tratamento de valores nulos
11. Validações de consistência
12. Remoção de duplicidades
13. Conversão adequada dos tipos de dados
"""

import logging
import pandas as pd
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# =============================================
# MAPEAMENTO CENTRALIZADO DE REGIÃO
# =============================================
# Os estados dos EUA são classificados em regiões
# conforme o U.S. Census Bureau.
# Este dicionário é a ÚNICA fonte de mapeamento.
# =============================================
STATE_TO_REGION: Dict[str, str] = {
    # NORTHEAST
    "CT": "NORTHEAST", "ME": "NORTHEAST", "MA": "NORTHEAST",
    "NH": "NORTHEAST", "RI": "NORTHEAST", "VT": "NORTHEAST",
    "NJ": "NORTHEAST", "NY": "NORTHEAST", "PA": "NORTHEAST",
    # MIDWEST
    "IL": "MIDWEST", "IN": "MIDWEST", "MI": "MIDWEST",
    "OH": "MIDWEST", "WI": "MIDWEST", "IA": "MIDWEST",
    "KS": "MIDWEST", "MN": "MIDWEST", "MO": "MIDWEST",
    "NE": "MIDWEST", "ND": "MIDWEST", "SD": "MIDWEST",
    # SOUTH
    "DE": "SOUTH", "FL": "SOUTH", "GA": "SOUTH",
    "MD": "SOUTH", "NC": "SOUTH", "SC": "SOUTH",
    "VA": "SOUTH", "WV": "SOUTH", "AL": "SOUTH",
    "KY": "SOUTH", "MS": "SOUTH", "TN": "SOUTH",
    "AR": "SOUTH", "LA": "SOUTH", "OK": "SOUTH",
    "TX": "SOUTH", "DC": "SOUTH",
    # WEST
    "AZ": "WEST", "CO": "WEST", "ID": "WEST",
    "MT": "WEST", "NV": "WEST", "NM": "WEST",
    "UT": "WEST", "WY": "WEST", "AK": "WEST",
    "CA": "WEST", "HI": "WEST", "OR": "WEST",
    "WA": "WEST",
}

# Mapeamento de número do mês para nome em MAIÚSCULO
MONTH_NAMES: Dict[int, str] = {
    1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO",
    4: "ABRIL", 5: "MAIO", 6: "JUNHO",
    7: "JULHO", 8: "AGOSTO", 9: "SETEMBRO",
    10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO",
}


def map_state_to_region(state: str) -> str:
    """Mapeia um estado dos EUA para sua região."""
    if pd.isna(state) or state is None:
        return "DESCONHECIDA"
    state_upper = str(state).strip().upper()
    return STATE_TO_REGION.get(state_upper, "DESCONHECIDA")


def to_upper(value) -> str:
    """Converte um valor para MAIÚSCULO com tratamento de nulos."""
    if pd.isna(value) or value is None:
        return ""
    return str(value).strip().upper()


def date_to_yyyymmdd(date_value) -> int:
    """Converte uma data para o formato inteiro YYYYMMDD."""
    if pd.isna(date_value):
        return 0
    dt = pd.to_datetime(date_value)
    return int(dt.strftime("%Y%m%d"))


def calculate_subtotal(quantity: int, price: float) -> float:
    """Calcula o subtotal: QUANTIDADE * PREÇO."""
    return round(float(quantity) * float(price), 2)


def calculate_commission(subtotal: float, commission_pct: float) -> float:
    """Calcula o valor da comissão: SUBTOTAL * COMISSÃO / 100."""
    return round(float(subtotal) * float(commission_pct) / 100.0, 2)


def transform_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma as datas e cria campos temporais."""
    logger.info("TRANSFORMANDO DATAS...")
    
    df = df.copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df["data_yyyymmdd"] = df["sale_date"].apply(date_to_yyyymmdd)
    df["ano"] = df["sale_date"].dt.year
    df["trimestre"] = df["sale_date"].dt.quarter
    df["mes"] = df["sale_date"].dt.month
    df["nome_mes"] = df["mes"].map(MONTH_NAMES)
    
    return df


def transform_texts_upper(df: pd.DataFrame) -> pd.DataFrame:
    """Converte todos os textos para MAIÚSCULO."""
    logger.info("CONVERTENDO TEXTOS PARA MAIÚSCULO...")
    
    df = df.copy()
    text_columns = [
        "customer_name", "customer_email", "customer_state",
        "seller_name", "seller_email", "seller_state",
        "supplier_name", "supplier_email", "supplier_state",
        "product_name", "category_name",
    ]
    
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(to_upper)
    
    return df


def transform_regions(df: pd.DataFrame) -> pd.DataFrame:
    """Cria o campo region para clientes, vendedores e fornecedores."""
    logger.info("CRIANDO CAMPO REGION...")
    
    df = df.copy()
    df["customer_region"] = df["customer_state"].apply(map_state_to_region)
    df["seller_region"] = df["seller_state"].apply(map_state_to_region)
    df["supplier_region"] = df["supplier_state"].apply(map_state_to_region)
    
    return df


def transform_calculations(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula subtotal e valor da comissão."""
    logger.info("CALCULANDO SUBTOTAL E COMISSÃO...")
    
    df = df.copy()
    df["subtotal"] = df.apply(
        lambda row: calculate_subtotal(row["quantity"], row["item_price"]),
        axis=1
    )
    df["valor_comissao"] = df.apply(
        lambda row: calculate_commission(row["subtotal"], row["tx_commission"]),
        axis=1
    )
    
    return df


def transform_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Garante os tipos de dados corretos."""
    logger.info("CONVERTENDO TIPOS DE DADOS...")
    
    df = df.copy()
    df["quantity"] = df["quantity"].astype(int)
    df["item_price"] = df["item_price"].astype(float)
    df["subtotal"] = df["subtotal"].astype(float)
    df["tx_commission"] = df["tx_commission"].astype(float)
    df["valor_comissao"] = df["valor_comissao"].astype(float)
    df["data_yyyymmdd"] = df["data_yyyymmdd"].astype(int)
    df["ano"] = df["ano"].astype(int)
    df["trimestre"] = df["trimestre"].astype(int)
    df["mes"] = df["mes"].astype(int)
    
    return df


def handle_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """Trata valores nulos."""
    logger.info("TRATANDO VALORES NULOS...")
    
    df = df.copy()
    
    # Campos texto: substituir nulos por string vazia
    text_cols = [c for c in df.columns if df[c].dtype == object]
    for col in text_cols:
        df[col] = df[col].fillna("")
    
    # Campos numéricos: substituir nulos por 0
    numeric_cols = ["quantity", "item_price", "subtotal", "tx_commission", "valor_comissao"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicidades baseadas em sales_id + item_id."""
    logger.info("VERIFICANDO DUPLICIDADES...")
    
    before = len(df)
    df = df.drop_duplicates(subset=["sales_id", "item_id"], keep="first")
    after = len(df)
    
    if before != after:
        logger.warning(f"REMOVIDAS {before - after} DUPLICIDADES.")
    else:
        logger.info("NENHUMA DUPLICIDADE ENCONTRADA.")
    
    return df


def validate_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida inconsistências entre sales.total_price e soma dos subtotais.
    Retorna DataFrame com a comparação por venda.
    """
    logger.info("VALIDANDO CONSISTÊNCIA DOS DADOS...")
    
    validation = df.groupby("sales_id").agg(
        total_price_oltp=("total_price", "first"),
        total_calculado=("subtotal", "sum")
    ).reset_index()
    
    validation["diferenca"] = (
        validation["total_price_oltp"] - validation["total_calculado"]
    ).round(2)
    validation["consistente"] = validation["diferenca"].abs() < 0.01
    
    inconsistentes = validation[~validation["consistente"]]
    if len(inconsistentes) > 0:
        logger.warning(
            f"ENCONTRADAS {len(inconsistentes)} VENDAS COM INCONSISTÊNCIA "
            f"ENTRE TOTAL_PRICE E SOMA DOS SUBTOTAIS DOS ITENS."
        )
        logger.warning(
            "O DW UTILIZA A SOMA DOS SUBTOTAIS DOS ITENS (QUANTITY * PRICE) "
            "COMO BASE PARA O FATURAMENTO ANALÍTICO."
        )
        for _, row in inconsistentes.iterrows():
            logger.warning(
                f"  VENDA {int(row['sales_id'])}: "
                f"TOTAL_PRICE={row['total_price_oltp']:.2f}, "
                f"SOMA ITENS={row['total_calculado']:.2f}, "
                f"DIFERENÇA={row['diferenca']:.2f}"
            )
    else:
        logger.info("TODOS OS TOTAIS SÃO CONSISTENTES.")
    
    return validation


def build_dim_tempo(df: pd.DataFrame) -> pd.DataFrame:
    """Constrói a dimensão tempo a partir das datas encontradas."""
    logger.info("CONSTRUINDO DIM_TEMPO...")
    
    dates = df[["sale_date"]].drop_duplicates().copy()
    dates["data_completa"] = pd.to_datetime(dates["sale_date"]).dt.date
    dates["data_yyyymmdd"] = dates["sale_date"].apply(date_to_yyyymmdd)
    dates["ano"] = pd.to_datetime(dates["sale_date"]).dt.year.astype(int)
    dates["trimestre"] = pd.to_datetime(dates["sale_date"]).dt.quarter.astype(int)
    dates["mes"] = pd.to_datetime(dates["sale_date"]).dt.month.astype(int)
    dates["nome_mes"] = dates["mes"].map(MONTH_NAMES)
    
    dim_tempo = dates[["data_completa", "data_yyyymmdd", "ano", "trimestre", "mes", "nome_mes"]]
    dim_tempo = dim_tempo.drop_duplicates().reset_index(drop=True)
    
    logger.info(f"DIM_TEMPO: {len(dim_tempo)} REGISTROS.")
    return dim_tempo


def build_dim_cliente(df: pd.DataFrame) -> pd.DataFrame:
    """Constrói a dimensão cliente."""
    logger.info("CONSTRUINDO DIM_CLIENTE...")
    
    dim_cliente = df[[
        "customer_id", "customer_name", "customer_email",
        "customer_state", "customer_region"
    ]].drop_duplicates(subset=["customer_id"]).copy()
    
    dim_cliente.columns = ["customer_id", "nome", "email", "estado", "region"]
    dim_cliente = dim_cliente.reset_index(drop=True)
    
    logger.info(f"DIM_CLIENTE: {len(dim_cliente)} REGISTROS.")
    return dim_cliente


def build_dim_vendedor(df: pd.DataFrame) -> pd.DataFrame:
    """Constrói a dimensão vendedor."""
    logger.info("CONSTRUINDO DIM_VENDEDOR...")
    
    dim_vendedor = df[[
        "seller_id", "seller_name", "seller_email",
        "seller_state", "seller_region", "tx_commission"
    ]].drop_duplicates(subset=["seller_id"]).copy()
    
    dim_vendedor.columns = [
        "seller_id", "nome", "email", "estado", "region", "comissao_percentual"
    ]
    dim_vendedor = dim_vendedor.reset_index(drop=True)
    
    logger.info(f"DIM_VENDEDOR: {len(dim_vendedor)} REGISTROS.")
    return dim_vendedor


def build_dim_fornecedor(df: pd.DataFrame) -> pd.DataFrame:
    """Constrói a dimensão fornecedor."""
    logger.info("CONSTRUINDO DIM_FORNECEDOR...")
    
    dim_fornecedor = df[[
        "supplier_id", "supplier_name", "supplier_email",
        "supplier_state", "supplier_region"
    ]].drop_duplicates(subset=["supplier_id"]).copy()
    
    dim_fornecedor.columns = ["supplier_id", "nome", "email", "estado", "region"]
    dim_fornecedor = dim_fornecedor.reset_index(drop=True)
    
    logger.info(f"DIM_FORNECEDOR: {len(dim_fornecedor)} REGISTROS.")
    return dim_fornecedor


def build_dim_produto(df: pd.DataFrame) -> pd.DataFrame:
    """Constrói a dimensão produto (com categoria incorporada)."""
    logger.info("CONSTRUINDO DIM_PRODUTO...")
    
    dim_produto = df[[
        "product_id", "product_name", "category_name", "product_price"
    ]].drop_duplicates(subset=["product_id"]).copy()
    
    dim_produto.columns = ["product_id", "nome_produto", "categoria", "preco_cadastro"]
    dim_produto = dim_produto.reset_index(drop=True)
    
    logger.info(f"DIM_PRODUTO: {len(dim_produto)} REGISTROS.")
    return dim_produto


def run_all_transforms(df: pd.DataFrame) -> Tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame,
    pd.DataFrame, pd.DataFrame, pd.DataFrame,
    pd.DataFrame, pd.DataFrame
]:
    """
    Executa todas as transformações e retorna as dimensões e fato.
    
    Retorna:
        (df_transformado, dim_tempo, dim_cliente, dim_vendedor,
         dim_fornecedor, dim_produto, fato_data, validation)
    """
    logger.info("=" * 60)
    logger.info("INICIANDO TRANSFORMAÇÕES...")
    logger.info("=" * 60)
    
    # 1. Transformar datas
    df = transform_dates(df)
    
    # 2. Converter textos para maiúsculo
    df = transform_texts_upper(df)
    
    # 3. Criar regions
    df = transform_regions(df)
    
    # 4. Calcular subtotal e comissão
    df = transform_calculations(df)
    
    # 5. Tratar nulos
    df = handle_nulls(df)
    
    # 6. Converter tipos
    df = transform_data_types(df)
    
    # 7. Remover duplicidades
    df = remove_duplicates(df)
    
    # 8. Validar consistência
    validation = validate_consistency(df)
    
    # 9. Construir dimensões
    dim_tempo = build_dim_tempo(df)
    dim_cliente = build_dim_cliente(df)
    dim_vendedor = build_dim_vendedor(df)
    dim_fornecedor = build_dim_fornecedor(df)
    dim_produto = build_dim_produto(df)
    
    logger.info("=" * 60)
    logger.info("TRANSFORMAÇÕES CONCLUÍDAS COM SUCESSO.")
    logger.info("=" * 60)
    
    return (df, dim_tempo, dim_cliente, dim_vendedor,
            dim_fornecedor, dim_produto, df, validation)
