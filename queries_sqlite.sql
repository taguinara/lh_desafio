-- Tainara Almeida — LH Nautical Analytics

-- ──────────────────────────────────────────────────────────────
-- Q1: Faturamento por ano
-- ──────────────────────────────────────────────────────────────
SELECT
    year                        AS ano,
    COUNT(*)                    AS total_transacoes,
    ROUND(SUM(total), 2)        AS receita_total,
    ROUND(SUM(profit), 2)       AS lucro_total,
    ROUND(AVG(margin_pct), 2)   AS margem_media_pct
FROM fato_vendas
GROUP BY year
ORDER BY year;

-- ──────────────────────────────────────────────────────────────
-- Q2: Top 10 produtos por receita
-- ──────────────────────────────────────────────────────────────
SELECT
    id_product,
    product_name,
    category,
    COUNT(*)                    AS qtd_vendas,
    ROUND(SUM(total), 2)        AS receita_total,
    ROUND(SUM(profit), 2)       AS lucro_total,
    ROUND(AVG(margin_pct), 2)   AS margem_media_pct,
    CASE
        WHEN SUM(profit) < 0 THEN 'PREJUIZO'
        WHEN AVG(margin_pct) < 3 THEN 'MARGEM BAIXA'
        ELSE 'OK'
    END                         AS status
FROM fato_vendas
GROUP BY id_product, product_name, category
ORDER BY receita_total DESC
LIMIT 10;

-- ──────────────────────────────────────────────────────────────
-- Q3: Receita por categoria
-- ──────────────────────────────────────────────────────────────
SELECT
    category                    AS categoria,
    COUNT(*)                    AS total_transacoes,
    ROUND(SUM(total), 2)        AS receita_total,
    ROUND(SUM(profit), 2)       AS lucro_total,
    ROUND(AVG(margin_pct), 2)   AS margem_media_pct
FROM fato_vendas
GROUP BY category
ORDER BY receita_total DESC;

-- ──────────────────────────────────────────────────────────────
-- Q4: Produtos com prejuízo
-- ──────────────────────────────────────────────────────────────
SELECT
    id_product,
    product_name,
    category,
    COUNT(*)                    AS qtd_vendas,
    ROUND(SUM(total), 2)        AS receita_total,
    ROUND(SUM(cost_total), 2)   AS custo_total,
    ROUND(SUM(profit), 2)       AS prejuizo_total
FROM fato_vendas
GROUP BY id_product, product_name, category
HAVING SUM(profit) < 0
ORDER BY prejuizo_total ASC;

-- ──────────────────────────────────────────────────────────────
-- Q5: Top 10 clientes por lucro
-- ──────────────────────────────────────────────────────────────
SELECT
    v.id_client,
    v.client_name,
    c.estado,
    COUNT(*)                    AS total_transacoes,
    ROUND(SUM(v.total), 2)      AS receita_total,
    ROUND(SUM(v.profit), 2)     AS lucro_total,
    ROUND(AVG(v.margin_pct), 2) AS margem_media_pct
FROM fato_vendas v
LEFT JOIN dim_clientes c ON v.id_client = c.id
GROUP BY v.id_client, v.client_name, c.estado
ORDER BY lucro_total DESC
LIMIT 10;

-- ──────────────────────────────────────────────────────────────
-- Q6: Vendas médias por dia da semana
-- ──────────────────────────────────────────────────────────────
SELECT
    t.dia_semana,
    t.nome_dia,
    COUNT(DISTINCT t.data)              AS total_dias,
    ROUND(SUM(COALESCE(v.total,0))
        / COUNT(DISTINCT t.data), 2)    AS media_receita_diaria
FROM dim_tempo t
LEFT JOIN fato_vendas v ON t.data = v.sale_date
WHERE t.ano BETWEEN 2023 AND 2024
GROUP BY t.dia_semana, t.nome_dia
ORDER BY t.dia_semana;

-- ──────────────────────────────────────────────────────────────
-- Q7: Série temporal mensal por produto (base para previsão)
-- ──────────────────────────────────────────────────────────────
SELECT
    year                        AS ano,
    month                       AS mes,
    id_product,
    product_name,
    category,
    SUM(qtd)                    AS qtd_total,
    ROUND(SUM(total), 2)        AS receita_total,
    ROUND(SUM(profit), 2)       AS lucro_total
FROM fato_vendas
GROUP BY year, month, id_product, product_name, category
ORDER BY id_product, year, month;

-- ──────────────────────────────────────────────────────────────
-- Q8: Matriz cliente x categoria (base para recomendação)
-- ──────────────────────────────────────────────────────────────
SELECT
    id_client,
    client_name,
    category,
    COUNT(*)                    AS qtd_transacoes,
    SUM(qtd)                    AS unidades_compradas,
    ROUND(SUM(total), 2)        AS receita_total
FROM fato_vendas
GROUP BY id_client, client_name, category
ORDER BY id_client, category;

-- ──────────────────────────────────────────────────────────────
-- Q9: Alertas — produtos com custo maior que receita por venda
-- ──────────────────────────────────────────────────────────────
SELECT
    id_product,
    product_name,
    category,
    COUNT(*)                                AS qtd_vendas,
    ROUND(SUM(total), 2)                    AS receita_total,
    ROUND(SUM(cost_total), 2)               AS custo_total,
    ROUND(SUM(profit), 2)                   AS prejuizo_total,
    ROUND(AVG(margin_pct), 2)               AS margem_media
FROM fato_vendas
WHERE profit < 0
GROUP BY id_product, product_name, category
ORDER BY prejuizo_total ASC;

-- ──────────────────────────────────────────────────────────────
-- Q10: KPIs executivos consolidados
-- ──────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                            AS total_transacoes,
    COUNT(DISTINCT id_client)           AS clientes_ativos,
    COUNT(DISTINCT id_product)          AS produtos_vendidos,
    ROUND(SUM(total), 2)                AS receita_total,
    ROUND(SUM(profit), 2)               AS lucro_total,
    ROUND(AVG(margin_pct), 2)           AS margem_media_pct,
    ROUND(AVG(total), 2)                AS ticket_medio
FROM fato_vendas;
