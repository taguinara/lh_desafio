# vendas.py
# Frente 3 — Análise de Vendas
# Faturamento, categorias, produtos e vendas por dia da semana
# Tainara Almeida — LH Nautical Analytics

import streamlit as st
import pandas as pd
import plotly.express as px
from config import CORES, dark_layout, DIAS_PT


def mostrar_vendas(df_f):
    """
    Recebe o dataframe já filtrado pelo sidebar e exibe a análise de vendas.
    """

    st.header("📦 Análise de Vendas")
    st.markdown(
        "Aqui analiso o faturamento por período, por categoria e por produto, "
        "além de entender quais dias da semana vendem mais."
    )

    st.markdown("---")

    # ── KPIs
    st.subheader("💰 Resumo financeiro do período selecionado")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Receita total",  f"R$ {df_f['total'].sum()/1e9:.2f}B")
    col2.metric("Lucro bruto",    f"R$ {df_f['profit'].sum()/1e6:.1f}M")
    col3.metric("Margem média",   f"{df_f['margin_pct'].mean():.1f}%")
    col4.metric("Transações",     f"{len(df_f):,}")

    st.markdown("---")

    # ── Receita mensal por ano
    st.subheader("📅 Receita mensal — 2023 vs 2024")

    mensal = df_f.groupby(["year", "month"])["total"].sum().reset_index()
    mensal["periodo"] = pd.to_datetime(
        mensal["year"].astype(str) + "-" + mensal["month"].astype(str),
        format="%Y-%m"
    )
    fig = px.line(
        mensal, x="periodo", y="total", color="year",
        title="Evolução da receita mês a mês",
        labels={"total": "Receita (R$)", "periodo": "", "year": "Ano"},
        color_discrete_map={2023: CORES["azul"], 2024: CORES["verde"]},
    )
    dark_layout(fig, height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Receita por categoria
    st.subheader("🗂️ Receita e lucro por categoria")

    cat_stats = (
        df_f.groupby("category")
        .agg(receita=("total", "sum"), lucro=("profit", "sum"))
        .reset_index()
        .sort_values("receita", ascending=False)
    )
    cat_stats["margem"] = (cat_stats["lucro"] / cat_stats["receita"] * 100).round(1)
    cat_stats["receita_fmt"] = cat_stats["receita"].apply(lambda x: f"R$ {x/1e9:.2f}B")
    cat_stats["lucro_fmt"]   = cat_stats["lucro"].apply(lambda x: f"R$ {x/1e6:.1f}M")
    cat_stats["margem_fmt"]  = cat_stats["margem"].apply(lambda x: f"{x}%")

    st.dataframe(
        cat_stats[["category","receita_fmt","lucro_fmt","margem_fmt"]]
        .rename(columns={
            "category":    "Categoria",
            "receita_fmt": "Receita",
            "lucro_fmt":   "Lucro",
            "margem_fmt":  "Margem",
        }),
        use_container_width=True,
        hide_index=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.pie(
            cat_stats, names="category", values="receita",
            title="Participação na receita total",
            hole=0.45,
            color_discrete_sequence=[CORES["azul"], CORES["verde"], CORES["ambar"]],
        )
        fig2.update_traces(textfont_color="#FFFFFF")
        dark_layout(fig2, height=320)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        fig3 = px.bar(
            cat_stats, x="category", y="lucro",
            title="Lucro total por categoria",
            labels={"category": "Categoria", "lucro": "Lucro (R$)"},
            color="category",
            color_discrete_map={
                "eletronicos": CORES["azul"],
                "propulsao":   CORES["verde"],
                "ancoragem":   CORES["ambar"],
            },
        )
        dark_layout(fig3, height=320)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── Top 15 produtos
    st.subheader("🏆 Top 15 produtos por receita")

    top_prod = (
        df_f.groupby(["id_product", "product_name"])
        .agg(receita=("total", "sum"), lucro=("profit", "sum"))
        .reset_index()
        .sort_values("receita", ascending=False)
        .head(15)
    )
    fig4 = px.bar(
        top_prod, x="receita", y="product_name", orientation="h",
        color="lucro",
        color_continuous_scale=[
            [0, CORES["vermelho"]],
            [0.5, CORES["ambar"]],
            [1, CORES["verde"]],
        ],
        title="Top 15 produtos — receita (cor = lucro: vermelho=prejuízo, verde=lucro)",
        labels={"receita": "Receita (R$)", "product_name": ""},
    )
    fig4.update_layout(yaxis={"categoryorder": "total ascending"})
    dark_layout(fig4, height=500)
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # ── Vendas por dia da semana
    st.subheader("📆 Vendas médias por dia da semana")
    st.markdown(
        "Para calcular essa média eu usei todos os dias do calendário — "
        "incluindo os dias em que não teve nenhuma venda (valor zero). "
        "Isso evita inflar a média ignorando dias inativos."
    )

    # Cria calendário completo com todos os dias
    cal = pd.date_range(
        df_f["sale_date"].min(),
        df_f["sale_date"].max(),
        freq="D"
    )
    # Agrupa receita por dia e preenche dias sem venda com zero
    vd = (
        df_f.groupby("sale_date")["total"]
        .sum()
        .reindex(cal, fill_value=0)
        .reset_index()
    )
    vd.columns = ["data", "total"]
    vd["dia"]   = vd["data"].dt.day_name().map(DIAS_PT)
    vd["ordem"] = vd["data"].dt.dayofweek

    media_sem = (
        vd.groupby(["ordem", "dia"])["total"]
        .mean()
        .reset_index()
        .sort_values("ordem")
    )

    fig5 = px.bar(
        media_sem, x="dia", y="total",
        title="Receita média diária por dia da semana (inclui dias sem venda = R$ 0)",
        labels={"total": "Receita média (R$)", "dia": ""},
        color="total",
        color_continuous_scale=[[0, "#252a7a"], [1, CORES["azul"]]],
    )
    fig5.update_layout(coloraxis_showscale=False)
    dark_layout(fig5, height=380)
    st.plotly_chart(fig5, use_container_width=True)

    # Tabela resumo da semana
    media_sem["Receita Média"] = media_sem["total"].apply(lambda x: f"R$ {x:,.0f}")
    media_sem["Ranking"] = media_sem["total"].rank(ascending=False).astype(int)
    st.dataframe(
        media_sem[["dia", "Receita Média", "Ranking"]]
        .rename(columns={"dia": "Dia da Semana"})
        .sort_values("Ranking"),
        use_container_width=True,
        hide_index=True,
    )
