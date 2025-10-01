import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import sqlite3  

app = Flask(__name__)

DB_FILE = os.getenv("DB_PATH", "habits.db") 

_dir = os.path.dirname(DB_FILE)
if _dir:
    os.makedirs(_dir, exist_ok=True)

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)
def ensure_schema():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            frequency INTEGER NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS done (
            id INTEGER PRIMARY KEY,
            habit_id INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

ensure_schema()

def today_str() -> str:
    return date.today().isoformat()

def iso_week_key(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-{w:02d}"

def done_this_week_db(habit_id: int) -> int:
    """SQL ekvivalent tvog done_this_week: preuzmi datume iz baze i izbroj one iz tekuće nedelje."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT date FROM done WHERE habit_id = ?", (habit_id,))
    rows = cur.fetchall()
    conn.close()

    wk = iso_week_key(date.today())
    # rows je lista tuple-ova [( 'YYYY-MM-DD', ), ...]
    return sum(1 for (ds,) in rows if iso_week_key(date.fromisoformat(ds)) == wk)

def today_done_db(habit_id: int) -> bool:
    """Da li za ovu naviku postoji zapis za današnji dan u tabeli done?"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM done WHERE habit_id = ? AND date = ? LIMIT 1", (habit_id, today_str()))
    row = cur.fetchone()
    conn.close()
    return row is not None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # ISTO kao ranije, ali INSERT u bazu umesto u dict
        name = request.form.get("name", "").strip()
        freq = request.form.get("frequency", "").strip()
        if name and freq.isdigit() and int(freq) > 0:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("INSERT INTO habits (name, frequency) VALUES (?, ?)", (name, int(freq)))
            conn.commit()
            conn.close()
        return redirect(url_for("index"))

    # GET: učitaj sve navike i pripremi view-model kao i ranije
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, frequency FROM habits ORDER BY id")
    all_habits = cur.fetchall()
    conn.close()

    vm = []
    for hid, name, freq in all_habits:
        vm.append({
            "id": hid,
            "name": name,
            "frequency": freq,
            "count_week": done_this_week_db(hid),  # broj za tekuću nedelju
            "today_done": today_done_db(hid),      # da li je danas urađeno
        })
    return render_template("index.html", habits=vm)

@app.route("/toggle/<int:hid>", methods=["POST"])
def toggle(hid: int):
    """Ponaša se isto kao pre: klik menja stanje 'danas urađeno'."""
    t = today_str()
    conn = get_conn()
    cur = conn.cursor()

    # Ako današnji zapis postoji -> obriši; ako ne postoji -> dodaj
    cur.execute("SELECT id FROM done WHERE habit_id = ? AND date = ? LIMIT 1", (hid, t))
    row = cur.fetchone()
    if row:
        cur.execute("DELETE FROM done WHERE id = ?", (row[0],))
    else:
        cur.execute("INSERT INTO done (habit_id, date) VALUES (?, ?)", (hid, t))

    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:hid>", methods=["POST"])
def delete(hid: int):
    """Isto ponašanje kao ranije, samo brisanje iz baze."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM done   WHERE habit_id = ?", (hid,))
    cur.execute("DELETE FROM habits WHERE id = ?", (hid,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(debug=True)
