-- Online Bookstore and Inventory Management

-- Authors table: stores author information separately (normalized out of books)
CREATE TABLE authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT
);

-- Categories table: book genres/categories stored separately
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Books table: each book references its author and category via foreign keys
CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (author_id) REFERENCES authors(author_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Inventory table: tracks stock per book (separated from books to isolate stock changes)
CREATE TABLE inventory (
    book_id INTEGER PRIMARY KEY,
    quantity INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- Customers table: stores customer details
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

-- Orders table: each order belongs to one customer
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,  -- stored as ISO-8601 string (e.g. '2026-01-15')
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Order_items table: junction table linking orders to books (many-to-many)
-- This uses a composite key (order_id, book_id)
CREATE TABLE order_items (
    order_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (order_id, book_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);
