-- PASSO 1: Criar tabela temporária de câmbio PTAX
-- ──────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS temp_ptax;

CREATE TEMPORARY TABLE temp_ptax (
    ano  INTEGER,
    mes  INTEGER,
    taxa REAL
);

INSERT INTO temp_ptax VALUES
    (2023,  1, 5.2197), (2023,  2, 5.2077), (2023,  3, 5.2260),
    (2023,  4, 5.0306), (2023,  5, 4.9771), (2023,  6, 4.8450),
    (2023,  7, 4.8003), (2023,  8, 4.9997), (2023,  9, 4.9998),
    (2023, 10, 5.0407), (2023, 11, 4.9107), (2023, 12, 4.8629),
    (2024,  1, 4.9726), (2024,  2, 4.9695), (2024,  3, 4.9978),
    (2024,  4, 5.1429), (2024,  5, 5.1467), (2024,  6, 5.3217),
    (2024,  7, 5.3965), (2024,  8, 5.4350), (2024,  9, 5.4359),
    (2024, 10, 5.6220), (2024, 11, 5.8177), (2024, 12, 6.0744);

-- ──────────────────────────────────────────────────────────────
-- PASSO 2: Query principal com CTEs
-- ──────────────────────────────────────────────────────────────
WITH

-- Custo USD vigente por produto (registro mais recente)
custo_vigente AS (
    SELECT
        product_id,
        usd_price
    FROM fato_custos_historico
    WHERE (product_id, start_date) IN (
        SELECT product_id, MAX(start_date)
        FROM fato_custos_historico
        GROUP BY product_id
    )
),

-- Calcular custo BRL e lucro por transação
transacoes AS (
    SELECT
        v.id_product,
        v.product_name,
        v.total                                              AS receita_venda,
        cv.usd_price                                         AS custo_usd,
        p.taxa                                               AS taxa_cambio,
        cv.usd_price * p.taxa * v.qtd                        AS custo_total_brl,
        v.total - (cv.usd_price * p.taxa * v.qtd)            AS lucro
    FROM fato_vendas v
    JOIN temp_ptax p
        ON  CAST(strftime('%Y', v.sale_date) AS INTEGER) = p.ano
        AND CAST(strftime('%m', v.sale_date) AS INTEGER) = p.mes
    JOIN custo_vigente cv
        ON v.id_product = cv.product_id
)

-- Agregação final por produto
SELECT
    id_product,
    product_name,
    COUNT(*)                                                  AS qtd_transacoes,
    ROUND(SUM(receita_venda), 2)                              AS receita_total,
    ROUND(
        SUM(CASE WHEN lucro < 0 THEN lucro ELSE 0 END)
    , 2)                                                      AS prejuizo_total,
    ROUND(
        SUM(CASE WHEN lucro < 0 THEN lucro ELSE 0 END)
        / SUM(receita_venda) * 100
    , 2)                                                      AS percentual_perda
FROM transacoes
GROUP BY id_product, product_name
HAVING prejuizo_total < 0
ORDER BY prejuizo_total ASC;