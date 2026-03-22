import sqlite3
import pandas as pd
from pathlib import Path

conn = sqlite3.connect(Path(__file__).parent / "lh_nautical.db")

# Cole aqui a query que quiser rodar
query = """
SELECT
    year,
    COUNT(*) AS total_transacoes,
    ROUND(SUM(total), 2) AS receita_total,
    ROUND(SUM(profit), 2) AS lucro_total
FROM fato_vendas
GROUP BY year
ORDER BY year
"""

df = pd.read_sql(query, conn)
print(df.to_string(index=False))
conn.close()