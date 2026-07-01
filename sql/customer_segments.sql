-- Customer value, purchasing, and attendance behavior by CRM segment.
WITH customer_ticket_value AS (
    SELECT
        customer_id,
        COUNT(DISTINCT match_id) AS matches_purchased,
        SUM(quantity) AS tickets_purchased,
        SUM(total_revenue) AS ticket_revenue
    FROM tickets
    GROUP BY customer_id
),
customer_attendance AS (
    SELECT
        customer_id,
        SUM(tickets_issued) AS tickets_issued,
        SUM(tickets_scanned) AS tickets_scanned
    FROM attendance
    GROUP BY customer_id
)
SELECT
    c.customer_segment,
    COUNT(*) AS customers,
    SUM(CASE WHEN ctv.customer_id IS NOT NULL THEN 1 ELSE 0 END) AS active_buyers,
    ROUND(AVG(c.lifetime_value), 2) AS avg_lifetime_value,
    ROUND(AVG(COALESCE(ctv.matches_purchased, 0)), 2) AS avg_matches_purchased,
    COALESCE(SUM(ctv.tickets_purchased), 0) AS tickets_purchased,
    ROUND(COALESCE(SUM(ctv.ticket_revenue), 0), 2) AS ticket_revenue,
    ROUND(
        100.0 * SUM(ca.tickets_scanned) / NULLIF(SUM(ca.tickets_issued), 0),
        1
    ) AS scan_rate_pct
FROM customers AS c
LEFT JOIN customer_ticket_value AS ctv
    ON ctv.customer_id = c.customer_id
LEFT JOIN customer_attendance AS ca
    ON ca.customer_id = c.customer_id
GROUP BY c.customer_segment
ORDER BY ticket_revenue DESC;

