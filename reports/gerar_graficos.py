"""
TECHPOP BI - GERADOR DE GRÁFICOS ESTÁTICOS
=============================================
Gera imagens PNG dos 7 gráficos obrigatórios.
As imagens são salvas em reports/outputs/

Executar: python reports/gerar_graficos.py
"""

import sys
import os

# Adicionar diretório raiz ao path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from config.database import get_dw_engine
from dashboard.queries import (
    get_produtos_mais_vendidos,
    get_faturamento_temporal,
    get_faturamento_categoria,
    get_faturamento_produto,
    get_comissoes_vendedor,
    get_fornecedores_por_estado,
    get_clientes_por_estado,
)

# Diretório de saída
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "reports", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configurações globais do matplotlib
plt.rcParams.update({
    "figure.figsize": (12, 7),
    "figure.dpi": 150,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})

# Paleta de cores
COLORS = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#3B1F2B",
          "#44BBA4", "#E94F37", "#393E41", "#D4B483", "#5C6B73"]


def save_chart(fig, filename: str):
    """Salva o gráfico como PNG."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.tight_layout()
    fig.savefig(filepath, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [OK] SALVO: {filepath}")


def chart_01_produtos_mais_vendidos(engine):
    """1. PRODUTOS MAIS VENDIDOS"""
    print("GERANDO GRÁFICO 01: PRODUTOS MAIS VENDIDOS...")
    df = get_produtos_mais_vendidos(engine)
    
    fig, ax = plt.subplots()
    bars = ax.barh(df["PRODUTO"], df["QUANTIDADE"], color=COLORS[:len(df)])
    ax.set_xlabel("QUANTIDADE VENDIDA")
    ax.set_ylabel("PRODUTO")
    ax.set_title("PRODUTOS MAIS VENDIDOS (POR QUANTIDADE)")
    ax.invert_yaxis()
    
    for bar, val in zip(bars, df["QUANTIDADE"]):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f"{int(val)}", va="center", fontweight="bold")
    
    save_chart(fig, "01_produtos_mais_vendidos.png")


def chart_02_faturamento_total(engine):
    """2. FATURAMENTO TOTAL (EVOLUÇÃO TEMPORAL)"""
    print("GERANDO GRÁFICO 02: FATURAMENTO TOTAL...")
    df = get_faturamento_temporal(engine, "MÊS")
    
    fig, ax = plt.subplots()
    ax.plot(df["PERÍODO"], df["FATURAMENTO"], marker="o", linewidth=2.5,
            color="#2E86AB", markersize=8)
    ax.fill_between(range(len(df)), df["FATURAMENTO"], alpha=0.15, color="#2E86AB")
    ax.set_xlabel("PERÍODO")
    ax.set_ylabel("FATURAMENTO (R$)")
    ax.set_title("EVOLUÇÃO DO FATURAMENTO TOTAL")
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df["PERÍODO"], rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.3)
    
    for i, val in enumerate(df["FATURAMENTO"]):
        ax.annotate(f"R$ {val:,.2f}", (i, val), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=9)
    
    save_chart(fig, "02_faturamento_total.png")


def chart_03_faturamento_categoria(engine):
    """3. FATURAMENTO POR CATEGORIA"""
    print("GERANDO GRÁFICO 03: FATURAMENTO POR CATEGORIA...")
    df = get_faturamento_categoria(engine)
    
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        df["FATURAMENTO"], labels=df["CATEGORIA"],
        autopct="%1.1f%%", colors=COLORS[:len(df)],
        startangle=90, textprops={"fontsize": 9}
    )
    for autotext in autotexts:
        autotext.set_fontweight("bold")
    ax.set_title("FATURAMENTO POR CATEGORIA")
    
    save_chart(fig, "03_faturamento_categoria.png")


def chart_04_faturamento_produto(engine):
    """4. FATURAMENTO POR PRODUTO"""
    print("GERANDO GRÁFICO 04: FATURAMENTO POR PRODUTO...")
    df = get_faturamento_produto(engine)
    
    fig, ax = plt.subplots()
    bars = ax.barh(df["PRODUTO"], df["FATURAMENTO"], color=COLORS[:len(df)])
    ax.set_xlabel("FATURAMENTO (R$)")
    ax.set_ylabel("PRODUTO")
    ax.set_title("FATURAMENTO POR PRODUTO")
    ax.invert_yaxis()
    
    for bar, val in zip(bars, df["FATURAMENTO"]):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f"R$ {val:,.2f}", va="center", fontsize=9)
    
    save_chart(fig, "04_faturamento_produto.png")


def chart_05_comissoes(engine):
    """5. MAIORES COMISSÕES DE VENDEDORES"""
    print("GERANDO GRÁFICO 05: MAIORES COMISSÕES DE VENDEDORES...")
    df = get_comissoes_vendedor(engine)
    
    fig, ax = plt.subplots()
    bars = ax.barh(df["VENDEDOR"], df["TOTAL COMISSÃO"],
                   color=["#F18F01", "#E94F37", "#A23B72", "#2E86AB",
                          "#44BBA4", "#C73E1D", "#3B1F2B", "#D4B483", "#5C6B73"])
    ax.set_xlabel("VALOR DA COMISSÃO (R$)")
    ax.set_ylabel("VENDEDOR")
    ax.set_title("MAIORES COMISSÕES DE VENDEDORES")
    ax.invert_yaxis()
    
    for bar, val in zip(bars, df["TOTAL COMISSÃO"]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f"R$ {val:,.2f}", va="center", fontsize=9)
    
    save_chart(fig, "05_maiores_comissoes.png")


def chart_06_fornecedores_estado(engine):
    """6. FORNECEDORES POR ESTADO"""
    print("GERANDO GRÁFICO 06: FORNECEDORES POR ESTADO...")
    df = get_fornecedores_por_estado(engine)
    
    fig, ax = plt.subplots()
    bars = ax.bar(df["ESTADO"], df["QTD FORNECEDORES"], color=COLORS[:len(df)])
    ax.set_xlabel("ESTADO")
    ax.set_ylabel("QUANTIDADE DE FORNECEDORES")
    ax.set_title("QUANTIDADE DE FORNECEDORES POR ESTADO")
    ax.grid(axis="y", alpha=0.3)
    
    for bar, val in zip(bars, df["QTD FORNECEDORES"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                str(int(val)), ha="center", fontweight="bold")
    
    save_chart(fig, "06_fornecedores_por_estado.png")


def chart_07_clientes_estado(engine):
    """7. CLIENTES POR ESTADO"""
    print("GERANDO GRÁFICO 07: CLIENTES POR ESTADO...")
    df = get_clientes_por_estado(engine)
    
    fig, ax = plt.subplots()
    bars = ax.bar(df["ESTADO"], df["QTD CLIENTES"], color=COLORS[:len(df)])
    ax.set_xlabel("ESTADO")
    ax.set_ylabel("QUANTIDADE DE CLIENTES")
    ax.set_title("QUANTIDADE DE CLIENTES POR ESTADO")
    ax.grid(axis="y", alpha=0.3)
    
    for bar, val in zip(bars, df["QTD CLIENTES"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                str(int(val)), ha="center", fontweight="bold")
    
    save_chart(fig, "07_clientes_por_estado.png")


def main():
    """Gera todos os 7 gráficos obrigatórios."""
    print("=" * 60)
    print("TECHPOP BI - GERAÇÃO DE GRÁFICOS ESTÁTICOS")
    print("=" * 60)
    
    engine = get_dw_engine()
    
    chart_01_produtos_mais_vendidos(engine)
    chart_02_faturamento_total(engine)
    chart_03_faturamento_categoria(engine)
    chart_04_faturamento_produto(engine)
    chart_05_comissoes(engine)
    chart_06_fornecedores_estado(engine)
    chart_07_clientes_estado(engine)
    
    print("=" * 60)
    print(f"TODOS OS 7 GRÁFICOS GERADOS EM: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
