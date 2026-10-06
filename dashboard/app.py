"""
TECHPOP BI - DASHBOARD STREAMLIT
===================================
Dashboard interativo para Business Intelligence.
Todos os textos em MAIÚSCULO conforme requisito acadêmico.

Executar com: streamlit run dashboard/app.py
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from config.database import get_dw_engine
from dashboard.queries import (
    get_kpis,
    get_produtos_mais_vendidos,
    get_faturamento_temporal,
    get_faturamento_categoria,
    get_faturamento_produto,
    get_comissoes_vendedor,
    get_fornecedores_por_estado,
    get_clientes_por_estado,
    get_filtros_tempo,
)

# =============================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================
st.set_page_config(
    page_title="TECHPOP - BUSINESS INTELLIGENCE",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================
# ESTILO CSS CUSTOMIZADO
# =============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #F8FAFC;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #0284C7;
        margin-bottom: 1.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .sub-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #38BDF8;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        text-transform: uppercase;
    }
    .kpi-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%);
        border: 1px solid #334155;
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 700;
        margin: 0.3rem 0;
        color: #F8FAFC;
    }
    .kpi-label {
        font-size: 0.85rem;
        opacity: 0.85;
        text-transform: uppercase;
        color: #94A3B8;
        font-weight: 600;
    }
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #334155 !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_engine():
    """Cria engine do DW (cacheada)."""
    return get_dw_engine()


def format_currency(value: float) -> str:
    """Formata valor monetário."""
    return f"R$ {value:,.2f}"


def main():
    """Função principal do dashboard."""
    engine = get_engine()

    # =============================================
    # TÍTULO
    # =============================================
    st.markdown('<div class="main-header">📊 TECHPOP - BUSINESS INTELLIGENCE</div>', unsafe_allow_html=True)

    # =============================================
    # SIDEBAR - FILTROS
    # =============================================
    st.sidebar.markdown("## 🔍 FILTROS")

    try:
        filtros = get_filtros_tempo(engine)
    except Exception as e:
        st.error(f"ERRO AO CONECTAR AO DW: {e}")
        st.info("EXECUTE O PIPELINE PRIMEIRO: python main.py")
        return

    ano_selecionado = st.sidebar.selectbox("ANO", filtros["anos"], index=0)
    trimestre_selecionado = st.sidebar.selectbox("TRIMESTRE", filtros["trimestres"], index=0)
    mes_selecionado = st.sidebar.selectbox("MÊS", filtros["meses"], index=0)

    # Converter para parâmetros de consulta
    ano = ano_selecionado if ano_selecionado != "TODOS" else None
    trimestre = trimestre_selecionado if trimestre_selecionado != "TODOS" else None
    mes = mes_selecionado if mes_selecionado != "TODOS" else None

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ SOBRE")
    st.sidebar.markdown(
        "DASHBOARD DE BI DA TECHPOP.\n\n"
        "MODELO ESTRELA COM GRANULARIDADE: "
        "**UM REGISTRO POR ITEM DE VENDA.**"
    )

    # =============================================
    # KPIs
    # =============================================
    st.markdown('<div class="sub-header">📈 INDICADORES PRINCIPAIS</div>', unsafe_allow_html=True)

    kpis = get_kpis(engine, ano, trimestre, mes)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">FATURAMENTO TOTAL</div>
            <div class="kpi-value">{format_currency(kpis['faturamento_total'])}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">ITENS VENDIDOS</div>
            <div class="kpi-value">{kpis['qtd_itens_vendidos']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">PRODUTOS VENDIDOS</div>
            <div class="kpi-value">{kpis['qtd_produtos']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">COMISSÕES PAGAS</div>
            <div class="kpi-value">{format_currency(kpis['comissoes_pagas'])}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =============================================
    # GRÁFICOS - LINHA 1
    # =============================================
    col_left, col_right = st.columns(2)

    # 1. PRODUTOS MAIS VENDIDOS
    with col_left:
        st.markdown('<div class="sub-header">🏆 PRODUTOS MAIS VENDIDOS</div>', unsafe_allow_html=True)
        df_produtos = get_produtos_mais_vendidos(engine, ano, trimestre, mes)
        if not df_produtos.empty:
            fig = px.bar(
                df_produtos, x="QUANTIDADE", y="PRODUTO",
                orientation="h",
                color="QUANTIDADE",
                color_continuous_scale="Blues",
                title="PRODUTOS MAIS VENDIDOS (POR QUANTIDADE)",
            )
            fig.update_layout(
                yaxis=dict(autorange="reversed"),
                showlegend=False,
                font=dict(size=11),
                title_font_size=14,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("NENHUM DADO ENCONTRADO PARA O PERÍODO.")

    # 2. FATURAMENTO TEMPORAL
    with col_right:
        st.markdown('<div class="sub-header">📊 FATURAMENTO POR PERÍODO</div>', unsafe_allow_html=True)
        granularidade = st.selectbox("GRANULARIDADE", ["ANO", "TRIMESTRE", "MÊS"], index=0)
        df_fat_temporal = get_faturamento_temporal(engine, granularidade, ano, trimestre, mes)
        if not df_fat_temporal.empty:
            fig = px.line(
                df_fat_temporal, x="PERÍODO", y="FATURAMENTO",
                markers=True,
                title=f"EVOLUÇÃO DO FATURAMENTO POR {granularidade}",
            )
            fig.update_traces(line_color="#2E86AB", line_width=3)
            fig.update_layout(font=dict(size=11), title_font_size=14)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("NENHUM DADO ENCONTRADO PARA O PERÍODO.")

    # =============================================
    # GRÁFICOS - LINHA 2
    # =============================================
    col_left2, col_right2 = st.columns(2)

    # 3. FATURAMENTO POR CATEGORIA
    with col_left2:
        st.markdown('<div class="sub-header">📦 FATURAMENTO POR CATEGORIA</div>', unsafe_allow_html=True)
        df_cat = get_faturamento_categoria(engine, ano, trimestre, mes)
        if not df_cat.empty:
            fig = px.pie(
                df_cat, values="FATURAMENTO", names="CATEGORIA",
                title="FATURAMENTO POR CATEGORIA",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_layout(font=dict(size=11), title_font_size=14)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("NENHUM DADO ENCONTRADO PARA O PERÍODO.")

    # 4. FATURAMENTO POR PRODUTO
    with col_right2:
        st.markdown('<div class="sub-header">💰 FATURAMENTO POR PRODUTO</div>', unsafe_allow_html=True)
        df_prod = get_faturamento_produto(engine, ano, trimestre, mes)
        if not df_prod.empty:
            fig = px.bar(
                df_prod, x="FATURAMENTO", y="PRODUTO",
                orientation="h",
                color="CATEGORIA",
                title="FATURAMENTO POR PRODUTO",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig.update_layout(
                yaxis=dict(autorange="reversed"),
                font=dict(size=11),
                title_font_size=14,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("NENHUM DADO ENCONTRADO PARA O PERÍODO.")

    # =============================================
    # GRÁFICOS - LINHA 3
    # =============================================
    col_left3, col_right3 = st.columns(2)

    # 5. COMISSÕES POR VENDEDOR
    with col_left3:
        st.markdown('<div class="sub-header">💼 MAIORES COMISSÕES DE VENDEDORES</div>', unsafe_allow_html=True)
        df_com = get_comissoes_vendedor(engine, ano, trimestre, mes)
        if not df_com.empty:
            fig = px.bar(
                df_com, x="TOTAL COMISSÃO", y="VENDEDOR",
                orientation="h",
                color="TOTAL COMISSÃO",
                color_continuous_scale="Oranges",
                title="COMISSÕES POR VENDEDOR",
            )
            fig.update_layout(
                yaxis=dict(autorange="reversed"),
                showlegend=False,
                font=dict(size=11),
                title_font_size=14,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("NENHUM DADO ENCONTRADO PARA O PERÍODO.")

    # 6. CLIENTES POR ESTADO
    with col_right3:
        st.markdown('<div class="sub-header">👥 CLIENTES POR ESTADO</div>', unsafe_allow_html=True)
        df_cli = get_clientes_por_estado(engine, ano, trimestre, mes)
        if not df_cli.empty:
            fig = px.bar(
                df_cli, x="ESTADO", y="QTD CLIENTES",
                color="REGIÃO",
                title="QUANTIDADE DE CLIENTES POR ESTADO",
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig.update_layout(font=dict(size=11), title_font_size=14)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("NENHUM DADO ENCONTRADO PARA O PERÍODO.")

    # =============================================
    # GRÁFICOS - LINHA 4
    # =============================================
    st.markdown('<div class="sub-header">🏭 FORNECEDORES POR ESTADO</div>', unsafe_allow_html=True)
    df_forn = get_fornecedores_por_estado(engine, ano, trimestre, mes)
    if not df_forn.empty:
        fig = px.bar(
            df_forn, x="ESTADO", y="QTD FORNECEDORES",
            color="REGIÃO",
            title="QUANTIDADE DE FORNECEDORES POR ESTADO",
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig.update_layout(font=dict(size=11), title_font_size=14)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("NENHUM DADO ENCONTRADO PARA O PERÍODO.")

    # =============================================
    # RODAPÉ
    # =============================================
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#888; font-size:0.8rem;'>"
        "TECHPOP BI © 2024 | PROJETO ACADÊMICO DE BUSINESS INTELLIGENCE | "
        "GRANULARIDADE: UM REGISTRO POR ITEM DE VENDA"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
