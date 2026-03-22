-- Questão 5 — Clientes Fiéis: Ticket Médio, Diversidade e

WITH
-- PASSO 1: Ticket Médio e Diversidade de Categorias por Cliente

metricas_cliente AS (
    SELECT
        v.id_client,
        c.nome                              AS cliente,
        COUNT(v.id)                         AS qtd_transacoes,
        ROUND(SUM(v.total), 2)              AS receita_total,
        COUNT(DISTINCT v.category)          AS diversidade_cats,
        SUM(v.qtd)                          AS qtd_total_itens,
        ROUND(SUM(v.total) / COUNT(v.id), 2) AS ticket_medio
    FROM fato_vendas v
    LEFT JOIN dim_clientes c ON v.id_client = c.id
    GROUP BY v.id_client, c.nome
),

-- PASSO 2: Top 10 Clientes Fiéis

top10_fieis AS (
    SELECT
        id_client,
        cliente,
        ticket_medio,
        diversidade_cats,
        qtd_transacoes,
        receita_total,
        ROW_NUMBER() OVER (ORDER BY ticket_medio DESC) AS ranking
    FROM metricas_cliente
    WHERE diversidade_cats >= 3
    LIMIT 10
),

-- PASSO 3: Categoria mais vendida entre os 10 fiéis (em qtd)
cat_fieis AS (
    SELECT
        v.category,
        SUM(v.qtd)                          AS qtd_total,
        ROW_NUMBER() OVER (ORDER BY SUM(v.qtd) DESC) AS ranking_cat
    FROM fato_vendas v
    WHERE v.id_client IN (SELECT id_client FROM top10_fieis)
    GROUP BY v.category
)

-- ──────────────────────────────────────────────────────────────
-- RESULTADO 1: Top 10 Clientes Fiéis
-- ──────────────────────────────────────────────────────────────
SELECT
    ranking,
    cliente,
    ticket_medio            AS "Ticket Médio (R$)",
    diversidade_cats        AS "Categorias",
    qtd_transacoes          AS "Transações",
    receita_total           AS "Receita Total (R$)"
FROM top10_fieis
ORDER BY ranking;

-- ──────────────────────────────────────────────────────────────
-- RESULTADO 2: Categoria mais vendida entre os 10 fiéis
-- ──────────────────────────────────────────────────────────────
SELECT
    category               AS "Categoria",
    qtd_total              AS "Qtd Total (itens)",
    ranking_cat            AS "Ranking"
FROM cat_fieis
ORDER BY ranking_cat;