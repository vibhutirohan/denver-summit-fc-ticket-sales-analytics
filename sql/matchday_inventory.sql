-- Sold, scanned, and remaining seat inventory by home match.
WITH sales AS (
    SELECT
        match_id,
        SUM(quantity) AS tickets_sold,
        SUM(total_revenue) AS revenue
    FROM tickets
    GROUP BY match_id
),
scans AS (
    SELECT
        match_id,
        SUM(tickets_scanned) AS tickets_scanned
    FROM attendance
    GROUP BY match_id
)
SELECT
    m.match_id,
    m.match_date,
    m.opponent,
    m.capacity,
    COALESCE(s.tickets_sold, 0) AS tickets_sold,
    m.capacity - COALESCE(s.tickets_sold, 0) AS seats_remaining,
    ROUND(100.0 * COALESCE(s.tickets_sold, 0) / m.capacity, 1) AS inventory_sold_pct,
    COALESCE(sc.tickets_scanned, 0) AS tickets_scanned,
    COALESCE(s.tickets_sold, 0) - COALESCE(sc.tickets_scanned, 0) AS sold_not_scanned,
    ROUND(COALESCE(s.revenue, 0), 2) AS ticket_revenue,
    ROUND(
        COALESCE(s.revenue, 0) / NULLIF(s.tickets_sold, 0),
        2
    ) AS revenue_per_ticket
FROM matches AS m
LEFT JOIN sales AS s
    ON s.match_id = m.match_id
LEFT JOIN scans AS sc
    ON sc.match_id = m.match_id
ORDER BY m.match_date;

