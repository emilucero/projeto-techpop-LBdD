# MODELO DIMENSIONAL - TECHPOP BI

## VISÃO GERAL

O Data Warehouse da TechPop utiliza o **MODELO ESTRELA (Star Schema)**, composto por uma tabela fato central e cinco dimensões.

## DIAGRAMA DO MODELO ESTRELA

```mermaid
erDiagram
    DIM_TEMPO ||--o{ FATO_VENDAS : "sk_tempo"
    DIM_CLIENTE ||--o{ FATO_VENDAS : "sk_cliente"
    DIM_VENDEDOR ||--o{ FATO_VENDAS : "sk_vendedor"
    DIM_PRODUTO ||--o{ FATO_VENDAS : "sk_produto"
    DIM_FORNECEDOR ||--o{ FATO_VENDAS : "sk_fornecedor"

    DIM_TEMPO {
        int sk_tempo PK
        date data_completa
        int data_yyyymmdd
        int ano
        int trimestre
        int mes
        varchar nome_mes
    }

    DIM_CLIENTE {
        int sk_cliente PK
        int customer_id NK
        varchar nome
        varchar email
        varchar estado
        varchar region
    }

    DIM_VENDEDOR {
        int sk_vendedor PK
        int seller_id NK
        varchar nome
        varchar email
        varchar estado
        varchar region
        numeric comissao_percentual
    }

    DIM_PRODUTO {
        int sk_produto PK
        int product_id NK
        varchar nome_produto
        varchar categoria
        numeric preco_cadastro
    }

    DIM_FORNECEDOR {
        int sk_fornecedor PK
        int supplier_id NK
        varchar nome
        varchar email
        varchar estado
        varchar region
    }

    FATO_VENDAS {
        int sk_venda PK
        int sk_tempo FK
        int sk_cliente FK
        int sk_vendedor FK
        int sk_produto FK
        int sk_fornecedor FK
        int sales_id
        int item_id
        int quantidade
        numeric preco_unitario
        numeric subtotal
        numeric comissao_percentual
        numeric valor_comissao
    }
```

## GRANULARIDADE

> **UM REGISTRO PARA CADA ITEM DE UMA VENDA.**

Cada linha da FATO_VENDAS representa um item específico dentro de uma venda. Isso permite responder:

- Quais produtos foram vendidos
- Quantas unidades foram vendidas
- Por qual vendedor
- Para qual cliente
- Qual fornecedor está relacionado ao produto
- Em qual data ocorreu a venda
- Qual categoria pertence ao produto
- Qual foi o subtotal daquele item
- Qual foi o valor da comissão daquele item

## DIMENSÕES

### DIM_TEMPO

| CAMPO | TIPO | DESCRIÇÃO |
|-------|------|-----------|
| sk_tempo | SERIAL (PK) | SURROGATE KEY |
| data_completa | DATE (NK) | DATA COMPLETA DA VENDA |
| data_yyyymmdd | INTEGER | DATA NO FORMATO YYYYMMDD (EX: 20230515) |
| ano | INTEGER | ANO DA VENDA |
| trimestre | INTEGER | TRIMESTRE (1-4) |
| mes | INTEGER | MÊS (1-12) |
| nome_mes | VARCHAR | NOME DO MÊS EM MAIÚSCULO |

**Chave Natural:** data_completa (DATE)
**Surrogate Key:** sk_tempo (SERIAL)

### DIM_CLIENTE

| CAMPO | TIPO | DESCRIÇÃO |
|-------|------|-----------|
| sk_cliente | SERIAL (PK) | SURROGATE KEY |
| customer_id | INTEGER (NK) | ID ORIGINAL DO OLTP |
| nome | VARCHAR | NOME DO CLIENTE (MAIÚSCULO) |
| email | VARCHAR | E-MAIL DO CLIENTE (MAIÚSCULO) |
| estado | VARCHAR | SIGLA DO ESTADO (EX: CA, NY) |
| region | VARCHAR | REGIÃO GEOGRÁFICA (CRIADA NO ETL) |

**Chave Natural:** customer_id
**Surrogate Key:** sk_cliente

### DIM_VENDEDOR

| CAMPO | TIPO | DESCRIÇÃO |
|-------|------|-----------|
| sk_vendedor | SERIAL (PK) | SURROGATE KEY |
| seller_id | INTEGER (NK) | ID ORIGINAL DO OLTP |
| nome | VARCHAR | NOME DO VENDEDOR (MAIÚSCULO) |
| email | VARCHAR | E-MAIL DO VENDEDOR (MAIÚSCULO) |
| estado | VARCHAR | SIGLA DO ESTADO |
| region | VARCHAR | REGIÃO GEOGRÁFICA |
| comissao_percentual | NUMERIC | PERCENTUAL DE COMISSÃO |

**Chave Natural:** seller_id
**Surrogate Key:** sk_vendedor

### DIM_PRODUTO

| CAMPO | TIPO | DESCRIÇÃO |
|-------|------|-----------|
| sk_produto | SERIAL (PK) | SURROGATE KEY |
| product_id | INTEGER (NK) | ID ORIGINAL DO OLTP |
| nome_produto | VARCHAR | NOME DO PRODUTO (MAIÚSCULO) |
| categoria | VARCHAR | CATEGORIA DO PRODUTO (INCORPORADA, EVITA SNOWFLAKE) |
| preco_cadastro | NUMERIC | PREÇO DE CADASTRO NO OLTP |

**Chave Natural:** product_id
**Surrogate Key:** sk_produto

> **NOTA:** A categoria foi incorporada à DIM_PRODUTO para manter o modelo estrela puro, evitando um snowflake desnecessário com uma DIM_CATEGORIA separada.

### DIM_FORNECEDOR

| CAMPO | TIPO | DESCRIÇÃO |
|-------|------|-----------|
| sk_fornecedor | SERIAL (PK) | SURROGATE KEY |
| supplier_id | INTEGER (NK) | ID ORIGINAL DO OLTP |
| nome | VARCHAR | NOME DO FORNECEDOR (MAIÚSCULO) |
| email | VARCHAR | E-MAIL DO FORNECEDOR (MAIÚSCULO) |
| estado | VARCHAR | SIGLA DO ESTADO |
| region | VARCHAR | REGIÃO GEOGRÁFICA |

**Chave Natural:** supplier_id
**Surrogate Key:** sk_fornecedor

## FATO VENDAS

### MEDIDAS

| MEDIDA | TIPO | FÓRMULA | DESCRIÇÃO |
|--------|------|---------|-----------|
| quantidade | INTEGER | sales_items.quantity | QUANTIDADE DE UNIDADES VENDIDAS |
| preco_unitario | NUMERIC | sales_items.price | PREÇO UNITÁRIO DO ITEM NA VENDA |
| subtotal | NUMERIC | QUANTIDADE × PREÇO | VALOR TOTAL DO ITEM |
| comissao_percentual | NUMERIC | sellers.tx_commission | PERCENTUAL DE COMISSÃO DO VENDEDOR |
| valor_comissao | NUMERIC | SUBTOTAL × COMISSÃO / 100 | VALOR DA COMISSÃO SOBRE O ITEM |

### CAMPOS DE RASTREABILIDADE

| CAMPO | DESCRIÇÃO |
|-------|-----------|
| sales_id | ID DA VENDA NO OLTP (RASTREABILIDADE) |
| item_id | ID DO ITEM NO OLTP (RASTREABILIDADE) |

### RELACIONAMENTOS

| DIMENSÃO | FK NA FATO | NK NA DIMENSÃO |
|----------|-----------|----------------|
| DIM_TEMPO | sk_tempo | data_completa |
| DIM_CLIENTE | sk_cliente | customer_id |
| DIM_VENDEDOR | sk_vendedor | seller_id |
| DIM_PRODUTO | sk_produto | product_id |
| DIM_FORNECEDOR | sk_fornecedor | supplier_id |

## CONTAGENS ESPERADAS

| TABELA | REGISTROS |
|--------|-----------|
| DIM_TEMPO | 2 |
| DIM_CLIENTE | 9 |
| DIM_VENDEDOR | 9 |
| DIM_FORNECEDOR | 9 |
| DIM_PRODUTO | 9 |
| FATO_VENDAS | 25 |
