from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sandhu123"
ADMIN_PASS = "admin123"

def db():
    con = sqlite3.connect("/tmp/academy.db")

    con.row_factory = sqlite3.Row
    return con

def init():
    con = db()
    con.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, course TEXT, fee TEXT, attendance TEXT, performance TEXT, date TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS trials (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, course TEXT, date TEXT)")
    con.commit(); con.close()
init()

@app.route("/")
def home():
    con = db()
    students = con.execute("SELECT * FROM students").fetchall()
    con.close()
    return render_template("index.html", students=students)

@app.route("/trial", methods=["POST"])
def trial():
    con = db()
    con.execute("INSERT INTO trials (name, phone, course, date) VALUES (?,?,?,?)",
    (request.form["name"], request.form["phone"], request.form["course"], datetime.now().strftime("%d-%m-%Y %I:%M %p")))
    con.commit(); con.close()
    return "Trial Book Ho Gaya! Hum Rabta Karenge."

@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASS:
            session["admin"] = True
        else:
            return "Galat Password"
    if not session.get("admin"):
        return render_template("admin.html", login=True)
    con = db()
    students = con.execute("SELECT * FROM students").fetchall()
    trials = con.execute("SELECT * FROM trials").fetchall()
    con.close()
    return render_template("admin.html", login=False, students=students, trials=trials)

@app.route("/add", methods=["POST"])
def add():
    if not session.get("admin"): return redirect("/admin")
    con = db()
    con.execute("INSERT INTO students (name, phone, course, fee, attendance, performance, date) VALUES (?,?,?,?,?,?,?)",
    (request.form["name"], request.form["phone"], request.form["course"], request.form["fee"], "0%", "New", datetime.now().strftime("%d-%m-%Y %I:%M %p")))
    con.commit(); con.close()
    return redirect("/admin")

@app.route("/delete/<int:id>")
def delete(id):
    if not session.get("admin"): return redirect("/admin")
    con = db(); con.execute("DELETE FROM students WHERE id=?", (id,)); con.commit(); con.close()
    return redirect("/admin")

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    if not session.get("admin"): return redirect("/admin")
    con = db()
    con.execute("UPDATE students SET attendance=?, performance=? WHERE id=?", (request.form["attendance"], request.form["performance"], id))
    con.commit(); con.close()
    return redirect("/admin")

@app.route("/student/<int:id>")
def student(id):
    con = db()
    s = con.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    con.close()
    return render_template("dashboard.html", s=s)

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.form["msg"].lower()
    if "timetable" in msg or "time" in msg:
        ans = "Classes: Mon - Sat, 4pm - 8pm. Sunday Off hai."
    elif "chutti" in msg or "off" in msg:
        ans = "Sunday ko chutti hoti hai."
    elif "fee" in msg or "fees" in msg:
        ans = "Fee Rs.1000 / subject hai. JazzCash se pay kar sakte hain."
    elif "trial" in msg:
        ans = "2 Days Free Trial ke liye home page pe form bharein."
    else:
        ans = "Salam! Timetable, Fee, Chutti ya Trial ke bare me puchein."
    return ans

if __name__ == "__main__":
    app.run(debug=True)
