# REGRAS DO ETL - TECHPOP BI

## VISÃO GERAL

O ETL (Extract, Transform, Load) é implementado em Python e segue três etapas claramente separadas. Todas as transformações ocorrem na camada ETL, sem alterar os dados do OLTP.

## EXTRACT (EXTRAÇÃO)

Os dados são extraídos diretamente do PostgreSQL OLTP via SQLAlchemy, com JOINs entre todas as tabelas necessárias:

```
sales_items ← sales ← customers
                    ← sellers
           ← products ← categories
                      ← suppliers
```

**Não utiliza CSV intermediário como fonte principal.**

## TRANSFORM (TRANSFORMAÇÃO)

### TABELA DE TRANSFORMAÇÕES

| # | ORIGEM | CAMPO ORIGINAL | TRANSFORMAÇÃO | DESTINO |
|---|--------|----------------|---------------|---------|
| 1 | sales | date | Conversão para datetime | dim_tempo.data_completa |
| 2 | sales | date | Formato YYYYMMDD (ex: 20230515) | dim_tempo.data_yyyymmdd |
| 3 | sales | date | Extração do ano | dim_tempo.ano |
| 4 | sales | date | Extração do trimestre (1-4) | dim_tempo.trimestre |
| 5 | sales | date | Extração do mês (1-12) | dim_tempo.mes |
| 6 | sales | date | Mapeamento mês → nome (MAIÚSCULO) | dim_tempo.nome_mes |
| 7 | customers | customer_name | UPPER() | dim_cliente.nome |
| 8 | customers | email | UPPER() | dim_cliente.email |
| 9 | customers | state | UPPER() | dim_cliente.estado |
| 10 | customers | state | Mapeamento estado → região | dim_cliente.region |
| 11 | sellers | seller_name | UPPER() | dim_vendedor.nome |
| 12 | sellers | email | UPPER() | dim_vendedor.email |
| 13 | sellers | state | UPPER() | dim_vendedor.estado |
| 14 | sellers | state | Mapeamento estado → região | dim_vendedor.region |
| 15 | sellers | tx_commission | Sem alteração | dim_vendedor.comissao_percentual |
| 16 | suppliers | supplier_name | UPPER() | dim_fornecedor.nome |
| 17 | suppliers | email | UPPER() | dim_fornecedor.email |
| 18 | suppliers | state | UPPER() | dim_fornecedor.estado |
| 19 | suppliers | state | Mapeamento estado → região | dim_fornecedor.region |
| 20 | products | product_name | UPPER() | dim_produto.nome_produto |
| 21 | categories | category_name | UPPER() | dim_produto.categoria |
| 22 | products | price | Sem alteração | dim_produto.preco_cadastro |
| 23 | sales_items | quantity | Sem alteração | fato_vendas.quantidade |
| 24 | sales_items | price | Sem alteração | fato_vendas.preco_unitario |
| 25 | sales_items | quantity × price | Cálculo do subtotal | fato_vendas.subtotal |
| 26 | (calculado) | subtotal × comissão / 100 | Cálculo da comissão | fato_vendas.valor_comissao |

### REGRA DE MAIÚSCULAS

**TODOS OS TEXTOS DEVEM FICAR EM MAIÚSCULO:**

- Nomes de clientes, vendedores, fornecedores
- Nomes de produtos e categorias
- Estados e regiões
- Nomes dos meses
- Títulos e labels do dashboard

Exemplo: `"John Doe"` → `"JOHN DOE"`

### REGRA DE REGION

O campo `region` não existe no OLTP. É criado durante o ETL usando um dicionário centralizado que mapeia estados dos EUA para regiões do U.S. Census Bureau:

| ESTADO | REGIÃO |
|--------|--------|
| CA | WEST |
| NY | NORTHEAST |
| TX | SOUTH |
| FL | SOUTH |
| WA | WEST |

**O mapeamento completo contém todos os 50 estados e está centralizado em uma única função (`map_state_to_region`) no módulo `etl/transform.py`.**

### CÁLCULO DO SUBTOTAL

```
SUBTOTAL = QUANTIDADE × PREÇO UNITÁRIO DO ITEM
```

Exemplo: quantidade=2, preço=50 → subtotal=100

**O subtotal é calculado usando `sales_items.quantity × sales_items.price`, NÃO o `sales.total_price`.**

### CÁLCULO DA COMISSÃO

```
VALOR_COMISSÃO = SUBTOTAL × COMISSÃO_PERCENTUAL / 100
```

Exemplo: subtotal=100, comissão=10% → valor_comissão=10.00

### TRATAMENTO DE NULOS

- Campos texto nulos → string vazia `""`
- Campos numéricos nulos → `0`

### REMOÇÃO DE DUPLICIDADES

- Baseada na chave composta `(sales_id, item_id)`
- Mantém o primeiro registro em caso de duplicidade

## INCONSISTÊNCIA DO TOTAL_PRICE

### PROBLEMA IDENTIFICADO

O campo `sales.total_price` no OLTP **NÃO corresponde** à soma dos subtotais dos itens (`SUM(quantity × price)`) em **TODAS as 9 vendas**.

### DECISÃO

- O DW utiliza a **soma dos subtotais dos itens** como base para o faturamento analítico
- O campo `sales.total_price` **NÃO é copiado** para a fato
- A inconsistência é **documentada** e uma **validação** compara os valores durante o ETL

### JUSTIFICATIVA

Os valores por item (quantity × price) representam a granularidade real da fato e são mais confiáveis para análise analítica do que um total consolidado que apresenta inconsistências.

## LOAD (CARGA)

### ORDEM DE CARGA

1. **DIM_TEMPO** (sem dependências)
2. **DIM_CLIENTE** (sem dependências)
3. **DIM_VENDEDOR** (sem dependências)
4. **DIM_FORNECEDOR** (sem dependências)
5. **DIM_PRODUTO** (sem dependências)
6. **FATO_VENDAS** (depende de todas as dimensões)

### IDEMPOTÊNCIA

O processo é idempotente: todas as tabelas são truncadas antes da recarga, garantindo que execuções repetidas não criem duplicações.

### SURROGATE KEYS

As surrogate keys (sk_*) são geradas automaticamente pelo PostgreSQL (SERIAL) e mapeadas em memória durante a carga para vincular a fato às dimensões corretas.
