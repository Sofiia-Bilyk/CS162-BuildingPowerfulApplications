# Online Bookstore and Inventory Management

A database for an online bookstore that tracks books, authors, inventory stock levels, customers, and their orders.

## Tables

- **authors** — Stores author details (name, country). Separated from books to avoid repeating author info for every book.
- **categories** — Book genres (e.g. Fiction, Dystopian). Normalized out so category names are stored once.
- **books** — The book catalog. Each book references an author and a category via foreign keys.
- **inventory** — Stock quantity per book. Separated from books so stock updates don't touch the catalog table.
- **customers** — Registered customers with name and email.
- **orders** — Each order belongs to one customer and has a date.
- **order_items** — Junction table linking orders to books (many-to-many). Uses a **composite key** `(order_id, book_id)`.

## Schema Diagram

```
ONLINE BOOKSTORE — SCHEMA DIAGRAM 
=========================================

  +------------+       +------------+
  |  authors   |       | categories |
  +------------+       +------------+
  | author_id  |PK     |category_id |PK
  | name       |       | name       |
  | country    |       +------------+
  +------------+            |
       |                    |
       | 1:N                | 1:N
       |                    |
  +----v--------------------v----+
  |           books              |
  +------------------------------+
  | book_id      PK              |
  | title                        |
  | author_id    FK -> authors   |
  | category_id  FK -> categories|
  | price                        |
  +------------------------------+
       |                |
       | 1:1            | N:M (via order_items)
       |                |
  +----v----+    +------v--------+
  |inventory|    | order_items   |
  +---------+    +---------------+
  |book_id PK|   |order_id PK,FK|  <-- Composite Key
  |quantity  |   |book_id  PK,FK|
  +---------+    |quantity       |
                 +------^--------+
                        |
                        | N:1
                        |
                 +------+--------+
                 |    orders     |
                 +---------------+
                 | order_id   PK |
                 | customer_id FK|---+
                 | order_date    |   |
                 +---------------+   |
                                     | N:1
                                     |
                              +------v------+
                              |  customers  |
                              +-------------+
                              |customer_id PK|
                              | name         |
                              | email        |
                              +-------------+


To DENORMALIZE (move to lower normal form):
- Embed author_name directly into books table (removes authors table)
- Store category_name in books instead of category_id
```
