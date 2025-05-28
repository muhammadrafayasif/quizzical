from flask import Flask, request, render_template, redirect, make_response, render_template_string, url_for
import sqlite3, json, datetime, random
def get_time(a):
    return datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y")
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.filters["date"] = get_time


@app.route("/", methods=["GET", "POST"])
def index():
    questions=[{'question':'', 'optionA':'', 'optionB':'', 'optionC':'', 'optionD':'', 'answer': ''}]

    DBASE = sqlite3.connect("quizzical.db")
    db = DBASE.cursor()
    quizzes=db.execute("SELECT DISTINCT quiz_id, name FROM quizzes ORDER BY quiz_id DESC LIMIT 20;").fetchall()

    res = make_response(render_template("home.html", quizzes=quizzes, submitted=request.form.get("submitted"), error=request.form.get("error")))
    res.set_cookie("questions", json.dumps(questions), samesite="Lax", secure="True")
    
    DBASE.close()
    return res

@app.route("/add_new", methods=["POST"])
def add_new():
    questions=request.get_json()
    questions.append({'question':'', 'optionA':'', 'optionB':'', 'optionC':'', 'optionD':'', 'answer': ''})
    res = make_response(redirect("make_a_quiz"))
    res.set_cookie("questions", json.dumps(questions), samesite="Lax", secure="True")
    return res

@app.route("/make_a_quiz", methods=["GET"])
def make_a_quiz():
    if not request.cookies.get("questions"): return redirect("/")
    questions=json.loads(request.cookies.get("questions"))
    DBASE = sqlite3.connect("quizzical.db")
    db = DBASE.cursor()
    latest_id = db.execute("SELECT quiz_id FROM quizzes ORDER BY quiz_id DESC;").fetchone()
    if not latest_id: latest_id = 0 
    else: latest_id = latest_id[0]
    _id = int(latest_id) + 1
    DBASE.close()
    return render_template("make_a_quiz.html", questions=questions)

@app.route("/quiz", methods=["GET"])
def take_a_quiz():
    try:
        DBASE = sqlite3.connect("quizzical.db")
        DBASE.row_factory = sqlite3.Row
        db = DBASE.cursor()

        id = request.args.get("id")
        if (int(id)>int(db.execute("SELECT COUNT(DISTINCT quiz_id) FROM quizzes;").fetchone()[0])):
            return redirect("/")

        res = db.execute("SELECT * from quizzes WHERE quiz_id=?", (id)).fetchall()

        DBASE.close()
        return render_template("quiz.html", questions=res, name=res[0]['name'], quiz_id=res[0]['quiz_id'], show_answers=False, score="")
    except:
        return redirect("/")

@app.route("/random", methods=["GET"])
def get_random_quiz():
    DBASE = sqlite3.connect("quizzical.db")
    db = DBASE.cursor()
    quizzes = db.execute("SELECT DISTINCT quiz_id FROM quizzes").fetchall()
    if not quizzes: 
        return render_template_string(f"""
        <html>
        <body>
            <form id="post-form" method="POST" action="/">
                <input type="hidden" name="error" value="Can't find a quiz =(">
            </form>
            <script>
                window.onload = function() {{
                    document.getElementById('post-form').submit();
                }}
            </script>
        </body>
        </html>
    """)
    DBASE.close()
    return redirect(f"/quiz?id={random.choice(quizzes)[0]}")

@app.route("/submit", methods=["POST"])
def submit():
    DBASE = sqlite3.connect("quizzical.db")
    DBASE.row_factory = sqlite3.Row
    db = DBASE.cursor()
    id = request.form.get("id")
    score = 0
    percentages = list()
    answers=db.execute("SELECT answer FROM quizzes WHERE quiz_id=?", (id)).fetchall()
    user_answers=list()
    res = db.execute("SELECT * from quizzes WHERE quiz_id=?", (id)).fetchall()

    for i in range(1, len(answers)+1):
        
        if db.execute("SELECT COUNT(*) FROM answers WHERE quiz_id=? AND q_no=?", (id, i)).fetchone()[0]>0:
            db.execute(
                f"UPDATE answers SET option{request.form.get(f'answer_{i}')}=option{request.form.get(f'answer_{i}')}+1 WHERE quiz_id=? AND q_no=?", 
                (id, i)
            )
        else:
            db.execute(
                f"INSERT INTO answers(quiz_id, q_no, option{request.form.get(f'answer_{i}')}) VALUES(?, ?, ?)", (id, i, 1)
            )
        
        percentages.append(int(db.execute(f"SELECT option{request.form.get(f'answer_{i}')} FROM answers WHERE quiz_id=? AND q_no=?", (id, i)).fetchone()[0]))
        user_answers.append(request.form.get(f"answer_{i}"))
        if request.form.get(f"answer_{i}") == answers[i-1][0]: score+=1

    DBASE.commit()
    DBASE.close()
    return render_template("quiz.html", user_answers=user_answers, percentages=percentages, questions=res, name=res[0]['name'], quiz_id=res[0]['quiz_id'], show_answers=True, score=str(round((score/len(answers))*100, 2))+'%')

@app.route("/save", methods=["POST"])
def save():
    DBASE = sqlite3.connect("quizzical.db", 1)
    db = DBASE.cursor()

    id = int(db.execute("SELECT COUNT(DISTINCT quiz_id) from quizzes;").fetchone()[0])
    for j,i in enumerate(range((len(request.form)-1) // 6)):
        db.execute("INSERT INTO quizzes(quiz_id, question, q_no, optionA, optionB, optionC, optionD, answer, name) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", 
            (
                id+1,
                request.form[f'question_{i+1}'],
                j+1,
                request.form[f'A_{i+1}'],
                request.form[f'B_{i+1}'],
                request.form[f'C_{i+1}'],
                request.form[f'D_{i+1}'],
                request.form[f'answer_{i+1}'],
                request.form['name']
            )
        )
    DBASE.commit()
    DBASE.close()
    return render_template_string(f"""
        <html>
            <body>
                <form id="post_form" method="POST" action="{{{{ url_for('index') }}}}">
                    <input type="hidden" name="submitted" value="{id+1}">
                </form>
                <script type="text/javascript">
                    document.getElementById('post_form').submit();
                </script>
            </body>
        </html>
    """)

if __name__ == '__main__':
    app.run()