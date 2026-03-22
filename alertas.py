# Frente 5 — Produtos com Prejuízo Operacional
# Ranking de produtos que vendem abaixo do custo de importação

import streamlit as st
import pandas as pd
import plotly.express as px
from config import CORES, dark_layout


def mostrar_alertas(df_f):
    """
    Recebe o dataframe filtrado e exibe os produtos em situação de prejuízo.
    """

    st.header("⚠️ Produtos em Alerta — Prejuízo Operacional")
    st.markdown(
        "Aqui identifico os produtos que estão sendo vendidos abaixo do custo "
        "de importação. Cada venda desses produtos gera prejuízo para a empresa."
    )

    st.warning(
        "🚨 Ação urgente necessária: esses produtos precisam de revisão de preço "
        "ou suspensão imediata de vendas."
    )

    st.markdown("---")

    # ── Calcular prejuízos por produto
    prej = (
        df_f
        .groupby(["id_product", "product_name", "category"])
        .agg(
            receita    = ("total",      "sum"),
            custo      = ("cost_total", "sum"),
            lucro      = ("profit",     "sum"),
            qtd_vendas = ("id_product", "count"),
        )
        .reset_index()
        .query("lucro < 0")
        .sort_values("lucro")
    )

    # ── KPIs de alerta
    col1, col2, col3 = st.columns(3)
    col1.metric("Produtos em prejuízo",   f"{len(prej)}")
    col2.metric("Prejuízo total acumulado", f"R$ {prej['lucro'].sum()/1e6:.1f}M")
    col3.metric("Pior produto",
                prej["product_name"].iloc[0][:30] + "..." if len(prej) > 0 else "—")

    st.markdown("---")

    # ── Gráfico 1: ranking de prejuízo
    st.subheader("📊 Ranking de prejuízo por produto")
    st.markdown(
        "Quanto maior a barra vermelha, maior o prejuízo acumulado. "
        "O Motor Volvo Hydro Dash é o caso mais crítico."
    )

    fig = px.bar(
        prej.head(10),
        x="lucro", y="product_name", orientation="h",
        title="Top 10 produtos com maior prejuízo acumulado",
        labels={"lucro": "Prejuízo (R$)", "product_name": ""},
        color="category",
        color_discrete_map={
            "propulsao":   CORES["vermelho"],
            "eletronicos": CORES["ambar"],
            "ancoragem":   CORES["azul"],
        },
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    dark_layout(fig, height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Gráfico 2: prejuízo absoluto (impacto visual)
    st.subheader("📉 Impacto financeiro — prejuízo absoluto")

    prej_abs = prej.sort_values("lucro").head(10).copy()
    prej_abs["prejuizo_abs"] = prej_abs["lucro"].abs()

    fig2 = px.bar(
        prej_abs,
        x="prejuizo_abs", y="product_name", orientation="h",
        color="category",
        title="Magnitude do prejuízo por produto (valor absoluto)",
        labels={"prejuizo_abs": "Prejuízo absoluto (R$)", "product_name": ""},
        color_discrete_map={
            "propulsao":   CORES["vermelho"],
            "eletronicos": CORES["ambar"],
            "ancoragem":   CORES["azul"],
        },
    )
    fig2.update_layout(yaxis={"categoryorder": "total ascending"})
    dark_layout(fig2, height=420)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Causa raiz
    st.subheader("🔍 Por que isso aconteceu?")
    st.markdown("""
- O custo de importação está em **USD**
- Quando o dólar sobe, o custo em BRL aumenta automaticamente
- Mas o preço de venda no catálogo **não foi atualizado** junto
- Resultado: a empresa vende mais barato do que comprou

**Solução imediata:** atualizar os preços ou pausar as vendas desses produtos.
    """)

    st.markdown("---")

    # ── Tabela completa
    st.subheader("📋 Tabela de produtos em prejuízo")

    tbl = prej[["product_name", "category", "qtd_vendas", "receita", "custo", "lucro"]].copy()
    tbl["receita"] = tbl["receita"].apply(lambda x: f"R$ {x:,.2f}")
    tbl["custo"]   = tbl["custo"].apply(lambda x: f"R$ {x:,.2f}")
    tbl["lucro"]   = tbl["lucro"].apply(lambda x: f"R$ {x:,.2f}")
    tbl = tbl.rename(columns={
        "product_name": "Produto",
        "category":     "Categoria",
        "qtd_vendas":   "Vendas",
        "receita":      "Receita",
        "custo":        "Custo",
        "lucro":        "Prejuízo",
    }).reset_index(drop=True)

    st.dataframe(tbl, use_container_width=True, hide_index=True)
