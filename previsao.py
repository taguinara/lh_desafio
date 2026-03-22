# Frente 6 — Previsão de Demanda
# Modelo de regressão linear para prever quantidade vendida por produto

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from config import CORES, dark_layout


def mostrar_previsao(df_f):
    """
    Recebe o dataframe filtrado e exibe o modelo de previsão de demanda.
    """

    st.header("🔮 Previsão de Demanda")
    st.markdown(
        "Aqui uso um modelo de regressão linear para prever a quantidade "
        "que cada produto vai vender nos próximos meses. "
        "O modelo aprende com o histórico de 2023-2024 e projeta a tendência."
    )

    st.markdown("---")

    # ── Seletor de produto
    st.subheader("📦 Selecione um produto para prever")

    prod_op = (
        df_f.groupby(["id_product", "product_name"])["total"]
        .sum()
        .reset_index()
        .sort_values("total", ascending=False)
        .head(20)
    )

    prod_sel = st.selectbox(
        "Produto:",
        prod_op["id_product"].tolist(),
        format_func=lambda i: prod_op.loc[
            prod_op["id_product"] == i, "product_name"
        ].values[0],
    )

    meses_prev = st.slider("Quantos meses prever?", 1, 12, 3)

    # ── Preparar série temporal
    serie = (
        df_f[df_f["id_product"] == prod_sel]
        .groupby(["year", "month"])["qtd"]
        .sum()
        .reset_index()
        .sort_values(["year", "month"])
    )
    serie["t"] = range(len(serie))
    serie["periodo"] = pd.to_datetime(
        serie["year"].astype(str) + "-" + serie["month"].astype(str),
        format="%Y-%m"
    )

    if len(serie) < 4:
        st.warning("Este produto tem histórico insuficiente para previsão (mínimo 4 meses).")
        return

    # ── Treinar modelo
    lr = LinearRegression()
    lr.fit(serie[["t"]], serie["qtd"])
    r2 = lr.score(serie[["t"]], serie["qtd"])

    # ── Gerar previsão
    datas_prev = pd.date_range(
        start  = serie["periodo"].max() + pd.DateOffset(months=1),
        periods= meses_prev,
        freq   = "MS",
    )
    qtd_prev = [
        max(0, lr.predict([[len(serie) + i]])[0])
        for i in range(meses_prev)
    ]

    # ── Gráfico
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=serie["periodo"], y=serie["qtd"],
        mode="lines+markers", name="Histórico real",
        line=dict(color=CORES["azul"], width=2),
        marker=dict(size=6),
    ))
    fig.add_trace(go.Scatter(
        x=datas_prev, y=qtd_prev,
        mode="lines+markers", name="Previsão",
        line=dict(color=CORES["verde"], dash="dash", width=2),
        marker=dict(symbol="diamond", size=8),
    ))
    # Linha divisória entre histórico e previsão
    # Convertendo para string para evitar erro com Timestamp no Plotly
    fig.add_vline(
        x=str(serie["periodo"].max()),
        line=dict(color=CORES["ambar"], dash="dot", width=1),
    )
    fig.update_layout(
        title=f"Previsão de demanda — R² = {r2:.3f}",
        yaxis_title="Quantidade vendida",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    dark_layout(fig, height=420)
    st.plotly_chart(fig, use_container_width=True)

    # ── Tabela de previsão
    st.subheader("📋 Valores previstos")

    tbl_prev = pd.DataFrame({
        "Mês":           datas_prev.strftime("%B/%Y"),
        "Qtd Prevista":  [f"{round(q, 1)} unidades" for q in qtd_prev],
        "Tendência":     ["↗ Alta" if qtd_prev[i] > (qtd_prev[i-1] if i > 0 else qtd_prev[0])
                          else "↘ Queda" if qtd_prev[i] < (qtd_prev[i-1] if i > 0 else qtd_prev[0])
                          else "→ Estável"
                          for i in range(len(qtd_prev))],
    })
    st.dataframe(tbl_prev, use_container_width=True, hide_index=True)

    # ── Métricas do modelo
    st.markdown("---")
    st.subheader("📐 Métricas do modelo")

    col1, col2, col3 = st.columns(3)
    col1.metric("R² (qualidade da tendência)", f"{r2:.3f}")
    col2.metric("Meses de histórico usados",   f"{len(serie)}")
    col3.metric("Inclinação (tend. mensal)",
                f"{'↗ +' if lr.coef_[0] > 0 else '↘ '}{abs(lr.coef_[0]):.1f} un/mês")