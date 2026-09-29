-- =============================================
-- TECHPOP - DATA WAREHOUSE
-- SCRIPT DDL - CRIAÇÃO DO MODELO ESTRELA
-- =============================================
-- Banco: techpop_dw
-- Modelo: Star Schema (Estrela)
-- Granularidade: Um registro por item de venda
-- =============================================

-- =============================================
-- DIMENSÃO TEMPO
-- =============================================
CREATE TABLE IF NOT EXISTS dim_tempo (
    sk_tempo        SERIAL PRIMARY KEY,
    data_completa   DATE NOT NULL UNIQUE,
    data_yyyymmdd   INTEGER NOT NULL,
    ano             INTEGER NOT NULL,
    trimestre       INTEGER NOT NULL,
    mes             INTEGER NOT NULL,
    nome_mes        VARCHAR(20) NOT NULL
);

-- =============================================
-- DIMENSÃO CLIENTE
-- =============================================
CREATE TABLE IF NOT EXISTS dim_cliente (
    sk_cliente      SERIAL PRIMARY KEY,
    customer_id     INTEGER NOT NULL UNIQUE,
    nome            VARCHAR(200) NOT NULL,
    email           VARCHAR(200),
    estado          VARCHAR(10),
    region          VARCHAR(50)
);

-- =============================================
-- DIMENSÃO VENDEDOR
-- =============================================
CREATE TABLE IF NOT EXISTS dim_vendedor (
    sk_vendedor         SERIAL PRIMARY KEY,
    seller_id           INTEGER NOT NULL UNIQUE,
    nome                VARCHAR(200) NOT NULL,
    email               VARCHAR(200),
    estado              VARCHAR(10),
    region              VARCHAR(50),
    comissao_percentual NUMERIC(5,2) NOT NULL
);

-- =============================================
-- DIMENSÃO FORNECEDOR
-- =============================================
CREATE TABLE IF NOT EXISTS dim_fornecedor (
    sk_fornecedor   SERIAL PRIMARY KEY,
    supplier_id     INTEGER NOT NULL UNIQUE,
    nome            VARCHAR(200) NOT NULL,
    email           VARCHAR(200),
    estado          VARCHAR(10),
    region          VARCHAR(50)
);

-- =============================================
-- DIMENSÃO PRODUTO
-- =============================================
CREATE TABLE IF NOT EXISTS dim_produto (
    sk_produto      SERIAL PRIMARY KEY,
    product_id      INTEGER NOT NULL UNIQUE,
    nome_produto    VARCHAR(200) NOT NULL,
    categoria       VARCHAR(200) NOT NULL,
    preco_cadastro  NUMERIC(12,2)
);

-- =============================================
-- FATO VENDAS
-- Granularidade: UM REGISTRO PARA CADA ITEM DE UMA VENDA
-- =============================================
CREATE TABLE IF NOT EXISTS fato_vendas (
    sk_venda            SERIAL PRIMARY KEY,
    sk_tempo            INTEGER NOT NULL REFERENCES dim_tempo(sk_tempo),
    sk_cliente          INTEGER NOT NULL REFERENCES dim_cliente(sk_cliente),
    sk_vendedor         INTEGER NOT NULL REFERENCES dim_vendedor(sk_vendedor),
    sk_produto          INTEGER NOT NULL REFERENCES dim_produto(sk_produto),
    sk_fornecedor       INTEGER NOT NULL REFERENCES dim_fornecedor(sk_fornecedor),
    sales_id            INTEGER NOT NULL,
    item_id             INTEGER NOT NULL,
    quantidade          INTEGER NOT NULL,
    preco_unitario      NUMERIC(12,2) NOT NULL,
    subtotal            NUMERIC(12,2) NOT NULL,
    comissao_percentual NUMERIC(5,2) NOT NULL,
    valor_comissao      NUMERIC(12,2) NOT NULL,
    CONSTRAINT fato_vendas_unique UNIQUE (sales_id, item_id)
);
