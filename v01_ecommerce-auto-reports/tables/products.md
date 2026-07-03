---
type: SQLite Table
title: Products
description: One row per product in the catalog.
resource: sqlite:///ecommerce.sqlite#products
tags: [ecommerce, catalog, inventory]
timestamp: 2026-06-30T12:45:34Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key for the product. |
| `category_id` | INTEGER | Foreign key to [categories](/tables/categories.md). |
| `sku` | TEXT | Unique stock keeping unit. |
| `name` | TEXT | Product name. |
| `brand` | TEXT | Brand or vendor name. |
| `price_cents` | INTEGER | Current price in cents. |
| `stock_qty` | INTEGER | Units currently in stock. |
| `tags` | TEXT | Comma-separated product tags. |
| `description` | TEXT | Free-text product description. |

# Joins

Joined with [categories](/tables/categories.md) on `products.category_id = categories.id`, [order_items](/tables/order_items.md) on `order_items.product_id = products.id`, and [reviews](/tables/reviews.md) on `reviews.product_id = products.id`.
