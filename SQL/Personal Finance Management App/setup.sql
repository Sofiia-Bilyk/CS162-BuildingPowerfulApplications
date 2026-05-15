-- Personal Finance Management App
-- Database Setup with Schema and Mock Data

PRAGMA foreign_keys = ON;

-- ============================================
-- TABLE 1: currency_rates
-- Stores conversion rates to USD
-- ============================================
CREATE TABLE IF NOT EXISTS currency_rates (
    currency TEXT PRIMARY KEY,
    conversion_rate REAL NOT NULL
);

INSERT INTO currency_rates (currency, conversion_rate) VALUES
    ('USD', 1.0),
    ('EUR', 1.08),
    ('UAH', 0.024),
    ('JPY', 0.0067);

-- ============================================
-- TABLE 2: categories
-- Defines spending categories with budget %
-- ============================================
CREATE TABLE IF NOT EXISTS categories (
    category TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    percentage INTEGER NOT NULL
);

INSERT INTO categories (category, description, percentage) VALUES
    ('income',        'Any income transaction: salary, freelance, gifts, refunds',                   0),
    ('savings',       'Money set aside for future goals, emergency fund, investments',              20),
    ('food',          'Groceries, dining out, coffee shops, food delivery',                         15),
    ('housing',       'Rent, mortgage, utilities, home maintenance and repairs',                    25),
    ('transport',     'Public transit, fuel, car maintenance, ride-sharing services',                8),
    ('health',        'Doctor visits, pharmacy, gym membership, mental health services',             5),
    ('entertainment', 'Movies, games, streaming subscriptions, concerts, hobbies',                  5),
    ('education',     'Courses, books, tutoring, school supplies, workshops',                       5),
    ('clothing',      'Clothes, shoes, accessories, laundry and dry cleaning',                      4),
    ('personal_care', 'Hygiene products, haircuts, skincare, cosmetics',                            3),
    ('gifts',         'Presents for others, charitable donations, holiday spending',                 5),
    ('miscellaneous', 'Anything that does not fit other categories: fees, fines, unexpected costs',  5);

-- ============================================
-- TABLE 3: paying_resources
-- Cards and cash sources used for payments
-- ============================================
CREATE TABLE IF NOT EXISTS paying_resources (
    id INTEGER PRIMARY KEY,
    card_number TEXT,
    currency TEXT NOT NULL,
    expiration_date TEXT,
    FOREIGN KEY (currency) REFERENCES currency_rates(currency)
);

-- 5 cards
INSERT INTO paying_resources (id, card_number, currency, expiration_date) VALUES
    (1, '4111-1111-1111-1234', 'USD', '2027-09'),
    (2, '5200-8282-8282-5678', 'EUR', '2026-12'),
    (3, '4000-1234-5678-9012', 'UAH', '2028-03'),
    (4, '3530-1113-3330-0000', 'JPY', '2027-06'),
    (5, '4916-3388-2200-7749', 'USD', '2026-08');

-- Cash rows for each currency
INSERT INTO paying_resources (id, card_number, currency, expiration_date) VALUES
    (6, NULL, 'USD', NULL),
    (7, NULL, 'EUR', NULL),
    (8, NULL, 'UAH', NULL),
    (9, NULL, 'JPY', NULL);

-- ============================================
-- TABLE 4: daily_logs
-- Main transaction log (30 rows)
-- ============================================
CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    category TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('income', 'expense')),
    description TEXT,
    source INTEGER NOT NULL,
    rationality INTEGER NOT NULL CHECK (rationality IN (0, 1)),
    FOREIGN KEY (currency) REFERENCES currency_rates(currency),
    FOREIGN KEY (category) REFERENCES categories(category),
    FOREIGN KEY (source) REFERENCES paying_resources(id)
);

-- === INCOME transactions ===
INSERT INTO daily_logs (date, amount, currency, category, state, description, source, rationality) VALUES
    ('2025-01-05', 3200.00, 'USD', 'income',    'income',  'Monthly salary',                          1, 1),
    ('2025-01-12', 500.00,  'EUR', 'income',    'income',  'Freelance web design project',            2, 1),
    ('2025-01-20', 45000.00,'UAH', 'income',    'income',  'Part-time tutoring payout',               3, 1),
    ('2025-01-28', 150.00,  'USD', 'income',    'income',  'Birthday gift from grandma',              6, 1);

-- === FOOD ===
INSERT INTO daily_logs (date, amount, currency, category, state, description, source, rationality) VALUES
    ('2025-01-03', 62.40,   'USD', 'food',      'expense', 'Weekly groceries at Walmart',             1, 1),
    ('2025-01-08', 34.50,   'USD', 'food',      'expense', 'Dinner with friends at restaurant',       1, 0),
    ('2025-01-14', 1200.00, 'UAH', 'food',      'expense', 'Groceries from local market',             3, 1),
    ('2025-01-19', 2500.00, 'JPY', 'food',      'expense', 'Sushi takeout',                           4, 1),
    ('2025-01-25', 18.90,   'USD', 'food',      'expense', 'Coffee and pastry',                       6, 0);

-- === HOUSING ===
INSERT INTO daily_logs (date, amount, currency, category, state, description, source, rationality) VALUES
    ('2025-01-01', 950.00,  'USD', 'housing',   'expense', 'Monthly rent payment',                    1, 1),
    ('2025-01-15', 85.00,   'USD', 'housing',   'expense', 'Electricity and water bill',              5, 1);

-- === TRANSPORT ===
INSERT INTO daily_logs (date, amount, currency, category, state, description, source, rationality) VALUES
    ('2025-01-06', 45.00,   'USD', 'transport', 'expense', 'Monthly metro pass',                      6, 1),
    ('2025-01-18', 28.50,   'EUR', 'transport', 'expense', 'Uber ride to airport',                    2, 1),
    ('2025-01-22', 600.00,  'UAH', 'transport', 'expense', 'Taxi across city',                        8, 0);

-- === HEALTH ===
INSERT INTO daily_logs (date, amount, currency, category, state, description, source, rationality) VALUES
    ('2025-01-10', 120.00,  'USD', 'health',    'expense', 'Doctor visit copay',                      1, 1),
    ('2025-01-17', 35.00,   'USD', 'health',    'expense', 'Pharmacy — cold medicine',                6, 1),
    ('2025-01-24', 50.00,   'USD', 'health',    'expense', 'Monthly gym membership',                  5, 1);

-- === ENTERTAINMENT ===
INSERT INTO daily_logs (date, amount, currency, category, state, description, source, rationality) VALUES
    ('2025-01-07', 15.99,   'USD', 'entertainment', 'expense', 'Netflix subscription',                1, 1),
    ('2025-01-13', 45.00,   'EUR', 'entertainment', 'expense', 'Concert tickets',                     2, 0),
    ('2025-01-21', 9.99,    'USD', 'entertainment', 'expense', 'Spotify premium',                     5, 1),
    ('2025-01-29', 60.00,   'USD', 'entertainment', 'expense', 'Video game purchase',                 1, 0);

-- === EDUCATION ===
INSERT INTO daily_logs (date, amount, currency, category, state, description, source, rationality) VALUES
    ('2025-01-04', 29.99,   'USD', 'education', 'expense', 'Udemy course on Python',                  1, 1),
    ('2025-01-16', 42.00,   'EUR', 'education', 'expense', 'Programming textbook',                    2, 1);

-- === CLOTHING ===
INSERT INTO daily_logs (date, amount, currency, category, state, description, source, rationality) VALUES
    ('2025-01-09', 89.00,   'USD', 'clothing',  'expense', 'Winter jacket on sale',                   1, 1),
    ('2025-01-26', 3500.00, 'UAH', 'clothing',  'expense', 'New pair of boots',                       3, 0);

-- === PERSONAL CARE ===
INSERT INTO daily_logs (date, amount, currency, category, state, description, source, rationality) VALUES
    ('2025-01-11', 25.00,   'USD', 'personal_care', 'expense', 'Haircut',                             6, 1),
    ('2025-01-23', 18.50,   'USD', 'personal_care', 'expense', 'Skincare products',                   1, 1);

-- === GIFTS ===
INSERT INTO daily_logs (date, amount, currency, category, state, description, source, rationality) VALUES
    ('2025-01-15', 75.00,   'USD', 'gifts',     'expense', 'Birthday present for a friend',           1, 1);

-- === SAVINGS ===
INSERT INTO daily_logs (date, amount, currency, category, state, description, source, rationality) VALUES
    ('2025-01-30', 400.00,  'USD', 'savings',   'expense', 'Monthly transfer to savings account',     1, 1);

-- === MISCELLANEOUS ===
INSERT INTO daily_logs (date, amount, currency, category, state, description, source, rationality) VALUES
    ('2025-01-27', 150.00,  'USD', 'miscellaneous', 'expense', 'Phone screen repair',                 5, 1);
