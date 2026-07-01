-- Renewal pipeline by customer segment and likelihood tier.
WITH scored_customers AS (
    SELECT
        customer_segment,
        renewal_likelihood,
        renewed_season_ticket,
        lifetime_value,
        CASE
            WHEN renewal_likelihood >= 75 THEN 'High'
            WHEN renewal_likelihood >= 50 THEN 'Medium'
            ELSE 'Low'
        END AS likelihood_tier
    FROM customers
)
SELECT
    customer_segment,
    likelihood_tier,
    COUNT(*) AS customers,
    ROUND(AVG(renewal_likelihood), 1) AS avg_renewal_likelihood,
    ROUND(SUM(lifetime_value), 2) AS lifetime_value_at_risk,
    SUM(
        CASE WHEN renewed_season_ticket = 1 THEN 1 ELSE 0 END
    ) AS confirmed_renewals,
    SUM(
        CASE WHEN renewed_season_ticket = 0 THEN 1 ELSE 0 END
    ) AS unrenewed_members
FROM scored_customers
GROUP BY customer_segment, likelihood_tier
ORDER BY
    customer_segment,
    CASE likelihood_tier WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;

