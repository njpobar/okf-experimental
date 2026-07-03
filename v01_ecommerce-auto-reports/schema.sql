PRAGMA foreign_keys = ON;

CREATE TABLE categories (
  id INTEGER PRIMARY KEY,
  department TEXT NOT NULL,
  name TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL
);

CREATE TABLE customers (
  id INTEGER PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  city TEXT NOT NULL,
  state TEXT NOT NULL,
  segment TEXT NOT NULL,
  signup_date TEXT NOT NULL,
  profile_note TEXT NOT NULL
);

CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  category_id INTEGER NOT NULL,
  sku TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  brand TEXT NOT NULL,
  price_cents INTEGER NOT NULL,
  stock_qty INTEGER NOT NULL,
  tags TEXT NOT NULL,
  description TEXT NOT NULL,
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  order_date TEXT NOT NULL,
  status TEXT NOT NULL,
  shipping_method TEXT NOT NULL,
  subtotal_cents INTEGER NOT NULL,
  tax_cents INTEGER NOT NULL,
  shipping_fee_cents INTEGER NOT NULL,
  total_cents INTEGER NOT NULL,
  notes TEXT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE order_items (
  id INTEGER PRIMARY KEY,
  order_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  unit_price_cents INTEGER NOT NULL,
  line_total_cents INTEGER NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE reviews (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  rating INTEGER NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_reviews_customer_id ON reviews(customer_id);
CREATE INDEX idx_reviews_product_id ON reviews(product_id);
