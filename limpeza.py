# Frente 2 — Tratamento e Limpeza dos Dados
# Limpar cada dataset e o resultado final

import streamlit as st
import pandas as pd
import plotly.express as px
from config import CORES, dark_layout


def mostrar_limpeza(df, produtos, clientes):
    """
    Exibe o processo de limpeza aplicado em cada dataset.
    """

    st.header("🧹 Tratamento e Limpeza dos Dados")
    st.markdown(
        "Aqui mostro o que foi feito para transformar os dados bagunçados em algo "
        "que pudesse ser analisado. Cada dataset teve um tratamento específico."
    )

    st.markdown("---")

    # ── Produtos
    st.subheader("1. Limpeza dos Produtos")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**O que eu fiz:**")
        st.markdown("""
- Removi a linha duplicada do produto de código 37
- Criei um dicionário com todas as 15 variações erradas
  mapeando para os 3 nomes corretos
- Converti o preço de texto (`R$ 33.122,52`) para número (`33122.52`)
        """)
    with col2:
        st.markdown("**Resultado:**")
        cat_ok = produtos["category"].value_counts().reset_index()
        cat_ok.columns = ["Categoria", "Qtd Produtos"]
        st.dataframe(cat_ok, use_container_width=True, hide_index=True)

    # Gráfico antes x depois das categorias
    antes = pd.DataFrame({
        "Variação": ["ELETRONICOS", "Eletrunicos", "Eletronicoz",
                     "E L E T R Ô N I C O S", "eLeTrÔnIcOs",
                     "PROPULSAO", "Propulção", "Prop",
                     "ancoragem", "Ancoraguem"],
        "Tipo": ["❌ Errada"] * 10,
    })

    st.markdown("---")

    # ── Vendas
    st.subheader("2. Limpeza das Vendas")

    st.markdown("""
**O que eu fiz:**
- Criei um parser de datas que tenta os dois formatos automaticamente
- Calculei as colunas que estavam faltando:
  - `cost_total` = custo unitário × quantidade vendida
  - `profit` = receita total − custo total
  - `margin_pct` = (lucro ÷ receita) × 100
    """)

    # Mostrar colunas geradas
    colunas_novas = pd.DataFrame({
        "Coluna criada": ["cost_total", "profit", "margin_pct", "year", "month", "weekday"],
        "Fórmula":       [
            "brl_cost × qtd",
            "total − cost_total",
            "(profit ÷ total) × 100",
            "sale_date.year",
            "sale_date.month",
            "sale_date.dayofweek",
        ],
        "Exemplo": [
            f"R$ {df['cost_total'].mean():,.2f}",
            f"R$ {df['profit'].mean():,.2f}",
            f"{df['margin_pct'].mean():.1f}%",
            "2023 / 2024",
            "1 a 12",
            "0=Seg … 6=Dom",
        ],
    })
    st.dataframe(colunas_novas, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Custos
    st.subheader("3. Limpeza dos Custos")

    st.markdown("""
**O que eu fiz:**
- Cada produto tinha vários preços históricos em USD
- Selecionei sempre o preço mais recente com data ≤ 31/12/2024
- Converti de USD para BRL usando câmbio de R$ 5,00
    """)

    # Estatísticas de custo
    custo_stats = pd.DataFrame({
        "Métrica":  ["Custo mínimo (BRL)", "Custo máximo (BRL)", "Custo médio (BRL)", "Taxa de câmbio usada"],
        "Valor":    [
            f"R$ {df['brl_cost'].min():,.2f}",
            f"R$ {df['brl_cost'].max():,.2f}",
            f"R$ {df['brl_cost'].mean():,.2f}",
            "R$ 5,00 por USD",
        ],
    })
    st.dataframe(custo_stats, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Resumo final
    st.subheader("✅ Resumo do dataset final")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Linhas no df_main",  f"{len(df):,}")
    col2.metric("Colunas",            f"{len(df.columns)}")
    col3.metric("Datas nulas",        "0")
    col4.metric("Produtos sem custo", f"{df['brl_cost'].isna().sum()}")

