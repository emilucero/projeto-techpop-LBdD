-- =============================================
-- TECHPOP - DATA WAREHOUSE
-- CONSULTAS ANALÍTICAS PARA APRESENTAÇÃO
-- =============================================

-- =============================================
-- 1. PRODUTOS MAIS VENDIDOS (POR QUANTIDADE)
-- =============================================
SELECT 
    p.nome_produto AS "PRODUTO",
    p.categoria AS "CATEGORIA",
    SUM(f.quantidade) AS "QUANTIDADE VENDIDA"
FROM fato_vendas f
JOIN dim_produto p ON f.sk_produto = p.sk_produto
GROUP BY p.nome_produto, p.categoria
ORDER BY SUM(f.quantidade) DESC;

-- =============================================
-- 2. FATURAMENTO TOTAL
-- =============================================
SELECT 
    SUM(f.subtotal) AS "FATURAMENTO TOTAL"
FROM fato_vendas f;

-- =============================================
-- 3. FATURAMENTO TOTAL POR ANO
-- =============================================
SELECT 
    t.ano AS "ANO",
    SUM(f.subtotal) AS "FATURAMENTO"
FROM fato_vendas f
JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano
ORDER BY t.ano;

-- =============================================
-- 4. FATURAMENTO TOTAL POR TRIMESTRE
-- =============================================
SELECT 
    t.ano AS "ANO",
    t.trimestre AS "TRIMESTRE",
    SUM(f.subtotal) AS "FATURAMENTO"
FROM fato_vendas f
JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano, t.trimestre
ORDER BY t.ano, t.trimestre;

-- =============================================
-- 5. FATURAMENTO TOTAL POR MÊS
-- =============================================
SELECT 
    t.ano AS "ANO",
    t.mes AS "MÊS",
    t.nome_mes AS "NOME MÊS",
    SUM(f.subtotal) AS "FATURAMENTO"
FROM fato_vendas f
JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano, t.mes, t.nome_mes
ORDER BY t.ano, t.mes;

-- =============================================
-- 6. FATURAMENTO POR CATEGORIA
-- =============================================
SELECT 
    p.categoria AS "CATEGORIA",
    SUM(f.subtotal) AS "FATURAMENTO"
FROM fato_vendas f
JOIN dim_produto p ON f.sk_produto = p.sk_produto
GROUP BY p.categoria
ORDER BY SUM(f.subtotal) DESC;

-- =============================================
-- 7. FATURAMENTO POR PRODUTO
-- =============================================
SELECT 
    p.nome_produto AS "PRODUTO",
    p.categoria AS "CATEGORIA",
    SUM(f.subtotal) AS "FATURAMENTO"
FROM fato_vendas f
JOIN dim_produto p ON f.sk_produto = p.sk_produto
GROUP BY p.nome_produto, p.categoria
ORDER BY SUM(f.subtotal) DESC;

-- =============================================
-- 8. MAIORES COMISSÕES DE VENDEDORES
-- =============================================
SELECT 
    v.nome AS "VENDEDOR",
    v.comissao_percentual AS "% COMISSÃO",
    SUM(f.valor_comissao) AS "TOTAL COMISSÃO"
FROM fato_vendas f
JOIN dim_vendedor v ON f.sk_vendedor = v.sk_vendedor
GROUP BY v.nome, v.comissao_percentual
ORDER BY SUM(f.valor_comissao) DESC;

-- =============================================
-- 9. QUANTIDADE DE FORNECEDORES POR ESTADO
-- =============================================
-- Nota: Considera fornecedores associados a itens de venda no período
SELECT 
    fo.estado AS "ESTADO",
    fo.region AS "REGIÃO",
    COUNT(DISTINCT fo.supplier_id) AS "QTD FORNECEDORES"
FROM fato_vendas f
JOIN dim_fornecedor fo ON f.sk_fornecedor = fo.sk_fornecedor
GROUP BY fo.estado, fo.region
ORDER BY COUNT(DISTINCT fo.supplier_id) DESC;

-- =============================================
-- 10. QUANTIDADE DE CLIENTES POR ESTADO
-- =============================================
-- Nota: Considera clientes envolvidos nas vendas do período
SELECT 
    c.estado AS "ESTADO",
    c.region AS "REGIÃO",
    COUNT(DISTINCT c.customer_id) AS "QTD CLIENTES"
FROM fato_vendas f
JOIN dim_cliente c ON f.sk_cliente = c.sk_cliente
GROUP BY c.estado, c.region
ORDER BY COUNT(DISTINCT c.customer_id) DESC;

-- =============================================
-- 11. VALIDAÇÃO: CONTAGEM DE REGISTROS
-- =============================================
SELECT 'DIM_TEMPO' AS TABELA, COUNT(*) AS REGISTROS FROM dim_tempo
UNION ALL
SELECT 'DIM_CLIENTE', COUNT(*) FROM dim_cliente
UNION ALL
SELECT 'DIM_VENDEDOR', COUNT(*) FROM dim_vendedor
UNION ALL
SELECT 'DIM_FORNECEDOR', COUNT(*) FROM dim_fornecedor
UNION ALL
SELECT 'DIM_PRODUTO', COUNT(*) FROM dim_produto
UNION ALL
SELECT 'FATO_VENDAS', COUNT(*) FROM fato_vendas;

-- =============================================
-- 12. VALIDAÇÃO: REGISTROS SEM CHAVE ESTRANGEIRA
-- =============================================
SELECT 'FATO SEM DIM_TEMPO' AS VALIDACAO, COUNT(*) AS QTD
FROM fato_vendas f
LEFT JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
WHERE t.sk_tempo IS NULL
UNION ALL
SELECT 'FATO SEM DIM_CLIENTE', COUNT(*)
FROM fato_vendas f
LEFT JOIN dim_cliente c ON f.sk_cliente = c.sk_cliente
WHERE c.sk_cliente IS NULL
UNION ALL
SELECT 'FATO SEM DIM_VENDEDOR', COUNT(*)
FROM fato_vendas f
LEFT JOIN dim_vendedor v ON f.sk_vendedor = v.sk_vendedor
WHERE v.sk_vendedor IS NULL
UNION ALL
SELECT 'FATO SEM DIM_PRODUTO', COUNT(*)
FROM fato_vendas f
LEFT JOIN dim_produto p ON f.sk_produto = p.sk_produto
WHERE p.sk_produto IS NULL
UNION ALL
SELECT 'FATO SEM DIM_FORNECEDOR', COUNT(*)
FROM fato_vendas f
LEFT JOIN dim_fornecedor fo ON f.sk_fornecedor = fo.sk_fornecedor
WHERE fo.sk_fornecedor IS NULL;

-- =============================================
-- 13. VALIDAÇÃO: DUPLICIDADES NA FATO
-- =============================================
SELECT sales_id, item_id, COUNT(*) AS QTD
FROM fato_vendas
GROUP BY sales_id, item_id
HAVING COUNT(*) > 1;

-- =============================================
-- 14. VALIDAÇÃO: VALORES NULOS NA FATO
-- =============================================
SELECT 
    COUNT(*) FILTER (WHERE sk_tempo IS NULL) AS "NULOS SK_TEMPO",
    COUNT(*) FILTER (WHERE sk_cliente IS NULL) AS "NULOS SK_CLIENTE",
    COUNT(*) FILTER (WHERE sk_vendedor IS NULL) AS "NULOS SK_VENDEDOR",
    COUNT(*) FILTER (WHERE sk_produto IS NULL) AS "NULOS SK_PRODUTO",
    COUNT(*) FILTER (WHERE sk_fornecedor IS NULL) AS "NULOS SK_FORNECEDOR",
    COUNT(*) FILTER (WHERE subtotal IS NULL) AS "NULOS SUBTOTAL",
    COUNT(*) FILTER (WHERE valor_comissao IS NULL) AS "NULOS COMISSAO"
FROM fato_vendas;
