# Cria o banco de dados SQLite e carrega os dados dos CSVs processados

import sqlite3
import pandas as pd
from pathlib import Path

# ──────────────────────────────────────────────────────────────
# CAMINHOS
# ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
PROC     = BASE_DIR / "data" / "processed"
DB_PATH  = BASE_DIR / "lh_nautical.db"

# ──────────────────────────────────────────────────────────────
# CONEXÃO COM O BANCO
# ──────────────────────────────────────────────────────────────
print("=" * 55)
print("  LH NAUTICAL — CRIAÇÃO DO BANCO SQLite")
print("=" * 55)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Ativa suporte a chaves estrangeiras
cursor.execute("PRAGMA foreign_keys = ON")

# ──────────────────────────────────────────────────────────────
# 1. TABELAS
# ──────────────────────────────────────────────────────────────
print("\n[1/3] Criando tabelas...")

cursor.executescript("""

    DROP TABLE IF EXISTS fato_vendas;
    DROP TABLE IF EXISTS fato_custos_historico;
    DROP TABLE IF EXISTS dim_produtos;
    DROP TABLE IF EXISTS dim_clientes;
    DROP TABLE IF EXISTS dim_categorias;
    DROP TABLE IF EXISTS dim_tempo;

    -- Categorias
    CREATE TABLE dim_categorias (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    );

    -- Produtos
    CREATE TABLE dim_produtos (
        id           INTEGER PRIMARY KEY,
        nome         TEXT    NOT NULL,
        preco_brl    REAL    NOT NULL,
        id_categoria INTEGER REFERENCES dim_categorias(id)
    );

    -- Clientes
    CREATE TABLE dim_clientes (
        id     INTEGER PRIMARY KEY,
        nome   TEXT NOT NULL,
        email  TEXT,
        cidade TEXT,
        estado TEXT,
        flag_nome_suspeito INTEGER DEFAULT 0
    );

    -- Tempo
    CREATE TABLE dim_tempo (
        data         TEXT PRIMARY KEY,
        ano          INTEGER,
        mes          INTEGER,
        dia          INTEGER,
        trimestre    INTEGER,
        dia_semana   INTEGER,
        nome_dia     TEXT,
        is_fim_semana INTEGER
    );

    -- Custos históricos
    CREATE TABLE fato_custos_historico (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id  INTEGER REFERENCES dim_produtos(id),
        start_date  TEXT,
        usd_price   REAL,
        brl_cost    REAL
    );

    -- Vendas (tabela principal)
    CREATE TABLE fato_vendas (
        id          INTEGER PRIMARY KEY,
        id_client   INTEGER REFERENCES dim_clientes(id),
        id_product  INTEGER REFERENCES dim_produtos(id),
        sale_date   TEXT,
        qtd         INTEGER,
        total       REAL,
        cost_total  REAL,
        profit      REAL,
        margin_pct  REAL,
        year        INTEGER,
        month       INTEGER,
        weekday     INTEGER,
        category    TEXT,
        product_name TEXT,
        client_name  TEXT
    );

""")
conn.commit()
print("    Tabelas criadas com sucesso!")

# ──────────────────────────────────────────────────────────────
# 2. CARREGAR DADOS DOS CSVs
# ──────────────────────────────────────────────────────────────
print("\n[2/3] Carregando dados dos CSVs...")

# ── Produtos
produtos = pd.read_csv(PROC / "produtos_clean.csv")
produtos.columns = produtos.columns.str.lower().str.strip()

# Inserir categorias únicas
categorias = produtos["category"].unique()
for cat in categorias:
    cursor.execute(
        "INSERT OR IGNORE INTO dim_categorias (nome) VALUES (?)", (cat,)
    )
conn.commit()

# Mapear categoria -> id
cat_map = {
    row[1]: row[0]
    for row in cursor.execute("SELECT id, nome FROM dim_categorias")
}

# Inserir produtos
for _, row in produtos.iterrows():
    cursor.execute("""
        INSERT OR REPLACE INTO dim_produtos (id, nome, preco_brl, id_categoria)
        VALUES (?, ?, ?, ?)
    """, (
        int(row["id"]),
        row["nome"],
        float(row["price"]),
        cat_map.get(row["category"]),
    ))
conn.commit()
print(f"    dim_produtos:    {len(produtos)} registros")

# ── Clientes
clientes = pd.read_csv(PROC / "clientes_clean.csv")
clientes.columns = clientes.columns.str.lower().str.strip()

for col in ["city", "state", "flag_nome_suspeito", "email"]:
    if col not in clientes.columns:
        clientes[col] = ""

for _, row in clientes.iterrows():
    cursor.execute("""
        INSERT OR REPLACE INTO dim_clientes
            (id, nome, email, cidade, estado, flag_nome_suspeito)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        int(row["id"]),
        row["nome"],
        row.get("email", ""),
        row.get("city", ""),
        row.get("state", ""),
        int(row.get("flag_nome_suspeito", 0)),
    ))
conn.commit()
print(f"    dim_clientes:    {len(clientes)} registros")

# ── Custos históricos
try:
    custos_hist = pd.read_csv(PROC / "custos_historico.csv")
    custos_hist.columns = custos_hist.columns.str.lower().str.strip()
    for _, row in custos_hist.iterrows():
        cursor.execute("""
            INSERT INTO fato_custos_historico
                (product_id, start_date, usd_price, brl_cost)
            VALUES (?, ?, ?, ?)
        """, (
            int(row["product_id"]),
            str(row["start_date"]),
            float(row["usd_price"]),
            float(row["usd_price"]) * 5.00,
        ))
    conn.commit()
    print(f"    fato_custos_historico: {len(custos_hist)} registros")
except FileNotFoundError:
    print("    custos_historico.csv não encontrado — pulando")

# ── Dim Tempo (gera calendário 2023-2025)
datas = pd.date_range("2023-01-01", "2025-12-31", freq="D")
dias_nome = {
    0:"Segunda", 1:"Terça", 2:"Quarta",
    3:"Quinta",  4:"Sexta", 5:"Sábado", 6:"Domingo"
}
for d in datas:
    cursor.execute("""
        INSERT OR IGNORE INTO dim_tempo
            (data, ano, mes, dia, trimestre, dia_semana, nome_dia, is_fim_semana)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(d.date()),
        d.year,
        d.month,
        d.day,
        d.quarter,
        d.dayofweek,
        dias_nome[d.dayofweek],
        1 if d.dayofweek >= 5 else 0,
    ))
conn.commit()
print(f"    dim_tempo:       {len(datas)} registros")

# ── Vendas (tabela principal — df_main.csv)
df = pd.read_csv(PROC / "df_main.csv")
df.columns = df.columns.str.lower().str.strip()

for _, row in df.iterrows():
    cursor.execute("""
        INSERT OR REPLACE INTO fato_vendas
            (id, id_client, id_product, sale_date, qtd, total,
             cost_total, profit, margin_pct, year, month, weekday,
             category, product_name, client_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        int(row["id"]),
        int(row["id_client"]),
        int(row["id_product"]),
        str(row["sale_date"])[:10],
        int(row["qtd"]),
        float(row["total"]),
        float(row["cost_total"])  if pd.notna(row.get("cost_total"))  else None,
        float(row["profit"])      if pd.notna(row.get("profit"))      else None,
        float(row["margin_pct"])  if pd.notna(row.get("margin_pct"))  else None,
        int(row["year"])          if pd.notna(row.get("year"))        else None,
        int(row["month"])         if pd.notna(row.get("month"))       else None,
        int(row["weekday"])       if pd.notna(row.get("weekday"))     else None,
        row.get("category", ""),
        row.get("product_name", ""),
        row.get("client_name", ""),
    ))
conn.commit()
print(f"    fato_vendas:     {len(df)} registros")

# ──────────────────────────────────────────────────────────────
# 3. VERIFICAÇÃO FINAL
# ──────────────────────────────────────────────────────────────
print("\n[3/3] Verificando banco criado...")

tabelas = [
    "dim_categorias", "dim_produtos", "dim_clientes",
    "dim_tempo", "fato_custos_historico", "fato_vendas"
]
for tabela in tabelas:
    count = cursor.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
    print(f"    {tabela:<30} {count:>6} registros")

conn.close()

print(f"""
{"=" * 55}
  Banco criado com sucesso!
  Arquivo: {DB_PATH}
{"=" * 55}

Rodar as queries diretamente em Python:
  import sqlite3
  conn = sqlite3.connect("lh_nautical.db")
  df = pd.read_sql("SELECT * FROM fato_vendas LIMIT 10", conn)
""")
