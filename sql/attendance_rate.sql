-- Matchday utilization and scan rate by opponent.
SELECT
    m.match_id,
    m.match_date,
    m.opponent,
    m.competition,
    m.capacity,
    COALESCE(SUM(a.tickets_issued), 0) AS tickets_issued,
    COALESCE(SUM(a.tickets_scanned), 0) AS tickets_scanned,
    ROUND(
        100.0 * SUM(a.tickets_scanned) / NULLIF(SUM(a.tickets_issued), 0),
        1
    ) AS scan_rate_pct,
    ROUND(
        100.0 * SUM(a.tickets_scanned) / m.capacity,
        1
    ) AS venue_utilization_pct
FROM matches AS m
LEFT JOIN attendance AS a
    ON a.match_id = m.match_id
GROUP BY
    m.match_id,
    m.match_date,
    m.opponent,
    m.competition,
    m.capacity
ORDER BY m.match_date;

