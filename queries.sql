-- event_type_counts
SELECT
    event_type,
    COUNT(*) AS count
FROM events
GROUP BY event_type
ORDER BY count DESC;


-- date_trend_7days
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS count
FROM events
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date;


-- top10_users_by_activity
SELECT
    user_id,
    COUNT(*) AS count
FROM events
GROUP BY user_id
ORDER BY count DESC
LIMIT 10;


-- event_type_ratio
SELECT
    event_type,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS percentage
FROM events
GROUP BY event_type
ORDER BY count DESC;
