import streamlit as st
from config import carregar_dados

# Importa cada módulo de análise
from eda          import mostrar_eda
from limpeza      import mostrar_limpeza
from vendas       import mostrar_vendas
from clientes     import mostrar_clientes
from alertas      import mostrar_alertas
from previsao     import mostrar_previsao
from recomendacao import mostrar_recomendacao
from sobre        import mostrar_sobre

# ──────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LH Nautical — Analytics",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# TEMA VISUAL - CSS de cor dos gráficos, filtros...
# ──────────────────────────────────────────────────────────────
st.markdown("""
    <style>
        /* Fundo principal e sidebar */
        .stApp                          { background-color: #191970 !important; }
        [data-testid="stSidebar"]       { background-color: #0d1b4b !important; }
        [data-testid="stSidebarContent"]{ background-color: #0d1b4b !important; }

        /* Textos gerais em branco */
        html, body                      { color: #FFFFFF !important; }
        h1, h2, h3, h4, h5, h6         { color: #FFFFFF !important; }
        label, p                        { color: #FFFFFF !important; }
        [data-testid="stSidebar"] label { color: #FFFFFF !important; }
        [data-testid="stMarkdownContainer"] { color: #FFFFFF !important; }
        .stApp > div                    { color: #FFFFFF !important; }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"]   { background-color: #0d1b4b !important; gap: 4px; }
        .stTabs [data-baseweb="tab"]        { background-color: #1a1f6e !important;
                                              color: #FFFFFF !important;
                                              border-radius: 6px 6px 0 0; }
        .stTabs [aria-selected="true"]      { background-color: #185FA5 !important;
                                              color: #FFFFFF !important; }

        /* Métricas */
        [data-testid="stMetric"]            { background-color: #0d1b4b !important;
                                              border-radius: 8px; padding: 12px;
                                              border: 1px solid #252a7a; }
        [data-testid="stMetricLabel"] *     { color: #AACCEE !important; }
        [data-testid="stMetricValue"] *     { color: #FFFFFF !important; }
        [data-testid="stMetricDelta"] *     { color: #1D9E75 !important; }

        /* Multiselect — caixa */
        .stMultiSelect > div > div          { background-color: #0d1b4b !important;
                                              border: 1px solid #252a7a !important; }

        /* Multiselect — tags VERMELHAS */
        div[data-baseweb="tag"]             { background-color: #E24B4A !important;
                                              border-color: #E24B4A !important; }
        div[data-baseweb="tag"] span        { color: #FFFFFF !important;
                                              background-color: transparent !important; }
        div[data-baseweb="tag"] span[role]  { color: #FFFFFF !important; }
        div[data-baseweb="tag"] button      { color: #FFFFFF !important;
                                              background-color: transparent !important; }
        div[data-baseweb="tag"] button svg  { fill: #FFFFFF !important; }
        .stMultiSelect input                { color: #FFFFFF !important; }

        /* Selectbox */
        .stSelectbox > div > div            { background-color: #0d1b4b !important;
                                              border: 1px solid #252a7a !important; }
        [data-baseweb="select"] > div       { background-color: #0d1b4b !important;
                                              color: #FFFFFF !important; }

        /* Dropdown de opções */
        [data-baseweb="popover"]            { background-color: #0d1b4b !important; }
        [data-baseweb="popover"] *          { background-color: #0d1b4b !important;
                                              color: #FFFFFF !important; }
        [role="listbox"]                    { background-color: #0d1b4b !important; }
        [role="option"]                     { background-color: #0d1b4b !important;
                                              color: #FFFFFF !important; }
        [role="option"]:hover               { background-color: #185FA5 !important; }

        /* Slider */
        [data-testid="stSlider"] *          { color: #FFFFFF !important; }

        /* Alertas */
        [data-testid="stAlert"]             { background-color: #1a1f6e !important;
                                              border-color: #185FA5 !important; }
        [data-testid="stAlert"] *           { color: #FFFFFF !important; }

        /* Divisores e containers */
        hr                                  { border-color: #252a7a !important; }
        [data-testid="block-container"]     { background-color: transparent !important; }
        [data-testid="stVerticalBlock"]     { background-color: transparent !important; }

        /* Caption */
        .stCaption, small                   { color: #AACCEE !important; }

        /* Scrollbar */
        ::-webkit-scrollbar                 { width: 6px; background: #0d1b4b; }
        ::-webkit-scrollbar-thumb           { background: #185FA5; border-radius: 3px; }
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# CARREGAMENTO DOS DADOS
# ──────────────────────────────────────────────────────────────
df, produtos, clientes = carregar_dados()

# ──────────────────────────────────────────────────────────────
# SIDEBAR — filtros globais
# ──────────────────────────────────────────────────────────────
st.sidebar.header("⚓ LH Nautical")
st.sidebar.markdown("---")
st.sidebar.header("Filtros")

anos     = sorted(df["year"].dropna().astype(int).unique())
anos_sel = st.sidebar.multiselect("Ano", anos, default=anos)

cats     = sorted(df["category"].dropna().unique())
cats_sel = st.sidebar.multiselect("Categoria", cats, default=cats)

# Aplica os filtros em todo o app
df_f = df[df["year"].isin(anos_sel) & df["category"].isin(cats_sel)]

st.sidebar.markdown("---")
st.sidebar.caption(f"**{len(df_f):,}** transações selecionadas")

# ──────────────────────────────────────────────────────────────
# ABAS DE NAVEGAÇÃO
# ──────────────────────────────────────────────────────────────
aba1, aba2, aba3, aba4, aba5, aba6, aba7, aba8 = st.tabs([
    "🔍 EDA",
    "🧹 Limpeza",
    "📦 Vendas",
    "👥 Clientes",
    "⚠️ Alertas",
    "🔮 Previsão",
    "💡 Recomendações",
    "ℹ️ Sobre",
])

# ──────────────────────────────────────────────────────────────
# RENDERIZAÇÃO DE CADA ABA
# ──────────────────────────────────────────────────────────────
with aba1:
    mostrar_eda(df_f, produtos, clientes)

with aba2:
    mostrar_limpeza(df_f, produtos, clientes)

with aba3:
    mostrar_vendas(df_f)

with aba4:
    mostrar_clientes(df_f, clientes)

with aba5:
    mostrar_alertas(df_f)

with aba6:
    mostrar_previsao(df_f)

with aba7:
    mostrar_recomendacao(df_f, produtos, clientes)

with aba8:
    mostrar_sobre()

# ──────────────────────────────────────────────────────────────
# RODAPÉ
# ──────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("LH Nautical Analytics · Desafio Lighthouse · Dados & IA · © 2026 Tainara Almeida")
