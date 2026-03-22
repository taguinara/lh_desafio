WITH

periodo AS (
    SELECT
        MIN(sale_date) AS data_min,
        MAX(sale_date) AS data_max
    FROM fato_vendas
),

calendario AS (
    SELECT
        t.data,
        t.dia_semana,
        CASE t.dia_semana
            WHEN 0 THEN 'Segunda-feira'
            WHEN 1 THEN 'Terça-feira'
            WHEN 2 THEN 'Quarta-feira'
            WHEN 3 THEN 'Quinta-feira'
            WHEN 4 THEN 'Sexta-feira'
            WHEN 5 THEN 'Sábado'
            WHEN 6 THEN 'Domingo'
        END AS nome_dia
    FROM dim_tempo t, periodo p
    WHERE t.data BETWEEN p.data_min AND p.data_max
),


vendas_por_dia AS (
    SELECT
        c.data,
        c.dia_semana,
        c.nome_dia,
        COALESCE(SUM(v.total), 0) AS total_dia
    FROM calendario c
    LEFT JOIN fato_vendas v ON c.data = v.sale_date
    GROUP BY c.data, c.dia_semana, c.nome_dia
)

SELECT
    nome_dia                            AS "Dia da Semana",
    COUNT(data)                         AS "Total de Dias",
    COUNT(CASE WHEN total_dia > 0
               THEN 1 END)              AS "Dias com Venda",
    COUNT(CASE WHEN total_dia = 0
               THEN 1 END)              AS "Dias sem Venda (R$0)",
    ROUND(SUM(total_dia), 2)            AS "Receita Total (R$)",
    ROUND(AVG(total_dia), 2)            AS "Média Diária (R$)"
FROM vendas_por_dia
GROUP BY dia_semana, nome_dia
ORDER BY AVG(total_dia) ASC;