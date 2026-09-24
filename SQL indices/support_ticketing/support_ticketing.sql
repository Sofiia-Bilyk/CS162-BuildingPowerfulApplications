-- ============================================================
-- E-commerce Customer Support Ticketing System
-- Run with: sqlite3 support_ticketing.db < support_ticketing.sql
-- ============================================================

PRAGMA foreign_keys = ON;
.mode column
.headers on

-- ============================================================
-- SCHEMA
-- ============================================================

-- Shoppers who place orders and open support tickets.
-- tier (standard / premium / vip) affects response priority.
CREATE TABLE Customer (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    phone       TEXT    NOT NULL,
    tier        TEXT    NOT NULL DEFAULT 'standard'
                    CHECK(tier IN ('standard','premium','vip')),
    joined_at   TEXT    NOT NULL   -- ISO-8601 datetime
);

-- Catalogue of items sold in the store.
CREATE TABLE Product (
    product_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    price       REAL    NOT NULL,
    sku         TEXT    NOT NULL UNIQUE
);

-- A purchase transaction. Named CustomerOrder to avoid the
-- SQL reserved word ORDER.
CREATE TABLE CustomerOrder (
    order_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date  TEXT    NOT NULL,
    total_amount REAL   NOT NULL,
    status      TEXT    NOT NULL
                    CHECK(status IN ('processing','shipped','delivered','returned','cancelled')),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- One row per product line inside an order (handles multi-item orders).
-- unit_price is stored at purchase time so it survives future price changes.
CREATE TABLE OrderItem (
    item_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL DEFAULT 1,
    unit_price REAL    NOT NULL,
    FOREIGN KEY (order_id)   REFERENCES CustomerOrder(order_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- Support staff who handle tickets.
CREATE TABLE Agent (
    agent_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL UNIQUE,
    department TEXT    NOT NULL
);

-- A support request raised by a customer, optionally linked to
-- a specific order. agent_id may be NULL if not yet assigned.
-- category groups tickets by problem type for reporting.
-- resolved_at is NULL while the ticket is open or in progress.
CREATE TABLE Ticket (
    ticket_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_id    INTEGER,                      -- NULL for account-level issues
    agent_id    INTEGER,                      -- NULL if unassigned
    subject     TEXT    NOT NULL,
    category    TEXT    NOT NULL
                    CHECK(category IN ('billing','shipping','technical','refund','general')),
    priority    TEXT    NOT NULL DEFAULT 'medium'
                    CHECK(priority IN ('low','medium','high')),
    status      TEXT    NOT NULL DEFAULT 'open'
                    CHECK(status IN ('open','in_progress','resolved')),
    created_at  TEXT    NOT NULL,
    resolved_at TEXT,                         -- NULL while unresolved
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (order_id)    REFERENCES CustomerOrder(order_id),
    FOREIGN KEY (agent_id)    REFERENCES Agent(agent_id)
);

-- Individual messages within a ticket thread.
-- sender_type distinguishes customer replies from agent replies.
-- sender_id holds customer_id or agent_id depending on sender_type.
CREATE TABLE TicketMessage (
    message_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id   INTEGER NOT NULL,
    sender_type TEXT    NOT NULL CHECK(sender_type IN ('customer','agent')),
    sender_id   INTEGER NOT NULL,
    message     TEXT    NOT NULL,
    sent_at     TEXT    NOT NULL,
    FOREIGN KEY (ticket_id) REFERENCES Ticket(ticket_id)
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Q1 agent queue: retrieve all open tickets for one agent in one seek.
-- Without this, the DB scans every ticket and checks agent_id + status per row.
CREATE INDEX idx_ticket_agent_status
    ON Ticket(agent_id, status);

-- Q3 customer ticket volume: jump to a customer's tickets and filter by date.
CREATE INDEX idx_ticket_customer_date
    ON Ticket(customer_id, created_at);

-- Q2 resolution time by category: group without scanning unrelated categories.
CREATE INDEX idx_ticket_category
    ON Ticket(category);

-- Q5 message thread: retrieve messages for one ticket sorted by time cheaply.
-- A covering index – the query only needs ticket_id, sent_at, and the
-- other columns, all stored in the index node, so no table row fetch is needed
-- for the ORDER BY pass.
CREATE INDEX idx_message_ticket_time
    ON TicketMessage(ticket_id, sent_at);

-- Q4 product ticket analysis: find order items for a given product quickly.
CREATE INDEX idx_orderitem_product
    ON OrderItem(product_id);

-- Join accelerator: look up all items in an order without a full OrderItem scan.
CREATE INDEX idx_orderitem_order
    ON OrderItem(order_id);

-- Join accelerator: find all orders for a customer.
CREATE INDEX idx_order_customer
    ON CustomerOrder(customer_id);

-- ============================================================
-- DATA
-- ============================================================

INSERT INTO Customer (name, email, phone, tier, joined_at) VALUES
    ('Sarah Connor',   'sarah@shop.com',   '555-2001', 'premium',  '2023-03-12 08:00'),
    ('John Smith',     'john@shop.com',    '555-2002', 'standard', '2022-07-04 09:30'),
    ('Emily Chen',     'emily@shop.com',   '555-2003', 'premium',  '2021-11-19 14:00'),
    ('Michael Brown',  'michael@shop.com', '555-2004', 'standard', '2024-01-08 11:00'),
    ('Jessica Davis',  'jessica@shop.com', '555-2005', 'vip',      '2020-06-22 10:00'),
    ('Chris Wilson',   'chris@shop.com',   '555-2006', 'standard', '2023-09-15 16:00'),
    ('Amy Taylor',     'amy@shop.com',     '555-2007', 'premium',  '2022-02-28 13:00'),
    ('Robert Martinez','robert@shop.com',  '555-2008', 'standard', '2024-05-01 09:00');

INSERT INTO Product (name, category, price, sku) VALUES
    ('Wireless Headphones', 'Electronics',  79.99, 'ELEC-WH-001'),
    ('Running Shoes',       'Footwear',    129.99, 'FOOT-RS-002'),
    ('Coffee Maker',        'Appliances',   89.99, 'APPL-CM-003'),
    ('Yoga Mat',            'Sports',       34.99, 'SPRT-YM-004'),
    ('Laptop Stand',        'Electronics',  49.99, 'ELEC-LS-005'),
    ('Desk Lamp',           'Home Office',  39.99, 'HOME-DL-006'),
    ('Protein Powder',      'Nutrition',    54.99, 'NUTR-PP-007'),
    ('Smart Watch',         'Electronics', 199.99, 'ELEC-SW-008');

INSERT INTO CustomerOrder (customer_id, order_date, total_amount, status) VALUES
    (2, '2025-12-20', 129.98, 'delivered'),   -- order 1: Headphones + Laptop Stand
    (1, '2026-01-15', 199.99, 'delivered'),   -- order 2: Smart Watch
    (3, '2026-02-10',  79.99, 'delivered'),   -- order 3: Wireless Headphones
    (1, '2026-02-18', 129.99, 'shipped'),     -- order 4: Running Shoes
    (4, '2025-12-15',  34.99, 'returned'),    -- order 5: Yoga Mat
    (6, '2025-10-25', 199.99, 'delivered'),   -- order 6: Smart Watch
    (5, '2026-02-01',  89.99, 'delivered'),   -- order 7: Coffee Maker
    (7, '2026-02-20',  49.99, 'delivered'),   -- order 8: Laptop Stand
    (8, '2026-01-20', 159.98, 'delivered'),   -- order 9: Headphones x2
    (5, '2025-09-20',  54.99, 'delivered');   -- order 10: Protein Powder

INSERT INTO OrderItem (order_id, product_id, quantity, unit_price) VALUES
    (1,  1, 1, 79.99),   -- order 1: Wireless Headphones
    (1,  5, 1, 49.99),   -- order 1: Laptop Stand
    (2,  8, 1, 199.99),  -- order 2: Smart Watch
    (3,  1, 1, 79.99),   -- order 3: Wireless Headphones
    (4,  2, 1, 129.99),  -- order 4: Running Shoes
    (5,  4, 1, 34.99),   -- order 5: Yoga Mat
    (6,  8, 1, 199.99),  -- order 6: Smart Watch
    (7,  3, 1, 89.99),   -- order 7: Coffee Maker
    (8,  5, 1, 49.99),   -- order 8: Laptop Stand
    (9,  1, 2, 79.99),   -- order 9: Wireless Headphones (qty 2)
    (10, 7, 1, 54.99);   -- order 10: Protein Powder

INSERT INTO Agent (name, email, department) VALUES
    ('Tom Baker',    'tom@support.com',   'Billing'),
    ('Lisa Park',    'lisa@support.com',  'Technical Support'),
    ('James Nguyen', 'james@support.com', 'Shipping'),
    ('Dana Foster',  'dana@support.com',  'Returns'),
    ('Arun Patel',   'arun@support.com',  'General Support');

-- Tickets for Q3: customer 1 (Sarah) has 2 open tickets → most open tickets.
-- Tickets for Q2: resolved tickets span billing(1 day), shipping(2 days),
--                 technical(1 day), refund(2 days), general(same day).
INSERT INTO Ticket (customer_id, order_id, agent_id, subject, category, priority, status, created_at, resolved_at) VALUES
    (1, 2,  1, 'Billing charge looks incorrect',        'billing',   'high',   'open',        '2026-02-10 09:00', NULL),
    (2, 1,  3, 'Package has not arrived',               'shipping',  'medium', 'resolved',    '2026-01-15 11:00', '2026-01-17 14:00'),
    (3, 3,  2, 'Headphones have static in left ear',    'technical', 'high',   'in_progress', '2026-02-18 10:00', NULL),
    (4, 5,  4, 'Want to return yoga mat',               'refund',    'low',    'resolved',    '2025-12-20 08:00', '2025-12-22 16:00'),
    (5, 7,  1, 'Return approved but refund not received','refund',   'high',   'open',        '2026-02-15 14:00', NULL),
    (1, 4,  1, 'Wrong item delivered in my order',      'shipping',  'medium', 'open',        '2026-02-20 16:00', NULL),
    (6, 6,  5, 'How do I set up the smart watch?',      'technical', 'low',    'resolved',    '2025-11-10 10:00', '2025-11-11 09:00'),
    (7, 8,  2, 'Laptop stand is wobbly and unstable',   'technical', 'medium', 'in_progress', '2026-02-22 13:00', NULL),
    (2, 1,  3, 'Still waiting — package not arrived',   'shipping',  'high',   'open',        '2026-02-01 09:00', NULL),
    (8, 9,  1, 'Charged twice for the same order',      'billing',   'high',   'resolved',    '2026-01-28 10:00', '2026-01-29 11:00'),
    (3, 3,  4, 'Requesting refund for faulty headphones','refund',   'medium', 'open',        '2026-02-19 15:00', NULL),
    (5, 10, 5, 'Question about protein powder expiry',  'general',   'low',    'resolved',    '2025-10-05 09:00', '2025-10-05 17:00');

-- Conversation thread for ticket 3 (Emily's static headphones – Q5).
INSERT INTO TicketMessage (ticket_id, sender_type, sender_id, message, sent_at) VALUES
    (3, 'customer', 3, 'My headphones have static noise in the left ear since I received them. Very frustrating!', '2026-02-18 10:05'),
    (3, 'agent',    2, 'Sorry to hear that! Could you try resetting them by holding the power button for 10 seconds while in the case?', '2026-02-18 11:30'),
    (3, 'customer', 3, 'I tried that three times and the static is still there. The right ear is fine but left is unusable.', '2026-02-18 14:00'),
    (3, 'agent',    2, 'Thank you for confirming. I am escalating this to a replacement. Please expect an email with a prepaid return label within 24 hours.', '2026-02-19 09:15'),
    -- A few messages from other tickets to populate the table.
    (1, 'customer', 1, 'I was charged $199.99 but the invoice says $159.99. Please advise.', '2026-02-10 09:10'),
    (1, 'agent',    1, 'Thank you for reaching out. I am pulling up your order now and will respond within 2 hours.', '2026-02-10 10:00'),
    (9, 'customer', 2, 'Order #1 placed six weeks ago — still nothing. Tracking has not updated in three weeks.', '2026-02-01 09:05'),
    (9, 'agent',    3, 'I am contacting the carrier on your behalf. I will update you within 48 hours.', '2026-02-01 11:00');

-- ============================================================
-- QUERIES
-- ============================================================

-- ------------------------------------------------------------
-- Q1: What open tickets are assigned to Agent 1 (Tom Baker)?
-- Relevance: Agents check their personal queue every morning
--            to prioritise the day's work.
-- Index used: idx_ticket_agent_status jumps directly to rows
--             where agent_id=1 AND status='open', returning
--             only the matching tickets without a full scan.
-- ------------------------------------------------------------
SELECT 'Q1: Open tickets assigned to Tom Baker (agent 1)' AS query;

EXPLAIN QUERY PLAN
SELECT  t.ticket_id,
        c.name          AS customer,
        t.subject,
        t.category,
        t.priority,
        t.created_at
FROM    Ticket   t
JOIN    Customer c ON c.customer_id = t.customer_id
WHERE   t.agent_id = 1
  AND   t.status   = 'open'
ORDER   BY t.priority DESC, t.created_at ASC;

SELECT  t.ticket_id,
        c.name          AS customer,
        t.subject,
        t.category,
        t.priority,
        t.created_at
FROM    Ticket   t
JOIN    Customer c ON c.customer_id = t.customer_id
WHERE   t.agent_id = 1
  AND   t.status   = 'open'
ORDER   BY t.priority DESC, t.created_at ASC;

-- ------------------------------------------------------------
-- Q2: What is the average resolution time (in hours) per
--     ticket category?
-- Relevance: Operations managers spot bottlenecks (e.g.
--            "refund tickets take 5× longer than technical
--            ones") and can reallocate agent headcount.
-- Index used: idx_ticket_category groups tickets by category
--             without a full sort.
-- SQLite stores datetimes as strings; julianday() converts
-- them to a floating-point day count so subtraction gives
-- elapsed days, which we multiply by 24 to get hours.
-- ------------------------------------------------------------
SELECT 'Q2: Average resolution time in hours by category' AS query;

EXPLAIN QUERY PLAN
SELECT   category,
         COUNT(*)                                                     AS resolved_count,
         ROUND(AVG((julianday(resolved_at) - julianday(created_at)) * 24), 1)
                                                                      AS avg_hours_to_resolve
FROM     Ticket
WHERE    status = 'resolved'
GROUP BY category
ORDER BY avg_hours_to_resolve;

SELECT   category,
         COUNT(*)                                                     AS resolved_count,
         ROUND(AVG((julianday(resolved_at) - julianday(created_at)) * 24), 1)
                                                                      AS avg_hours_to_resolve
FROM     Ticket
WHERE    status = 'resolved'
GROUP BY category
ORDER BY avg_hours_to_resolve;

-- ------------------------------------------------------------
-- Q3: Which customers have the most open tickets in the last
--     90 days (from 2026-02-24)?
-- Relevance: High-friction accounts often signal product
--            quality issues or misaligned expectations;
--            proactive outreach can prevent churn.
-- Index used: idx_ticket_customer_date seeks by customer then
--             filters on created_at within the index node,
--             avoiding a full Ticket scan.
-- ------------------------------------------------------------
SELECT 'Q3: Customers with most open tickets in last 90 days' AS query;

EXPLAIN QUERY PLAN
SELECT   c.customer_id,
         c.name,
         c.tier,
         COUNT(*) AS open_tickets
FROM     Ticket   t
JOIN     Customer c ON c.customer_id = t.customer_id
WHERE    t.status     = 'open'
  AND    t.created_at >= date('2026-02-24', '-90 days')
GROUP BY c.customer_id, c.name, c.tier
ORDER BY open_tickets DESC;

SELECT   c.customer_id,
         c.name,
         c.tier,
         COUNT(*) AS open_tickets
FROM     Ticket   t
JOIN     Customer c ON c.customer_id = t.customer_id
WHERE    t.status     = 'open'
  AND    t.created_at >= date('2026-02-24', '-90 days')
GROUP BY c.customer_id, c.name, c.tier
ORDER BY open_tickets DESC;

-- ------------------------------------------------------------
-- Q4: Which products appear most often in support tickets?
-- Relevance: The product team uses this to prioritise quality
--            improvements — a product generating many tickets
--            is either faulty or poorly documented.
-- Path: Ticket → CustomerOrder → OrderItem → Product.
--       A ticket references an order; that order may contain
--       multiple products, each of which gets counted.
-- Index used: idx_ticket_agent_status / idx_orderitem_order
--             and idx_orderitem_product accelerate the joins.
-- ------------------------------------------------------------
SELECT 'Q4: Products ranked by number of associated tickets' AS query;

EXPLAIN QUERY PLAN
SELECT   p.name          AS product,
         p.category,
         COUNT(DISTINCT t.ticket_id) AS ticket_count
FROM     Ticket        t
JOIN     CustomerOrder o  ON o.order_id   = t.order_id
JOIN     OrderItem     oi ON oi.order_id  = o.order_id
JOIN     Product       p  ON p.product_id = oi.product_id
WHERE    t.order_id IS NOT NULL
GROUP BY p.product_id, p.name, p.category
ORDER BY ticket_count DESC;

SELECT   p.name          AS product,
         p.category,
         COUNT(DISTINCT t.ticket_id) AS ticket_count
FROM     Ticket        t
JOIN     CustomerOrder o  ON o.order_id   = t.order_id
JOIN     OrderItem     oi ON oi.order_id  = o.order_id
JOIN     Product       p  ON p.product_id = oi.product_id
WHERE    t.order_id IS NOT NULL
GROUP BY p.product_id, p.name, p.category
ORDER BY ticket_count DESC;

-- ------------------------------------------------------------
-- Q5: Full conversation thread for Ticket 3 (Emily's
--     faulty headphones).
-- Relevance: Agents must read the full history before
--            responding — asking the customer to repeat
--            themselves destroys satisfaction scores.
-- Index used: idx_message_ticket_time is a covering index on
--             (ticket_id, sent_at). The query needs ticket_id
--             for the WHERE clause and sent_at for ORDER BY;
--             both live in the index node, so no table row
--             fetch is needed for the sort step.
-- ------------------------------------------------------------
SELECT 'Q5: Full message thread for Ticket 3' AS query;

EXPLAIN QUERY PLAN
SELECT  tm.sent_at,
        tm.sender_type,
        CASE tm.sender_type
            WHEN 'customer' THEN c.name
            WHEN 'agent'    THEN a.name
        END            AS sender_name,
        tm.message
FROM    TicketMessage tm
LEFT JOIN Customer c ON c.customer_id = tm.sender_id AND tm.sender_type = 'customer'
LEFT JOIN Agent    a ON a.agent_id    = tm.sender_id AND tm.sender_type = 'agent'
WHERE   tm.ticket_id = 3
ORDER   BY tm.sent_at;

SELECT  tm.sent_at,
        tm.sender_type,
        CASE tm.sender_type
            WHEN 'customer' THEN c.name
            WHEN 'agent'    THEN a.name
        END            AS sender_name,
        tm.message
FROM    TicketMessage tm
LEFT JOIN Customer c ON c.customer_id = tm.sender_id AND tm.sender_type = 'customer'
LEFT JOIN Agent    a ON a.agent_id    = tm.sender_id AND tm.sender_type = 'agent'
WHERE   tm.ticket_id = 3
ORDER   BY tm.sent_at;
