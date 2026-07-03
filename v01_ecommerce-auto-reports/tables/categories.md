---
type: SQLite Table
title: Categories
description: One row per product category.
resource: sqlite:///ecommerce.sqlite#categories
tags: [ecommerce, catalog, lookup]
timestamp: 2026-06-30T12:45:34Z
---

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key for the category. |
| `department` | TEXT | High-level department grouping. |
| `name` | TEXT | Unique category name. |
| `description` | TEXT | Human-readable description of the category. |

# Joins

Joined with [products](/tables/products.md) on `products.category_id = categories.id`.
