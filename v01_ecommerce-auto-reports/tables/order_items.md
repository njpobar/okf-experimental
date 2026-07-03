---
type: SQLite Table
title: Order Items
description: One row per product line item in an order.
resource: sqlite:///ecommerce.sqlite#order_items
tags: [ecommerce, sales, line-items]
timestamp: 2026-06-30T12:45:34Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key for the line item. |
| `order_id` | INTEGER | Foreign key to [orders](/tables/orders.md). |
| `product_id` | INTEGER | Foreign key to [products](/tables/products.md). |
| `quantity` | INTEGER | Number of units ordered. |
| `unit_price_cents` | INTEGER | Unit price in cents at purchase time. |
| `line_total_cents` | INTEGER | Extended line total in cents. |

# Joins

Joined with [orders](/tables/orders.md) on `order_items.order_id = orders.id` and [products](/tables/products.md) on `order_items.product_id = products.id`.
