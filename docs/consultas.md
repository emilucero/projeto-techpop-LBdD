# CONSULTAS ANALÍTICAS - TECHPOP BI

## VISÃO GERAL

As consultas abaixo atendem às necessidades analíticas da alta gestão da TechPop.
Todas as consultas podem ser executadas diretamente no banco `techpop_dw`.

---

## 1. PRODUTOS MAIS VENDIDOS

```sql
SELECT 
    p.nome_produto AS "PRODUTO",
    p.categoria AS "CATEGORIA",
    SUM(f.quantidade) AS "QUANTIDADE VENDIDA"
FROM fato_vendas f
JOIN dim_produto p ON f.sk_produto = p.sk_produto
JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
-- WHERE t.ano = 2023  -- FILTRO OPCIONAL
GROUP BY p.nome_produto, p.categoria
ORDER BY SUM(f.quantidade) DESC;
```

**Métrica:** SUM(QUANTIDADE)
**Agrupamento:** PRODUTO
**Ordenação:** DECRESCENTE

---

## 2. FATURAMENTO TOTAL

```sql
SELECT SUM(f.subtotal) AS "FATURAMENTO TOTAL"
FROM fato_vendas f;
```

### POR ANO
```sql
SELECT t.ano AS "ANO", SUM(f.subtotal) AS "FATURAMENTO"
FROM fato_vendas f
JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano ORDER BY t.ano;
```

### POR TRIMESTRE
```sql
SELECT t.ano AS "ANO", t.trimestre AS "TRIMESTRE", SUM(f.subtotal) AS "FATURAMENTO"
FROM fato_vendas f
JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano, t.trimestre ORDER BY t.ano, t.trimestre;
```

### POR MÊS
```sql
SELECT t.ano AS "ANO", t.mes AS "MÊS", t.nome_mes AS "NOME MÊS", SUM(f.subtotal) AS "FATURAMENTO"
FROM fato_vendas f
JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano, t.mes, t.nome_mes ORDER BY t.ano, t.mes;
```

---

## 3. FATURAMENTO POR CATEGORIA

```sql
SELECT p.categoria AS "CATEGORIA", SUM(f.subtotal) AS "FATURAMENTO"
FROM fato_vendas f
JOIN dim_produto p ON f.sk_produto = p.sk_produto
GROUP BY p.categoria
ORDER BY SUM(f.subtotal) DESC;
```

---

## 4. FATURAMENTO POR PRODUTO

```sql
SELECT p.nome_produto AS "PRODUTO", p.categoria AS "CATEGORIA", SUM(f.subtotal) AS "FATURAMENTO"
FROM fato_vendas f
JOIN dim_produto p ON f.sk_produto = p.sk_produto
GROUP BY p.nome_produto, p.categoria
ORDER BY SUM(f.subtotal) DESC;
```

---

## 5. MAIORES COMISSÕES DE VENDEDORES

```sql
SELECT v.nome AS "VENDEDOR", v.comissao_percentual AS "% COMISSÃO", SUM(f.valor_comissao) AS "TOTAL COMISSÃO"
FROM fato_vendas f
JOIN dim_vendedor v ON f.sk_vendedor = v.sk_vendedor
GROUP BY v.nome, v.comissao_percentual
ORDER BY SUM(f.valor_comissao) DESC;
```

---

## 6. FORNECEDORES POR ESTADO

```sql
SELECT fo.estado AS "ESTADO", fo.region AS "REGIÃO", COUNT(DISTINCT fo.supplier_id) AS "QTD FORNECEDORES"
FROM fato_vendas f
JOIN dim_fornecedor fo ON f.sk_fornecedor = fo.sk_fornecedor
GROUP BY fo.estado, fo.region
ORDER BY COUNT(DISTINCT fo.supplier_id) DESC;
```

> **NOTA:** Como fornecedor não possui data de cadastro no OLTP, a dimensão temporal considera fornecedores associados aos itens de vendas dentro do período analisado.

---

## 7. CLIENTES POR ESTADO

```sql
SELECT c.estado AS "ESTADO", c.region AS "REGIÃO", COUNT(DISTINCT c.customer_id) AS "QTD CLIENTES"
FROM fato_vendas f
JOIN dim_cliente c ON f.sk_cliente = c.sk_cliente
GROUP BY c.estado, c.region
ORDER BY COUNT(DISTINCT c.customer_id) DESC;
```

> **NOTA:** Quando filtrado temporalmente, considera clientes envolvidos nas vendas do período.

---

## VALIDAÇÕES

### CONTAGEM DE REGISTROS
```sql
SELECT 'DIM_TEMPO' AS TABELA, COUNT(*) AS REGISTROS FROM dim_tempo
UNION ALL SELECT 'DIM_CLIENTE', COUNT(*) FROM dim_cliente
UNION ALL SELECT 'DIM_VENDEDOR', COUNT(*) FROM dim_vendedor
UNION ALL SELECT 'DIM_FORNECEDOR', COUNT(*) FROM dim_fornecedor
UNION ALL SELECT 'DIM_PRODUTO', COUNT(*) FROM dim_produto
UNION ALL SELECT 'FATO_VENDAS', COUNT(*) FROM fato_vendas;
```

### VERIFICAÇÃO DE DUPLICIDADES
```sql
SELECT sales_id, item_id, COUNT(*) AS QTD
FROM fato_vendas
GROUP BY sales_id, item_id
HAVING COUNT(*) > 1;
```

### VERIFICAÇÃO DE INTEGRIDADE REFERENCIAL
```sql
SELECT 'FATO SEM DIM_TEMPO' AS VALIDACAO, COUNT(*) AS QTD
FROM fato_vendas f LEFT JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo WHERE t.sk_tempo IS NULL
UNION ALL
SELECT 'FATO SEM DIM_CLIENTE', COUNT(*)
FROM fato_vendas f LEFT JOIN dim_cliente c ON f.sk_cliente = c.sk_cliente WHERE c.sk_cliente IS NULL;
```
