---
type: SQLite Table
title: Orders
description: One row per customer order.
resource: sqlite:///ecommerce.sqlite#orders
tags: [ecommerce, sales, revenue]
timestamp: 2026-06-30T12:45:34Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key for the order. |
| `customer_id` | INTEGER | Foreign key to [customers](/tables/customers.md). |
| `order_date` | TEXT | Date the order was placed. |
| `status` | TEXT | Order lifecycle status. |
| `shipping_method` | TEXT | Shipping method selected for the order. |
| `subtotal_cents` | INTEGER | Item subtotal in cents. |
| `tax_cents` | INTEGER | Tax amount in cents. |
| `shipping_fee_cents` | INTEGER | Shipping fee in cents. |
| `total_cents` | INTEGER | Total order value in cents. |
| `notes` | TEXT | Free-text order note. |

# Joins

Joined with [customers](/tables/customers.md) on `orders.customer_id = customers.id` and [order_items](/tables/order_items.md) on `order_items.order_id = orders.id`.
