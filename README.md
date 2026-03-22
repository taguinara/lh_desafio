# ⚓ LH Nautical — Analytics Dashboard

Dashboard analítico desenvolvido para o Desafio Lighthouse de Dados & IA, 2026.

## Tecnologias
- Python 3.10+
- Streamlit · Pandas · Plotly · Scikit-learn · NumPy

## Estrutura
```
lh_nautical/
├── app_streamlit.py
├── config.py
├── eda.py
├── limpeza.py
├── vendas.py
├── clientes.py
├── alertas.py
├── previsao.py
├── recomendacao.py
├── sobre.py
├── etl_pipeline.py
├── criar_bd_lh.py       
├── schema_e_queries.sql
├── queries_sqlite.sql    
├── requirements.txt
├── lh_nautical.db         
└── data/
    ├── raw/
    │   ├── produtos_raw.csv
    │   ├── vendas_2023_2024.csv
    │   ├── clientes_crm.json
    │   └── custos_importacao.json
    └── processed/
        ├── df_main.csv
        ├── produtos_clean.csv
        ├── clientes_clean.csv
        ├── custos_vigentes.csv
        └── custos_historico.csv
```

## Como executar

1. Clone o repositório
```bash
git clone https://github.com/taguinara/lh_desafio
cd lh-nautical
```

2. Crie e ative o ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

3. Instale as dependências
```bash
pip install -r requirements.txt
```

4. Adicione os arquivos brutos em `data/raw/` e rode o ETL
```bash
python etl_pipeline.py
```

5. Crie o banco de dados SQLite
```bash
python criar_bd_lh.py
```

6. Rode o app streamlit
```bash
streamlit run app_streamlit.py
```

7. Autora do projeto
```bash
Tainara Almeida
```

## 📄 Licença

**Copyright (c) 2026 Tainara Almeida**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
