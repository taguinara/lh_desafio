# Frente 4 — Análise de Clientes
# Ranking por lucro, concentração (Pareto) e distribuição por estado

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import CORES, dark_layout


def mostrar_clientes(df_f, clientes):
    """
    Recebe o dataframe filtrado e o dataframe de clientes e exibe a análise.
    """

    st.header("👥 Análise de Clientes")
    st.markdown(
        "Aqui entendo quais clientes geram mais lucro, como a riqueza está "
        "concentrada na base e de onde eles vêm geograficamente."
    )

    st.markdown("---")

    # ── Preparar dados de clientes com lucro
    cli_base = clientes[["id", "nome"]].copy()
    cli_base["state"] = (
        clientes["state"].fillna("").astype(str).str.upper().str.strip()
    )

    # Agrupa lucro por cliente — sem incluir state no groupby para evitar erro
    cli_lucro = (
        df_f
        .merge(cli_base[["id", "nome"]], left_on="id_client", right_on="id", how="left")
        .groupby(["id_client", "nome"], as_index=False)
        .agg(
            lucro       = ("profit",     "sum"),
            receita     = ("total",      "sum"),
            transacoes  = ("id_client",  "count"),
        )
        .sort_values("lucro", ascending=False)
    )
    # Junta estado depois do groupby
    cli_lucro = cli_lucro.merge(
        cli_base[["id", "state"]].rename(columns={"id": "id_client"}),
        on="id_client", how="left"
    )
    cli_lucro["state"] = cli_lucro["state"].fillna("")

    # ── KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de clientes",       f"{len(cli_lucro)}")
    col2.metric("Lucro do top 1 cliente",  f"R$ {cli_lucro['lucro'].max()/1e6:.2f}M")
    col3.metric("Lucro médio por cliente", f"R$ {cli_lucro['lucro'].mean()/1e3:.0f}K")

    st.markdown("---")

    # ── Top N clientes
    st.subheader("🏆 Clientes com maior lucro gerado")

    top_n = st.slider("Quantos clientes exibir?", 5, 49, 10)

    fig = px.bar(
        cli_lucro.head(top_n),
        x="lucro", y="nome", orientation="h",
        title=f"Top {top_n} clientes por lucro acumulado",
        labels={"lucro": "Lucro (R$)", "nome": ""},
        color="lucro",
        color_continuous_scale=[[0, "#252a7a"], [1, CORES["verde"]]],
        height=max(350, top_n * 30),
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    dark_layout(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Curva de Lorenz (concentração de lucro)
    st.subheader("📈 Concentração de lucro — Curva de Lorenz")
    st.markdown(
        "Essa curva mostra o quanto o lucro está concentrado em poucos clientes. "
        "Quanto mais a linha azul se afasta da diagonal pontilhada, "
        "maior a concentração. No nosso caso, 20% dos clientes respondem por ~60% do lucro."
    )

    pos = (
        cli_lucro[cli_lucro["lucro"] > 0]
        .sort_values("lucro", ascending=False)
        .reset_index(drop=True)
    )
    pos["acum_pct"] = pos["lucro"].cumsum() / pos["lucro"].sum() * 100
    pos["rank_pct"] = (pos.index + 1) / len(pos) * 100

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=pos["rank_pct"], y=pos["acum_pct"],
        mode="lines", fill="tozeroy",
        name="Lucro acumulado",
        line=dict(color=CORES["azul"]),
        fillcolor="rgba(24,95,165,0.25)",
    ))
    fig2.add_shape(
        type="line", x0=0, x1=100, y0=0, y1=100,
        line=dict(color=CORES["cinza"], dash="dash"),
    )
    fig2.add_annotation(
        x=20, y=60,
        text="20% dos clientes → ~60% do lucro",
        font=dict(color="#FFFFFF", size=12),
        showarrow=True, arrowcolor="#FFFFFF",
    )
    fig2.update_layout(
        title="Curva de Lorenz — concentração de lucro por cliente",
        xaxis_title="% de clientes (ranking)",
        yaxis_title="% de lucro acumulado",
    )
    dark_layout(fig2, height=380)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Distribuição por estado
    st.subheader("🗺️ Receita por estado")

    mapa = (
        cli_lucro[cli_lucro["state"] != ""]
        .groupby("state", as_index=False)
        .agg(receita=("receita", "sum"), lucro=("lucro", "sum"))
        .sort_values("receita", ascending=True)
    )

    if not mapa.empty:
        fig3 = px.bar(
            mapa,
            x="receita", y="state", orientation="h",
            title="Receita por estado (UF)",
            labels={"receita": "Receita (R$)", "state": "Estado"},
            color="receita",
            color_continuous_scale=[[0, "#252a7a"], [1, CORES["azul"]]],
        )
        fig3.update_layout(coloraxis_showscale=False, yaxis_title="")
        dark_layout(fig3, height=max(300, len(mapa) * 28))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Sem dados de estado para exibir.")

    st.markdown("---")

    # ── Tabela detalhada
    st.subheader("📋 Tabela detalhada de clientes")

    tbl = cli_lucro[["nome", "state", "transacoes", "receita", "lucro"]].copy()
    tbl["receita"] = tbl["receita"].apply(lambda x: f"R$ {x:,.2f}")
    tbl["lucro"]   = tbl["lucro"].apply(lambda x: f"R$ {x:,.2f}")
    tbl = tbl.rename(columns={
        "nome":       "Cliente",
        "state":      "UF",
        "transacoes": "Transações",
        "receita":    "Receita",
        "lucro":      "Lucro",
    }).reset_index(drop=True)

    st.dataframe(tbl, use_container_width=True, hide_index=True)
