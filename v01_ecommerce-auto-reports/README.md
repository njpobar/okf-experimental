# E-commerce SQLite database

This repo now contains a small seeded SQLite database you can use for experiments, joins, and lightweight analytics.

## What’s included

- `categories`
- `customers`
- `products`
- `orders`
- `order_items`
- `reviews`

The seed data is intentionally realistic enough for joins and text filtering:

- categorization fields such as department, segment, status, shipping method, and tags
- free-text fields such as product descriptions, customer profile notes, order notes, and review bodies
- a modest dataset size of roughly 5,000 rows total

## SQLite vs PostgreSQL

SQLite is a file-based database engine that lives in a single `.sqlite` file. It is simple to ship, easy to copy around, and great for experiments, local prototyping, and small-to-medium workloads.

PostgreSQL is a separate database server. It is better when you need concurrent writers, richer operational features, stronger scalability, advanced indexing and query planning options, or a production multi-user setup.

For your use case, SQLite is the fastest path to something usable right now. If this grows into a shared or production workload later, we can move the same schema over to Postgres.

## Build it

```bash
python3 build_db.py
```

That creates `ecommerce.sqlite` in the repo root.

## Example joins

```sql
SELECT
  o.id AS order_id,
  o.order_date,
  c.first_name || ' ' || c.last_name AS customer_name,
  p.name AS product_name,
  oi.quantity,
  oi.line_total_cents
FROM orders o
JOIN customers c ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
ORDER BY o.order_date DESC
LIMIT 25;
```

```sql
SELECT
  c.name AS category_name,
  COUNT(*) AS product_count,
  ROUND(AVG(p.price_cents) / 100.0, 2) AS avg_price
FROM categories c
JOIN products p ON p.category_id = c.id
GROUP BY c.id
ORDER BY product_count DESC;
```

```sql
SELECT
  p.name,
  AVG(r.rating) AS avg_rating,
  COUNT(r.id) AS review_count
FROM products p
LEFT JOIN reviews r ON r.product_id = p.id
GROUP BY p.id
HAVING review_count > 0
ORDER BY avg_rating DESC, review_count DESC;
```
