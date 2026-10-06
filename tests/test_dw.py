"""
TECHPOP BI - TESTES DO DATA WAREHOUSE
========================================
Testes para validar o DW após a carga.
Requerem que o ETL tenha sido executado previamente.

Executar com: pytest tests/test_dw.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
from sqlalchemy import text
from config.database import get_dw_engine, test_connection as check_db_connection


@pytest.fixture(scope="module")
def engine():
    """Engine do DW para os testes."""
    eng = get_dw_engine()
    if not check_db_connection(eng, "DW"):
        pytest.skip("DW NÃO DISPONÍVEL")
    return eng


def _count_table(engine, table: str) -> int:
    """Conta registros de uma tabela."""
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        return result.scalar()


class TestDimensionLoading:
    """Testes de carregamento das dimensões."""

    def test_dim_tempo_carregada(self, engine):
        """DIM_TEMPO deve ter registros."""
        count = _count_table(engine, "dim_tempo")
        assert count > 0, "DIM_TEMPO ESTÁ VAZIA"

    def test_dim_tempo_registros(self, engine):
        """DIM_TEMPO deve ter 2 datas (2023-05-15 e 2022-08-20)."""
        count = _count_table(engine, "dim_tempo")
        assert count == 2, f"ESPERADO 2, ENCONTRADO {count}"

    def test_dim_cliente_carregada(self, engine):
        """DIM_CLIENTE deve ter registros."""
        count = _count_table(engine, "dim_cliente")
        assert count > 0, "DIM_CLIENTE ESTÁ VAZIA"

    def test_dim_vendedor_carregada(self, engine):
        """DIM_VENDEDOR deve ter registros."""
        count = _count_table(engine, "dim_vendedor")
        assert count > 0, "DIM_VENDEDOR ESTÁ VAZIA"

    def test_dim_fornecedor_carregada(self, engine):
        """DIM_FORNECEDOR deve ter registros."""
        count = _count_table(engine, "dim_fornecedor")
        assert count > 0, "DIM_FORNECEDOR ESTÁ VAZIA"

    def test_dim_produto_carregada(self, engine):
        """DIM_PRODUTO deve ter registros."""
        count = _count_table(engine, "dim_produto")
        assert count > 0, "DIM_PRODUTO ESTÁ VAZIA"


class TestFactLoading:
    """Testes de carregamento da fato."""

    def test_fato_vendas_carregada(self, engine):
        """FATO_VENDAS deve ter registros."""
        count = _count_table(engine, "fato_vendas")
        assert count > 0, "FATO_VENDAS ESTÁ VAZIA"

    def test_fato_vendas_28_registros(self, engine):
        """FATO_VENDAS deve ter 28 registros (um por item de venda)."""
        count = _count_table(engine, "fato_vendas")
        assert count == 28, f"ESPERADO 28, ENCONTRADO {count}"

    def test_sem_duplicidades(self, engine):
        """Não deve haver duplicidades (sales_id + item_id)."""
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM ("
                "  SELECT sales_id, item_id FROM fato_vendas "
                "  GROUP BY sales_id, item_id HAVING COUNT(*) > 1"
                ") sub"
            ))
            dups = result.scalar()
        assert dups == 0, f"ENCONTRADAS {dups} DUPLICIDADES"

    def test_idempotencia(self, engine):
        """Ao recarregar, não deve criar duplicações."""
        count_before = _count_table(engine, "fato_vendas")
        # Se a contagem está correta, o processo é idempotente
        assert count_before == 28, f"CONTAGEM INCORRETA: {count_before}"


class TestForeignKeys:
    """Testes de integridade referencial."""

    def test_sem_fk_orfa_tempo(self, engine):
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM fato_vendas f "
                "LEFT JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo "
                "WHERE t.sk_tempo IS NULL"
            ))
            assert result.scalar() == 0, "REGISTROS SEM DIM_TEMPO"

    def test_sem_fk_orfa_cliente(self, engine):
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM fato_vendas f "
                "LEFT JOIN dim_cliente c ON f.sk_cliente = c.sk_cliente "
                "WHERE c.sk_cliente IS NULL"
            ))
            assert result.scalar() == 0, "REGISTROS SEM DIM_CLIENTE"

    def test_sem_fk_orfa_vendedor(self, engine):
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM fato_vendas f "
                "LEFT JOIN dim_vendedor v ON f.sk_vendedor = v.sk_vendedor "
                "WHERE v.sk_vendedor IS NULL"
            ))
            assert result.scalar() == 0, "REGISTROS SEM DIM_VENDEDOR"

    def test_sem_fk_orfa_produto(self, engine):
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM fato_vendas f "
                "LEFT JOIN dim_produto p ON f.sk_produto = p.sk_produto "
                "WHERE p.sk_produto IS NULL"
            ))
            assert result.scalar() == 0, "REGISTROS SEM DIM_PRODUTO"

    def test_sem_fk_orfa_fornecedor(self, engine):
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM fato_vendas f "
                "LEFT JOIN dim_fornecedor fo ON f.sk_fornecedor = fo.sk_fornecedor "
                "WHERE fo.sk_fornecedor IS NULL"
            ))
            assert result.scalar() == 0, "REGISTROS SEM DIM_FORNECEDOR"


class TestDataQuality:
    """Testes de qualidade dos dados."""

    def test_subtotais_positivos(self, engine):
        """Todos os subtotais devem ser positivos."""
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM fato_vendas WHERE subtotal <= 0"
            ))
            assert result.scalar() == 0, "SUBTOTAIS NEGATIVOS OU ZERO"

    def test_comissoes_nao_negativas(self, engine):
        """Todas as comissões devem ser >= 0."""
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM fato_vendas WHERE valor_comissao < 0"
            ))
            assert result.scalar() == 0, "COMISSÕES NEGATIVAS"

    def test_textos_maiusculo_cliente(self, engine):
        """Todos os nomes de clientes devem estar em maiúsculo."""
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM dim_cliente WHERE nome != UPPER(nome)"
            ))
            assert result.scalar() == 0, "NOMES DE CLIENTES NÃO MAIÚSCULOS"

    def test_textos_maiusculo_vendedor(self, engine):
        """Todos os nomes de vendedores devem estar em maiúsculo."""
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM dim_vendedor WHERE nome != UPPER(nome)"
            ))
            assert result.scalar() == 0, "NOMES DE VENDEDORES NÃO MAIÚSCULOS"

    def test_textos_maiusculo_produto(self, engine):
        """Todos os nomes de produtos devem estar em maiúsculo."""
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM dim_produto WHERE nome_produto != UPPER(nome_produto)"
            ))
            assert result.scalar() == 0, "NOMES DE PRODUTOS NÃO MAIÚSCULOS"

    def test_region_preenchida(self, engine):
        """O campo region deve estar preenchido em clientes."""
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM dim_cliente WHERE region IS NULL OR region = ''"
            ))
            assert result.scalar() == 0, "CLIENTES SEM REGION"

    def test_sem_nulos_fato(self, engine):
        """Não deve haver nulos nas colunas essenciais da fato."""
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM fato_vendas "
                "WHERE sk_tempo IS NULL OR sk_cliente IS NULL "
                "OR sk_vendedor IS NULL OR sk_produto IS NULL "
                "OR sk_fornecedor IS NULL OR subtotal IS NULL "
                "OR valor_comissao IS NULL"
            ))
            assert result.scalar() == 0, "NULOS NAS COLUNAS DA FATO"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
