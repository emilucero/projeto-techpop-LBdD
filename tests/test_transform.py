"""
TECHPOP BI - TESTES DE TRANSFORMAÇÃO
======================================
Testes unitários para validar as regras de transformação do ETL.
Executar com: pytest tests/test_transform.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from etl.transform import (
    calculate_subtotal,
    calculate_commission,
    to_upper,
    map_state_to_region,
    date_to_yyyymmdd,
    MONTH_NAMES,
)


class TestCalculateSubtotal:
    """Testes para cálculo do subtotal."""

    def test_subtotal_basico(self):
        """quantidade=2, preço=50 → subtotal=100"""
        assert calculate_subtotal(2, 50) == 100.0

    def test_subtotal_unitario(self):
        """quantidade=1, preço=800 → subtotal=800"""
        assert calculate_subtotal(1, 800) == 800.0

    def test_subtotal_multiplo(self):
        """quantidade=3, preço=25 → subtotal=75"""
        assert calculate_subtotal(3, 25) == 75.0

    def test_subtotal_decimal(self):
        """quantidade=2, preço=10.50 → subtotal=21.0"""
        assert calculate_subtotal(2, 10.50) == 21.0

    def test_subtotal_zero_quantidade(self):
        """quantidade=0, preço=100 → subtotal=0"""
        assert calculate_subtotal(0, 100) == 0.0


class TestCalculateCommission:
    """Testes para cálculo da comissão."""

    def test_comissao_10_porcento(self):
        """subtotal=100, comissão=10% → 10.0"""
        assert calculate_commission(100, 10) == 10.0

    def test_comissao_15_porcento(self):
        """subtotal=200, comissão=15% → 30.0"""
        assert calculate_commission(200, 15) == 30.0

    def test_comissao_12_porcento(self):
        """subtotal=120, comissão=12% → 14.4"""
        assert calculate_commission(120, 12) == 14.4

    def test_comissao_zero(self):
        """subtotal=500, comissão=0% → 0.0"""
        assert calculate_commission(500, 0) == 0.0


class TestToUpper:
    """Testes para conversão em maiúsculo."""

    def test_nome_simples(self):
        assert to_upper("John Doe") == "JOHN DOE"

    def test_email(self):
        assert to_upper("john@example.com") == "JOHN@EXAMPLE.COM"

    def test_ja_maiusculo(self):
        assert to_upper("CALIFORNIA") == "CALIFORNIA"

    def test_none(self):
        assert to_upper(None) == ""

    def test_com_espacos(self):
        assert to_upper("  Jane Smith  ") == "JANE SMITH"


class TestMapStateToRegion:
    """Testes para mapeamento estado → região."""

    def test_california_west(self):
        assert map_state_to_region("CA") == "WEST"

    def test_new_york_northeast(self):
        assert map_state_to_region("NY") == "NORTHEAST"

    def test_texas_south(self):
        assert map_state_to_region("TX") == "SOUTH"

    def test_florida_south(self):
        assert map_state_to_region("FL") == "SOUTH"

    def test_washington_west(self):
        assert map_state_to_region("WA") == "WEST"

    def test_minusculo(self):
        assert map_state_to_region("ca") == "WEST"

    def test_none(self):
        assert map_state_to_region(None) == "DESCONHECIDA"

    def test_invalido(self):
        assert map_state_to_region("XX") == "DESCONHECIDA"


class TestDateToYYYYMMDD:
    """Testes para conversão de data para YYYYMMDD."""

    def test_data_normal(self):
        assert date_to_yyyymmdd("2023-05-15") == 20230515

    def test_data_agosto(self):
        assert date_to_yyyymmdd("2022-08-20") == 20220820

    def test_data_primeiro_jan(self):
        assert date_to_yyyymmdd("2024-01-01") == 20240101

    def test_data_ultimo_dez(self):
        assert date_to_yyyymmdd("2023-12-31") == 20231231


class TestMonthNames:
    """Testes para nomes dos meses."""

    def test_todos_meses_mapeados(self):
        assert len(MONTH_NAMES) == 12

    def test_janeiro(self):
        assert MONTH_NAMES[1] == "JANEIRO"

    def test_maio(self):
        assert MONTH_NAMES[5] == "MAIO"

    def test_agosto(self):
        assert MONTH_NAMES[8] == "AGOSTO"

    def test_dezembro(self):
        assert MONTH_NAMES[12] == "DEZEMBRO"

    def test_todos_maiusculo(self):
        for nome in MONTH_NAMES.values():
            assert nome == nome.upper(), f"{nome} não está em maiúsculo"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
