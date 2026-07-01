-- Revenue pacing by match, including season-to-date cumulative revenue.
WITH match_sales AS (
    SELECT
        m.match_id,
        m.match_date,
        m.opponent,
        m.competition,
        m.capacity,
        COALESCE(SUM(t.quantity), 0) AS tickets_sold,
        COALESCE(SUM(t.total_revenue), 0) AS match_revenue
    FROM matches AS m
    LEFT JOIN tickets AS t
        ON t.match_id = m.match_id
    GROUP BY
        m.match_id,
        m.match_date,
        m.opponent,
        m.competition,
        m.capacity
)
SELECT
    match_id,
    match_date,
    opponent,
    competition,
    tickets_sold,
    ROUND(match_revenue, 2) AS match_revenue,
    ROUND(
        SUM(match_revenue) OVER (
            ORDER BY match_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS cumulative_revenue,
    ROUND(100.0 * tickets_sold / capacity, 1) AS inventory_sold_pct
FROM match_sales
ORDER BY match_date;

