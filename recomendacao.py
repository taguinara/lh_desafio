# Frente 7 — Sistema de Recomendação
# Collaborative filtering com similaridade de cosseno entre clientes

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from config import CORES, dark_layout


# ── Funções do algoritmo de recomendação
def cosine_sim(a, b):
    """
    Calcula a similaridade de cosseno entre dois vetores.
    Resultado entre 0 (nenhuma similaridade) e 1 (idênticos).
    """
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def recomendar(matrix, client_id, n=5):
    """
    Para um cliente, encontra os mais parecidos e recomenda
    produtos que eles compraram mas o cliente ainda não comprou.
    """
    if client_id not in matrix.index:
        return []

    # Vetor de compras do cliente alvo
    vec = matrix.loc[client_id].values

    # Calcula similaridade com todos os outros clientes
    sims = {
        outro: cosine_sim(vec, matrix.loc[outro].values)
        for outro in matrix.index
        if outro != client_id
    }

    # Pega os 5 clientes mais parecidos
    vizinhos = sorted(sims, key=sims.get, reverse=True)[:5]

    # Produtos que o cliente alvo ainda não comprou
    ja_comprou = set(matrix.columns[vec > 0])

    # Pontua produtos dos vizinhos
    scores = {}
    for viz in vizinhos:
        for prod in matrix.columns:
            if prod not in ja_comprou and matrix.loc[viz, prod] > 0:
                scores[prod] = scores.get(prod, 0) + sims[viz] * matrix.loc[viz, prod]

    # Retorna os N mais pontuados
    return sorted(scores, key=scores.get, reverse=True)[:n]


@st.cache_data
def build_matrix(data):
    """
    Cria a matriz cliente × produto com quantidade comprada.
    Células vazias (produto não comprado) = 0.
    """
    return data.pivot_table(
        index    = "id_client",
        columns  = "id_product",
        values   = "qtd",
        aggfunc  = "sum",
        fill_value = 0,
    )


def mostrar_recomendacao(df_f, produtos, clientes):
    """
    Exibe o sistema de recomendação com explicação didática.
    """

    st.header("💡 Sistema de Recomendação")
    st.markdown(
        "Aqui uso um algoritmo chamado *Collaborative Filtering* para recomendar "
        "produtos a cada cliente com base no que clientes parecidos compraram."
    )

    st.markdown("---")

    # ── Matriz de exemplo
    st.subheader("📊 Amostra da matriz cliente × produto")
    matrix = build_matrix(df_f)
    st.markdown(
        f"A matriz tem **{matrix.shape[0]} clientes** × **{matrix.shape[1]} produtos**. "
        "Mostrando apenas os 5 primeiros clientes e 8 primeiros produtos:"
    )
    st.dataframe(
        matrix.iloc[:5, :8],
        use_container_width=True,
    )

    st.markdown("---")

    # ── Seletor de cliente
    st.subheader("🎯 Gerar recomendações para um cliente")

    cli_op  = clientes[["id", "nome"]].sort_values("nome")
    cli_sel = st.selectbox(
        "Selecione o cliente:",
        cli_op["id"].tolist(),
        format_func=lambda i: cli_op.loc[cli_op["id"] == i, "nome"].values[0],
    )
    n_recs = st.slider("Quantas recomendações gerar?", 3, 10, 5)

    # ── Gerar recomendações
    recs     = recomendar(matrix, cli_sel, n=n_recs)
    nome_cli = cli_op.loc[cli_op["id"] == cli_sel, "nome"].values[0]

    if not recs:
        st.warning("Não foi possível gerar recomendações para este cliente.")
        return

    recs_df = (
        produtos[produtos["id"].isin(recs)]
        .set_index("id")
        .loc[recs]
        .reset_index()
    )

    # ── Mostrar recomendações em cards
    st.subheader(f"✅ Recomendações para {nome_cli}")

    for i, row in recs_df.iterrows():
        col1, col2, col3 = st.columns([4, 1, 1])
        col1.write(f"**{row['nome']}**")
        col2.write(f"R$ {row['price']:,.2f}")
        col3.write(f"`{row['category']}`")

    st.markdown("---")

    # ── Gráfico de recomendações
    fig = px.bar(
        recs_df,
        x="nome", y="price", color="category",
        title=f"Produtos recomendados para {nome_cli} — preço de venda",
        labels={"nome": "", "price": "Preço (R$)"},
        color_discrete_map={
            "propulsao":   CORES["azul"],
            "eletronicos": CORES["verde"],
            "ancoragem":   CORES["ambar"],
        },
    )
    fig.update_layout(xaxis_tickangle=-20)
    dark_layout(fig, height=380)
    st.plotly_chart(fig, use_container_width=True)

    # ── O que o cliente já comprou
    st.subheader(f"🛒 O que {nome_cli} já comprou?")

    ja_comprou_ids = list(matrix.columns[matrix.loc[cli_sel].values > 0])
    ja_comprou_df  = produtos[produtos["id"].isin(ja_comprou_ids)][["nome", "category", "price"]]
    ja_comprou_df["price"] = ja_comprou_df["price"].apply(lambda x: f"R$ {x:,.2f}")
    ja_comprou_df = ja_comprou_df.rename(columns={
        "nome":     "Produto",
        "category": "Categoria",
        "price":    "Preço",
    }).reset_index(drop=True)

    st.dataframe(ja_comprou_df, use_container_width=True, hide_index=True)
