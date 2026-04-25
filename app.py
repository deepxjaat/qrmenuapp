from flask import Flask, request, jsonify, render_template
import sqlite3, json

app = Flask(__name__)

# ---------- DB ----------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        category TEXT,
        image TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        items TEXT,
        total_price INTEGER,
        status TEXT,
        table_number INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------
@app.route('/')
def home():
    return "QR Menu Running"

@app.route('/menu-page')
def menu_page():
    return render_template("menu.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

# ---------- MENU ----------
@app.route('/menu')
def menu():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM menu")
    rows = cur.fetchall()
    return jsonify([dict(row) for row in rows])

@app.route('/all-menu')
def all_menu():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM menu")
    rows = cur.fetchall()
    return jsonify([dict(row) for row in rows])

# ---------- ADD ITEM ----------
@app.route('/add-item', methods=['POST'])
def add_item():
    data = request.json

    name = data.get('name')
    price = data.get('price')
    category = data.get('category')

    image_map = {
        "burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd",
        "pizza": "https://images.unsplash.com/photo-1548365328-5c6db322f6e7",
        "coke": "https://images.unsplash.com/photo-1580910051074-3eb694886505",
        "sprite": "https://images.unsplash.com/photo-1622483767028-3f66f32aefdb"
    }

    image = image_map.get(name.lower(), "https://via.placeholder.com/300")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO menu (name, price, category, image) VALUES (?, ?, ?, ?)",
        (name, price, category, image)
    )

    conn.commit()
    return "OK"

# DELETE ITEM
@app.route('/delete-item/<int:id>', methods=['POST'])
def delete_item(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM menu WHERE id=?", (id,))
    conn.commit()
    return "Deleted"

# ---------- ORDER (FIXED) ----------
@app.route('/order', methods=['POST'])
def order():
    try:
        data = request.json

        items = json.dumps(data.get('items'))
        total = data.get('total_price')
        table = data.get('table_number')

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO orders (items, total_price, status, table_number) VALUES (?, ?, ?, ?)",
            (items, total, 'pending', table)
        )

        conn.commit()
        return "OK"

    except Exception as e:
        print("ORDER ERROR:", e)
        return "Error", 500

@app.route('/orders')
def orders():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders")
    rows = cur.fetchall()

    result = []
    for r in rows:
        result.append({
            "order_id": r["order_id"],
            "items": r["items"],
            "total": r["total_price"],
            "status": r["status"]
        })

    return jsonify(result)

@app.route('/update-status/<int:id>', methods=['POST'])
def update_status(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status='completed' WHERE order_id=?", (id,))
    conn.commit()
    return "Done"

import os

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))