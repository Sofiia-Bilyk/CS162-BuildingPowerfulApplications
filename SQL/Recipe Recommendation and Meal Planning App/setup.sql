-- Recipe Recommendation and Meal Planning App
-- Database Setup with Schema and Mock Data

PRAGMA foreign_keys = ON;

-- ============================================
-- TABLE 1: dietary_tags
-- Labels like vegan, gluten-free, etc.
-- ============================================
CREATE TABLE IF NOT EXISTS dietary_tags (
    id INTEGER PRIMARY KEY,
    tag_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

INSERT INTO dietary_tags (id, tag_name, description) VALUES
    (1, 'vegan',        'Contains no animal products whatsoever'),
    (2, 'vegetarian',   'No meat or fish, but may include dairy and eggs'),
    (3, 'gluten-free',  'Free from wheat, barley, rye, and other gluten sources'),
    (4, 'dairy-free',   'Contains no milk, cheese, butter, or other dairy'),
    (5, 'low-carb',     'Under 20 g of carbohydrates per serving'),
    (6, 'high-protein', 'At least 25 g of protein per serving'),
    (7, 'nut-free',     'Free from all tree nuts and peanuts');

-- ============================================
-- TABLE 2: ingredients
-- Master list of ingredients with nutrition/cost
-- ============================================
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit TEXT NOT NULL,
    calories_per_unit REAL NOT NULL,
    price_per_unit REAL NOT NULL
);

INSERT INTO ingredients (id, name, category, unit, calories_per_unit, price_per_unit) VALUES
    (1,  'chicken breast',   'meat',      '100g', 165.0, 1.80),
    (2,  'salmon fillet',    'seafood',   '100g', 208.0, 3.50),
    (3,  'rice',             'grains',    '100g', 130.0, 0.30),
    (4,  'pasta',            'grains',    '100g', 131.0, 0.25),
    (5,  'eggs',             'dairy',     'unit', 72.0,  0.30),
    (6,  'milk',             'dairy',     '100ml', 42.0, 0.15),
    (7,  'cheddar cheese',   'dairy',     '100g', 403.0, 1.20),
    (8,  'olive oil',        'oils',      'tbsp',  119.0, 0.20),
    (9,  'broccoli',         'produce',   '100g', 34.0,  0.50),
    (10, 'spinach',          'produce',   '100g', 23.0,  0.60),
    (11, 'tomato',           'produce',   'unit', 22.0,  0.40),
    (12, 'onion',            'produce',   'unit', 44.0,  0.25),
    (13, 'garlic',           'produce',   'clove', 5.0,  0.10),
    (14, 'bell pepper',      'produce',   'unit', 31.0,  0.75),
    (15, 'banana',           'produce',   'unit', 105.0, 0.20),
    (16, 'oats',             'grains',    '100g', 389.0, 0.35),
    (17, 'black beans',      'legumes',   '100g', 132.0, 0.40),
    (18, 'tofu',             'protein',   '100g', 76.0,  0.55),
    (19, 'bread (whole wheat)', 'grains', 'slice', 69.0, 0.15),
    (20, 'avocado',          'produce',   'unit', 240.0, 1.50);

-- ============================================
-- TABLE 3: recipes
-- Core recipe information
-- ============================================
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    cuisine TEXT NOT NULL,
    prep_time_min INTEGER NOT NULL,
    cook_time_min INTEGER NOT NULL,
    servings INTEGER NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    description TEXT
);

INSERT INTO recipes (id, name, cuisine, prep_time_min, cook_time_min, servings, difficulty, description) VALUES
    (1,  'Grilled Chicken Salad',     'American',  10, 15, 2, 'easy',   'Light salad with grilled chicken, spinach, and tomatoes'),
    (2,  'Salmon with Broccoli',      'American',  10, 20, 2, 'medium', 'Pan-seared salmon served with steamed broccoli'),
    (3,  'Spaghetti Bolognese',       'Italian',   15, 30, 4, 'medium', 'Classic meat sauce over spaghetti pasta'),
    (4,  'Vegetable Stir-Fry',        'Asian',     15, 10, 2, 'easy',   'Quick stir-fry with tofu, bell pepper, and broccoli'),
    (5,  'Oatmeal with Banana',       'American',   5,  5, 1, 'easy',   'Quick breakfast oats topped with sliced banana'),
    (6,  'Avocado Toast',             'American',   5,  3, 1, 'easy',   'Whole wheat toast with mashed avocado and egg'),
    (7,  'Black Bean Tacos',          'Mexican',   10, 10, 3, 'easy',   'Seasoned black beans with peppers and onion in tortillas'),
    (8,  'Cheese Omelette',           'French',     5, 10, 1, 'easy',   'Fluffy omelette with cheddar cheese and spinach'),
    (9,  'Tofu Rice Bowl',            'Asian',     10, 20, 2, 'medium', 'Crispy tofu served over rice with garlic sauce'),
    (10, 'Chicken Pasta Bake',        'Italian',   15, 35, 4, 'medium', 'Baked pasta with chicken, cheese, and tomato sauce');

-- ============================================
-- TABLE 4: recipe_ingredients (junction)
-- Links recipes to their ingredients with qty
-- ============================================
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);

-- Recipe 1: Grilled Chicken Salad
INSERT INTO recipe_ingredients VALUES (1, 1, 2.0);   -- 200g chicken
INSERT INTO recipe_ingredients VALUES (1, 10, 1.5);  -- 150g spinach
INSERT INTO recipe_ingredients VALUES (1, 11, 2.0);  -- 2 tomatoes
INSERT INTO recipe_ingredients VALUES (1, 8, 2.0);   -- 2 tbsp olive oil

-- Recipe 2: Salmon with Broccoli
INSERT INTO recipe_ingredients VALUES (2, 2, 3.0);   -- 300g salmon
INSERT INTO recipe_ingredients VALUES (2, 9, 2.0);   -- 200g broccoli
INSERT INTO recipe_ingredients VALUES (2, 13, 3.0);  -- 3 cloves garlic
INSERT INTO recipe_ingredients VALUES (2, 8, 1.0);   -- 1 tbsp olive oil

-- Recipe 3: Spaghetti Bolognese
INSERT INTO recipe_ingredients VALUES (3, 4, 4.0);   -- 400g pasta
INSERT INTO recipe_ingredients VALUES (3, 1, 3.0);   -- 300g chicken (ground)
INSERT INTO recipe_ingredients VALUES (3, 11, 3.0);  -- 3 tomatoes
INSERT INTO recipe_ingredients VALUES (3, 12, 1.0);  -- 1 onion
INSERT INTO recipe_ingredients VALUES (3, 13, 2.0);  -- 2 cloves garlic
INSERT INTO recipe_ingredients VALUES (3, 8, 2.0);   -- 2 tbsp olive oil

-- Recipe 4: Vegetable Stir-Fry
INSERT INTO recipe_ingredients VALUES (4, 18, 2.0);  -- 200g tofu
INSERT INTO recipe_ingredients VALUES (4, 14, 2.0);  -- 2 bell peppers
INSERT INTO recipe_ingredients VALUES (4, 9, 1.5);   -- 150g broccoli
INSERT INTO recipe_ingredients VALUES (4, 13, 2.0);  -- 2 cloves garlic
INSERT INTO recipe_ingredients VALUES (4, 8, 2.0);   -- 2 tbsp olive oil

-- Recipe 5: Oatmeal with Banana
INSERT INTO recipe_ingredients VALUES (5, 16, 1.0);  -- 100g oats
INSERT INTO recipe_ingredients VALUES (5, 6, 2.0);   -- 200ml milk
INSERT INTO recipe_ingredients VALUES (5, 15, 1.0);  -- 1 banana

-- Recipe 6: Avocado Toast
INSERT INTO recipe_ingredients VALUES (6, 19, 2.0);  -- 2 slices bread
INSERT INTO recipe_ingredients VALUES (6, 20, 1.0);  -- 1 avocado
INSERT INTO recipe_ingredients VALUES (6, 5, 1.0);   -- 1 egg

-- Recipe 7: Black Bean Tacos
INSERT INTO recipe_ingredients VALUES (7, 17, 2.0);  -- 200g black beans
INSERT INTO recipe_ingredients VALUES (7, 14, 1.0);  -- 1 bell pepper
INSERT INTO recipe_ingredients VALUES (7, 12, 1.0);  -- 1 onion
INSERT INTO recipe_ingredients VALUES (7, 8, 1.0);   -- 1 tbsp olive oil

-- Recipe 8: Cheese Omelette
INSERT INTO recipe_ingredients VALUES (8, 5, 3.0);   -- 3 eggs
INSERT INTO recipe_ingredients VALUES (8, 7, 0.5);   -- 50g cheddar
INSERT INTO recipe_ingredients VALUES (8, 10, 0.5);  -- 50g spinach
INSERT INTO recipe_ingredients VALUES (8, 8, 1.0);   -- 1 tbsp olive oil

-- Recipe 9: Tofu Rice Bowl
INSERT INTO recipe_ingredients VALUES (9, 18, 2.0);  -- 200g tofu
INSERT INTO recipe_ingredients VALUES (9, 3, 2.0);   -- 200g rice
INSERT INTO recipe_ingredients VALUES (9, 13, 3.0);  -- 3 cloves garlic
INSERT INTO recipe_ingredients VALUES (9, 8, 2.0);   -- 2 tbsp olive oil

-- Recipe 10: Chicken Pasta Bake
INSERT INTO recipe_ingredients VALUES (10, 1, 3.0);  -- 300g chicken
INSERT INTO recipe_ingredients VALUES (10, 4, 3.0);  -- 300g pasta
INSERT INTO recipe_ingredients VALUES (10, 7, 1.0);  -- 100g cheddar
INSERT INTO recipe_ingredients VALUES (10, 11, 2.0); -- 2 tomatoes
INSERT INTO recipe_ingredients VALUES (10, 12, 1.0); -- 1 onion
INSERT INTO recipe_ingredients VALUES (10, 8, 1.0);  -- 1 tbsp olive oil

-- ============================================
-- TABLE 5: recipe_tags (junction)
-- Links recipes to dietary tags
-- ============================================
CREATE TABLE IF NOT EXISTS recipe_tags (
    recipe_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (recipe_id, tag_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (tag_id) REFERENCES dietary_tags(id)
);

-- Grilled Chicken Salad: gluten-free, dairy-free, low-carb, high-protein
INSERT INTO recipe_tags VALUES (1, 3);
INSERT INTO recipe_tags VALUES (1, 4);
INSERT INTO recipe_tags VALUES (1, 5);
INSERT INTO recipe_tags VALUES (1, 6);

-- Salmon with Broccoli: gluten-free, dairy-free, high-protein
INSERT INTO recipe_tags VALUES (2, 3);
INSERT INTO recipe_tags VALUES (2, 4);
INSERT INTO recipe_tags VALUES (2, 6);

-- Spaghetti Bolognese: dairy-free, high-protein
INSERT INTO recipe_tags VALUES (3, 4);
INSERT INTO recipe_tags VALUES (3, 6);

-- Vegetable Stir-Fry: vegan, dairy-free, gluten-free, nut-free
INSERT INTO recipe_tags VALUES (4, 1);
INSERT INTO recipe_tags VALUES (4, 4);
INSERT INTO recipe_tags VALUES (4, 3);
INSERT INTO recipe_tags VALUES (4, 7);

-- Oatmeal with Banana: vegetarian, nut-free
INSERT INTO recipe_tags VALUES (5, 2);
INSERT INTO recipe_tags VALUES (5, 7);

-- Avocado Toast: vegetarian, dairy-free, nut-free
INSERT INTO recipe_tags VALUES (6, 2);
INSERT INTO recipe_tags VALUES (6, 4);
INSERT INTO recipe_tags VALUES (6, 7);

-- Black Bean Tacos: vegan, dairy-free, gluten-free, nut-free, high-protein
INSERT INTO recipe_tags VALUES (7, 1);
INSERT INTO recipe_tags VALUES (7, 4);
INSERT INTO recipe_tags VALUES (7, 3);
INSERT INTO recipe_tags VALUES (7, 7);
INSERT INTO recipe_tags VALUES (7, 6);

-- Cheese Omelette: vegetarian, gluten-free, low-carb, nut-free
INSERT INTO recipe_tags VALUES (8, 2);
INSERT INTO recipe_tags VALUES (8, 3);
INSERT INTO recipe_tags VALUES (8, 5);
INSERT INTO recipe_tags VALUES (8, 7);

-- Tofu Rice Bowl: vegan, dairy-free, gluten-free, nut-free
INSERT INTO recipe_tags VALUES (9, 1);
INSERT INTO recipe_tags VALUES (9, 4);
INSERT INTO recipe_tags VALUES (9, 3);
INSERT INTO recipe_tags VALUES (9, 7);

-- Chicken Pasta Bake: nut-free, high-protein
INSERT INTO recipe_tags VALUES (10, 7);
INSERT INTO recipe_tags VALUES (10, 6);

-- ============================================
-- TABLE 6: meal_plan
-- Weekly plan assigning recipes to meals
-- ============================================
CREATE TABLE IF NOT EXISTS meal_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    meal_type TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    recipe_id INTEGER NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);

-- Week of 2025-01-06 to 2025-01-12
INSERT INTO meal_plan (date, meal_type, recipe_id) VALUES
    -- Monday
    ('2025-01-06', 'breakfast', 5),   -- Oatmeal with Banana
    ('2025-01-06', 'lunch',     1),   -- Grilled Chicken Salad
    ('2025-01-06', 'dinner',    3),   -- Spaghetti Bolognese

    -- Tuesday
    ('2025-01-07', 'breakfast', 6),   -- Avocado Toast
    ('2025-01-07', 'lunch',     4),   -- Vegetable Stir-Fry
    ('2025-01-07', 'dinner',    2),   -- Salmon with Broccoli

    -- Wednesday
    ('2025-01-08', 'breakfast', 8),   -- Cheese Omelette
    ('2025-01-08', 'lunch',     7),   -- Black Bean Tacos
    ('2025-01-08', 'dinner',   10),   -- Chicken Pasta Bake

    -- Thursday
    ('2025-01-09', 'breakfast', 5),   -- Oatmeal with Banana
    ('2025-01-09', 'lunch',     9),   -- Tofu Rice Bowl
    ('2025-01-09', 'dinner',    1),   -- Grilled Chicken Salad

    -- Friday
    ('2025-01-10', 'breakfast', 6),   -- Avocado Toast
    ('2025-01-10', 'lunch',     7),   -- Black Bean Tacos
    ('2025-01-10', 'dinner',    3),   -- Spaghetti Bolognese

    -- Saturday
    ('2025-01-11', 'breakfast', 8),   -- Cheese Omelette
    ('2025-01-11', 'lunch',     4),   -- Vegetable Stir-Fry
    ('2025-01-11', 'dinner',    2),   -- Salmon with Broccoli

    -- Sunday
    ('2025-01-12', 'breakfast', 5),   -- Oatmeal with Banana
    ('2025-01-12', 'lunch',     9),   -- Tofu Rice Bowl
    ('2025-01-12', 'dinner',   10);   -- Chicken Pasta Bake
