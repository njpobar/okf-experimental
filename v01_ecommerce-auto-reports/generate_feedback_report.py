from __future__ import annotations

import html
import sqlite3
from collections import Counter
from pathlib import Path


DB_PATH = Path("ecommerce.sqlite")
OUTPUT_PATH = Path("reports/product_feedback_report.html")
NEGATIVE_RATING = 2
POSITIVE_RATING_FLOOR = 4
COMPLETED_STATUSES = ("paid", "shipped", "delivered")

THEME_PHRASES = [
    ("small tradeoffs", "Small tradeoffs"),
    ("setup was straightforward", "Setup"),
    ("held up nicely", "Held up nicely"),
    ("build feels sturdy", "Build quality"),
    ("design is pleasantly simple", "Simple design"),
    ("realistic text field", "Realistic text field"),
    ("natural shape for joins and filters", "Joins and filters"),
    ("category fit", "Category fit"),
]

OPERATIONS_TERMS = [
    "shipping",
    "delivery",
    "late",
    "delayed",
    "refund",
    "return",
    "support",
    "customer service",
]


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def money(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"${float(value):,.2f}"


def pct(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.{digits}f}%"


def query_all(conn: sqlite3.Connection, sql: str, params: tuple[object, ...] = ()) -> list[sqlite3.Row]:
    return conn.execute(sql, params).fetchall()


def query_one(conn: sqlite3.Connection, sql: str, params: tuple[object, ...] = ()) -> sqlite3.Row:
    row = conn.execute(sql, params).fetchone()
    if row is None:
        raise ValueError("Expected one row")
    return row


def build_bar(value: float, max_value: float, label: str) -> str:
    width = 0 if max_value <= 0 else (value / max_value) * 100
    return (
        '<div class="bar-row">'
        f'<div class="bar-label">{esc(label)}</div>'
        '<div class="bar-track"><div class="bar-fill" '
        f'style="width: {width:.1f}%"></div></div>'
        f'<div class="bar-value">{value:.1f}%</div>'
        "</div>"
    )


def detect_product_theme(rows: list[sqlite3.Row]) -> str | None:
    counts: Counter[str] = Counter()
    for row in rows:
        body = (row["body"] or "").lower()
        for phrase, label in THEME_PHRASES:
            if phrase in body:
                counts[label] += 1
    if not counts:
        return None
    label, count = counts.most_common(1)[0]
    if count >= 2 and count / len(rows) >= 0.5:
        return f"{label} appeared in {count} of {len(rows)} negative reviews."
    return None


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    status_placeholders = ", ".join("?" for _ in COMPLETED_STATUSES)

    review_summary = query_one(
        conn,
        f"""
        SELECT
          COUNT(*) AS reviews,
          SUM(CASE WHEN rating = ? THEN 1 ELSE 0 END) AS negative_reviews,
          SUM(CASE WHEN rating >= ? THEN 1 ELSE 0 END) AS positive_reviews,
          ROUND(AVG(rating), 2) AS avg_rating,
          MIN(created_at) AS first_review_at,
          MAX(created_at) AS last_review_at
        FROM reviews
        """,
        (NEGATIVE_RATING, POSITIVE_RATING_FLOOR),
    )
    total_products = query_one(conn, "SELECT COUNT(*) AS total_products FROM products")["total_products"]
    total_customers = query_one(conn, "SELECT COUNT(*) AS total_customers FROM customers")["total_customers"]
    reviewed_products = query_one(conn, "SELECT COUNT(DISTINCT product_id) AS reviewed_products FROM reviews")["reviewed_products"]
    reviewing_customers = query_one(conn, "SELECT COUNT(DISTINCT customer_id) AS reviewing_customers FROM reviews")["reviewing_customers"]

    baseline_negative_rate = review_summary["negative_reviews"] / review_summary["reviews"]

    product_review_risk = query_all(
        conn,
        f"""
        WITH sales AS (
          SELECT
            oi.product_id,
            COUNT(DISTINCT o.id) AS completed_orders,
            SUM(oi.quantity) AS units_sold,
            SUM(oi.line_total_cents) / 100.0 AS revenue
          FROM orders o
          JOIN order_items oi ON oi.order_id = o.id
          WHERE o.status IN ({status_placeholders})
          GROUP BY oi.product_id
        ),
        review_rollup AS (
          SELECT
            r.product_id,
            COUNT(*) AS reviews,
            SUM(CASE WHEN r.rating = ? THEN 1 ELSE 0 END) AS negative_reviews,
            SUM(CASE WHEN r.rating = 3 THEN 1 ELSE 0 END) AS mixed_reviews,
            ROUND(AVG(r.rating), 2) AS avg_rating
          FROM reviews r
          GROUP BY r.product_id
        )
        SELECT
          p.id,
          p.name,
          p.brand,
          c.department,
          c.name AS category_name,
          rr.reviews,
          rr.negative_reviews,
          rr.mixed_reviews,
          rr.avg_rating,
          COALESCE(s.completed_orders, 0) AS completed_orders,
          COALESCE(s.units_sold, 0) AS units_sold,
          COALESCE(s.revenue, 0) AS revenue,
          1.0 * rr.negative_reviews / rr.reviews AS negative_review_rate,
          CASE
            WHEN COALESCE(s.completed_orders, 0) = 0 THEN NULL
            ELSE 100.0 * rr.negative_reviews / s.completed_orders
          END AS negative_reviews_per_100_orders
        FROM review_rollup rr
        JOIN products p ON p.id = rr.product_id
        JOIN categories c ON c.id = p.category_id
        LEFT JOIN sales s ON s.product_id = rr.product_id
        WHERE rr.reviews >= 3
        ORDER BY negative_review_rate DESC, rr.negative_reviews DESC, rr.reviews DESC, completed_orders DESC
        LIMIT 12
        """,
        (*COMPLETED_STATUSES, NEGATIVE_RATING),
    )

    product_sales_risk = query_all(
        conn,
        f"""
        WITH sales AS (
          SELECT
            oi.product_id,
            COUNT(DISTINCT o.id) AS completed_orders,
            SUM(oi.quantity) AS units_sold,
            SUM(oi.line_total_cents) / 100.0 AS revenue
          FROM orders o
          JOIN order_items oi ON oi.order_id = o.id
          WHERE o.status IN ({status_placeholders})
          GROUP BY oi.product_id
        ),
        review_rollup AS (
          SELECT
            r.product_id,
            COUNT(*) AS reviews,
            SUM(CASE WHEN r.rating = ? THEN 1 ELSE 0 END) AS negative_reviews,
            ROUND(AVG(r.rating), 2) AS avg_rating
          FROM reviews r
          GROUP BY r.product_id
        )
        SELECT
          p.id,
          p.name,
          p.brand,
          c.department,
          c.name AS category_name,
          rr.reviews,
          rr.negative_reviews,
          rr.avg_rating,
          s.completed_orders,
          s.units_sold,
          s.revenue,
          1.0 * rr.negative_reviews / rr.reviews AS negative_review_rate,
          100.0 * rr.negative_reviews / s.completed_orders AS negative_reviews_per_100_orders
        FROM review_rollup rr
        JOIN sales s ON s.product_id = rr.product_id
        JOIN products p ON p.id = rr.product_id
        JOIN categories c ON c.id = p.category_id
        WHERE s.completed_orders >= 8
          AND rr.negative_reviews >= 2
        ORDER BY negative_reviews_per_100_orders DESC, rr.negative_reviews DESC, s.completed_orders DESC
        LIMIT 12
        """,
        (*COMPLETED_STATUSES, NEGATIVE_RATING),
    )

    category_risk = query_all(
        conn,
        f"""
        SELECT
          c.department,
          c.name AS category_name,
          COUNT(*) AS reviews,
          SUM(CASE WHEN r.rating = ? THEN 1 ELSE 0 END) AS negative_reviews,
          ROUND(AVG(r.rating), 2) AS avg_rating,
          1.0 * SUM(CASE WHEN r.rating = ? THEN 1 ELSE 0 END) / COUNT(*) AS negative_review_rate
        FROM reviews r
        JOIN products p ON p.id = r.product_id
        JOIN categories c ON c.id = p.category_id
        GROUP BY c.id
        HAVING COUNT(*) >= 15
        ORDER BY negative_review_rate DESC, negative_reviews DESC, reviews DESC
        LIMIT 8
        """,
        (NEGATIVE_RATING, NEGATIVE_RATING),
    )

    negative_customers = query_all(
        conn,
        f"""
        SELECT
          c.id,
          c.first_name || ' ' || c.last_name AS customer_name,
          c.segment,
          c.state,
          COUNT(*) AS reviews,
          SUM(CASE WHEN r.rating = ? THEN 1 ELSE 0 END) AS negative_reviews,
          SUM(CASE WHEN r.rating >= ? THEN 1 ELSE 0 END) AS positive_reviews,
          ROUND(AVG(r.rating), 2) AS avg_rating,
          1.0 * SUM(CASE WHEN r.rating = ? THEN 1 ELSE 0 END) / COUNT(*) AS negative_review_rate
        FROM reviews r
        JOIN customers c ON c.id = r.customer_id
        GROUP BY c.id
        HAVING COUNT(*) >= 2
        ORDER BY negative_review_rate DESC, negative_reviews DESC, reviews DESC, avg_rating ASC
        LIMIT 12
        """,
        (NEGATIVE_RATING, POSITIVE_RATING_FLOOR, NEGATIVE_RATING),
    )

    positive_customers = query_all(
        conn,
        f"""
        SELECT
          c.id,
          c.first_name || ' ' || c.last_name AS customer_name,
          c.segment,
          c.state,
          COUNT(*) AS reviews,
          SUM(CASE WHEN r.rating >= ? THEN 1 ELSE 0 END) AS positive_reviews,
          SUM(CASE WHEN r.rating = ? THEN 1 ELSE 0 END) AS negative_reviews,
          ROUND(AVG(r.rating), 2) AS avg_rating,
          1.0 * SUM(CASE WHEN r.rating >= ? THEN 1 ELSE 0 END) / COUNT(*) AS positive_review_rate
        FROM reviews r
        JOIN customers c ON c.id = r.customer_id
        GROUP BY c.id
        HAVING COUNT(*) >= 3
        ORDER BY positive_review_rate DESC, positive_reviews DESC, reviews DESC, avg_rating DESC
        LIMIT 12
        """,
        (POSITIVE_RATING_FLOOR, NEGATIVE_RATING, POSITIVE_RATING_FLOOR),
    )

    segment_mix = query_all(
        conn,
        f"""
        SELECT
          c.segment,
          COUNT(*) AS reviews,
          SUM(CASE WHEN r.rating = ? THEN 1 ELSE 0 END) AS negative_reviews,
          ROUND(AVG(r.rating), 2) AS avg_rating,
          1.0 * SUM(CASE WHEN r.rating = ? THEN 1 ELSE 0 END) / COUNT(*) AS negative_review_rate
        FROM reviews r
        JOIN customers c ON c.id = r.customer_id
        GROUP BY c.segment
        ORDER BY negative_review_rate DESC, negative_reviews DESC
        """,
        (NEGATIVE_RATING, NEGATIVE_RATING),
    )

    state_mix = query_all(
        conn,
        f"""
        SELECT
          c.state,
          COUNT(*) AS reviews,
          SUM(CASE WHEN r.rating = ? THEN 1 ELSE 0 END) AS negative_reviews,
          ROUND(AVG(r.rating), 2) AS avg_rating,
          1.0 * SUM(CASE WHEN r.rating = ? THEN 1 ELSE 0 END) / COUNT(*) AS negative_review_rate
        FROM reviews r
        JOIN customers c ON c.id = r.customer_id
        GROUP BY c.state
        ORDER BY negative_review_rate DESC, negative_reviews DESC
        """,
        (NEGATIVE_RATING, NEGATIVE_RATING),
    )

    operations_mentions = []
    for term in OPERATIONS_TERMS:
        row = query_one(
            conn,
            """
            SELECT
              COUNT(*) AS total_mentions,
              SUM(CASE WHEN rating = ? THEN 1 ELSE 0 END) AS negative_mentions
            FROM reviews
            WHERE lower(title) LIKE ?
               OR lower(body) LIKE ?
            """,
            (NEGATIVE_RATING, f"%{term}%", f"%{term}%"),
        )
        operations_mentions.append(
            {"term": term, "total_mentions": row["total_mentions"], "negative_mentions": row["negative_mentions"] or 0}
        )

    phrase_analysis = []
    for phrase, label in THEME_PHRASES:
        row = query_one(
            conn,
            """
            SELECT
              COUNT(*) AS total_reviews,
              SUM(CASE WHEN rating = ? THEN 1 ELSE 0 END) AS negative_reviews
            FROM reviews
            WHERE lower(body) LIKE ?
            """,
            (NEGATIVE_RATING, f"%{phrase}%"),
        )
        total_reviews = row["total_reviews"]
        negative_reviews = row["negative_reviews"] or 0
        negative_rate = (negative_reviews / total_reviews) if total_reviews else 0.0
        phrase_analysis.append(
            {
                "label": label,
                "total_reviews": total_reviews,
                "negative_reviews": negative_reviews,
                "negative_rate": negative_rate,
                "uplift": negative_rate - baseline_negative_rate,
            }
        )
    phrase_analysis.sort(key=lambda item: (item["uplift"], item["negative_reviews"]), reverse=True)

    product_watchlist = []
    watchlist_ids: list[int] = []
    for row in product_review_risk[:5]:
        watchlist_ids.append(row["id"])
    for row in product_sales_risk:
        if row["id"] not in watchlist_ids and len(watchlist_ids) < 8:
            watchlist_ids.append(row["id"])

    for product_id in watchlist_ids:
        product_row = next((row for row in product_review_risk if row["id"] == product_id), None)
        if product_row is None:
            product_row = next(row for row in product_sales_risk if row["id"] == product_id)
        negative_rows = query_all(
            conn,
            """
            SELECT r.rating, r.title, r.body, r.created_at, c.first_name || ' ' || c.last_name AS customer_name
            FROM reviews r
            JOIN customers c ON c.id = r.customer_id
            WHERE r.product_id = ?
              AND r.rating = ?
            ORDER BY r.created_at DESC
            """,
            (product_id, NEGATIVE_RATING),
        )
        product_watchlist.append(
            {
                "product": product_row,
                "theme": detect_product_theme(negative_rows),
                "negative_rows": negative_rows[:2],
            }
        )

    highest_negative_customer = max(
        negative_customers,
        key=lambda row: (row["negative_reviews"], row["negative_review_rate"], row["reviews"]),
    )
    most_positive_customer = max(
        positive_customers,
        key=lambda row: (row["positive_review_rate"], row["positive_reviews"], row["reviews"], row["avg_rating"]),
    )
    riskiest_category = category_risk[0]
    highest_sales_risk_product = product_sales_risk[0]

    review_rate_rows = "".join(
        "<tr>"
        f"<td>{esc(row['name'])}</td>"
        f"<td>{esc(row['brand'])}</td>"
        f"<td>{esc(row['category_name'])}</td>"
        f"<td>{row['reviews']}</td>"
        f"<td>{row['negative_reviews']}</td>"
        f"<td>{pct(row['negative_review_rate'])}</td>"
        f"<td>{row['avg_rating']}</td>"
        f"<td>{row['completed_orders']}</td>"
        "</tr>"
        for row in product_review_risk
    )

    sales_risk_rows = "".join(
        "<tr>"
        f"<td>{esc(row['name'])}</td>"
        f"<td>{esc(row['brand'])}</td>"
        f"<td>{esc(row['category_name'])}</td>"
        f"<td>{row['completed_orders']}</td>"
        f"<td>{row['units_sold']}</td>"
        f"<td>{row['negative_reviews']}</td>"
        f"<td>{row['reviews']}</td>"
        f"<td>{row['negative_reviews_per_100_orders']:.1f}</td>"
        "</tr>"
        for row in product_sales_risk
    )

    category_rows = "".join(
        "<tr>"
        f"<td>{esc(row['department'])}</td>"
        f"<td>{esc(row['category_name'])}</td>"
        f"<td>{row['reviews']}</td>"
        f"<td>{row['negative_reviews']}</td>"
        f"<td>{pct(row['negative_review_rate'])}</td>"
        f"<td>{row['avg_rating']}</td>"
        "</tr>"
        for row in category_risk
    )

    negative_customer_rows = "".join(
        "<tr>"
        f"<td>{esc(row['customer_name'])}</td>"
        f"<td>{esc(row['segment'])}</td>"
        f"<td>{esc(row['state'])}</td>"
        f"<td>{row['reviews']}</td>"
        f"<td>{row['negative_reviews']}</td>"
        f"<td>{pct(row['negative_review_rate'])}</td>"
        f"<td>{row['avg_rating']}</td>"
        "</tr>"
        for row in negative_customers
    )

    positive_customer_rows = "".join(
        "<tr>"
        f"<td>{esc(row['customer_name'])}</td>"
        f"<td>{esc(row['segment'])}</td>"
        f"<td>{esc(row['state'])}</td>"
        f"<td>{row['reviews']}</td>"
        f"<td>{row['positive_reviews']}</td>"
        f"<td>{pct(row['positive_review_rate'])}</td>"
        f"<td>{row['avg_rating']}</td>"
        "</tr>"
        for row in positive_customers
    )

    segment_max = max(row["negative_review_rate"] for row in segment_mix)
    state_max = max(row["negative_review_rate"] for row in state_mix)
    segment_bars = "".join(build_bar(row["negative_review_rate"] * 100.0, segment_max * 100.0, row["segment"]) for row in segment_mix)
    state_bars = "".join(build_bar(row["negative_review_rate"] * 100.0, state_max * 100.0, row["state"]) for row in state_mix)

    theme_rows = "".join(
        "<tr>"
        f"<td>{esc(item['label'])}</td>"
        f"<td>{item['total_reviews']}</td>"
        f"<td>{item['negative_reviews']}</td>"
        f"<td>{pct(item['negative_rate'])}</td>"
        f"<td>{item['uplift'] * 100:+.1f} pp</td>"
        "</tr>"
        for item in phrase_analysis[:6]
    )

    watchlist_cards = []
    for item in product_watchlist:
        row = item["product"]
        review_snippets = "".join(
            f"""
            <div class="snippet">
              <div class="snippet-meta">{esc(snippet['created_at'])} • {esc(snippet['customer_name'])}</div>
              <strong>{esc(snippet['title'])}</strong>
              <p>{esc(snippet['body'])}</p>
            </div>
            """
            for snippet in item["negative_rows"]
        )
        theme_line = f"<p class=\"note\"><strong>Repeated theme:</strong> {esc(item['theme'])}</p>" if item["theme"] else ""
        watchlist_cards.append(
            f"""
            <article class="watch-card">
              <h3>{esc(row['name'])}</h3>
              <div class="subline">{esc(row['brand'])} • {esc(row['category_name'])}</div>
              <div class="mini-grid">
                <div><span class="mini-label">Negative review rate</span><strong>{pct(row['negative_review_rate'])}</strong></div>
                <div><span class="mini-label">Negative reviews</span><strong>{row['negative_reviews']} / {row['reviews']}</strong></div>
                <div><span class="mini-label">Completed orders</span><strong>{row['completed_orders']}</strong></div>
                <div><span class="mini-label">Negative per 100 orders</span><strong>{row['negative_reviews_per_100_orders']:.1f}</strong></div>
              </div>
              {theme_line}
              {review_snippets}
            </article>
            """
        )

    operation_zero_terms = [item["term"] for item in operations_mentions if item["total_mentions"] == 0]

    html_text = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Product Feedback Report</title>
  <style>
    :root {{
      --bg: #f7f4ef;
      --panel: #fffdf9;
      --ink: #2f2118;
      --muted: #756153;
      --line: #e8ddd3;
      --accent: #b5422c;
      --accent-soft: #f8dfd8;
      --good: #2a7a57;
      --good-soft: #dff0e8;
      --warn: #a8671b;
      --shadow: 0 18px 38px rgba(61, 35, 23, 0.08);
      --radius: 18px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top right, rgba(181, 66, 44, 0.10), transparent 28%),
        linear-gradient(180deg, #fbf8f2 0%, var(--bg) 100%);
    }}
    .wrap {{
      max-width: 1260px;
      margin: 0 auto;
      padding: 40px 20px 60px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(181, 66, 44, 0.10), rgba(255,255,255,0.96));
      border: 1px solid rgba(181, 66, 44, 0.12);
      border-radius: 28px;
      padding: 32px;
      box-shadow: var(--shadow);
    }}
    .eyebrow {{
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    h1, h2, h3 {{
      margin: 0;
      font-weight: 600;
    }}
    h1 {{
      margin-top: 12px;
      font-size: clamp(2rem, 4vw, 3.2rem);
      line-height: 1.04;
    }}
    p {{
      color: var(--muted);
      line-height: 1.6;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(12, minmax(0, 1fr));
      gap: 18px;
      margin-top: 22px;
    }}
    .card {{
      grid-column: span 3;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 20px;
      box-shadow: var(--shadow);
    }}
    .card.wide {{ grid-column: span 6; }}
    .card.full {{ grid-column: 1 / -1; }}
    .label {{
      color: var(--muted);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .metric {{
      font-size: 2rem;
      line-height: 1.1;
      margin: 10px 0 6px;
    }}
    .subtle {{
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .warn-pill, .good-pill {{
      display: inline-block;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 0.84rem;
      margin-top: 10px;
    }}
    .warn-pill {{
      color: var(--accent);
      background: var(--accent-soft);
    }}
    .good-pill {{
      color: var(--good);
      background: var(--good-soft);
    }}
    .table-wrap {{
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }}
    th, td {{
      text-align: left;
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .bars {{
      margin-top: 14px;
    }}
    .bar-row {{
      display: grid;
      grid-template-columns: 120px 1fr 72px;
      gap: 10px;
      align-items: center;
      margin-top: 10px;
    }}
    .bar-label, .bar-value {{
      font-size: 0.92rem;
      color: var(--muted);
    }}
    .bar-track {{
      height: 10px;
      background: #efe4da;
      border-radius: 999px;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      background: linear-gradient(90deg, #d06d54, #b5422c);
      border-radius: 999px;
    }}
    .watch-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }}
    .watch-card {{
      background: #fffaf5;
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
    }}
    .subline {{
      color: var(--muted);
      margin-top: 6px;
    }}
    .mini-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .mini-label {{
      display: block;
      color: var(--muted);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 4px;
    }}
    .snippet {{
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px;
      margin-top: 12px;
    }}
    .snippet-meta {{
      color: var(--muted);
      font-size: 0.84rem;
      margin-bottom: 6px;
    }}
    .note {{
      margin-top: 12px;
      color: var(--ink);
    }}
    ul {{
      margin: 14px 0 0;
      padding-left: 20px;
      color: var(--muted);
    }}
    li + li {{ margin-top: 8px; }}
    code {{
      background: #f3ebe2;
      border-radius: 6px;
      padding: 2px 6px;
      font-size: 0.95em;
    }}
    @media (max-width: 980px) {{
      .card, .card.wide {{ grid-column: 1 / -1; }}
      .watch-grid {{ grid-template-columns: 1fr; }}
      .mini-grid {{ grid-template-columns: 1fr 1fr; }}
    }}
  </style>
</head>
<body>
  <main class="wrap">
    <section class="hero">
      <span class="eyebrow">Feedback Risk Review</span>
      <h1>Which products and customers skew negative, and do the reviews point to a real theme?</h1>
      <p>
        This report joins <code>reviews</code> with <code>products</code>, <code>categories</code>, <code>customers</code>,
        <code>orders</code>, and <code>order_items</code>. In this dataset, the negative tier is the <strong>2-star rating</strong>,
        because no 1-star reviews exist. Sales-normalized calculations use only completed orders with statuses
        <code>paid</code>, <code>shipped</code>, or <code>delivered</code>.
      </p>
    </section>

    <section class="grid">
      <article class="card">
        <div class="label">Review Coverage</div>
        <div class="metric">{review_summary["reviews"]}</div>
        <div class="subtle">Reviews across {reviewed_products} of {total_products} products and {reviewing_customers} of {total_customers} customers.</div>
      </article>
      <article class="card">
        <div class="label">Negative Review Rate</div>
        <div class="metric">{pct(baseline_negative_rate)}</div>
        <div class="subtle">{review_summary["negative_reviews"]} of {review_summary["reviews"]} reviews are 2-star.</div>
      </article>
      <article class="card">
        <div class="label">Positive Review Rate</div>
        <div class="metric">{pct(review_summary["positive_reviews"] / review_summary["reviews"])}</div>
        <div class="subtle">{review_summary["positive_reviews"]} reviews are 4-star or 5-star.</div>
      </article>
      <article class="card">
        <div class="label">Average Rating</div>
        <div class="metric">{review_summary["avg_rating"]}</div>
        <div class="subtle">Review activity runs from {esc(review_summary["first_review_at"])} to {esc(review_summary["last_review_at"])}.</div>
      </article>
    </section>

    <section class="grid">
      <article class="card wide">
        <div class="label">Main Findings</div>
        <ul>
          <li><strong>{esc(highest_sales_risk_product["name"])}</strong> is the clearest product risk when normalized by sales volume, with <strong>{highest_sales_risk_product["negative_reviews_per_100_orders"]:.1f}</strong> negative reviews per 100 completed orders.</li>
          <li><strong>{esc(riskiest_category["category_name"])}</strong> is the harshest category pocket, with a negative review rate of <strong>{pct(riskiest_category["negative_review_rate"])}</strong>.</li>
          <li><strong>{esc(highest_negative_customer["customer_name"])}</strong> stands out on negative tendency, while <strong>{esc(most_positive_customer["customer_name"])}</strong> is one of the strongest consistently positive reviewers.</li>
          <li>The text does <strong>not</strong> support a shipping or customer-service issue narrative: {", ".join(operation_zero_terms[:5])} and related operational terms never appear in the reviews.</li>
        </ul>
      </article>
      <article class="card wide">
        <div class="label">Interpretation Guardrails</div>
        <p class="subtle">
          The review text is templated and often generic, so rating-based outliers are much more reliable than
          attempting to infer precise complaint causes from wording. This report therefore treats product risk as a
          combination of rating distribution, review volume, and completed-sales volume, and only calls out a theme
          when the text genuinely repeats.
        </p>
        <div class="warn-pill">Negative here means 2-star, not 1-star</div>
        <div class="good-pill">No explicit shipping, delivery, or refund complaints found in text</div>
      </article>
    </section>

    <section class="grid">
      <article class="card full">
        <div class="label">Product Watchlist</div>
        <h2 style="margin-top: 8px;">Products most worth investigating</h2>
        <p>These are the products that rise to the top when you look at either negative share of reviews or negative volume relative to completed sales.</p>
        <div class="watch-grid">
          {"".join(watchlist_cards)}
        </div>
      </article>
    </section>

    <section class="grid">
      <article class="card wide">
        <div class="label">Highest Negative Share Among Reviewed Products</div>
        <p class="subtle">Filtered to products with at least 3 reviews so one-off ratings do not dominate the ranking.</p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Product</th>
                <th>Brand</th>
                <th>Category</th>
                <th>Reviews</th>
                <th>2-Star</th>
                <th>Negative Rate</th>
                <th>Avg Rating</th>
                <th>Completed Orders</th>
              </tr>
            </thead>
            <tbody>{review_rate_rows}</tbody>
          </table>
        </div>
      </article>
      <article class="card wide">
        <div class="label">Highest Negative Load Relative to Sales</div>
        <p class="subtle">Filtered to products with at least 8 completed orders and at least 2 negative reviews.</p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Product</th>
                <th>Brand</th>
                <th>Category</th>
                <th>Completed Orders</th>
                <th>Units</th>
                <th>2-Star</th>
                <th>Reviews</th>
                <th>2-Star per 100 Orders</th>
              </tr>
            </thead>
            <tbody>{sales_risk_rows}</tbody>
          </table>
        </div>
      </article>
    </section>

    <section class="grid">
      <article class="card wide">
        <div class="label">Category-Level Hotspots</div>
        <p class="subtle">Categories with at least 15 reviews, ranked by 2-star share.</p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Department</th>
                <th>Category</th>
                <th>Reviews</th>
                <th>2-Star</th>
                <th>Negative Rate</th>
                <th>Avg Rating</th>
              </tr>
            </thead>
            <tbody>{category_rows}</tbody>
          </table>
        </div>
      </article>
      <article class="card wide">
        <div class="label">Who Trends More Negative?</div>
        <p class="subtle">Negative-rate bars normalize for review volume, so these show rate rather than raw count.</p>
        <div class="bars">
          <h3 style="font-size:1rem; margin-top: 0;">By Segment</h3>
          {segment_bars}
        </div>
        <div class="bars">
          <h3 style="font-size:1rem;">By State</h3>
          {state_bars}
        </div>
      </article>
    </section>

    <section class="grid">
      <article class="card wide">
        <div class="label">Customers Who Tend Negative</div>
        <p class="subtle">Customers need at least 2 reviews to appear here.</p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Customer</th>
                <th>Segment</th>
                <th>State</th>
                <th>Reviews</th>
                <th>2-Star</th>
                <th>Negative Rate</th>
                <th>Avg Rating</th>
              </tr>
            </thead>
            <tbody>{negative_customer_rows}</tbody>
          </table>
        </div>
      </article>
      <article class="card wide">
        <div class="label">Customers Who Tend Positive</div>
        <p class="subtle">Customers need at least 3 reviews to appear here.</p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Customer</th>
                <th>Segment</th>
                <th>State</th>
                <th>Reviews</th>
                <th>4-5 Star</th>
                <th>Positive Rate</th>
                <th>Avg Rating</th>
              </tr>
            </thead>
            <tbody>{positive_customer_rows}</tbody>
          </table>
        </div>
      </article>
    </section>

    <section class="grid">
      <article class="card wide">
        <div class="label">Text Theme Check</div>
        <ul>
          <li>Operational complaint terms such as <code>shipping</code>, <code>delivery</code>, <code>late</code>, <code>refund</code>, and <code>support</code> appear <strong>zero times</strong> in the review text.</li>
          <li>The highest-overindex phrases inside 2-star reviews are only modestly above the overall negative baseline of <strong>{pct(baseline_negative_rate)}</strong>, which is not strong enough to claim a distinct cross-product complaint theme.</li>
          <li>In practice, the dataset supports a reliable answer on <strong>which products and customers skew negative</strong>, but not a strong answer on <strong>why</strong> from the text alone.</li>
        </ul>
      </article>
      <article class="card wide">
        <div class="label">Most Common Review Phrases in 2-Star Reviews</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Phrase Bucket</th>
                <th>Reviews Using Phrase</th>
                <th>2-Star Reviews</th>
                <th>2-Star Rate</th>
                <th>Uplift vs Baseline</th>
              </tr>
            </thead>
            <tbody>{theme_rows}</tbody>
          </table>
        </div>
      </article>
    </section>
  </main>
</body>
</html>
"""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html_text, encoding="utf-8")
    print(f"Wrote report to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
