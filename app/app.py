from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "inventory_user",
    "password": "inventory_pass",
    "database": "inventory_db"
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/")
def welcome():
    return "Welcome to the inventory app!"


@app.route("/add", methods=["POST"])
def add_item():
    """
    Adds item to inventory. If the item exists, increment amount. Else,
    create a new row.
    """
    data = request.get_json()

    if not data or "item" not in data or "amount" not in data:
        return jsonify({"error": "Missing item or amount"}), 400

    item = data["item"].strip().lower()
    amount = data["amount"]

    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO inventory (item_name, amount)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE amount = amount + VALUES(amount);
        """
        cursor.execute(query, (item, amount))
        conn.commit()

        return jsonify({
            "message": "Success",
            "item": item,
            "amount_added": amount
        }), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/remove", methods=["POST"])
def remove_item():
    """
    Removes amount from inventory. Errors if item does not exist or
    it makes the amount become less than 0.
    """
    data = request.get_json()

    if not data or "item" not in data or "amount" not in data:
        return jsonify({"error": "Missing item or amount"}), 400

    item = data["item"].strip().lower()
    amount = data["amount"]

    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT amount FROM inventory WHERE item_name = %s",
            (item,)
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Item does not exist."}), 404
        if row["amount"] < amount:
            return jsonify({"error": "Removing more than exists."}), 400

        new_amount = row["amount"] - amount
        cursor.execute(
            "UPDATE inventory SET amount = %s WHERE item_name = %s",
            (new_amount, item)
        )
        conn.commit()

        return jsonify({
            "message": "Success",
            "item": item,
            "amount_removed": amount,
            "remaining": new_amount
        }), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/inventory", methods=["GET"])
def list_inventory():
    """
    Returns the full inventory as a JSON list.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, item_name, amount FROM inventory ORDER BY item_name"
        )
        rows = cursor.fetchall()

        return jsonify(rows), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
