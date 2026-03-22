# Frente 1 — Análise Exploratória dos Dados (EDA)
# Dados brutos, problemas encontrados e estatísticas iniciais

import streamlit as st
import pandas as pd
import plotly.express as px
from config import CORES, dark_layout


def mostrar_eda(df, produtos, clientes):
    """
    Recebe os três dataframes já carregados e exibe a análise exploratória.
    """

    st.header("🔍 Análise Exploratória dos Dados")
    st.markdown(
        "Nesta etapa eu explorei os dados brutos para entender o que tinha disponível, "
        "quais eram os problemas e o que precisava ser corrigido antes de qualquer análise."
    )

    st.markdown("---")

    # ── Inventário dos arquivos
    st.subheader("📁 Inventário dos arquivos recebidos")

    inventario = pd.DataFrame({
        "Arquivo":     ["produtos_raw.csv", "vendas_2023_2024.csv",
                        "clientes_crm.json", "custos_importacao.json"],
        "Registros":   ["157 linhas", "9.895 transações", "49 clientes", "150 produtos"],
        "Formato":     ["CSV", "CSV", "JSON", "JSON"],
        "Problemas":   [
            "1 duplicata, 15 variações de categoria, preço como string",
            "Datas em 2 formatos diferentes",
            "30 emails com # no lugar de @, localização inconsistente",
            "Preços em USD, múltiplas vigências por produto",
        ],
    })
    st.dataframe(inventario, use_container_width=True, hide_index=True)
    
    st.markdown("---")

    # ── Estatísticas descritivas
    st.subheader("📊 Estatísticas descritivas das vendas")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de transações", f"{len(df):,}")
    col2.metric("Receita total",        f"R$ {df['total'].sum()/1e9:.2f}B")
    col3.metric("Ticket médio",         f"R$ {df['total'].mean():,.0f}")
    col4.metric("Período",              "Jan/2023 – Dez/2024")

    st.markdown("---")

    # ── Distribuição de vendas por categoria
    st.subheader("📦 Distribuição de transações por categoria")

    cat_count = df.groupby("category").size().reset_index(name="transacoes")
    fig = px.bar(
        cat_count,
        x="category", y="transacoes",
        title="Quantidade de transações por categoria",
        labels={"category": "Categoria", "transacoes": "Nº de transações"},
        color="category",
        color_discrete_map={
            "eletronicos": CORES["azul"],
            "propulsao":   CORES["verde"],
            "ancoragem":   CORES["ambar"],
        },
    )
    dark_layout(fig, height=350)
    st.plotly_chart(fig, use_container_width=True)

    # ── Distribuição de preços dos produtos
    st.subheader("💰 Distribuição de preços dos produtos")

    fig2 = px.histogram(
        produtos, x="price",
        nbins=30,
        title="Distribuição de preços do catálogo",
        labels={"price": "Preço (R$)", "count": "Qtd de produtos"},
        color_discrete_sequence=[CORES["azul"]],
    )
    dark_layout(fig2, height=350)
    st.plotly_chart(fig2, use_container_width=True)

    # ── Amostra dos dados brutos
    st.subheader("🗂️ Amostra dos dados processados")

    opcao = st.selectbox(
        "Qual tabela você quer visualizar?",
        ["Vendas (df_main)", "Produtos", "Clientes"]
    )

    if opcao == "Vendas (df_main)":
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    elif opcao == "Produtos":
        st.dataframe(produtos.head(10), use_container_width=True, hide_index=True)
    else:
        st.dataframe(clientes.head(10), use_container_width=True, hide_index=True)
