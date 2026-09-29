-- =============================================
-- TECHPOP - DATA WAREHOUSE
-- ÍNDICES PARA CONSULTAS ANALÍTICAS
-- =============================================

-- Índices na FATO_VENDAS para acelerar consultas analíticas
CREATE INDEX IF NOT EXISTS idx_fato_vendas_sk_tempo ON fato_vendas(sk_tempo);
CREATE INDEX IF NOT EXISTS idx_fato_vendas_sk_cliente ON fato_vendas(sk_cliente);
CREATE INDEX IF NOT EXISTS idx_fato_vendas_sk_vendedor ON fato_vendas(sk_vendedor);
CREATE INDEX IF NOT EXISTS idx_fato_vendas_sk_produto ON fato_vendas(sk_produto);
CREATE INDEX IF NOT EXISTS idx_fato_vendas_sk_fornecedor ON fato_vendas(sk_fornecedor);
CREATE INDEX IF NOT EXISTS idx_fato_vendas_sales_id ON fato_vendas(sales_id);

-- Índices nas dimensões para facilitar filtros
CREATE INDEX IF NOT EXISTS idx_dim_tempo_ano ON dim_tempo(ano);
CREATE INDEX IF NOT EXISTS idx_dim_tempo_trimestre ON dim_tempo(trimestre);
CREATE INDEX IF NOT EXISTS idx_dim_tempo_mes ON dim_tempo(mes);
CREATE INDEX IF NOT EXISTS idx_dim_tempo_yyyymmdd ON dim_tempo(data_yyyymmdd);
CREATE INDEX IF NOT EXISTS idx_dim_cliente_estado ON dim_cliente(estado);
CREATE INDEX IF NOT EXISTS idx_dim_cliente_region ON dim_cliente(region);
CREATE INDEX IF NOT EXISTS idx_dim_vendedor_estado ON dim_vendedor(estado);
CREATE INDEX IF NOT EXISTS idx_dim_fornecedor_estado ON dim_fornecedor(estado);
CREATE INDEX IF NOT EXISTS idx_dim_produto_categoria ON dim_produto(categoria);
