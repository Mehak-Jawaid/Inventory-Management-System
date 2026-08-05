# StockFlow - Inventory Management System

A full-stack inventory management system built with Python, Flask, SQLite, HTML, CSS, and JavaScript.

Designed for small businesses to manage inventory, track stock levels, search products, and export reports.

## Screenshots

| Login | Dashboard |
|-------|-----------|
| ![Login](docs/screenshots/login.png) | ![Dashboard](docs/screenshots/dashboard.png) |

| Products | Add Product |
|----------|-------------|
| ![Products](docs/screenshots/products.png) | ![Add Product](docs/screenshots/add-product.png) |

## Features

- Secure login with hashed passwords
- Dashboard with inventory statistics
- Add, edit, and delete products
- Product search and category filtering
- Low stock alerts
- Export inventory to CSV
- Responsive user interface

## Technologies

- Python
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript

## Installation

### 1. Prerequisites

- Python 3.10+ installed  
  Check with: `python --version`

### 2. Open the project folder

```bash
cd "Inventory Management System"
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows (PowerShell):**

```bash
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```bash
venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the app

```bash
python app.py
```

### 7. Open in your browser

Go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

On first run, the app creates `inventory.db` and seeds sample products automatically.

## Demo Login

| Field    | Value            |
|----------|------------------|
| Username | `admin`          |
| Password | `Inventory@2026` |

## Folder Structure

```text
Inventory Management System/
├── app.py                 # Flask routes, database, auth, CSV export
├── requirements.txt       # Python packages
├── BUILD_GUIDE.md         # Step-by-step development walkthrough
├── inventory.db           # Created automatically on first run
├── docs/
│   └── screenshots/       # README screenshots
├── static/
│   ├── css/style.css      # Styling
│   └── js/main.js         # Delete confirm + mobile menu
└── templates/
    ├── base.html          # Shared layout / nav
    ├── login.html
    ├── dashboard.html
    ├── products.html
    └── product_form.html  # Add + Edit form
```

For a detailed walkthrough of how the app was built, see [BUILD_GUIDE.md](BUILD_GUIDE.md).

## Security

- Passwords are hashed (Werkzeug), not stored in plain text.
- Routes that change data require login.
- SQL uses parameterized queries (`?` placeholders) to avoid SQL injection.
- For a real deployment: set a strong `SECRET_KEY` env var, turn off `debug=True`, and use a production server (e.g. Gunicorn) behind HTTPS.

## What I Learned

- Building a Flask web application
- User authentication with hashed passwords
- CRUD operations with SQLite
- Server-side validation
- Session management
- Exporting data as CSV
- Organizing a full-stack project

## Future Improvements

- Role-based access (Admin / Employee)
- Product images
- Barcode support
- PDF report export
- Sales management
- Supplier management

## License

This project is open source and available under the [MIT License](LICENSE).
