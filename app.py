from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import requests
import re
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from io import BytesIO
from docx import Document
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("PRAGMA journal_model=WAL")

    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT UNIQUE,
            password TEXT,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT,
            last_login TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            language TEXT,
            question TEXT,
            code TEXT,
            explanation TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS activity(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            login_time TEXT,
            logout_time TEXT,
            status TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            code TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HELPER ----------------

def get_conn():
    conn = sqlite3.connect("users.db",timeout=10,check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- START ----------------

@app.route("/")
def start():
    return render_template("select_login.html")

# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))

        conn = get_conn()
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO users (username,email,password,created_at) VALUES (?,?,?,?)",
                (username,email,password,datetime.now())
            )
            conn.commit()
        except Exception as e:
            conn.close()
            return f"Error: {e}"

        conn.close()
        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("username")
        password = request.form.get("password")

        conn = get_conn()
        c = conn.cursor()

        try:
            c.execute("SELECT * FROM users WHERE email=?", (email,))
            user = c.fetchone()

            if user and check_password_hash(user["password"], password):

                session["username"] = user["username"]
                session["is_admin"] = user["is_admin"]

                login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                c.execute(
                    "INSERT INTO activity (username,login_time,status) VALUES (?,?,?)",
                    (user["username"], login_time, "active")
                )

                conn.commit()

                if user["is_admin"]:
                    return redirect("/admin_dashboard")
                else:
                    return redirect("/home")

        except Exception as e:
            return f"DB Error: {e}"

        finally:
            conn.close()   # ✅ ALWAYS CLOSE

        return "Invalid username or password"

    return render_template("login.html")
# ---------------- ADMIN REGISTER ----------------

@app.route("/admin_register", methods=["GET","POST"])
def admin_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))

        conn = get_conn()
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO users (username,email,password,is_admin,created_at) VALUES (?,?,?,?,?)",
                (username, username+"@admin.com", password, 1, datetime.now())
            )
            conn.commit()

        except Exception as e:
            conn.close()
            return f"Error: {e}"

        conn.close()
        return redirect("/admin_login")

    return render_template("admin_register.html")

# ---------------- ADMIN LOGIN ----------------

@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_conn()
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND is_admin=1", (username,))
        admin = c.fetchone()

        if admin and check_password_hash(admin["password"], password):
            session["username"] = admin["username"]
            session["is_admin"] = 1
            return redirect("/admin_dashboard")

        return "Invalid Admin Credentials"

    return render_template("admin_login.html")

# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin_dashboard")
def admin_dashboard():
    if "username" not in session or not session.get("is_admin"):
        return redirect("/login")

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) as total_users FROM users")
    total_users = c.fetchone()["total_users"]

    # Active users
    c.execute("SELECT COUNT(*) as active FROM activity WHERE status='active'")
    active_users = c.fetchone()["active"]

    # New users today
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) as new_users FROM users WHERE created_at LIKE ?", (f"{today}%",))
    new_users = c.fetchone()["new_users"]

    c.execute("SELECT COUNT(*) as total_codes FROM history")
    total_codes = c.fetchone()["total_codes"]

    c.execute("SELECT language, COUNT(*) as cnt FROM history GROUP BY language")
    codes_by_lang = [{"language": r["language"], "cnt": r["cnt"]} for r in c.fetchall()]

    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) as logins_today FROM activity WHERE login_time LIKE ?", (f"{today}%",))
    logins_today = c.fetchone()["logins_today"]

    c.execute("SELECT DATE(login_time) as day, COUNT(*) as cnt FROM activity GROUP BY day")
    daily_logins = [{"day": r["day"], "cnt": r["cnt"]} for r in c.fetchall()]

    c.execute("SELECT DATE(created_at) as day, COUNT(*) as cnt FROM history GROUP BY day")
    codes_daily = [{"day": r["day"], "cnt": r["cnt"]} for r in c.fetchall()]

    c.execute("SELECT strftime('%W', created_at) as week, COUNT(*) as cnt FROM users GROUP BY week")
    registrations_week = [{"week": r["week"], "cnt": r["cnt"]} for r in c.fetchall()]

    conn.close()

    return render_template("admin_dashboard.html",
        total_users=total_users,
        total_codes=total_codes,
        codes_by_lang=codes_by_lang,
        logins_today=logins_today,
        daily_logins=daily_logins,
        codes_daily=codes_daily,
        registrations_week=registrations_week,
        active_users=active_users,
        new_users=new_users
    )

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    if "username" in session:
        conn = get_conn()
        c = conn.cursor()

        logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute(
            "UPDATE activity SET logout_time=?,status=? WHERE username=? AND logout_time IS NULL",
            (logout_time,"inactive",session["username"])
        )

        conn.commit()
        conn.close()

        session.clear()

    return redirect("/")

# ---------------- HOME ----------------

@app.route("/home", methods=["GET","POST"])
def home():
    generated_code = ""
    if "username" not in session or session.get("is_admin"):
        return redirect("/login")

    code_output = ""
    explanation_output = ""
    selected_language = "python"

    if request.method == "POST":
        language = request.form["language"]
        question = request.form["question"]

        selected_language = language  # ✅ keep selected language

        prompt = f"""
Generate a correct {language} program for:

{question}

STRICT FORMAT:
1. First give ONLY code
2. Then write EXACTLY 'EXPLANATION:'
3. Then explain clearly step by step
4. Also include a small example

EXPLANATION:
"""

        import os
        from dotenv import load_dotenv
        import requests

        load_dotenv()

        api_key = os.getenv("OPENROUTER_API_KEY").strip()

        print("RAW KEY:", api_key)  # debug

        try:
            response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json",
                "HTTP-Referer": "http://127.0.0.1:5000",   # VERY IMPORTANT
                "X-Title": "CodeGenie AI",                 # VERY IMPORTANT
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text)

            result = response.json()
            generated_code = result["choices"][0]["message"]["content"]

        except Exception as e:
            print("ERROR:", e)
            # ✅ DEBUG (VERY IMPORTANT)
            print("FULL API RESPONSE:", result)
            
            #safe check---
            if "choices" not in result:
                raise Exception(result)
            raw = result["choices"][0]["message"]["content"]

            print("RAW OUTPUT:,raw")

            # ✅ SAFE PARSING (fix explanation missing issue)
            if "EXPLANATION:" in raw:
                parts = raw.split("EXPLANATION:")
                code_output = parts[0].strip()
                explanation_output = parts[1].strip()
            else:
                code_output = raw.strip()
                explanation_output = "Explanation not available."

        except Exception as e:
            print("ERROR:", e)
            code_output = ""
            explanation_output = "Check API key or internet connection."

        # ✅ SAVE HISTORY (FIXED - no error data stored)
        try:
            if code_output and len(code_output.strip()) > 20:

                conn = get_conn()
                c = conn.cursor()

                c.execute(
                    "INSERT INTO history (username,language,question,code,explanation,created_at) VALUES (?,?,?,?,?,?)",
                    (
                        session["username"],
                        language,
                        question,
                        code_output,
                        explanation_output,
                        datetime.now()
                    )
                )

                conn.commit()
                conn.close()

                print("Saved to history:", question)

            else:
                print("Skipped saving (invalid or small response)")

        except Exception as e:
            print("History Save Error:", e)

    return render_template("home.html",
        username=session["username"],
        code_output=generated_code,
        explanation_output=explanation_output,
        selected_language=selected_language
    )

# ---------------- SAVE CODE ----------------

@app.route("/save_code", methods=["POST"])
def save_code():
    code = request.form.get("code")
    filename = request.form.get("filename")
    filetype = request.form.get("filetype")

    if filetype == "txt":
        return send_file(BytesIO(code.encode()), download_name=filename+".txt", as_attachment=True)

    elif filetype == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in code.split("\n"):
            pdf.cell(0,8,txt=line,ln=True)
        return send_file(BytesIO(pdf.output(dest='S').encode('latin-1')),
                         download_name=filename+".pdf", as_attachment=True)

    elif filetype == "docx":
        doc = Document()
        doc.add_paragraph(code)
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return send_file(file_stream, download_name=filename+".docx", as_attachment=True)

    return "Invalid file type"

#history app route-------------------------

@app.route("/history")
def history():

    if "username" not in session:
        return redirect("/login")

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT language,question,code,explanation,created_at
    FROM history
    WHERE username=?
    ORDER BY id DESC
    """,(session["username"],))

    rows = c.fetchall()

    # 🔥 CONVERT TO NORMAL LIST (VERY IMPORTANT)
    records = [dict(row) for row in rows]

    print("Fetched records:", records)   # DEBUG

    conn.close()

    return render_template("history.html", records=records)


#profile route---------------------------

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect("/login")

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?", (session["username"],))
    user = c.fetchone()

    c.execute("SELECT COUNT(*) as total FROM history WHERE username=?", (session["username"],))
    total_prompts = c.fetchone()["total"]

    c.execute("SELECT * FROM activity WHERE username=? ORDER BY login_time DESC LIMIT 1",(session["username"],))
    activity = c.fetchone()

    conn.close()

    return render_template("profile.html",
        user=user,
        total_prompts=total_prompts,
        activity=activity
    )


#feedback route-----------------

@app.route("/feedback", methods=["GET","POST"])
def feedback():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        message = request.form.get("message")
        rating = request.form.get("rating") or "No Rating"

        full_msg = rating = request.form.get("rating") or "No Rating"
        message = request.form.get("message") or ""

        full_message = message + " | Rating: " + rating

        (full_message, datetime.now())

        conn = get_conn()
        c = conn.cursor()

        c.execute(
            "INSERT INTO feedback (username,message,created_at) VALUES (?,?,?)",
            (session["username"], full_msg, datetime.now())
        )

        conn.commit()
        conn.close()

        return redirect("/home")

    return render_template("feedback.html")

#bookmark-----------------------

@app.route("/bookmark", methods=["POST"])
def bookmark():
    if "username" not in session:
        return "Not logged in"

    data = request.get_json()
    code = data.get("code")

    conn = get_conn()
    c = conn.cursor()

    c.execute(
        "INSERT INTO bookmarks (username,code,created_at) VALUES (?,?,?)",
        (session["username"], code, datetime.now())
    )

    conn.commit()
    conn.close()

    return "Saved"

#view bookmarks------------------------------


@app.route("/bookmarks")
def bookmarks():
    if "username" not in session:
        return redirect("/login")

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM bookmarks WHERE username=? ORDER BY id DESC",(session["username"],))
    rows = c.fetchall()

    records = [dict(r) for r in rows]

    conn.close()

    return render_template("bookmarks.html", records=records)


#bookmarks viewed in admin dashboard--------------------------

@app.route("/admin_feedback")
def admin_feedback():
    if "username" not in session or not session.get("is_admin"):
        return redirect("/login")

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM feedback ORDER BY id DESC")
    rows = c.fetchall()

    records = [dict(r) for r in rows]

    conn.close()

    return render_template("admin_feedback.html", records=records)

#analytics------------------
@app.route("/analytics")
def analytics():
    if "username" not in session or not session.get("is_admin"):
        return redirect("/login")

    conn = get_conn()
    c = conn.cursor()

    # get language stats
    c.execute("SELECT language, COUNT(*) as cnt FROM history GROUP BY language")
    rows = c.fetchall()

    data = [dict(r) for r in rows]

    # get top language safely
    if data:
        top_lang = max(data, key=lambda x: x["cnt"])
    else:
        top_lang = None

    conn.close()

    return render_template("analytics.html", data=data, top_lang=top_lang)

#user history--------------------------

@app.route("/user_history")
def user_history():
    if "username" not in session or not session.get("is_admin"):
        return redirect("/login")

    conn = get_conn()
    c = conn.cursor()

    search_user = request.args.get("user")

    if search_user:
        c.execute("SELECT * FROM history WHERE username LIKE ? ORDER BY id DESC", (f"%{search_user}%",))
    else:
        c.execute("SELECT * FROM history ORDER BY id DESC")

    rows = c.fetchall()

    # ✅ IMPORTANT FIX
    records = []
    for r in rows:
        records.append({
            "username": r["username"],
            "question": r["question"],
            "code": r["code"]
        })

    conn.close()

    print("Fetched records:", len(records))  # DEBUG

    return render_template("user_history.html", records=records)

#login tracking-----------------------

@app.route("/login_tracking")
def login_tracking():
    if "username" not in session or not session.get("is_admin"):
        return redirect("/login")

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM activity ORDER BY id DESC")
    rows = c.fetchall()

    records = [dict(r) for r in rows]   # ✅ IMPORTANT

    # calculate session duration
    from datetime import datetime

    for r in records:
        if r["logout_time"]:
            login = datetime.strptime(r["login_time"], "%Y-%m-%d %H:%M:%S")
            logout = datetime.strptime(r["logout_time"], "%Y-%m-%d %H:%M:%S")
            r["duration"] = str(logout - login)
        else:
            r["duration"] = "Active"

    conn.close()

    return render_template("login_tracking.html", records=records)

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)