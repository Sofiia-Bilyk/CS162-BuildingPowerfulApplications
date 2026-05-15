-- Personal Finance Management App — Queries
-- All monetary values are converted to USD using the currency_rates table.

-- ============================================
-- QUERY 1: What is my total income and total expenses for the last month in USD?
-- ============================================
-- RELEVANCE: This is the most fundamental personal finance question. Knowing
-- the balance between income and expenses tells the user whether they are
-- living within their means or overspending. It is the starting point for
-- any budgeting decision.
-- ============================================

SELECT
    state,
    ROUND(SUM(dl.amount * cr.conversion_rate), 2) AS total_usd
FROM daily_logs dl
JOIN currency_rates cr ON dl.currency = cr.currency
WHERE dl.date >= '2025-01-01'
    AND dl.date <  '2025-02-01'
GROUP BY dl.state;


-- ============================================
-- QUERY 2: In what categories did I spend more than planned (based on the
--           percentage in the categories table) for the last month?
-- ============================================
-- RELEVANCE: Setting a budget is only useful if the user can see where they
-- exceeded it. This query compares actual spending per category against the
-- planned percentage of total income, highlighting areas that need attention
-- so the user can adjust habits or reallocate their budget.
-- ============================================

WITH monthly_income AS (
    SELECT SUM(dl.amount * cr.conversion_rate) AS total_income_usd
    FROM daily_logs dl
    JOIN currency_rates cr ON dl.currency = cr.currency
    WHERE dl.state = 'income'
        AND dl.date >= '2025-01-01'
        AND dl.date <  '2025-02-01'
),
monthly_spending AS (
    SELECT
        dl.category,
        SUM(dl.amount * cr.conversion_rate) AS spent_usd
    FROM daily_logs dl
    JOIN currency_rates cr ON dl.currency = cr.currency
    WHERE dl.state = 'expense'
        AND dl.date >= '2025-01-01'
        AND dl.date <  '2025-02-01'
    GROUP BY dl.category
)
SELECT
    ms.category,
    ROUND(ms.spent_usd, 2)                                    AS spent_usd,
    c.percentage                                                AS planned_pct,
    ROUND(mi.total_income_usd * c.percentage / 100.0, 2)       AS planned_usd,
    ROUND(ms.spent_usd - mi.total_income_usd * c.percentage / 100.0, 2) AS over_by_usd
FROM monthly_spending ms
JOIN categories c       ON ms.category = c.category
CROSS JOIN monthly_income mi
WHERE ms.spent_usd > (mi.total_income_usd * c.percentage / 100.0)
ORDER BY over_by_usd DESC;


-- ============================================
-- QUERY 3: For what category did I spend the most and how much (in USD)?
-- ============================================
-- RELEVANCE: Even without a formal budget, users want to know their biggest
-- expense category. This helps identify the dominant cost driver — whether
-- it is housing, food, or something unexpected — and decide where to cut
-- back first if savings are needed.
-- ============================================

SELECT
    dl.category,
    ROUND(SUM(dl.amount * cr.conversion_rate), 2) AS total_spent_usd
FROM daily_logs dl
JOIN currency_rates cr ON dl.currency = cr.currency
WHERE dl.state = 'expense'
GROUP BY dl.category
ORDER BY total_spent_usd DESC
LIMIT 1;


-- ============================================
-- QUERY 4: What percentage of my spending was irrational this month,
--           and what were those transactions?
-- ============================================
-- RELEVANCE: Tracking rationality helps the user build self-awareness about
-- impulsive or unnecessary purchases. Seeing the percentage of income lost
-- to irrational spending motivates behavioral change and helps prioritize
-- which habits to fix first (e.g., impulse dining, unnecessary shopping).
-- ============================================

SELECT
    ROUND(SUM(dl.amount * cr.conversion_rate), 2) AS irrational_total_usd,
    ROUND(
        SUM(dl.amount * cr.conversion_rate) * 100.0 /
        (SELECT SUM(d2.amount * c2.conversion_rate)
         FROM daily_logs d2
         JOIN currency_rates c2 ON d2.currency = c2.currency
         WHERE d2.state = 'expense'),
    2) AS irrational_pct
FROM daily_logs dl
JOIN currency_rates cr ON dl.currency = cr.currency
WHERE dl.state = 'expense'
  AND dl.rationality = 0;

-- Detail of each irrational transaction:
SELECT
    dl.date,
    dl.description,
    dl.category,
    ROUND(dl.amount * cr.conversion_rate, 2) AS amount_usd
FROM daily_logs dl
JOIN currency_rates cr ON dl.currency = cr.currency
WHERE dl.state = 'expense'
  AND dl.rationality = 0
ORDER BY amount_usd DESC;


-- ============================================
-- QUERY 5: How much did I spend from each payment source (card / cash)
--           this month, and which source is used the most?
-- ============================================
-- RELEVANCE: Users often spread spending across multiple cards and cash.
-- This query reveals which payment method dominates their spending, helping
-- them optimize for rewards programs, track cash leakage, or consolidate
-- accounts. It also catches unexpectedly high usage on a specific card.
-- ============================================

SELECT
    CASE
        WHEN pr.card_number IS NULL THEN 'Cash (' || pr.currency || ')'
        ELSE pr.card_number
    END AS payment_source,
    pr.currency AS source_currency,
    COUNT(dl.id)                                     AS num_transactions,
    ROUND(SUM(dl.amount * cr.conversion_rate), 2)    AS total_spent_usd
FROM daily_logs dl
JOIN paying_resources pr ON dl.source = pr.id
JOIN currency_rates cr   ON dl.currency = cr.currency
WHERE dl.state = 'expense'
GROUP BY dl.source
ORDER BY total_spent_usd DESC;
