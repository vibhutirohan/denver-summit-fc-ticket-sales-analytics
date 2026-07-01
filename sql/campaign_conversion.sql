-- Funnel performance and return on ad spend by campaign.
SELECT
    c.campaign_id,
    c.campaign_name,
    c.channel,
    c.target_segment,
    c.objective,
    c.budget,
    SUM(cc.sent) AS sends,
    SUM(cc.opened) AS opens,
    SUM(cc.clicked) AS clicks,
    SUM(cc.converted) AS conversions,
    ROUND(100.0 * SUM(cc.opened) / NULLIF(SUM(cc.sent), 0), 1) AS open_rate_pct,
    ROUND(100.0 * SUM(cc.clicked) / NULLIF(SUM(cc.sent), 0), 1) AS click_rate_pct,
    ROUND(100.0 * SUM(cc.converted) / NULLIF(SUM(cc.sent), 0), 2) AS conversion_rate_pct,
    ROUND(SUM(cc.revenue), 2) AS attributed_revenue,
    ROUND(SUM(cc.revenue) / NULLIF(c.budget, 0), 2) AS return_on_ad_spend
FROM campaigns AS c
JOIN campaign_conversions AS cc
    ON cc.campaign_id = c.campaign_id
GROUP BY
    c.campaign_id,
    c.campaign_name,
    c.channel,
    c.target_segment,
    c.objective,
    c.budget
ORDER BY attributed_revenue DESC;

