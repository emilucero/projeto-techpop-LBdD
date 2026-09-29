# TECHPOP - BUSINESS INTELLIGENCE

## 📋 OBJETIVO DO PROJETO

Projeto acadêmico de Business Intelligence para a empresa fictícia **TechPop**, da indústria de tecnologia. A empresa enfrenta uma queda nas vendas e precisa de uma solução de BI para apoiar a tomada de decisões da alta gestão.

## 🏢 PROBLEMA DE NEGÓCIO

A TechPop possui um sistema operacional chamado **FatorV** que controla vendas, vendedores, clientes, produtos, fornecedores e categorias. A alta gestão precisa de indicadores analíticos para entender o desempenho comercial.

## 🏗️ ARQUITETURA

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  OLTP        │     │  ETL         │     │  DATA WAREHOUSE │     │  DASHBOARD   │
│  (FatorV)    │────▶│  (Python)    │────▶│  (Estrela)      │────▶│  (Streamlit) │
│  PostgreSQL  │     │  Pandas      │     │  PostgreSQL     │     │  Plotly      │
└─────────────┘     └──────────────┘     └─────────────────┘     └──────────────┘
```

## 🛠️ TECNOLOGIAS

| COMPONENTE | TECNOLOGIA |
|------------|------------|
| OLTP | PostgreSQL |
| DATA WAREHOUSE | PostgreSQL |
| ETL | Python + Pandas + SQLAlchemy |
| DASHBOARD | Streamlit + Plotly |
| GRÁFICOS ESTÁTICOS | Matplotlib |
| TESTES | pytest |

## 📁 ESTRUTURA DE PASTAS

```
techpop-bi/
│
├── README.md                          # ESTE ARQUIVO
├── requirements.txt                   # DEPENDÊNCIAS PYTHON
├── .env.example                       # MODELO DE VARIÁVEIS DE AMBIENTE
├── .gitignore                         # ARQUIVOS IGNORADOS PELO GIT
├── main.py                            # PIPELINE PRINCIPAL
│
├── config/
│   ├── __init__.py
│   └── database.py                    # CONEXÕES COM POSTGRESQL
│
├── sql/
│   ├── oltp/
│   │   ├── 01_create_oltp.sql         # DDL DO OLTP (FATORV)
│   │   └── 02_insert_oltp.sql         # DML DO OLTP (DADOS)
│   └── dw/
│       ├── 01_create_dw.sql           # DDL DO DATA WAREHOUSE
│       ├── 02_indexes.sql             # ÍNDICES ANALÍTICOS
│       └── 03_queries.sql             # CONSULTAS ANALÍTICAS
│
├── etl/
│   ├── __init__.py
│   ├── extract.py                     # EXTRAÇÃO DO OLTP
│   ├── transform.py                   # TRANSFORMAÇÕES
│   ├── load.py                        # CARGA NO DW
│   └── main.py                        # ORQUESTRADOR DO ETL
│
├── dashboard/
│   ├── app.py                         # DASHBOARD STREAMLIT
│   └── queries.py                     # CONSULTAS PARAMETRIZADAS
│
├── reports/
│   ├── gerar_graficos.py              # GERADOR DE GRÁFICOS PNG
│   └── outputs/                       # IMAGENS DOS GRÁFICOS
│
├── docs/
│   ├── modelo_dimensional.md          # DOCUMENTAÇÃO DO MODELO
│   ├── regras_etl.md                  # REGRAS DE TRANSFORMAÇÃO
│   └── consultas.md                   # CONSULTAS ANALÍTICAS
│
└── tests/
    ├── test_transform.py              # TESTES DAS TRANSFORMAÇÕES
    └── test_dw.py                     # TESTES DO DATA WAREHOUSE
```

## ⭐ MODELO ESTRELA

```
    DIM_TEMPO ──────────┐
    DIM_CLIENTE ────────┤
    DIM_VENDEDOR ───────┼──── FATO_VENDAS
    DIM_PRODUTO ────────┤
    DIM_FORNECEDOR ─────┘
```

**A categoria está incorporada à DIM_PRODUTO, evitando um snowflake desnecessário.**

## 📏 GRANULARIDADE DA FATO

> **UM REGISTRO PARA CADA ITEM DE UMA VENDA.**

Cada linha da FATO_VENDAS representa um item específico dentro de uma venda, permitindo análises detalhadas por produto, vendedor, cliente, fornecedor e período.

## 📊 CONTAGENS ESPERADAS

| TABELA | REGISTROS |
|--------|-----------|
| DIM_TEMPO | 2 |
| DIM_CLIENTE | 9 |
| DIM_VENDEDOR | 9 |
| DIM_FORNECEDOR | 9 |
| DIM_PRODUTO | 9 |
| FATO_VENDAS | 25 |

## 🔄 REGRAS DO ETL

### SUBTOTAL
```
SUBTOTAL = QUANTIDADE × PREÇO UNITÁRIO DO ITEM
```
O subtotal é calculado no ETL e armazenado fisicamente na FATO_VENDAS.

### COMISSÃO
```
VALOR_COMISSÃO = SUBTOTAL × COMISSÃO_PERCENTUAL / 100
```

### REGION
O campo `region` não existe no OLTP. É criado no ETL usando mapeamento centralizado:

| ESTADO | REGIÃO |
|--------|--------|
| CA | WEST |
| NY | NORTHEAST |
| TX | SOUTH |
| FL | SOUTH |
| WA | WEST |

### MAIÚSCULAS
**TODOS os textos são convertidos para MAIÚSCULO** no ETL: nomes, emails, estados, regiões, categorias, nomes de meses, títulos dos gráficos.

### DATAS
Todas as datas possuem o formato adicional **YYYYMMDD** (inteiro).
Exemplo: `2023-05-15` → `20230515`

Disponíveis para análise: **ANO, TRIMESTRE, MÊS.**

## ⚠️ INCONSISTÊNCIA DO TOTAL_PRICE

### PROBLEMA IDENTIFICADO

O campo `sales.total_price` no OLTP **NÃO corresponde** à soma dos subtotais dos itens em **TODAS as 9 vendas**:

| VENDA | TOTAL_PRICE (OLTP) | SOMA DOS ITENS | DIFERENÇA |
|-------|-------------------|----------------|-----------|
| 1 | 700,00 | 900,00 | -200,00 |
| 2 | 70,00 | 266,00 | -196,00 |
| 3 | 180,00 | 52,00 | 128,00 |
| 4 | 250,00 | 104,00 | 146,00 |
| 5 | 90,00 | 50,00 | 40,00 |
| 6 | 480,00 | 160,00 | 320,00 |
| 7 | 160,00 | 104,00 | 56,00 |
| 8 | 150,00 | 115,00 | 35,00 |
| 9 | 36,00 | 516,00 | -480,00 |

### DECISÃO

O DW utiliza a **soma dos subtotais dos itens** (`quantity × price`) como base para o faturamento analítico. O campo `sales.total_price` **NÃO é utilizado** na fato.

### JUSTIFICATIVA

Os valores por item representam a granularidade real da fato e são mais confiáveis para análise analítica.

## 🚀 INSTRUÇÕES DE INSTALAÇÃO

### 1. PRÉ-REQUISITOS

- Python 3.9+
- PostgreSQL 12+

### 2. CRIAR AMBIENTE VIRTUAL

```bash
cd techpop-bi
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. INSTALAR DEPENDÊNCIAS

```bash
pip install -r requirements.txt
```

### 4. CONFIGURAR VARIÁVEIS DE AMBIENTE

```bash
copy .env.example .env
```

Edite o arquivo `.env` com suas credenciais do PostgreSQL:

```
OLTP_HOST=localhost
OLTP_PORT=5432
OLTP_DATABASE=techpop_oltp
OLTP_USER=postgres
OLTP_PASSWORD=sua_senha

DW_HOST=localhost
DW_PORT=5432
DW_DATABASE=techpop_dw
DW_USER=postgres
DW_PASSWORD=sua_senha
```

### 5. CONFIGURAR POSTGRESQL

Certifique-se de que o PostgreSQL está rodando. Os bancos `techpop_oltp` e `techpop_dw` serão criados automaticamente pelo pipeline.

### 6. EXECUTAR O PIPELINE COMPLETO

```bash
python main.py
```

Este comando:
1. Cria os bancos `techpop_oltp` e `techpop_dw`
2. Executa o DDL e DML do OLTP
3. Cria as tabelas do DW
4. Executa o ETL (Extract → Transform → Load)
5. Exibe validações e relatório de consistência

### 7. GERAR GRÁFICOS ESTÁTICOS

```bash
python reports/gerar_graficos.py
```

Gera 7 imagens PNG em `reports/outputs/`.

### 8. INICIAR DASHBOARD

```bash
streamlit run dashboard/app.py
```

Acesse em: `http://localhost:8501`

### 9. EXECUTAR TESTES

```bash
# Testes de transformação (não requerem banco)
pytest tests/test_transform.py -v

# Testes do DW (requerem ETL executado)
pytest tests/test_dw.py -v

# Todos os testes
pytest tests/ -v
```

## 📈 GRÁFICOS GERADOS

1. **PRODUTOS MAIS VENDIDOS** - Barras horizontais (SUM quantidade)
2. **FATURAMENTO TOTAL** - Linha temporal (SUM subtotal)
3. **FATURAMENTO POR CATEGORIA** - Pizza (SUM subtotal por categoria)
4. **FATURAMENTO POR PRODUTO** - Barras horizontais (SUM subtotal por produto)
5. **MAIORES COMISSÕES DE VENDEDORES** - Barras horizontais (SUM valor_comissao)
6. **FORNECEDORES POR ESTADO** - Barras verticais (COUNT DISTINCT supplier_id)
7. **CLIENTES POR ESTADO** - Barras verticais (COUNT DISTINCT customer_id)

## 🖥️ DASHBOARD

O dashboard Streamlit inclui:

- **KPIs**: Faturamento total, itens vendidos, produtos vendidos, comissões pagas
- **Filtros**: ANO, TRIMESTRE, MÊS (com opção "TODOS")
- **7 gráficos interativos** com Plotly
- **Todos os textos em MAIÚSCULO**

## 📋 CONSULTAS PARA APRESENTAÇÃO

Execute no banco `techpop_dw` durante a apresentação:

```sql
-- FATURAMENTO TOTAL
SELECT SUM(subtotal) AS "FATURAMENTO TOTAL" FROM fato_vendas;

-- PRODUTOS MAIS VENDIDOS
SELECT p.nome_produto, SUM(f.quantidade) AS qtd
FROM fato_vendas f JOIN dim_produto p ON f.sk_produto = p.sk_produto
GROUP BY p.nome_produto ORDER BY qtd DESC;

-- COMISSÕES POR VENDEDOR
SELECT v.nome, SUM(f.valor_comissao) AS comissao
FROM fato_vendas f JOIN dim_vendedor v ON f.sk_vendedor = v.sk_vendedor
GROUP BY v.nome ORDER BY comissao DESC;

-- CLIENTES POR ESTADO
SELECT c.estado, COUNT(DISTINCT c.customer_id) AS qtd
FROM fato_vendas f JOIN dim_cliente c ON f.sk_cliente = c.sk_cliente
GROUP BY c.estado ORDER BY qtd DESC;

-- FORNECEDORES POR ESTADO
SELECT fo.estado, COUNT(DISTINCT fo.supplier_id) AS qtd
FROM fato_vendas f JOIN dim_fornecedor fo ON f.sk_fornecedor = fo.sk_fornecedor
GROUP BY fo.estado ORDER BY qtd DESC;

-- VALIDAÇÃO DE REGISTROS
SELECT 'DIM_TEMPO' AS TABELA, COUNT(*) FROM dim_tempo
UNION ALL SELECT 'DIM_CLIENTE', COUNT(*) FROM dim_cliente
UNION ALL SELECT 'DIM_VENDEDOR', COUNT(*) FROM dim_vendedor
UNION ALL SELECT 'DIM_FORNECEDOR', COUNT(*) FROM dim_fornecedor
UNION ALL SELECT 'DIM_PRODUTO', COUNT(*) FROM dim_produto
UNION ALL SELECT 'FATO_VENDAS', COUNT(*) FROM fato_vendas;
```

## 📋 INSTRUÇÕES PARA APRESENTAÇÃO

1. Mostre o **modelo dimensional** (`docs/modelo_dimensional.md`)
2. Execute `python main.py` para demonstrar o **ETL**
3. Mostre o **relatório de consistência** gerado pelo ETL
4. Execute consultas SQL no `techpop_dw` para mostrar os **dados**
5. Execute `streamlit run dashboard/app.py` para o **dashboard**
6. Demonstre os **filtros temporais** (ANO, TRIMESTRE, MÊS)
7. Mostre os **gráficos PNG** em `reports/outputs/`
8. Execute `pytest tests/ -v` para os **testes**

## 📝 NOTAS IMPORTANTES

- **Fornecedores por estado**: Como fornecedor não possui data de cadastro no OLTP, a análise temporal considera fornecedores associados aos itens de vendas no período.
- **Clientes por estado**: Quando filtrado temporalmente, considera clientes envolvidos nas vendas do período.
- **Dados**: Todos os dados são os fornecidos pelo professor. Nenhum dado adicional foi inventado.
- **Idempotência**: O ETL pode ser executado múltiplas vezes sem criar duplicações.
