import csv
import io
import os
import sqlite3
from functools import wraps

from flask import (
    Flask,
    Response,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
if os.environ.get("FLASK_ENV") == "production" or os.environ.get("RENDER"):
    app.config["SESSION_COOKIE_SECURE"] = True

DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.db"),
)
LOW_STOCK_THRESHOLD = 10


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            price REAL NOT NULL DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    admin_password_hash = generate_password_hash("Inventory@2026")
    admin = cursor.execute(
        "SELECT id FROM users WHERE username = ?", ("admin",)
    ).fetchone()
    if not admin:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("admin", admin_password_hash),
        )
    else:
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (admin_password_hash, "admin"),
        )

    sample_count = cursor.execute("SELECT COUNT(*) AS count FROM products").fetchone()[
        "count"
    ]
    if sample_count == 0:
        samples = [
            ("Wireless Mouse", "WM-001", "Electronics", 45, 19.99, "Ergonomic wireless mouse"),
            ("USB-C Cable", "UC-002", "Electronics", 8, 12.50, "1m braided USB-C cable"),
            ("Notebook A5", "NB-003", "Stationery", 120, 4.99, "Lined A5 notebook"),
            ("Desk Lamp", "DL-004", "Office", 5, 34.00, "LED desk lamp with dimmer"),
            ("Keyboard", "KB-005", "Electronics", 22, 49.99, "Mechanical keyboard"),
            ("Sticky Notes", "SN-006", "Stationery", 3, 2.49, "Pack of 5 sticky note pads"),
            ("Monitor Stand", "MS-007", "Office", 15, 29.99, "Adjustable wooden monitor stand"),
            ("Webcam HD", "WC-008", "Electronics", 7, 59.99, "1080p USB webcam"),
        ]
        cursor.executemany(
            """
            INSERT INTO products (name, sku, category, quantity, price, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            samples,
        )

    db.commit()
    db.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()

    total_products = db.execute("SELECT COUNT(*) AS count FROM products").fetchone()[
        "count"
    ]
    total_units = db.execute(
        "SELECT COALESCE(SUM(quantity), 0) AS total FROM products"
    ).fetchone()["total"]
    inventory_value = db.execute(
        "SELECT COALESCE(SUM(quantity * price), 0) AS value FROM products"
    ).fetchone()["value"]
    low_stock_items = db.execute(
        "SELECT * FROM products WHERE quantity <= ? ORDER BY quantity ASC",
        (LOW_STOCK_THRESHOLD,),
    ).fetchall()
    categories = db.execute(
        """
        SELECT category, COUNT(*) AS count, SUM(quantity) AS units
        FROM products
        GROUP BY category
        ORDER BY count DESC
        """
    ).fetchall()
    recent_products = db.execute(
        "SELECT * FROM products ORDER BY updated_at DESC LIMIT 5"
    ).fetchall()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_units=total_units,
        inventory_value=inventory_value,
        low_stock_items=low_stock_items,
        low_stock_threshold=LOW_STOCK_THRESHOLD,
        categories=categories,
        recent_products=recent_products,
    )


@app.route("/products")
@login_required
def products():
    db = get_db()
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR sku LIKE ? OR description LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like, like])

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY name ASC"
    items = db.execute(query, params).fetchall()
    categories = db.execute(
        "SELECT DISTINCT category FROM products ORDER BY category"
    ).fetchall()

    return render_template(
        "products.html",
        products=items,
        search=search,
        selected_category=category,
        categories=categories,
        low_stock_threshold=LOW_STOCK_THRESHOLD,
    )


@app.route("/products/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        sku = request.form.get("sku", "").strip().upper()
        category = request.form.get("category", "").strip()
        quantity = request.form.get("quantity", "0").strip()
        price = request.form.get("price", "0").strip()
        description = request.form.get("description", "").strip()

        errors = []
        if not name:
            errors.append("Product name is required.")
        if not sku:
            errors.append("SKU is required.")
        if not category:
            errors.append("Category is required.")

        try:
            quantity = int(quantity)
            if quantity < 0:
                errors.append("Quantity cannot be negative.")
        except ValueError:
            errors.append("Quantity must be a whole number.")
            quantity = 0

        try:
            price = float(price)
            if price < 0:
                errors.append("Price cannot be negative.")
        except ValueError:
            errors.append("Price must be a valid number.")
            price = 0

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "product_form.html",
                product=None,
                form_data=request.form,
                title="Add Product",
            )

        db = get_db()
        try:
            db.execute(
                """
                INSERT INTO products (name, sku, category, quantity, price, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, sku, category, quantity, price, description),
            )
            db.commit()
            flash(f'Product "{name}" added successfully.', "success")
            return redirect(url_for("products"))
        except sqlite3.IntegrityError:
            flash("A product with that SKU already exists.", "error")
            return render_template(
                "product_form.html",
                product=None,
                form_data=request.form,
                title="Add Product",
            )

    return render_template(
        "product_form.html", product=None, form_data=None, title="Add Product"
    )


@app.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    db = get_db()
    product = db.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()

    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("products"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        sku = request.form.get("sku", "").strip().upper()
        category = request.form.get("category", "").strip()
        quantity = request.form.get("quantity", "0").strip()
        price = request.form.get("price", "0").strip()
        description = request.form.get("description", "").strip()

        errors = []
        if not name:
            errors.append("Product name is required.")
        if not sku:
            errors.append("SKU is required.")
        if not category:
            errors.append("Category is required.")

        try:
            quantity = int(quantity)
            if quantity < 0:
                errors.append("Quantity cannot be negative.")
        except ValueError:
            errors.append("Quantity must be a whole number.")
            quantity = 0

        try:
            price = float(price)
            if price < 0:
                errors.append("Price cannot be negative.")
        except ValueError:
            errors.append("Price must be a valid number.")
            price = 0

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "product_form.html",
                product=product,
                form_data=request.form,
                title="Edit Product",
            )

        try:
            db.execute(
                """
                UPDATE products
                SET name = ?, sku = ?, category = ?, quantity = ?, price = ?,
                    description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (name, sku, category, quantity, price, description, product_id),
            )
            db.commit()
            flash(f'Product "{name}" updated successfully.', "success")
            return redirect(url_for("products"))
        except sqlite3.IntegrityError:
            flash("A product with that SKU already exists.", "error")
            return render_template(
                "product_form.html",
                product=product,
                form_data=request.form,
                title="Edit Product",
            )

    return render_template(
        "product_form.html", product=product, form_data=None, title="Edit Product"
    )


@app.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    db = get_db()
    product = db.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()

    if product is None:
        flash("Product not found.", "error")
    else:
        db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        db.commit()
        flash(f'Product "{product["name"]}" deleted.', "success")

    return redirect(url_for("products"))


@app.route("/export")
@login_required
def export_csv():
    db = get_db()
    products = db.execute(
        "SELECT name, sku, category, quantity, price, description, created_at, updated_at FROM products ORDER BY name"
    ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Name",
            "SKU",
            "Category",
            "Quantity",
            "Price",
            "Description",
            "Created At",
            "Updated At",
        ]
    )

    for product in products:
        writer.writerow(
            [
                product["name"],
                product["sku"],
                product["category"],
                product["quantity"],
                f"{product['price']:.2f}",
                product["description"] or "",
                product["created_at"],
                product["updated_at"],
            ]
        )

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=inventory_export.csv"
    return response


# Initialize DB when the app starts (local `python app.py` or Gunicorn on Render)
init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "1") == "1")
