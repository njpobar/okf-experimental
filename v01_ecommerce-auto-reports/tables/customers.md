---
type: SQLite Table
title: Customers
description: One row per customer.
resource: sqlite:///ecommerce.sqlite#customers
tags: [ecommerce, customer, profile]
timestamp: 2026-06-30T12:45:34Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key for the customer. |
| `first_name` | TEXT | Customer first name. |
| `last_name` | TEXT | Customer last name. |
| `email` | TEXT | Unique customer email address. |
| `city` | TEXT | Customer city. |
| `state` | TEXT | Customer state or region code. |
| `segment` | TEXT | Customer segment label. |
| `signup_date` | TEXT | Date the customer signed up. |
| `profile_note` | TEXT | Free-text note about the customer. |

# Joins

Joined with [orders](/tables/orders.md) on `orders.customer_id = customers.id` and [reviews](/tables/reviews.md) on `reviews.customer_id = customers.id`.
