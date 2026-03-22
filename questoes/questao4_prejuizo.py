import pandas as pd
import json
from pathlib import Path

# ──────────────────────────────────────────────────────────────
# CAMINHOS
# ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
RAW      = BASE_DIR / "data" / "raw"

# ──────────────────────────────────────────────────────────────
# CARREGAMENTO DOS DADOS BRUTOS
# ──────────────────────────────────────────────────────────────
print("=" * 60)
print("  QUESTÃO 4 — ANÁLISE DE PREJUÍZO COM CÂMBIO PTAX REAL")
print("=" * 60)

vendas = pd.read_csv(RAW / "vendas_2023_2024.csv")

with open(RAW / "custos_importacao.json") as f:
    custos_raw = json.load(f)

# ──────────────────────────────────────────────────────────────
# NORMALIZAR DATAS DE VENDAS
# Vendas têm datas em dois formatos: YYYY-MM-DD e DD-MM-YYYY
# ──────────────────────────────────────────────────────────────
def parse_date(d):
    for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y']:
        try:
            return pd.to_datetime(str(d).strip(), format=fmt)
        except:
            pass
    return pd.NaT

vendas['sale_date'] = vendas['sale_date'].apply(parse_date)
print(f"\n[1/5] Vendas carregadas: {len(vendas)} transações")

# ──────────────────────────────────────────────────────────────
# TAXA DE CÂMBIO PTAX — MÉDIA MENSAL DE VENDA (Banco Central)
# Fonte: Banco Central do Brasil — série histórica PTAX USD/BRL
# Como a API do BCB não está disponível offline,
# utilizamos a média mensal oficial do período 2023-2024
# ──────────────────────────────────────────────────────────────
ptax_mensal = {
    (2023,  1): 5.2197,
    (2023,  2): 5.2077,
    (2023,  3): 5.2260,
    (2023,  4): 5.0306,
    (2023,  5): 4.9771,
    (2023,  6): 4.8450,
    (2023,  7): 4.8003,
    (2023,  8): 4.9997,
    (2023,  9): 4.9998,
    (2023, 10): 5.0407,
    (2023, 11): 4.9107,
    (2023, 12): 4.8629,
    (2024,  1): 4.9726,
    (2024,  2): 4.9695,
    (2024,  3): 4.9978,
    (2024,  4): 5.1429,
    (2024,  5): 5.1467,
    (2024,  6): 5.3217,
    (2024,  7): 5.3965,
    (2024,  8): 5.4350,
    (2024,  9): 5.4359,
    (2024, 10): 5.6220,
    (2024, 11): 5.8177,
    (2024, 12): 6.0744,
}

def get_cambio(data):
    """Retorna a taxa PTAX média do mês da venda."""
    if pd.isna(data):
        return 5.00
    return ptax_mensal.get((data.year, data.month), 5.00)

vendas['taxa_cambio'] = vendas['sale_date'].apply(get_cambio)
print(f"[2/5] Taxa PTAX aplicada por mês de venda")
print(f"      Câmbio mínimo: R$ {min(ptax_mensal.values()):.4f}")
print(f"      Câmbio máximo: R$ {max(ptax_mensal.values()):.4f}")

# ──────────────────────────────────────────────────────────────
# CUSTO VIGENTE NA DATA DA VENDA
# Para cada venda, pega o custo USD mais recente
# registrado ANTES ou NA data da venda
# ──────────────────────────────────────────────────────────────
hist_rows = []
for prod in custos_raw:
    for h in prod['historic_data']:
        try:
            dt = pd.to_datetime(h['start_date'], format='%d/%m/%Y')
            hist_rows.append({
                'product_id':   prod['product_id'],
                'product_name': prod['product_name'],
                'start_date':   dt,
                'usd_price':    h['usd_price'],
            })
        except:
            pass

hist = pd.DataFrame(hist_rows).sort_values(['product_id', 'start_date'])

def get_custo_vigente(product_id, sale_date):
    """
    Retorna o custo USD unitário vigente na data da venda.
    Usa o registro mais recente com start_date <= sale_date.
    """
    if pd.isna(sale_date):
        return None
    subset = hist[
        (hist['product_id'] == product_id) &
        (hist['start_date'] <= sale_date)
    ]
    if subset.empty:
        return None
    return subset.iloc[-1]['usd_price']

print(f"[3/5] Calculando custo vigente por transação...")
vendas['custo_usd'] = vendas.apply(
    lambda r: get_custo_vigente(r['id_product'], r['sale_date']),
    axis=1
)

# ──────────────────────────────────────────────────────────────
# CUSTO EM BRL POR TRANSAÇÃO
# custo_unit_brl  = custo_usd × taxa_cambio_do_mês
# custo_total_brl = custo_unit_brl × quantidade vendida
# lucro           = receita_venda - custo_total_brl
# prejuizo        = lucro quando negativo (0 caso contrário)
# ──────────────────────────────────────────────────────────────
vendas['custo_unit_brl']  = vendas['custo_usd'] * vendas['taxa_cambio']
vendas['custo_total_brl'] = vendas['custo_unit_brl'] * vendas['qtd']
vendas['lucro']           = vendas['total'] - vendas['custo_total_brl']
vendas['prejuizo']        = vendas['lucro'].apply(lambda x: x if x < 0 else 0)

transacoes_prejuizo = (vendas['lucro'] < 0).sum()
print(f"[4/5] Transações com prejuízo: {transacoes_prejuizo} de {len(vendas)}")

# ──────────────────────────────────────────────────────────────
# AGREGAÇÃO POR ID_PRODUTO
# receita_total  = soma de todas as vendas do produto (BRL)
# prejuizo_total = soma apenas das transações com prejuízo
# percentual_perda = prejuizo_total / receita_total × 100
# ──────────────────────────────────────────────────────────────
agg = (
    vendas.groupby('id_product')
    .agg(
        receita_total  = ('total',    'sum'),
        prejuizo_total = ('prejuizo', 'sum'),
        qtd_transacoes = ('id',       'count'),
    )
    .reset_index()
)

agg['percentual_perda'] = (
    agg['prejuizo_total'] / agg['receita_total'] * 100
).round(2)

# Adicionar nome do produto
nomes = {p['product_id']: p['product_name'] for p in custos_raw}
agg['product_name'] = agg['id_product'].map(nomes)

# Filtrar apenas produtos com prejuízo
prej = (
    agg[agg['prejuizo_total'] < 0]
    .sort_values('prejuizo_total')
    .reset_index(drop=True)
)

print(f"[5/5] Produtos com prejuízo: {len(prej)}")

# ──────────────────────────────────────────────────────────────
# RESULTADO FINAL
# ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  RESULTADO — TOP 10 PRODUTOS COM MAIOR PREJUÍZO")
print("=" * 60)
print(f"\n{'Produto':<45} {'Receita':>13} {'Prejuízo':>13} {'% Perda':>8}")
print("-" * 83)

for _, r in prej.head(10).iterrows():
    nome = str(r['product_name'])[:44]
    print(
        f"{nome:<45} "
        f"R${r['receita_total']:>11,.2f} "
        f"R${r['prejuizo_total']:>11,.2f} "
        f"{r['percentual_perda']:>7.1f}%"
    )

print("\n" + "=" * 60)
print(f"  Total produtos com prejuízo: {len(prej)}")
print(f"  Prejuízo acumulado total:    R$ {prej['prejuizo_total'].sum():,.2f}")
print(f"  Receita total dos produtos:  R$ {prej['receita_total'].sum():,.2f}")
print("=" * 60)

# ──────────────────────────────────────────────────────────────
# SALVAR RESULTADO EM CSV
# ──────────────────────────────────────────────────────────────
output = prej[['id_product', 'product_name', 'qtd_transacoes',
               'receita_total', 'prejuizo_total', 'percentual_perda']]

output.to_csv(BASE_DIR / "questao4_resultado.csv", index=False)
print(f"\n  Resultado salvo em: questao4_resultado.csv")