---
type: SQLite Table
title: Reviews
description: One row per customer review of a product.
resource: sqlite:///ecommerce.sqlite#reviews
tags: [ecommerce, feedback, ratings]
timestamp: 2026-06-30T12:45:34Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key for the review. |
| `customer_id` | INTEGER | Foreign key to [customers](/tables/customers.md). |
| `product_id` | INTEGER | Foreign key to [products](/tables/products.md). |
| `rating` | INTEGER | Numeric product rating. |
| `title` | TEXT | Short review title. |
| `body` | TEXT | Free-text review body. |
| `created_at` | TEXT | Review creation timestamp. |

# Joins

Joined with [customers](/tables/customers.md) on `reviews.customer_id = customers.id` and [products](/tables/products.md) on `reviews.product_id = products.id`.
