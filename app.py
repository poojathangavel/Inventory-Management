from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",        
        password="Murugar", 
        database="ivc"
    )
    return conn


@app.route("/")
def home():
    return redirect(url_for("report"))


@app.route("/products", methods=["GET", "POST"])
def products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        product_id = request.form["product_id"]
        product_name = request.form["product_name"]

        if "add" in request.form:
            cursor.execute("INSERT INTO Product VALUES (%s, %s)", (product_id, product_name))
        elif "edit" in request.form:
            cursor.execute("UPDATE Product SET product_name=%s WHERE product_id=%s", (product_name, product_id))

        conn.commit()
        return redirect(url_for("products"))

    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    conn.close()
    return render_template("products.html", products=products)


@app.route("/locations", methods=["GET", "POST"])
def locations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        location_id = request.form["location_id"]
        location_name = request.form["location_name"]

        if "add" in request.form:
            cursor.execute("INSERT INTO Location VALUES (%s, %s)", (location_id, location_name))
        elif "edit" in request.form:
            cursor.execute("UPDATE Location SET location_name=%s WHERE location_id=%s", (location_name, location_id))

        conn.commit()
        return redirect(url_for("locations"))

    cursor.execute("SELECT * FROM Location")
    locations = cursor.fetchall()
    conn.close()
    return render_template("locations.html", locations=locations)



@app.route("/movements", methods=["GET", "POST"])
def movements():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        movement_id = request.form["movement_id"]
        from_location = request.form.get("from_location") or None
        to_location = request.form.get("to_location") or None
        product_id = request.form["product_id"]
        qty = request.form["qty"]

        if "add" in request.form:
            cursor.execute("""
                INSERT INTO ProductMovement (movement_id, from_location, to_location, product_id, qty)
                VALUES (%s, %s, %s, %s, %s)
            """, (movement_id, from_location, to_location, product_id, qty))
        elif "edit" in request.form:
            cursor.execute("""
                UPDATE ProductMovement
                SET from_location=%s, to_location=%s, product_id=%s, qty=%s
                WHERE movement_id=%s
            """, (from_location, to_location, product_id, qty, movement_id))

        conn.commit()
        return redirect(url_for("movements"))

 
    cursor.execute("""
        SELECT pm.movement_id, pm.from_location, pm.to_location, p.product_name, pm.qty
        FROM ProductMovement pm
        JOIN Product p ON pm.product_id = p.product_id
    """)
    movements = cursor.fetchall()

  
    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    cursor.execute("SELECT * FROM Location")
    locations = cursor.fetchall()

    conn.close()
    return render_template("movements.html", movements=movements, products=products, locations=locations)



@app.route("/report")
def report():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.product_name AS Product,
            l.location_name AS Location,
            COALESCE(SUM(
                CASE WHEN pm.to_location = l.location_id THEN pm.qty ELSE 0 END
            ), 0) -
            COALESCE(SUM(
                CASE WHEN pm.from_location = l.location_id THEN pm.qty ELSE 0 END
            ), 0) AS Qty
        FROM Product p
        CROSS JOIN Location l
        LEFT JOIN ProductMovement pm ON p.product_id = pm.product_id
        GROUP BY p.product_id, l.location_id;
    """)
    report_data = cursor.fetchall()
    conn.close()
    return render_template("report.html", report=report_data)


if __name__ == "__main__":
    app.run(debug=True)
