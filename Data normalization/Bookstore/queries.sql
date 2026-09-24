-- ============================================================
-- QUERIES FOR THE ONLINE BOOKSTORE
-- ============================================================

-- Q1: What books does the store sell, and who are their authors?
-- WHY: A customer browsing the store needs to see the catalog with author names.
-- This is the most basic lookup any bookstore app would need.

SELECT b.title, a.name AS author, c.name AS category, b.price
FROM books b
JOIN authors a ON b.author_id = a.author_id
JOIN categories c ON b.category_id = c.category_id
ORDER BY b.title;

-- Q2: Which books are low in stock (fewer than 15 copies)?
-- WHY: The store manager needs to know which books to reorder
-- so the store doesn't run out of popular titles.

SELECT b.title, i.quantity
FROM inventory i
JOIN books b ON i.book_id = b.book_id
WHERE i.quantity < 15
ORDER BY i.quantity;

-- Q3: Which author's books have been ordered the most (by total copies sold)?
-- WHY: Helps the store decide which authors to stock more of
-- and which authors to feature in promotions.

SELECT a.name AS author, SUM(oi.quantity) AS total_copies_sold
FROM order_items oi
JOIN books b ON oi.book_id = b.book_id
JOIN authors a ON b.author_id = a.author_id
GROUP BY a.author_id
ORDER BY total_copies_sold DESC;
