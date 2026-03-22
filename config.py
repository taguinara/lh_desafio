# Configurações globais do projeto: cores, caminhos e funções compartilhadas

import streamlit as st
import pandas as pd
from pathlib import Path

# ──────────────────────────────────────────────────────────────
# CAMINHOS
# ──────────────────────────────────────────────────────────────
# BASE_DIR aponta para a pasta onde o app está salvo
BASE_DIR = Path(__file__).parent.resolve()
PROC     = BASE_DIR / "data" / "processed"

# ──────────────────────────────────────────────────────────────
# PALETA DE CORES
# ──────────────────────────────────────────────────────────────
CORES = {
    "azul":     "#185FA5",
    "verde":    "#1D9E75",
    "ambar":    "#BA7517",
    "vermelho": "#E24B4A",
    "cinza":    "#4a6fa5",
}

# Cores do tema de fundo
BG_MAIN = "#191970"   # midnight blue — fundo principal
BG_PLOT = "#0d1b4b"   # fundo dos gráficos
GRID    = "#252a7a"   # linhas de grade
TEXTO   = "#FFFFFF"   # cor de todos os textos

# ──────────────────────────────────────────────────────────────
# TRADUÇÃO DOS DIAS DA SEMANA
# ──────────────────────────────────────────────────────────────
DIAS_PT = {
    "Monday":    "Segunda",
    "Tuesday":   "Terça",
    "Wednesday": "Quarta",
    "Thursday":  "Quinta",
    "Friday":    "Sexta",
    "Saturday":  "Sábado",
    "Sunday":    "Domingo",
}

# ──────────────────────────────────────────────────────────────
# FUNÇÃO: aplicar tema escuro em gráficos Plotly
# ──────────────────────────────────────────────────────────────
def dark_layout(fig, height=None):
    """
    Recebe um gráfico Plotly e aplica o tema escuro do projeto.
    Chame essa função antes de todo st.plotly_chart().
    """
    updates = dict(
        paper_bgcolor = BG_MAIN,
        plot_bgcolor  = BG_PLOT,
        font          = dict(color=TEXTO, family="Arial"),
        title_font    = dict(color=TEXTO),
        legend        = dict(
            font        = dict(color=TEXTO),
            bgcolor     = BG_PLOT,
            bordercolor = GRID,
            borderwidth = 1,
        ),
        xaxis = dict(
            tickfont    = dict(color=TEXTO),
            title_font  = dict(color=TEXTO),
            gridcolor   = GRID,
            linecolor   = GRID,
            zerolinecolor = GRID,
        ),
        yaxis = dict(
            tickfont    = dict(color=TEXTO),
            title_font  = dict(color=TEXTO),
            gridcolor   = GRID,
            linecolor   = GRID,
            zerolinecolor = GRID,
        ),
        coloraxis_colorbar = dict(
            tickfont   = dict(color=TEXTO),
            title_font = dict(color=TEXTO),
        ),
    )
    if height:
        updates["height"] = height
    fig.update_layout(**updates)
    return fig

# ──────────────────────────────────────────────────────────────
# FUNÇÃO: carregar os dados processados (com cache)
# ──────────────────────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    """
    Lê os CSVs gerados pelo etl_pipeline.py.
    O @st.cache_data faz o Streamlit guardar os dados na memória
    para não precisar ler o arquivo toda vez que a página atualiza.
    """
    df       = pd.read_csv(PROC / "df_main.csv",        parse_dates=["sale_date"])
    produtos = pd.read_csv(PROC / "produtos_clean.csv")
    clientes = pd.read_csv(PROC / "clientes_clean.csv")

    # Padroniza nomes de colunas
    df.columns       = df.columns.str.lower().str.strip()
    produtos.columns = produtos.columns.str.lower().str.strip()
    clientes.columns = clientes.columns.str.lower().str.strip()

    # Garante que colunas opcionais existam mesmo se não foram geradas pelo ETL
    for col in ["state", "city", "flag_nome_suspeito"]:
        if col not in clientes.columns:
            clientes[col] = ""

    clientes["state"] = (
        clientes["state"].fillna("").astype(str).str.upper().str.strip()
    )

    return df, produtos, clientes
