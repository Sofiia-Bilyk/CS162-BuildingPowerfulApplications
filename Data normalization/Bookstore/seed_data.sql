-- Mock data for the Online Bookstore

-- Authors (6 rows)
INSERT INTO authors (name, country) VALUES ('George Orwell', 'United Kingdom');
INSERT INTO authors (name, country) VALUES ('Harper Lee', 'United States');
INSERT INTO authors (name, country) VALUES ('Gabriel Garcia Marquez', 'Colombia');
INSERT INTO authors (name, country) VALUES ('Haruki Murakami', 'Japan');
INSERT INTO authors (name, country) VALUES ('Chimamanda Ngozi Adichie', 'Nigeria');
INSERT INTO authors (name, country) VALUES ('Jane Austen', 'United Kingdom');

-- Categories (4 rows)
INSERT INTO categories (name) VALUES ('Fiction');
INSERT INTO categories (name) VALUES ('Dystopian');
INSERT INTO categories (name) VALUES ('Classic');
INSERT INTO categories (name) VALUES ('Magical Realism');

-- Books (8 rows)
INSERT INTO books (title, author_id, category_id, price) VALUES ('1984', 1, 2, 12.99);
INSERT INTO books (title, author_id, category_id, price) VALUES ('Animal Farm', 1, 2, 9.99);
INSERT INTO books (title, author_id, category_id, price) VALUES ('To Kill a Mockingbird', 2, 3, 14.99);
INSERT INTO books (title, author_id, category_id, price) VALUES ('One Hundred Years of Solitude', 3, 4, 16.99);
INSERT INTO books (title, author_id, category_id, price) VALUES ('Norwegian Wood', 4, 1, 13.50);
INSERT INTO books (title, author_id, category_id, price) VALUES ('Purple Hibiscus', 5, 1, 11.99);
INSERT INTO books (title, author_id, category_id, price) VALUES ('Pride and Prejudice', 6, 3, 10.50);
INSERT INTO books (title, author_id, category_id, price) VALUES ('Kafka on the Shore', 4, 1, 14.00);

-- Inventory (8 rows — one per book)
INSERT INTO inventory (book_id, quantity) VALUES (1, 25);
INSERT INTO inventory (book_id, quantity) VALUES (2, 30);
INSERT INTO inventory (book_id, quantity) VALUES (3, 12);
INSERT INTO inventory (book_id, quantity) VALUES (4, 8);
INSERT INTO inventory (book_id, quantity) VALUES (5, 20);
INSERT INTO inventory (book_id, quantity) VALUES (6, 15);
INSERT INTO inventory (book_id, quantity) VALUES (7, 18);
INSERT INTO inventory (book_id, quantity) VALUES (8, 10);

-- Customers (5 rows)
INSERT INTO customers (name, email) VALUES ('Alice Johnson', 'alice@example.com');
INSERT INTO customers (name, email) VALUES ('Bob Smith', 'bob@example.com');
INSERT INTO customers (name, email) VALUES ('Carol White', 'carol@example.com');
INSERT INTO customers (name, email) VALUES ('David Brown', 'david@example.com');
INSERT INTO customers (name, email) VALUES ('Eva Martinez', 'eva@example.com');

-- Orders (7 rows)
INSERT INTO orders (customer_id, order_date) VALUES (1, '2026-01-05');
INSERT INTO orders (customer_id, order_date) VALUES (2, '2026-01-10');
INSERT INTO orders (customer_id, order_date) VALUES (1, '2026-01-20');
INSERT INTO orders (customer_id, order_date) VALUES (3, '2026-02-01');
INSERT INTO orders (customer_id, order_date) VALUES (4, '2026-02-05');
INSERT INTO orders (customer_id, order_date) VALUES (5, '2026-02-10');
INSERT INTO orders (customer_id, order_date) VALUES (2, '2026-02-15');

-- Order_items (12 rows)
INSERT INTO order_items (order_id, book_id, quantity) VALUES (1, 1, 1);
INSERT INTO order_items (order_id, book_id, quantity) VALUES (1, 3, 2);
INSERT INTO order_items (order_id, book_id, quantity) VALUES (2, 5, 1);
INSERT INTO order_items (order_id, book_id, quantity) VALUES (2, 7, 1);
INSERT INTO order_items (order_id, book_id, quantity) VALUES (3, 4, 1);
INSERT INTO order_items (order_id, book_id, quantity) VALUES (3, 6, 1);
INSERT INTO order_items (order_id, book_id, quantity) VALUES (4, 2, 3);
INSERT INTO order_items (order_id, book_id, quantity) VALUES (4, 8, 1);
INSERT INTO order_items (order_id, book_id, quantity) VALUES (5, 1, 2);
INSERT INTO order_items (order_id, book_id, quantity) VALUES (5, 5, 1);
INSERT INTO order_items (order_id, book_id, quantity) VALUES (6, 3, 1);
INSERT INTO order_items (order_id, book_id, quantity) VALUES (7, 4, 1);
