# Build Guide — StockFlow

Step-by-step learning path for rebuilding this inventory management system from scratch.

Use this if you want to understand how each part of the project was built. For a concise overview, see [README.md](README.md).

---

## Step 1 — Set up Flask

1. Create a folder and virtual environment.
2. Install Flask: `pip install Flask`
3. Create `app.py` with a basic route that returns HTML.
4. Run with `python app.py` and open `http://127.0.0.1:5000`.

**Concepts:** routes, `app.run()`, development server.

---

## Step 2 — Add templates and static files

1. Create `templates/` and `static/css`, `static/js`.
2. Use `render_template("login.html")` instead of returning raw HTML strings.
3. Extend a shared `base.html` with Jinja blocks (`{% block content %}`).
4. Link CSS/JS with `url_for('static', filename='...')`.

**Concepts:** Jinja2 templates, inheritance, static assets.

---

## Step 3 — Connect SQLite

1. Create tables for `users` and `products` with `CREATE TABLE IF NOT EXISTS`.
2. Use `sqlite3` + `row_factory = sqlite3.Row` for dict-like rows.
3. Open a DB connection per request (`get_db`) and close it on teardown.
4. Seed a default admin user and sample products on first launch.

**Concepts:** relational schema, primary keys, unique SKU, CRUD SQL.

---

## Step 4 — Build login / logout

1. Store a **password hash** (never plain text) with `generate_password_hash`.
2. On login, verify with `check_password_hash`.
3. Save `user_id` in Flask `session`.
4. Protect pages with a `@login_required` decorator that redirects guests to `/login`.

**Concepts:** authentication, sessions, cookies, password hashing, decorators.

---

## Step 5 — Dashboard

1. Query aggregates: product count, sum of quantities, inventory value (`SUM(quantity * price)`).
2. Query products where `quantity <= 10` for low-stock alerts.
3. Group by category for a simple breakdown.

**Concepts:** SQL aggregates, dashboard UX, business rules.

---

## Step 6 — Product CRUD

| Action | Method | Route |
|--------|--------|-------|
| List   | GET    | `/products` |
| Add    | GET/POST | `/products/add` |
| Edit   | GET/POST | `/products/<id>/edit` |
| Delete | POST   | `/products/<id>/delete` |

1. Validate required fields and numeric values on the server.
2. Handle duplicate SKU with `IntegrityError`.
3. Flash success/error messages after each action.

**Concepts:** REST-ish routes, forms, validation, flash messages.

---

## Step 7 — Search and filters

1. Read `?q=` and `?category=` from `request.args`.
2. Build SQL with `LIKE` for name/SKU/description.
3. Keep the form values so the UI reflects the current filters.

**Concepts:** query parameters, dynamic SQL (with bound parameters — never string-concat user input into SQL).

---

## Step 8 — Export CSV

1. Query all products.
2. Write rows with Python’s `csv` module into an in-memory buffer.
3. Return a Flask `Response` with `Content-Disposition: attachment`.

**Concepts:** file downloads, CSV, HTTP headers.

---

## Step 9 — Frontend polish

1. Style a clear layout (sidebar + main content).
2. Use JavaScript for delete confirmation and mobile nav.
3. Show status badges for in-stock / low / out-of-stock.

**Concepts:** UX, progressive enhancement, responsive CSS.
