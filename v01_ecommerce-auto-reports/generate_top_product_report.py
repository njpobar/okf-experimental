from __future__ import annotations

import html
import math
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


DB_PATH = Path("ecommerce.sqlite")
OUTPUT_PATH = Path("reports/top_product_sales_report.html")
COMPLETED_STATUSES = ("paid", "shipped", "delivered")


@dataclass
class MonthlyPoint:
    month: str
    revenue: float
    units: int
    orders: int


def query_all(conn: sqlite3.Connection, sql: str, params: Iterable[object] = ()) -> list[sqlite3.Row]:
    return conn.execute(sql, tuple(params)).fetchall()


def query_one(conn: sqlite3.Connection, sql: str, params: Iterable[object] = ()) -> sqlite3.Row:
    row = conn.execute(sql, tuple(params)).fetchone()
    if row is None:
        raise ValueError("Expected query to return one row")
    return row


def month_range(start_month: str, end_month: str) -> list[str]:
    start = datetime.strptime(start_month, "%Y-%m")
    end = datetime.strptime(end_month, "%Y-%m")
    months: list[str] = []
    current = start
    while current <= end:
        months.append(current.strftime("%Y-%m"))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return months


def money(amount: float) -> str:
    return f"${amount:,.2f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def build_line_chart(points: list[MonthlyPoint]) -> str:
    width = 920
    height = 340
    margin_left = 68
    margin_right = 20
    margin_top = 24
    margin_bottom = 52
    inner_width = width - margin_left - margin_right
    inner_height = height - margin_top - margin_bottom

    max_revenue = max((point.revenue for point in points), default=0.0)
    y_max = max(100.0, math.ceil(max_revenue / 100.0) * 100.0)
    x_step = inner_width / max(1, len(points) - 1)

    def x_pos(index: int) -> float:
        return margin_left + index * x_step

    def y_pos(revenue: float) -> float:
        return margin_top + inner_height - ((revenue / y_max) * inner_height if y_max else 0)

    path = " ".join(
        f"{'M' if index == 0 else 'L'} {x_pos(index):.2f} {y_pos(point.revenue):.2f}"
        for index, point in enumerate(points)
    )

    y_ticks = 4
    grid_lines: list[str] = []
    for tick in range(y_ticks + 1):
        value = y_max * tick / y_ticks
        y = y_pos(value)
        grid_lines.append(
            f'<line x1="{margin_left}" y1="{y:.2f}" x2="{width - margin_right}" y2="{y:.2f}" '
            f'stroke="#d9e4df" stroke-width="1" />'
        )
        grid_lines.append(
            f'<text x="{margin_left - 10}" y="{y + 4:.2f}" text-anchor="end" '
            f'font-size="12" fill="#4f5f5a">{esc(money(value))}</text>'
        )

    x_labels: list[str] = []
    for index, point in enumerate(points):
        if len(points) <= 12 or index % 2 == 0 or index == len(points) - 1:
            label = datetime.strptime(point.month, "%Y-%m").strftime("%b %Y")
            x_labels.append(
                f'<text x="{x_pos(index):.2f}" y="{height - 20}" text-anchor="middle" '
                f'font-size="11" fill="#4f5f5a">{esc(label)}</text>'
            )

    point_marks = []
    for index, point in enumerate(points):
        x = x_pos(index)
        y = y_pos(point.revenue)
        tooltip = f"{point.month}: {money(point.revenue)} revenue, {point.units} units, {point.orders} orders"
        point_marks.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.5" fill="#0f766e">'
            f'<title>{esc(tooltip)}</title></circle>'
        )

    return f"""
    <svg viewBox="0 0 {width} {height}" role="img" aria-label="Monthly revenue trend for the overall top product">
      <rect x="0" y="0" width="{width}" height="{height}" rx="18" fill="#f8fbfa" />
      {''.join(grid_lines)}
      <line x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" stroke="#8ea39d" stroke-width="1.2" />
      <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" stroke="#8ea39d" stroke-width="1.2" />
      <path d="{path}" fill="none" stroke="#0f766e" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
      {''.join(point_marks)}
      {''.join(x_labels)}
    </svg>
    """


def build_distribution_rows(rows: list[sqlite3.Row], total: int, value_label: str) -> str:
    body = []
    for row in rows:
        share = (row["customers"] / total) if total else 0
        body.append(
            "<tr>"
            f"<td>{esc(row[value_label])}</td>"
            f"<td>{row['customers']}</td>"
            f"<td>{pct(share)}</td>"
            "</tr>"
        )
    return "".join(body)


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    status_placeholders = ", ".join("?" for _ in COMPLETED_STATUSES)
    status_params = list(COMPLETED_STATUSES)

    monthly_winners = query_all(
        conn,
        f"""
        WITH monthly_product_sales AS (
          SELECT
            substr(o.order_date, 1, 7) AS month,
            p.id AS product_id,
            p.name AS product_name,
            p.brand AS brand,
            c.department AS department,
            c.name AS category_name,
            SUM(oi.line_total_cents) / 100.0 AS revenue,
            SUM(oi.quantity) AS units_sold,
            COUNT(DISTINCT o.id) AS order_count
          FROM orders o
          JOIN order_items oi ON oi.order_id = o.id
          JOIN products p ON p.id = oi.product_id
          JOIN categories c ON c.id = p.category_id
          WHERE o.status IN ({status_placeholders})
          GROUP BY 1, 2, 3, 4, 5, 6
        ),
        ranked AS (
          SELECT
            *,
            ROW_NUMBER() OVER (
              PARTITION BY month
              ORDER BY revenue DESC, units_sold DESC, order_count DESC, product_id
            ) AS rn
          FROM monthly_product_sales
        )
        SELECT
          month,
          product_id,
          product_name,
          brand,
          department,
          category_name,
          revenue,
          units_sold,
          order_count
        FROM ranked
        WHERE rn = 1
        ORDER BY month
        """,
        status_params,
    )

    overall_top_product = query_one(
        conn,
        f"""
        SELECT
          p.id,
          p.name,
          p.brand,
          p.sku,
          p.tags,
          p.stock_qty,
          p.price_cents / 100.0 AS current_price,
          c.department,
          c.name AS category_name,
          SUM(oi.line_total_cents) / 100.0 AS revenue,
          SUM(oi.quantity) AS units_sold,
          COUNT(DISTINCT o.id) AS order_count
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p ON p.id = oi.product_id
        JOIN categories c ON c.id = p.category_id
        WHERE o.status IN ({status_placeholders})
        GROUP BY p.id, p.name, p.brand, p.sku, p.tags, p.stock_qty, current_price, c.department, c.name
        ORDER BY revenue DESC, units_sold DESC, order_count DESC, p.id
        LIMIT 1
        """,
        status_params,
    )

    bounds = query_one(
        conn,
        "SELECT substr(min(order_date), 1, 7) AS start_month, substr(max(order_date), 1, 7) AS end_month FROM orders",
    )
    all_months = month_range(bounds["start_month"], bounds["end_month"])

    top_product_monthly_sales_raw = query_all(
        conn,
        f"""
        SELECT
          substr(o.order_date, 1, 7) AS month,
          SUM(oi.line_total_cents) / 100.0 AS revenue,
          SUM(oi.quantity) AS units_sold,
          COUNT(DISTINCT o.id) AS order_count
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        WHERE oi.product_id = ?
          AND o.status IN ({status_placeholders})
        GROUP BY 1
        ORDER BY 1
        """,
        [overall_top_product["id"], *status_params],
    )
    monthly_sales_map = {row["month"]: row for row in top_product_monthly_sales_raw}
    top_product_series = [
        MonthlyPoint(
            month=month,
            revenue=monthly_sales_map.get(month, {"revenue": 0.0})["revenue"] if month in monthly_sales_map else 0.0,
            units=monthly_sales_map.get(month, {"units_sold": 0})["units_sold"] if month in monthly_sales_map else 0,
            orders=monthly_sales_map.get(month, {"order_count": 0})["order_count"] if month in monthly_sales_map else 0,
        )
        for month in all_months
    ]

    review_summary = query_one(
        conn,
        """
        SELECT
          COUNT(*) AS review_count,
          ROUND(AVG(rating), 2) AS avg_rating,
          MIN(created_at) AS first_review_at,
          MAX(created_at) AS last_review_at
        FROM reviews
        WHERE product_id = ?
        """,
        [overall_top_product["id"]],
    )

    rating_distribution = query_all(
        conn,
        """
        SELECT rating, COUNT(*) AS reviews
        FROM reviews
        WHERE product_id = ?
        GROUP BY rating
        ORDER BY rating DESC
        """,
        [overall_top_product["id"]],
    )

    sample_reviews = query_all(
        conn,
        """
        SELECT rating, title, body, created_at
        FROM reviews
        WHERE product_id = ?
        ORDER BY created_at DESC
        LIMIT 3
        """,
        [overall_top_product["id"]],
    )

    buyer_summary = query_one(
        conn,
        f"""
        WITH product_buyers AS (
          SELECT
            o.customer_id,
            COUNT(DISTINCT o.id) AS product_orders,
            SUM(oi.quantity) AS units
          FROM orders o
          JOIN order_items oi ON oi.order_id = o.id
          WHERE oi.product_id = ?
            AND o.status IN ({status_placeholders})
          GROUP BY o.customer_id
        )
        SELECT
          COUNT(*) AS unique_buyers,
          SUM(CASE WHEN product_orders > 1 THEN 1 ELSE 0 END) AS repeat_buyers,
          ROUND(AVG(product_orders), 2) AS avg_product_orders_per_buyer,
          ROUND(AVG(units), 2) AS avg_units_per_buyer
        FROM product_buyers
        """,
        [overall_top_product["id"], *status_params],
    )

    first_order_mix = query_one(
        conn,
        f"""
        WITH completed_orders AS (
          SELECT id, customer_id, order_date
          FROM orders
          WHERE status IN ({status_placeholders})
        ),
        first_completed_order AS (
          SELECT customer_id, MIN(order_date) AS first_order_date
          FROM completed_orders
          GROUP BY customer_id
        ),
        top_product_first_purchase AS (
          SELECT o.customer_id, MIN(o.order_date) AS first_top_product_order_date
          FROM completed_orders o
          JOIN order_items oi ON oi.order_id = o.id
          WHERE oi.product_id = ?
          GROUP BY o.customer_id
        )
        SELECT
          COUNT(*) AS buyers,
          SUM(CASE WHEN fco.first_order_date = tpfp.first_top_product_order_date THEN 1 ELSE 0 END) AS acquired_via_product
        FROM top_product_first_purchase tpfp
        JOIN first_completed_order fco ON fco.customer_id = tpfp.customer_id
        """,
        [*status_params, overall_top_product["id"]],
    )

    reviewer_overlap = query_one(
        conn,
        f"""
        WITH buyers AS (
          SELECT DISTINCT o.customer_id
          FROM orders o
          JOIN order_items oi ON oi.order_id = o.id
          WHERE oi.product_id = ?
            AND o.status IN ({status_placeholders})
        )
        SELECT COUNT(DISTINCT r.customer_id) AS buyer_reviewers
        FROM reviews r
        JOIN buyers b ON b.customer_id = r.customer_id
        WHERE r.product_id = ?
        """,
        [overall_top_product["id"], *status_params, overall_top_product["id"]],
    )

    segment_mix = query_all(
        conn,
        f"""
        SELECT c.segment, COUNT(DISTINCT c.id) AS customers
        FROM customers c
        JOIN orders o ON o.customer_id = c.id
        JOIN order_items oi ON oi.order_id = o.id
        WHERE oi.product_id = ?
          AND o.status IN ({status_placeholders})
        GROUP BY c.segment
        ORDER BY customers DESC, c.segment
        """,
        [overall_top_product["id"], *status_params],
    )

    state_mix = query_all(
        conn,
        f"""
        SELECT c.state, COUNT(DISTINCT c.id) AS customers
        FROM customers c
        JOIN orders o ON o.customer_id = c.id
        JOIN order_items oi ON oi.order_id = o.id
        WHERE oi.product_id = ?
          AND o.status IN ({status_placeholders})
        GROUP BY c.state
        ORDER BY customers DESC, c.state
        LIMIT 6
        """,
        [overall_top_product["id"], *status_params],
    )

    shipping_mix = query_all(
        conn,
        f"""
        SELECT o.shipping_method, COUNT(DISTINCT o.id) AS orders
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        WHERE oi.product_id = ?
          AND o.status IN ({status_placeholders})
        GROUP BY o.shipping_method
        ORDER BY orders DESC, o.shipping_method
        """,
        [overall_top_product["id"], *status_params],
    )

    total_orders = query_one(conn, "SELECT COUNT(*) AS orders FROM orders")["orders"]
    total_completed_orders = query_one(
        conn,
        f"SELECT COUNT(*) AS completed_orders FROM orders WHERE status IN ({status_placeholders})",
        status_params,
    )["completed_orders"]
    total_unique_customers = query_one(conn, "SELECT COUNT(*) AS customers FROM customers")["customers"]
    monthly_winner_names = defaultdict(int)
    for row in monthly_winners:
        monthly_winner_names[f"{row['product_name']} ({row['brand']})"] += 1
    repeated_monthly_winners = sorted(
        ((name, count) for name, count in monthly_winner_names.items() if count > 1),
        key=lambda item: (-item[1], item[0]),
    )

    top_month = max(top_product_series, key=lambda point: point.revenue)
    active_months = sum(1 for point in top_product_series if point.revenue > 0)
    buyer_total = buyer_summary["unique_buyers"] or 0
    acquired_via_product = first_order_mix["acquired_via_product"] or 0
    buyer_reviewers = reviewer_overlap["buyer_reviewers"] or 0

    monthly_rows_html = "".join(
        "<tr>"
        f"<td>{esc(row['month'])}</td>"
        f"<td>{esc(row['product_name'])}</td>"
        f"<td>{esc(row['brand'])}</td>"
        f"<td>{esc(row['department'])}</td>"
        f"<td>{esc(row['category_name'])}</td>"
        f"<td>{money(row['revenue'])}</td>"
        f"<td>{row['units_sold']}</td>"
        f"<td>{row['order_count']}</td>"
        "</tr>"
        for row in monthly_winners
    )

    rating_rows_html = "".join(
        "<tr>"
        f"<td>{row['rating']}</td>"
        f"<td>{row['reviews']}</td>"
        "</tr>"
        for row in rating_distribution
    ) or '<tr><td colspan="2">No reviews available.</td></tr>'

    review_cards_html = "".join(
        f"""
        <article class="review-card">
          <div class="review-meta">Rating {row['rating']} / 5 • {esc(row['created_at'])}</div>
          <h4>{esc(row['title'])}</h4>
          <p>{esc(row['body'])}</p>
        </article>
        """
        for row in sample_reviews
    ) or "<p>No written reviews were available for the top product.</p>"

    shipping_rows_html = "".join(
        "<tr>"
        f"<td>{esc(row['shipping_method'])}</td>"
        f"<td>{row['orders']}</td>"
        f"<td>{pct((row['orders'] / overall_top_product['order_count']) if overall_top_product['order_count'] else 0)}</td>"
        "</tr>"
        for row in shipping_mix
    )

    html_text = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Top Product Sales Report</title>
  <style>
    :root {{
      --bg: #f3f5ef;
      --panel: #ffffff;
      --panel-soft: #f8fbfa;
      --ink: #17312b;
      --muted: #5d726b;
      --accent: #0f766e;
      --accent-soft: #d8efe9;
      --line: #dbe4df;
      --shadow: 0 18px 40px rgba(21, 53, 45, 0.08);
      --radius: 18px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background:
        radial-gradient(circle at top left, rgba(15, 118, 110, 0.10), transparent 30%),
        linear-gradient(180deg, #f5f7f2 0%, var(--bg) 100%);
      color: var(--ink);
    }}
    .wrap {{
      max-width: 1220px;
      margin: 0 auto;
      padding: 40px 20px 56px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(15, 118, 110, 0.12), rgba(255, 255, 255, 0.96));
      border: 1px solid rgba(15, 118, 110, 0.12);
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
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    h1, h2, h3, h4 {{
      margin: 0;
      font-weight: 600;
    }}
    h1 {{
      margin-top: 14px;
      font-size: clamp(2rem, 4vw, 3.3rem);
      line-height: 1.05;
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
    .card.wide {{
      grid-column: span 6;
    }}
    .card.full {{
      grid-column: 1 / -1;
    }}
    .metric {{
      font-size: 2rem;
      line-height: 1.1;
      margin: 10px 0 6px;
    }}
    .label {{
      font-size: 0.82rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .subtle {{
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .chart-shell {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 14px;
      box-shadow: var(--shadow);
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
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}
    .table-wrap {{
      overflow-x: auto;
    }}
    .review-card {{
      background: var(--panel-soft);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 16px;
      margin-top: 12px;
    }}
    .review-meta {{
      color: var(--muted);
      font-size: 0.86rem;
      margin-bottom: 6px;
    }}
    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }}
    ul {{
      margin: 14px 0 0;
      padding-left: 20px;
      color: var(--muted);
    }}
    li + li {{
      margin-top: 8px;
    }}
    code {{
      background: #edf4f1;
      border-radius: 6px;
      padding: 2px 6px;
      font-size: 0.95em;
    }}
    @media (max-width: 980px) {{
      .card, .card.wide {{
        grid-column: 1 / -1;
      }}
      .two-col {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main class="wrap">
    <section class="hero">
      <span class="eyebrow">E-commerce Sales Review</span>
      <h1>Monthly winners plus a focused look at the overall top-selling product</h1>
      <p>
        This report uses the SQLite data documented in <code>tables/</code> and joins
        <code>orders</code>, <code>order_items</code>, <code>products</code>, <code>categories</code>,
        <code>reviews</code>, and <code>customers</code>. To keep the sales signal clean, the analysis
        includes only orders with statuses <code>paid</code>, <code>shipped</code>, or <code>delivered</code>.
      </p>
    </section>

    <section class="grid">
      <article class="card">
        <div class="label">Data Window</div>
        <div class="metric">{esc(bounds["start_month"])} to {esc(bounds["end_month"])}</div>
        <div class="subtle">{len(all_months)} monthly periods across {total_orders} orders.</div>
      </article>
      <article class="card">
        <div class="label">Completed Orders Used</div>
        <div class="metric">{total_completed_orders}</div>
        <div class="subtle">{pct(total_completed_orders / total_orders)} of all orders after excluding pending and cancelled records.</div>
      </article>
      <article class="card">
        <div class="label">Overall Top Product</div>
        <div class="metric">{esc(overall_top_product["name"])}</div>
        <div class="subtle">{esc(overall_top_product["brand"])} • {money(overall_top_product["revenue"])} revenue • {overall_top_product["units_sold"]} units</div>
      </article>
      <article class="card">
        <div class="label">Top Product Reviews</div>
        <div class="metric">{review_summary["review_count"]}</div>
        <div class="subtle">Average rating {review_summary["avg_rating"] or "n/a"} / 5.</div>
      </article>
    </section>

    <section class="grid">
      <article class="card wide">
        <div class="label">What Stands Out</div>
        <ul>
          <li>Monthly product leadership is fragmented across the catalog. Only <strong>{esc(repeated_monthly_winners[0][0]) if repeated_monthly_winners else "no product"}</strong>{f" won more than once ({repeated_monthly_winners[0][1]} months)." if repeated_monthly_winners else "won more than one month."}</li>
          <li>The overall revenue leader is <strong>{esc(overall_top_product["name"])}</strong>, even though it led only one individual month. That makes it a strong steady performer rather than a single-month spike.</li>
          <li><strong>{esc(overall_top_product["name"])}</strong> sold in {active_months} of {len(all_months)} months, peaking in <strong>{datetime.strptime(top_month.month, "%Y-%m").strftime("%B %Y")}</strong> at <strong>{money(top_month.revenue)}</strong>.</li>
        </ul>
      </article>
      <article class="card wide">
        <div class="label">Product Snapshot</div>
        <p class="subtle">
          <strong>{esc(overall_top_product["name"])}</strong> sits in <strong>{esc(overall_top_product["department"])}</strong> /
          <strong>{esc(overall_top_product["category_name"])}</strong>, sold under SKU <code>{esc(overall_top_product["sku"])}</code>.
          Current catalog price is {money(overall_top_product["current_price"])}, stock on hand is {overall_top_product["stock_qty"]},
          and the product tags are <code>{esc(overall_top_product["tags"])}</code>.
        </p>
      </article>
    </section>

    <section class="grid">
      <article class="card full">
        <div class="label">Time Series: {esc(overall_top_product["name"])}</div>
        <h2 style="margin-top: 8px;">Monthly sales trend for the overall top product</h2>
        <p>
          Revenue is shown across the full dataset window, with zero-value months included so gaps are visible instead of hidden.
        </p>
        <div class="chart-shell">
          {build_line_chart(top_product_series)}
        </div>
      </article>
    </section>

    <section class="grid">
      <article class="card">
        <div class="label">Top Product Revenue</div>
        <div class="metric">{money(overall_top_product["revenue"])}</div>
        <div class="subtle">{overall_top_product["order_count"]} completed orders contributed to this total.</div>
      </article>
      <article class="card">
        <div class="label">Units Sold</div>
        <div class="metric">{overall_top_product["units_sold"]}</div>
        <div class="subtle">Average of {buyer_summary["avg_units_per_buyer"]} units per buyer.</div>
      </article>
      <article class="card">
        <div class="label">Unique Buyers</div>
        <div class="metric">{buyer_total}</div>
        <div class="subtle">{pct(buyer_total / total_unique_customers)} of the total customer base bought this product.</div>
      </article>
      <article class="card">
        <div class="label">New-Customer Entry Point</div>
        <div class="metric">{acquired_via_product}</div>
        <div class="subtle">{pct((acquired_via_product / buyer_total) if buyer_total else 0)} of buyers purchased it in their first completed order.</div>
      </article>
    </section>

    <section class="grid">
      <article class="card wide">
        <div class="label">Customer Base for {esc(overall_top_product["name"])}</div>
        <h3 style="margin-top: 8px;">Who is buying it?</h3>
        <ul>
          <li>The product reached <strong>{buyer_total}</strong> unique customers and no buyer purchased it in more than one completed order, suggesting broad one-off adoption rather than repeat replenishment.</li>
          <li><strong>{segment_mix[0]['segment']}</strong> and <strong>{segment_mix[1]['segment']}</strong> customers were tied as the largest segments, each with <strong>{segment_mix[0]['customers']}</strong> buyers.</li>
          <li><strong>{state_mix[0]['state']}</strong> was the leading state with <strong>{state_mix[0]['customers']}</strong> buyers, followed by <strong>{state_mix[1]['state']}</strong> with <strong>{state_mix[1]['customers']}</strong>.</li>
          <li><strong>{shipping_mix[0]['shipping_method']}</strong> was the dominant fulfillment choice, used in <strong>{pct(shipping_mix[0]['orders'] / overall_top_product['order_count'])}</strong> of completed orders containing this product.</li>
        </ul>
      </article>
      <article class="card wide">
        <div class="label">Review Signal</div>
        <h3 style="margin-top: 8px;">How are customers rating it?</h3>
        <ul>
          <li>The product has <strong>{review_summary["review_count"]}</strong> reviews with an average rating of <strong>{review_summary["avg_rating"] or "n/a"}</strong> / 5.</li>
          <li>Review activity spans from <strong>{esc(review_summary["first_review_at"] or "n/a")}</strong> to <strong>{esc(review_summary["last_review_at"] or "n/a")}</strong>.</li>
          <li><strong>{buyer_reviewers}</strong> of the product's buyers also left a review, a buyer-to-review conversion rate of <strong>{pct((buyer_reviewers / buyer_total) if buyer_total else 0)}</strong>.</li>
        </ul>
      </article>
    </section>

    <section class="grid">
      <article class="card wide">
        <div class="label">Buyer Segment Mix</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>Segment</th><th>Customers</th><th>Share of Buyers</th></tr>
            </thead>
            <tbody>
              {build_distribution_rows(segment_mix, buyer_total, "segment")}
            </tbody>
          </table>
        </div>
      </article>
      <article class="card wide">
        <div class="label">Top Buyer States</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>State</th><th>Customers</th><th>Share of Buyers</th></tr>
            </thead>
            <tbody>
              {build_distribution_rows(state_mix, buyer_total, "state")}
            </tbody>
          </table>
        </div>
      </article>
    </section>

    <section class="grid">
      <article class="card wide">
        <div class="label">Shipping Mix for Orders Containing the Top Product</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>Shipping Method</th><th>Orders</th><th>Share of Product Orders</th></tr>
            </thead>
            <tbody>
              {shipping_rows_html}
            </tbody>
          </table>
        </div>
      </article>
      <article class="card wide">
        <div class="label">Rating Distribution</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>Rating</th><th>Reviews</th></tr>
            </thead>
            <tbody>
              {rating_rows_html}
            </tbody>
          </table>
        </div>
      </article>
    </section>

    <section class="grid">
      <article class="card full">
        <div class="label">Monthly Number One Sales Product</div>
        <h2 style="margin-top: 8px;">Revenue leader by month</h2>
        <p>The table below ranks the single top product in each month by line-item revenue among completed orders.</p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Month</th>
                <th>Product</th>
                <th>Brand</th>
                <th>Department</th>
                <th>Category</th>
                <th>Revenue</th>
                <th>Units</th>
                <th>Orders</th>
              </tr>
            </thead>
            <tbody>
              {monthly_rows_html}
            </tbody>
          </table>
        </div>
      </article>
    </section>

    <section class="grid">
      <article class="card wide">
        <div class="label">Sample Reviews for {esc(overall_top_product["name"])}</div>
        {review_cards_html}
      </article>
      <article class="card wide">
        <div class="label">Method Notes</div>
        <ul>
          <li>Sales are measured from <code>order_items.line_total_cents</code> joined through <code>orders</code> to get the month and status.</li>
          <li>The monthly winners table uses revenue as the primary ranking, then breaks ties with units sold, order count, and product id.</li>
          <li>The time-series chart focuses on the <strong>overall</strong> top revenue product across the full period: <strong>{esc(overall_top_product["name"])}</strong>.</li>
          <li>Review counts come from the <code>reviews</code> table and customer profiling comes from joins to <code>customers</code>.</li>
        </ul>
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
