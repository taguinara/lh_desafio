import streamlit as st


def mostrar_sobre():
    """
    Exibe as informações do projeto: tecnologias, funcionalidades e autoria.
    """

    st.title("ℹ️ Sobre o Sistema")
    st.subheader("Dashboard Analítico desenvolvido em Streamlit para a LH Nautical.")

    st.markdown("---")

    st.markdown("""
Dashboard desenvolvido como entrega do Desafio Lighthouse — Dados & IA.

***Tecnologias utilizadas:***

- **Streamlit** `1.32+` — Framework para criação de apps web interativos em Python
- **Pandas** `2.0+` — Manipulação, limpeza e análise de dados tabulares
- **Plotly Express / Graph Objects** `5.18+` — Visualizações interativas e gráficos dinâmicos
- **NumPy** `1.26+` — Operações numéricas e cálculo de similaridade de cosseno
- **Scikit-learn** `1.4+` — Modelo de regressão linear para previsão de demanda
- **Pathlib** — Gerenciamento de caminhos de arquivos de forma multiplataforma
    """)

    st.markdown("---")

    st.markdown("""
***Funcionalidades:***

🔍 **EDA** — Exploração dos dados brutos, problemas encontrados e estatísticas iniciais

🧹 **Limpeza** — Tratamento completo dos 4 datasets com antes e depois de cada etapa

📦 **Análise de Vendas** — Receita mensal, ranking de produtos e vendas por dia da semana

👥 **Clientes** — Top clientes por lucro, curva de Lorenz e distribuição por estado

⚠️ **Alertas** — Produtos vendendo abaixo do custo com ranking de impacto financeiro

🔮 **Previsão** — Regressão linear com projeção configurável de 1 a 12 meses

💡 **Recomendações** — Collaborative filtering com similaridade de cosseno entre clientes
    """)

    st.markdown("---")

    st.markdown("""
***Pipeline de dados:***

- **Fonte:** 4 arquivos brutos (`produtos_raw.csv`, `vendas_2023_2024.csv`,
  `clientes_crm.json`, `custos_importacao.json`)
- **ETL:** `etl_pipeline.py` — limpeza, normalização e integração dos datasets
- **Saída:** 5 CSVs processados em `data/processed/`
- **Modelagem:** Star Schema com 4 dimensões e 2 tabelas fato (`schema_e_queries.sql`)

***Estrutura do projeto:***

- `app_streamlit.py` — arquivo principal: configuração, sidebar e navegação
- `config.py` — cores, caminhos, tema Plotly e carregamento dos dados
- `eda.py` — análise exploratória dos dados brutos
- `limpeza.py` — tratamento e limpeza de cada dataset
- `vendas.py` — análise de faturamento, categorias e dias da semana
- `clientes.py` — ranking de clientes, Pareto e distribuição por estado
- `alertas.py` — produtos em prejuízo operacional
- `previsao.py` — modelo de regressão linear para previsão de demanda
- `recomendacao.py` — sistema de recomendação por collaborative filtering
- `sobre.py` — esta página
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.metric("Transações analisadas", "9.895")
    col2.metric("Produtos no catálogo",  "150")
    col3.metric("Clientes na base",      "49")

    st.markdown("---")

    st.markdown("""
***Autora:***

**Tainara Almeida**

Copyright © 2026 Tainara Almeida. Licença MIT.
    """)
