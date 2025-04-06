from flask import Blueprint, render_template, current_app, request, redirect, url_for, send_file, flash
import sqlite3
import math
import csv
import io
import requests
from io import StringIO

main = Blueprint("main", __name__)

#  Get a database connection
def get_connection():
    db_path = current_app.config["DB_PATH"]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

#  front page
@main.route("/")
def home():
    return render_template("home.html")

#  news page（Hacker News Top Stories）
@main.route("/news")
def news():
    try:
        top_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:5]
        stories = []
        for story_id in top_ids:
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json").json()
            stories.append({
                "title": item.get("title"),
                "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}")
            })
        return render_template("news.html", stories=stories)
    except Exception as e:
        flash(f"❌ Failed to load news: {e}")
        return redirect(url_for("main.home"))

#  Table list page
@main.route("/tables")
def list_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return render_template("tables.html", tables=tables)

#  Data table details page (paging + search)
@main.route("/data/<table_name>")
def show_table(table_name):
    page = int(request.args.get("page", 1))
    per_page = 20
    offset = (page - 1) * per_page
    search = request.args.get("search", "").strip()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if search:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row["name"] for row in cursor.fetchall()]
            conditions = " OR ".join([f"{col} LIKE ?" for col in columns])
            query = f"SELECT * FROM {table_name} WHERE {conditions} LIMIT ? OFFSET ?"
            args = [f"%{search}%"] * len(columns) + [per_page, offset]
            count_query = f"SELECT COUNT(*) FROM {table_name} WHERE {conditions}"
            count_args = [f"%{search}%"] * len(columns)
        else:
            query = f"SELECT * FROM {table_name} LIMIT ? OFFSET ?"
            args = [per_page, offset]
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            count_args = []

        cursor.execute(count_query, count_args)
        total_rows = cursor.fetchone()[0]
        total_pages = math.ceil(total_rows / per_page)

        cursor.execute(query, args)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

    except sqlite3.Error as e:
        flash(f"❌ Error loading table: {e}")
        return redirect(url_for("main.list_tables"))
    finally:
        conn.close()

    return render_template("data.html", table_name=table_name, rows=rows, columns=columns,
                           page=page, total_pages=total_pages, search=search)

#  Export to CSV file
@main.route("/export/<table_name>")
def export_csv(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row[col] for col in columns])

        output.seek(0)
        flash(f"✅ CSV for '{table_name}' exported successfully.")
        return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name=f"{table_name}.csv")
    except Exception as e:
        flash(f"❌ Failed to export CSV: {e}")
        return redirect(url_for("main.list_tables"))
    finally:
        conn.close()

#  Region card display page
@main.route("/areas")
def list_areas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT area_code, area_name FROM Area")
    areas = cursor.fetchall()
    conn.close()
    return render_template("areas.html", areas=areas)

#  Regional dual chart display page
@main.route("/area_chart/<area_code>")
def area_chart(area_code):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT area_name FROM Area WHERE area_code = ?", (area_code,))
        area = cursor.fetchone()
        area_name = area["area_name"] if area else area_code

        cursor.execute("""
            SELECT Y.year, 
                   A.housing_units, 
                   W.households_count
            FROM Year Y
            LEFT JOIN Affordable_Housing_Data A ON Y.year = A.year AND A.area_code = ?
            LEFT JOIN Waiting_List_Data W ON Y.year = W.year AND W.area_code = ?
            ORDER BY Y.year
        """, (area_code, area_code))
        rows = cursor.fetchall()

        years = [str(row["year"]) for row in rows]
        housing_units = [row["housing_units"] if row["housing_units"] is not None else 0 for row in rows]
        waiting_counts = [row["households_count"] if row["households_count"] is not None else 0 for row in rows]

        return render_template("chart_area_dual.html", area_code=area_code, area_name=area_name,
                               years=years, housing_units=housing_units, waiting_counts=waiting_counts)
    except sqlite3.Error as e:
        flash(f"❌ Error generating chart: {e}")
        return redirect(url_for("main.list_areas"))
    finally:
        conn.close()

#  Region details page (double table)
@main.route("/area_detail/<area_code>")
def area_detail(area_code):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT area_name FROM Area WHERE area_code = ?", (area_code,))
        area = cursor.fetchone()
        if not area:
            flash(f"❌ Area code '{area_code}' not found.")
            return redirect(url_for("main.list_areas"))

        cursor.execute("""
            SELECT year, housing_units
            FROM Affordable_Housing_Data
            WHERE area_code = ?
            ORDER BY year
        """, (area_code,))
        housing_data = cursor.fetchall()

        cursor.execute("""
            SELECT year, households_count
            FROM Waiting_List_Data
            WHERE area_code = ?
            ORDER BY year
        """, (area_code,))
        waiting_data = cursor.fetchall()

        return render_template("area_detail.html", area_code=area_code, area_name=area["area_name"],
                               housing_data=housing_data, waiting_data=waiting_data)
    except sqlite3.Error as e:
        flash(f"❌ Error loading area detail: {e}")
        return redirect(url_for("main.list_areas"))
    finally:
        conn.close()

#  Export multi-indicator data for a single region
@main.route("/export_area/<area_code>")
def export_area_csv(area_code):
    conn = get_connection()
    cursor = conn.cursor()

    # Query area name
    cursor.execute("SELECT area_name FROM Area WHERE area_code = ?", (area_code,))
    area = cursor.fetchone()
    area_name = area["area_name"] if area else area_code

    # Get related data
    cursor.execute("""
        SELECT Y.year, 
               A.housing_units, 
               W.households_count
        FROM Year Y
        LEFT JOIN Affordable_Housing_Data A ON Y.year = A.year AND A.area_code = ?
        LEFT JOIN Waiting_List_Data W ON Y.year = W.year AND W.area_code = ?
        ORDER BY Y.year
    """, (area_code, area_code))
    rows = cursor.fetchall()

    # Return 404 if no data
    if not rows:
        flash(f"❌ No data available to export for area code: {area_code}")
        return redirect(url_for("main.list_areas")), 404

    conn.close()

    # Build CSV content
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Year", "Housing Units", "Waiting List Households"])
    for row in rows:
        writer.writerow([
            row["year"],
            row["housing_units"] if row["housing_units"] is not None else "",
            row["households_count"] if row["households_count"] is not None else ""
        ])

    # Convert StringIO to BytesIO before sending
    output_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
    output_bytes.seek(0)

    # Send CSV response
    flash(f"✅ CSV for {area_name} exported successfully.")
    filename = f"{area_name.replace(' ', '_')}_data.csv"
    return send_file(output_bytes, mimetype="text/csv", download_name=filename, as_attachment=True)
#  404 error page
@main.app_errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404
