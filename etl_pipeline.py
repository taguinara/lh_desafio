import pandas as pd
import json
import numpy as np
import re
import unicodedata
from pathlib import Path

# ──────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DE CAMINHOS
# ──────────────────────────────────────────────────────────────
# BASE_DIR = pasta onde este script está salvo
BASE_DIR   = Path(__file__).parent.resolve()
DATA_DIR   = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

# Cria a pasta de saída se não existir
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Taxa de câmbio USD → BRL usada para os custos de importação
USD_BRL     = 5.00
COST_CUTOFF = pd.Timestamp("2024-12-31")


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
def normalizar_str(s: str) -> str:
    """Remove acentos, espaços extras e converte para minúsculo."""
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", "", s.strip().lower())


CATEGORIA_MAP = {
    "eletronicos":  "eletronicos",
    "eletrunicos":  "eletronicos",
    "eletronicoz":  "eletronicos",
    "eletroniscos": "eletronicos",
    "propulsao":    "propulsao",
    "propusao":     "propulsao",
    "propucao":     "propulsao",
    "propulssao":   "propulsao",
    "propulsam":    "propulsao",
    "prop":         "propulsao",
    "ancoragem":    "ancoragem",
    "ancoraguem":   "ancoragem",
    "ancorajem":    "ancoragem",
    "ancorajm":     "ancoragem",
    "encoragem":    "ancoragem",
    "ancoragen":    "ancoragem",
    "ancorajen":    "ancoragem",
}


def parse_date(d: str) -> pd.Timestamp:
    """Tenta múltiplos formatos de data."""
    for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]:
        try:
            return pd.to_datetime(str(d).strip(), format=fmt)
        except ValueError:
            pass
    return pd.NaT


def parse_location(loc: str) -> tuple:
    """Extrai (cidade, estado) de strings inconsistentes."""
    loc = loc.strip()
    parts = [p.strip() for p in re.split(r"\s*[-,/]\s*", loc) if p.strip()]
    if len(parts) == 2:
        a, b = parts
        if len(a) == 2 and a.isupper():
            return b, a   # (cidade, UF)
        if len(b) == 2 and b.isupper():
            return a, b
        return a, b
    return loc, ""


def checar_arquivo(path: Path):
    """Lança erro claro se o arquivo não existir."""
    if not path.exists():
        raise FileNotFoundError(
            f"\n\n  ARQUIVO NÃO ENCONTRADO: {path}"
            f"\n  Coloque o arquivo em:    {path.parent}\n"
        )


# ──────────────────────────────────────────────────────────────
# 1. PRODUTOS
# ──────────────────────────────────────────────────────────────
def tratar_produtos() -> pd.DataFrame:
    path = DATA_DIR / "produtos_raw.csv"
    checar_arquivo(path)
    df = pd.read_csv(path)

    antes = len(df)
    df = df.drop_duplicates(subset="code", keep="first").copy()
    duplicatas = antes - len(df)

    df["category"] = df["actual_category"].apply(
        lambda c: CATEGORIA_MAP.get(normalizar_str(c), normalizar_str(c))
    )
    df["price"] = (
        df["price"]
        .str.replace(r"R\$\s*", "", regex=True)
        .str.replace(",", ".")
        .astype(float)
    )

    df = df.rename(columns={"code": "id", "name": "nome"})[
        ["id", "nome", "price", "category"]
    ]
    df.to_csv(OUTPUT_DIR / "produtos_clean.csv", index=False)
    print(f"[ETL] Produtos:  {len(df)} registros salvos  |  {duplicatas} duplicata(s) removida(s)")
    print(f"       Categorias: {df['category'].value_counts().to_dict()}")
    return df


# ──────────────────────────────────────────────────────────────
# 2. CLIENTES
# ──────────────────────────────────────────────────────────────
def tratar_clientes() -> pd.DataFrame:
    path = DATA_DIR / "clientes_crm.json"
    checar_arquivo(path)
    df = pd.read_json(path)

    emails_corrompidos = df["email"].str.contains("#").sum()
    df["email"] = df["email"].str.replace("#", "@")

    df[["city", "state"]] = df["location"].apply(
        lambda x: pd.Series(parse_location(x))
    )
    df["flag_nome_suspeito"] = df["full_name"].str.lower().str.startswith("femininos")

    df = df.rename(columns={"code": "id", "full_name": "nome"})[
        ["id", "nome", "email", "city", "state", "flag_nome_suspeito"]
    ]
    df.to_csv(OUTPUT_DIR / "clientes_clean.csv", index=False)
    print(f"[ETL] Clientes:  {len(df)} registros salvos  |  {emails_corrompidos} e-mail(s) corrigido(s)  |  {df['flag_nome_suspeito'].sum()} nome(s) suspeito(s)")
    return df


# ──────────────────────────────────────────────────────────────
# 3. CUSTOS
# ──────────────────────────────────────────────────────────────
def tratar_custos() -> pd.DataFrame:
    path = DATA_DIR / "custos_importacao.json"
    checar_arquivo(path)
    with open(path) as f:
        raw = json.load(f)

    rows = []
    for prod in raw:
        for h in prod["historic_data"]:
            try:
                dt = pd.to_datetime(h["start_date"], format="%d/%m/%Y")
                rows.append({
                    "product_id":   prod["product_id"],
                    "product_name": prod["product_name"],
                    "category":     prod["category"],
                    "start_date":   dt,
                    "usd_price":    h["usd_price"],
                })
            except Exception:
                pass

    hist = pd.DataFrame(rows)

    # Custo vigente = registro mais recente com data ≤ COST_CUTOFF
    custo_vigente = (
        hist[hist["start_date"] <= COST_CUTOFF]
        .sort_values("start_date")
        .groupby("product_id")
        .last()
        .reset_index()[["product_id", "product_name", "usd_price", "start_date"]]
    )
    custo_vigente["brl_cost"] = (custo_vigente["usd_price"] * USD_BRL).round(2)

    custo_vigente.to_csv(OUTPUT_DIR / "custos_vigentes.csv",  index=False)
    hist.to_csv(          OUTPUT_DIR / "custos_historico.csv", index=False)
    print(f"[ETL] Custos:    {len(custo_vigente)} produtos com custo vigente  |  {len(hist)} registros históricos")
    return custo_vigente


# ──────────────────────────────────────────────────────────────
# 4. VENDAS
# ──────────────────────────────────────────────────────────────
def tratar_vendas() -> pd.DataFrame:
    path = DATA_DIR / "vendas_2023_2024.csv"
    checar_arquivo(path)
    df = pd.read_csv(path)

    df["sale_date"] = df["sale_date"].apply(parse_date)
    nulos = df["sale_date"].isna().sum()
    if nulos:
        print(f"  ATENÇÃO: {nulos} data(s) não parseada(s) — linha(s) removida(s)")
        df = df.dropna(subset=["sale_date"])

    print(f"[ETL] Vendas:    {len(df)} transações  |  {df['sale_date'].min().date()} → {df['sale_date'].max().date()}")
    return df


# ──────────────────────────────────────────────────────────────
# 5. JOIN PRINCIPAL → df_main.csv
# ──────────────────────────────────────────────────────────────
def construir_dataset_principal(
    vendas:   pd.DataFrame,
    produtos: pd.DataFrame,
    clientes: pd.DataFrame,
    custos:   pd.DataFrame,
) -> pd.DataFrame:

    df = vendas.merge(
        produtos.rename(columns={"id": "id_product", "nome": "product_name"}),
        on="id_product", how="left"
    )
    df = df.merge(
        clientes.rename(columns={"id": "id_client", "nome": "client_name"})[
            ["id_client", "client_name", "city", "state"]
        ],
        on="id_client", how="left"
    )
    df = df.merge(
        custos[["product_id", "brl_cost"]].rename(columns={"product_id": "id_product"}),
        on="id_product", how="left"
    )

    # Campos derivados financeiros
    df["cost_total"] = (df["brl_cost"] * df["qtd"]).round(2)
    df["profit"]     = (df["total"]    - df["cost_total"]).round(2)
    df["margin_pct"] = (df["profit"] / df["total"].replace(0, np.nan) * 100).round(2)

    # Campos de tempo
    df["year"]    = df["sale_date"].dt.year
    df["month"]   = df["sale_date"].dt.month
    df["weekday"] = df["sale_date"].dt.dayofweek   # 0 = Segunda, 6 = Domingo

    df.to_csv(OUTPUT_DIR / "df_main.csv", index=False)
    print(f"[ETL] df_main:   {df.shape[0]} linhas × {df.shape[1]} colunas")
    print(f"       Receita total:  R$ {df['total'].sum():>16,.2f}")
    print(f"       Lucro total:    R$ {df['profit'].sum():>16,.2f}")
    print(f"       Margem média:   {df['margin_pct'].mean():.1f}%")
    return df


# ──────────────────────────────────────────────────────────────
# ENTRYPOINT
# ──────────────────────────────────────────────────────────────
def run():
    print("=" * 55)
    print("  LH NAUTICAL — ETL PIPELINE")
    print(f"  Lendo de:   {DATA_DIR}")
    print(f"  Salvando em:{OUTPUT_DIR}")
    print("=" * 55)

    produtos = tratar_produtos()
    clientes = tratar_clientes()
    custos   = tratar_custos()
    vendas   = tratar_vendas()
    df       = construir_dataset_principal(vendas, produtos, clientes, custos)

    print("=" * 55)
    print("  ETL concluído! Arquivos gerados em data/processed/:")
    for f in sorted(OUTPUT_DIR.iterdir()):
        print(f"    ✓ {f.name}")
    print("=" * 55)
    return df


if __name__ == "__main__":
    run()
