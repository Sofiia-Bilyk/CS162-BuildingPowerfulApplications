-- Recipe Recommendation and Meal Planning App — Queries

-- ============================================
-- QUERY 1: What ingredients do I need to buy for this week's meal plan
--           and how much of each? (Shopping list)
-- ============================================
-- RELEVANCE: The core value of a meal planning app is turning a weekly plan
-- into a concrete shopping list. Without this, the user has to manually
-- cross-reference every recipe — tedious and error-prone. This query
-- aggregates quantities across all planned meals so nothing is forgotten
-- and nothing is double-bought.
-- ============================================

SELECT
    i.name,
    i.category,
    ROUND(SUM(ri.quantity), 1) AS total_quantity,
    i.unit,
    ROUND(SUM(ri.quantity * i.price_per_unit), 2) AS estimated_cost
FROM meal_plan mp
JOIN recipe_ingredients ri ON mp.recipe_id = ri.recipe_id
JOIN ingredients i         ON ri.ingredient_id = i.id
WHERE mp.date BETWEEN '2025-01-06' AND '2025-01-12'
GROUP BY i.id
ORDER BY i.category, i.name;


-- ============================================
-- QUERY 2: Which recipes can I make in under 30 minutes total
--           (prep + cook)?
-- ============================================
-- RELEVANCE: Users are often short on time, especially on weekday evenings.
-- Filtering by total time lets them quickly find fast meal options when they
-- cannot afford a long cooking session. This is one of the most common
-- filters in any recipe app.
-- ============================================

SELECT
    r.name,
    r.cuisine,
    (r.prep_time_min + r.cook_time_min) AS total_time_min,
    r.difficulty,
    r.servings
FROM recipes r
WHERE (r.prep_time_min + r.cook_time_min) < 30
ORDER BY total_time_min ASC;


-- ============================================
-- QUERY 3: What is the estimated calorie count for each day in my
--           weekly meal plan?
-- ============================================
-- RELEVANCE: Calorie tracking is essential for users managing their weight
-- or following a nutrition plan. By summing calories across all meals for
-- each day, the app gives a quick daily overview without requiring a
-- separate calorie-counting tool.
-- ============================================

SELECT
    mp.date,
    ROUND(SUM(ri.quantity * i.calories_per_unit), 0) AS total_calories
FROM meal_plan mp
JOIN recipe_ingredients ri ON mp.recipe_id = ri.recipe_id
JOIN ingredients i         ON ri.ingredient_id = i.id
WHERE mp.date BETWEEN '2025-01-06' AND '2025-01-12'
GROUP BY mp.date
ORDER BY mp.date;


-- ============================================
-- QUERY 4: Which recipes in my plan are suitable for a vegan diet?
-- ============================================
-- RELEVANCE: Dietary restrictions are non-negotiable for many users —
-- whether for health, ethical, or religious reasons. Being able to filter
-- the recipe catalog by a tag (here, "vegan") lets the user or their
-- guests quickly see safe options. The same pattern works for any tag
-- (gluten-free, nut-free, etc.).
-- ============================================

SELECT DISTINCT
    r.name,
    r.cuisine,
    r.difficulty,
    (r.prep_time_min + r.cook_time_min) AS total_time_min
FROM recipes r
JOIN recipe_tags rt   ON r.id = rt.recipe_id
JOIN dietary_tags dt  ON rt.tag_id = dt.id
WHERE dt.tag_name = 'vegan'
ORDER BY r.name;


-- ============================================
-- QUERY 5: What is the estimated total cost of my weekly meal plan,
--           broken down by day?
-- ============================================
-- RELEVANCE: Budgeting matters alongside nutrition. If a user can see that
-- Wednesday's meals are disproportionately expensive, they can swap a recipe
-- for a cheaper alternative. This query gives daily and weekly cost
-- visibility so the user can plan meals that fit their finances.
-- ============================================

SELECT
    mp.date,
    ROUND(SUM(ri.quantity * i.price_per_unit), 2) AS daily_cost
FROM meal_plan mp
JOIN recipe_ingredients ri ON mp.recipe_id = ri.recipe_id
JOIN ingredients i         ON ri.ingredient_id = i.id
WHERE mp.date BETWEEN '2025-01-06' AND '2025-01-12'
GROUP BY mp.date
ORDER BY mp.date;

-- Weekly total:
SELECT
    ROUND(SUM(ri.quantity * i.price_per_unit), 2) AS weekly_total_cost
FROM meal_plan mp
JOIN recipe_ingredients ri ON mp.recipe_id = ri.recipe_id
JOIN ingredients i         ON ri.ingredient_id = i.id
WHERE mp.date BETWEEN '2025-01-06' AND '2025-01-12';
