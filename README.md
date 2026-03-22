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
├── schema_e_queries.sql
├── requirements.txt
└── data/
    ├── raw/
    └── processed/
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

5. Rode o dashboard
```bash
streamlit run app_streamlit.py
```

5. Autora do projeto
```bash
Tainara Almeida
```

## 📄 Licença

**Copyright (c) 2026 Tainara Almeida**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
