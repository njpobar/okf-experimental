#!/usr/bin/env python3

from __future__ import annotations

import argparse
import random
import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


FIRST_NAMES = [
    "Ava", "Mia", "Noah", "Liam", "Ivy", "Elena", "Ethan", "Owen", "Zoe", "Maya",
    "Luca", "Nora", "Kai", "Sophie", "Leo", "Aria", "Finn", "Jasper", "Ruby", "Theo",
]

LAST_NAMES = [
    "Walker", "Nguyen", "Patel", "Garcia", "Hughes", "Kim", "Lopez", "Bennett", "Ross",
    "Morgan", "Turner", "Price", "Carter", "Diaz", "Wood", "Bell", "Reed", "Sullivan",
    "Brooks", "Cooper",
]

CITIES = [
    ("Brisbane", "QLD"),
    ("Sydney", "NSW"),
    ("Melbourne", "VIC"),
    ("Perth", "WA"),
    ("Adelaide", "SA"),
    ("Canberra", "ACT"),
    ("Gold Coast", "QLD"),
    ("Newcastle", "NSW"),
]

SEGMENTS = ["consumer", "b2b", "vip", "student"]
DEPARTMENTS = {
    "Electronics": [
        ("Wearables", [
            ("Fitness tracker", ["health", "wearable", "compact"]),
            ("Smartwatch", ["watch", "bluetooth", "app"]),
            ("Wireless earbuds", ["audio", "portable", "noise-cancel"]),
        ]),
        ("Computing", [
            ("Laptop sleeve", ["protective", "travel", "portable"]),
            ("Mechanical keyboard", ["typing", "desk", "tactile"]),
            ("USB-C hub", ["connectivity", "compact", "adapter"]),
        ]),
    ],
    "Home": [
        ("Kitchen", [
            ("Air fryer", ["cooking", "quick", "easy-clean"]),
            ("Blender", ["smoothies", "kitchen", "powerful"]),
            ("Coffee grinder", ["coffee", "fresh", "compact"]),
        ]),
        ("Living", [
            ("Desk lamp", ["lighting", "minimal", "home"]),
            ("Throw blanket", ["soft", "cozy", "decor"]),
            ("Storage basket", ["organize", "woven", "practical"]),
        ]),
    ],
    "Outdoors": [
        ("Travel", [
            ("Daypack", ["travel", "durable", "lightweight"]),
            ("Water bottle", ["hydration", "reusable", "sport"]),
            ("Portable charger", ["power", "travel", "battery"]),
        ]),
        ("Fitness", [
            ("Yoga mat", ["fitness", "grip", "comfort"]),
            ("Resistance bands", ["exercise", "portable", "strength"]),
            ("Running belt", ["running", "storage", "snug"]),
        ]),
    ],
}

ORDER_STATUSES = ["pending", "paid", "shipped", "delivered", "cancelled"]
SHIPPING_METHODS = ["standard", "express", "pickup"]
REVIEW_TITLES = [
    "Exactly what I needed",
    "Solid everyday choice",
    "Better than expected",
    "Nice quality for the price",
    "Would buy again",
    "Works well so far",
]
REVIEW_SNIPPETS = [
    "The build feels sturdy and the finish is better than I expected.",
    "It fits neatly into my routine and the setup was straightforward.",
    "There were a few small tradeoffs, but the overall value is strong.",
    "The product does the job well and the design is pleasantly simple.",
    "I have been using it for a couple of weeks and it has held up nicely.",
]
ORDER_NOTES = [
    "Left at the front door per customer request.",
    "Customer asked for a quiet delivery window.",
    "Gift order with no packing slip.",
    "Requested extra padding for fragile items.",
    "No special instructions.",
]


def money_to_text(cents: int) -> str:
    return f"${cents / 100:.2f}"


def random_date(rng: random.Random, start: date, end: date) -> date:
    span = (end - start).days
    return start + timedelta(days=rng.randint(0, span))


def build_categories():
    categories = []
    cat_id = 1
    for department, groups in DEPARTMENTS.items():
        for group_name, product_lines in groups:
            for item_name, tags in product_lines:
                categories.append(
                    (
                        cat_id,
                        department,
                        f"{group_name}: {item_name}",
                        f"{item_name} items for the {group_name.lower()} range in the {department.lower()} department. Tags: {', '.join(tags)}.",
                    )
                )
                cat_id += 1
    return categories


def build_products(rng: random.Random, categories, count: int):
    brands = ["Northstar", "Fieldwork", "Cinder", "Atlas", "Juniper", "Harbor", "Mosaic", "Pioneer"]
    products = []
    for product_id in range(1, count + 1):
        category = rng.choice(categories)
        category_id = category[0]
        category_name = category[2].split(": ", 1)[1]
        adjective = rng.choice(["Essential", "Compact", "Premium", "Everyday", "Performance", "Classic", "Modern"])
        product_name = f"{adjective} {category_name}"
        brand = rng.choice(brands)
        base_price = rng.randint(1500, 18000)
        price_cents = base_price - (base_price % 25)
        stock_qty = rng.randint(12, 400)
        tags = [
            category[3].split("Tags: ", 1)[1].split(", ")[0],
            rng.choice(["new", "popular", "giftable", "starter", "pro"]),
            rng.choice(["online-only", "warehouse", "seasonal", "core"]),
        ]
        description = (
            f"{product_name} from {brand} designed for {category[1].lower()} use. "
            f"It combines a clean finish with practical details, making it a reliable option for everyday experiments and analysis."
        )
        sku = f"SKU-{product_id:05d}"
        products.append(
            (
                product_id,
                category_id,
                sku,
                product_name,
                brand,
                price_cents,
                stock_qty,
                ", ".join(dict.fromkeys(tags)),
                description,
            )
        )
    return products


def build_customers(rng: random.Random, count: int):
    customers = []
    for customer_id in range(1, count + 1):
        first_name = rng.choice(FIRST_NAMES)
        last_name = rng.choice(LAST_NAMES)
        city, state = rng.choice(CITIES)
        segment = rng.choice(SEGMENTS)
        signup = random_date(rng, date(2023, 1, 1), date(2026, 6, 30))
        profile_note = rng.choice([
            "Interested in recurring purchases and fast shipping.",
            "Prefers value picks with clear product descriptions.",
            "Often leaves detailed feedback after purchase.",
            "Buys a mix of starter items and higher-end upgrades.",
            "Usually shops after reading comparison notes.",
        ])
        email = f"{first_name.lower()}.{last_name.lower()}.{customer_id:03d}@example.com"
        customers.append(
            (
                customer_id,
                first_name,
                last_name,
                email,
                city,
                state,
                segment,
                signup.isoformat(),
                profile_note,
            )
        )
    return customers


def build_orders_and_items(rng: random.Random, customers, products, order_count: int):
    orders = []
    items = []
    item_id = 1
    for order_id in range(1, order_count + 1):
        customer = rng.choice(customers)
        order_date = random_date(rng, date(2024, 1, 1), date(2026, 6, 30))
        status_weights = [10, 30, 28, 24, 8]
        status = rng.choices(ORDER_STATUSES, weights=status_weights, k=1)[0]
        shipping_method = rng.choices(SHIPPING_METHODS, weights=[60, 30, 10], k=1)[0]
        line_count = rng.randint(1, 4)
        chosen_products = rng.sample(products, k=line_count)
        line_items = []
        subtotal = 0
        for product in chosen_products:
            quantity = rng.randint(1, 3)
            unit_price = product[5]
            line_total = quantity * unit_price
            subtotal += line_total
            line_items.append(
                (
                    item_id,
                    order_id,
                    product[0],
                    quantity,
                    unit_price,
                    line_total,
                )
            )
            item_id += 1
        tax_cents = round(subtotal * 0.1)
        shipping_fee_cents = 0 if shipping_method == "pickup" else (0 if subtotal >= 12000 else (1200 if shipping_method == "express" else 700))
        total_cents = subtotal + tax_cents + shipping_fee_cents
        notes = rng.choice(ORDER_NOTES)
        orders.append(
            (
                order_id,
                customer[0],
                order_date.isoformat(),
                status,
                shipping_method,
                subtotal,
                tax_cents,
                shipping_fee_cents,
                total_cents,
                notes,
            )
        )
        items.extend(line_items)
    return orders, items


def build_reviews(rng: random.Random, customers, products, count: int):
    reviews = []
    for review_id in range(1, count + 1):
        customer = rng.choice(customers)
        product = rng.choice(products)
        rating = rng.randint(2, 5)
        title = rng.choice(REVIEW_TITLES)
        body = rng.choice(REVIEW_SNIPPETS) + " " + rng.choice([
            "The category fit makes joining this data especially convenient.",
            "I like having a realistic text field for free-form experiments.",
            "It gives the database a more natural shape for joins and filters.",
        ])
        created_at = random_date(rng, date(2024, 1, 1), date(2026, 6, 30)).isoformat()
        reviews.append(
            (
                review_id,
                customer[0],
                product[0],
                rating,
                title,
                body,
                created_at,
            )
        )
    return reviews


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a seeded SQLite e-commerce database.")
    parser.add_argument("--db", default="ecommerce.sqlite", help="Output SQLite file path.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic data.")
    parser.add_argument("--customers", type=int, default=450)
    parser.add_argument("--products", type=int, default=240)
    parser.add_argument("--orders", type=int, default=1200)
    parser.add_argument("--reviews", type=int, default=600)
    args = parser.parse_args()

    output = Path(args.db)
    if output.exists():
        output.unlink()

    rng = random.Random(args.seed)
    categories = build_categories()
    customers = build_customers(rng, args.customers)
    products = build_products(rng, categories, args.products)
    orders, order_items = build_orders_and_items(rng, customers, products, args.orders)
    reviews = build_reviews(rng, customers, products, args.reviews)

    conn = sqlite3.connect(output)
    conn.execute("PRAGMA foreign_keys = ON;")
    schema_sql = Path("schema.sql").read_text(encoding="utf-8")
    conn.executescript(schema_sql)

    conn.executemany(
        "INSERT INTO categories (id, department, name, description) VALUES (?, ?, ?, ?)",
        categories,
    )
    conn.executemany(
        "INSERT INTO customers (id, first_name, last_name, email, city, state, segment, signup_date, profile_note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        customers,
    )
    conn.executemany(
        "INSERT INTO products (id, category_id, sku, name, brand, price_cents, stock_qty, tags, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        products,
    )
    conn.executemany(
        "INSERT INTO orders (id, customer_id, order_date, status, shipping_method, subtotal_cents, tax_cents, shipping_fee_cents, total_cents, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        orders,
    )
    conn.executemany(
        "INSERT INTO order_items (id, order_id, product_id, quantity, unit_price_cents, line_total_cents) VALUES (?, ?, ?, ?, ?, ?)",
        order_items,
    )
    conn.executemany(
        "INSERT INTO reviews (id, customer_id, product_id, rating, title, body, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        reviews,
    )
    conn.commit()

    counts = {
        "categories": len(categories),
        "customers": len(customers),
        "products": len(products),
        "orders": len(orders),
        "order_items": len(order_items),
        "reviews": len(reviews),
    }
    total_rows = sum(counts.values())
    print(f"Built {output} with {total_rows} rows across 6 tables.")
    for table, count in counts.items():
        print(f"{table}: {count}")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
