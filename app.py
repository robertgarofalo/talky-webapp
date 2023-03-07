from flask import Flask, flash, redirect, render_template, request, session, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from helpers import login_required


app = Flask(__name__)

# # Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Global template variables
@app.context_processor
def inject_username():
    username = session.get("username")
    print(username)
    return dict(user=username)

# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///talky.db")

# Dashboard
@app.route("/")
@login_required
def index():
    """Show dashboard"""
    username = session.get("username")
    is_admin = session.get("is_admin")

    # results = db.execute("SELECT COUNT(username) AS total_users FROM users")
    totals = db.execute("SELECT (SELECT COUNT(id) FROM users) AS total_users, (SELECT COUNT(id) FROM categories) AS total_categories, (SELECT COUNT(id) FROM conjugated_verbs) AS total_conjugated_verbs, (SELECT COUNT(id) FROM phrases) AS total_phrases, (SELECT COUNT(id) FROM verbs) AS total_verbs, (SELECT COUNT(id) FROM words) AS total_words FROM users LIMIT 1")

    #check if user is an admin
    if is_admin == 1:
        return render_template("admin.html", username=username, totals=totals)
    else:
        return render_template("dashboard.html", username=username)

#ADMIN
# CATEGORIES -----
# View categories
@app.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    """Show categories"""
    word_categories = []
    phrase_categories = []
    try:
        all_categories = db.execute(
            "SELECT * FROM categories ORDER BY category_type DESC, category_name ASC")
        word_categories = db.execute(
            "SELECT * FROM categories WHERE category_type = 'Words'")
        phrase_categories = db.execute(
            "SELECT * FROM categories WHERE category_type = 'Phrases'")
    except:
        return render_template("error.html", error="Error!")

    if request.method == "GET":
        return render_template("categories.html", categories=all_categories)

    if request.method == "POST":
        category_type = request.form.get("category-type")
        if category_type == "Phrases":
            return render_template("categories.html", categories=phrase_categories, category_type=category_type)
        elif category_type == "Words":
            return render_template("categories.html", categories=word_categories, category_type=category_type)
        else:
            return render_template("categories.html", categories=all_categories, category_type=category_type)

# Add category
@app.route("/add-category", methods=["GET", "POST"])
@login_required
def add_category():
    if request.method == "POST":
        category_name = request.form.get("category-name")
        category_type = request.form.get("category-type")
        print('cat name - ', category_name)
        print('cat type - ', category_type)

        # Check if category exists
        result = db.execute(
            "SELECT category_name FROM categories WHERE category_name = ? AND category_type = ?", category_name, category_type)

        if result:
            return render_template("error.html", error="Category name already exists!")

        db.execute("INSERT INTO categories (category_type, category_name) VALUES (?, ?)",
                   category_type, category_name)
        return redirect("/categories")

    return render_template("add-category.html")

# Edit  category
@app.route("/edit-category/<string:id>", methods=["GET", "POST"])
@login_required
def edit_category(id):

    if request.method == "GET":
        category = db.execute("SELECT * FROM categories WHERE id = ?", id)

        return render_template("edit-category.html", category=category)

    if request.method == "POST":
        category_name = request.form.get("category-name")
        category_type = request.form.get("category-type")

        db.execute("UPDATE categories SET category_type = ?, category_name = ?, date = ? WHERE id = ?",
                   category_type, category_name, datetime.datetime.now(), id)

        flash('Category Updated')

        return redirect('/categories')

# Delete Categories
@app.route("/categories/delete/<string:id>", methods=["POST"])
@login_required
def delete_category(id):
    if request.method == "POST":

        db.execute("DELETE FROM categories WHERE id = ?", id)
        return redirect('/categories')

# WORDS
# View words
@app.route("/words", methods=["GET", "POST"])
@login_required
def words():
    """Show words"""
    categories = db.execute(
        "SELECT * FROM categories WHERE category_type='Words'")
    words = db.execute(
        "SELECT * FROM words ORDER BY category_name ASC, word ASC")

    if request.method == "GET":
        return render_template("words.html", words=words, categories=categories)

    if request.method == "POST":
        selected = request.form.get("category-name")

        if selected == "All":
            return redirect('/words')

        result = db.execute(
            "SELECT * FROM words WHERE category_name = ?", selected)
        print('SELECTED - ', selected)
        print('RESULT - ', result)
        # return redirect('/words')
        return render_template("words.html", categories=categories, words=result, selected=selected)


# Add word
@app.route("/add-word", methods=["GET", "POST"])
@login_required
def add_word():
    if request.method == "GET":
        # Get categories
        categories = db.execute(
            "SELECT category_name FROM categories WHERE category_type = 'Words' ORDER BY category_name ASC")

        return render_template("add-word.html", categories=categories)

    if request.method == "POST":
        word = request.form.get("word-name")
        translation = request.form.get("word-translation")
        category_name = request.form.get("category-name")

        # Check if word exists
        result = db.execute(
            "SELECT word FROM words WHERE word = ? OR translation = ?", word, translation)

        if result:
            return render_template("error.html", error="Word already exists!")

        db.execute("INSERT INTO words (category_type, category_name, word, translation) VALUES (?, ?, ?, ?)",
                   "Words", category_name, word, translation)
        return redirect("/words")

    return render_template("add-word.html")

# Edit word
@app.route("/edit-word/<string:id>", methods=["GET", "POST"])
@login_required
def edit_word(id):
    categories = db.execute(
        "SELECT category_name FROM categories WHERE category_type = 'Words' ORDER BY category_name ASC")

    if request.method == "GET":
        result = db.execute("SELECT * FROM words WHERE id = ?", id)
        return render_template("edit-word.html", result=result, categories=categories)

    if request.method == "POST":
        word = request.form.get("word")
        translation = request.form.get("translation")
        category_name = request.form.get("category-name")

        print("RESULTS - ", word, translation, category_name)

        db.execute("UPDATE words SET category_name = ?, word = ?, translation = ?, date = ? WHERE id = ?",
                   category_name, word, translation, datetime.datetime.now(), id)

        flash('Word Updated')

        return redirect('/words')

# Delete Word
@app.route("/words/delete/<string:id>", methods=["POST"])
@login_required
def delete_word(id):
    if request.method == "POST":

        db.execute("DELETE FROM words WHERE id = ?", id)
        return redirect('/words')

# PHRASES -------
# View phrases
@app.route("/phrases", methods=["GET", "POST"])
@login_required
def phrases():
    """Show phrases"""
    categories = db.execute(
        "SELECT * FROM categories WHERE category_type='Phrases'")
    phrases = db.execute(
        "SELECT * FROM phrases ORDER BY category_name ASC, phrase ASC")

    if request.method == "GET":
        return render_template("phrases.html", phrases=phrases, categories=categories)

    if request.method == "POST":
        selected = request.form.get("category-name")

        if selected == "All":
            return redirect('/phrases')

        result = db.execute(
            "SELECT * FROM phrases WHERE category_name = ?", selected)
        print('SELECTED - ', selected)
        print('RESULT - ', result)

        return render_template("phrases.html", categories=categories, phrases=result, selected=selected)

# Add phrase
@app.route("/add-phrase", methods=["GET", "POST"])
@login_required
def add_phrase():
    if request.method == "GET":
        # Get categories
        categories = db.execute(
            "SELECT category_name FROM categories WHERE category_type = 'Phrases' ORDER BY category_name ASC")

        return render_template("add-phrase.html", categories=categories)

    if request.method == "POST":
        phrase = request.form.get("phrase-name")
        translation = request.form.get("phrase-translation")
        category_name = request.form.get("category-name")

        # Check if word exists
        result = db.execute(
            "SELECT phrase FROM phrases WHERE phrase = ? OR translation = ?", phrase, translation)

        if result:
            return render_template("error.html", error="Phrase already exists!")

        db.execute("INSERT INTO phrases (category_type, category_name, phrase, translation) VALUES (?, ?, ?, ?)",
                   "Phrases", category_name, phrase, translation)
        return redirect("/phrases")

    return render_template("add-phrase.html")

# Edit phrase
@app.route("/edit-phrase/<string:id>", methods=["GET", "POST"])
@login_required
def edit_phrase(id):
    categories = db.execute(
        "SELECT category_name FROM categories WHERE category_type = 'Phrases' ORDER BY category_name ASC")

    if request.method == "GET":
        result = db.execute("SELECT * FROM phrases WHERE id = ?", id)
        return render_template("edit-phrase.html", result=result, categories=categories)

    if request.method == "POST":
        phrase = request.form.get("phrase")
        translation = request.form.get("translation")
        category_name = request.form.get("category-name")

        db.execute("UPDATE phrases SET category_name = ?, phrase = ?, translation = ?, date = ? WHERE id = ?",
                   category_name, phrase, translation, datetime.datetime.now(), id)

        flash('Phrase Updated')

        return redirect('/phrases')

# Delete Phrase
@app.route("/phrases/delete/<string:id>", methods=["POST"])
@login_required
def delete_phrase(id):
    if request.method == "POST":

        db.execute("DELETE FROM phrases WHERE id = ?", id)
        return redirect('/phrases')

# VERBS -------
# INFINITIVE
# View INFINITIVE verbs


@app.route("/verbs", methods=["GET", "POST"])
@login_required
def verbs():
    """Show verbs"""
    # return render_template("verbs.html")

    # categories = db.execute("SELECT * FROM categories WHERE category_type='Phrases'")
    verbs = db.execute("SELECT * FROM verbs ORDER BY eng_verb_name ASC")

    if request.method == "GET":
        return render_template("verbs.html", verbs=verbs)

# Add verb
@app.route("/add-verb", methods=["GET", "POST"])
@login_required
def add_verb():

    if request.method == "POST":
        eng_verb_name = request.form.get("verb-name")
        translation = request.form.get("verb-translation")

        # Check if word exists
        result = db.execute(
            "SELECT eng_verb_name FROM verbs WHERE eng_verb_name = ? OR translation = ?", eng_verb_name, translation)

        if result:
            return render_template("error.html", error="Verb already exists!")

        # Insert new verb into verb table
        db.execute("INSERT INTO verbs (eng_verb_name, translation) VALUES (?, ?)",
                   eng_verb_name, translation)

        #create empty rows for new verb in the verb_conjugations table
        result = db.execute("SELECT id FROM verbs WHERE translation = ?", translation)
        verb_id = result[0]["id"]
        for n in range(1, 7):
            db.execute("INSERT INTO conjugated_verbs(verb_id, conjugation_position) VALUES (?, ?)", verb_id, n)

        return redirect("/verbs")

    return render_template("add-verb.html")

# Edit verb
@app.route("/edit-verb/<string:translation>", methods=["GET", "POST"])
@login_required
def edit_verb(translation):

    if request.method == "GET":
        result = db.execute("SELECT * FROM verbs WHERE translation = ?", translation)
        return render_template("edit-verb.html", result=result, translation=result[0]["translation"])

    if request.method == "POST":
        verb = request.form.get("eng-verb")
        verb_translation = request.form.get("translation")

        db.execute("UPDATE verbs SET eng_verb_name = ?, translation = ?, date = ? WHERE translation = ?",
                   verb, verb_translation, datetime.datetime.now(), translation)

        flash('Verb Updated')

        return redirect(url_for('verbs'))

# Delete Verb

@app.route("/verbs/delete/<string:translation>", methods=["POST"])
@login_required
def delete_verb(translation):
    if request.method == "POST":

        db.execute("DELETE FROM verbs WHERE translation = ?", translation)
        return redirect('/verbs')

# VERBS
# CONJUGATED
# View CONJUGATED verbs
@app.route("/verb-conjugated/<string:translation>", methods=["GET", "POST"])
@login_required
def verb_conjugated(translation):
    """Show conjugated verbs"""
    results = db.execute("SELECT * FROM conjugated_verbs JOIN verbs ON verb_id = verbs.id WHERE translation = ? ORDER BY conjugation_position ASC", translation)
    verb_details = db.execute("SELECT eng_verb_name, translation AS infinitive_verb FROM verbs WHERE translation = ?", translation)

    if request.method == "GET":

        return render_template("verb-conjugated.html", results=results, verb_details=verb_details)

# Edit CONJUGATED verb
@app.route("/edit-conjugations/<string:translation>", methods=["GET", "POST"])
@login_required
def edit_conjugations(translation):

    if request.method == "GET":
        results = db.execute(
            "SELECT * FROM conjugated_verbs JOIN verbs ON verb_id = verbs.id WHERE translation = ? ORDER BY conjugation_position ASC", translation)
        verb_details = db.execute(
            "SELECT eng_verb_name, translation AS infinitive_verb FROM verbs WHERE translation = ?", translation)

        return render_template('edit-conjugations.html', results=results, verb_details=verb_details)

    if request.method == "POST":
        my_dict = {}

        # Get infinitive verb id
        result = db.execute("SELECT id FROM verbs WHERE translation = ?", translation)
        verb_id = result[0]["id"]

        # Check if data exists in conjugated_verbs table
        verb_conjugation_data = db.execute("SELECT verb_id FROM conjugated_verbs JOIN verbs ON verbs.id = verb_id WHERE translation = ?", translation )
        # print(verb_conjugation_data)

        verb_tenses = ["indicative_presente", "indicative_imperfetto", "indicative_passato_remoto",
                       "indicative_futuro_semplice", "indicative_passato_prossimo", "indicative_trapassato_prossimo",
                       "indicative_trapassato_remoto", "indicative_futuro_anteriore", "congiuntivo_presente",
                        "congiuntivo_passato", "congiuntivo_imperfetto", "congiuntivo_trapassato",
                        "condizionale_presente", "condizionale_passato", "imperative_presente", "gerundio_presente", "gerundio_passato"]

        insert_or_update_verb_conjugations(verb_tenses, my_dict, verb_conjugation_data, verb_id)

        flash('Verbs Updated')

        return redirect(url_for("verb_conjugated", translation=translation))

# Get user info
@app.route("/users")
@login_required
def total_users():
    """ Show table of registered users"""
    user_info = db.execute("SELECT username, STRFTIME('%d/%m/%Y, %H:%M', date) AS registered, is_admin FROM users")
    return render_template("users.html", user_info=user_info)

# USER FRONT END

# QUIZZES ---------------------
# Words quiz
@app.route("/words-quiz")
@login_required
def words_quiz():
    """ Show word quiz"""
    # data = {"title": "hello world"}
    data = db.execute("SELECT * FROM words")
    return render_template("words-quiz.html", data=data)

# Phrases quiz
@app.route("/phrases-quiz")
@login_required
def phrases_quiz():
    """ Show phrases quiz"""
    data = db.execute("SELECT * FROM phrases")
    return render_template("phrases-quiz.html", data=data)

@app.route("/verbs-quiz")
def verbs_quiz():
    """ Show verbs quiz"""
    data = db.execute("SELECT * FROM verbs")
    return render_template("verbs-quiz.html", data=data)


# AUTHENTICATION ----
# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        session.clear()
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return render_template("error.html", error="Error! Missing one or more fields")

        if not password == confirmation:
            return render_template("error.html", error="Error! Passwords do not match")

        # Insert into db
        try:
            db.execute("INSERT INTO users (username, hash, date) VALUES (?, ?, ?)",
                       username, generate_password_hash(password), datetime.datetime.now())
            rows = db.execute("SELECT id, username, is_admin FROM users WHERE username = ?", username)

            session["user_id"] = rows[0]["id"]
            session["username"] = rows[0]["username"]
            session["is_admin"] = rows[0]["is_admin"]

            return redirect(url_for('index'))
        except:
            return render_template("error.html", error="Something went wrong")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", error="No username submitted")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", error="No password submitted")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("error.html", error="username or password error")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        session["is_admin"] = rows[0]["is_admin"]

        #Redirect home
        return redirect(url_for("index"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# FUNCTIONS --------

# Insert or update verb conjugations
def insert_or_update_verb_conjugations(verb_tenses, my_dict, verb_conjugation_data, verb_id):
    for item in verb_tenses:
        for n in range(1, 7):
            my_dict["{0}_{1}".format(item, n)] = request.form.get("{0}_{1}".format(item, n))

    n = 1
    for tense in verb_tenses:
        for item in my_dict:
            if verb_conjugation_data:
                # check if the verb tense is in the value
                if tense in item:
                    #update rows
                    db.execute("UPDATE conjugated_verbs SET {} = ? WHERE verb_id = ? AND conjugation_position = ?".format(tense), my_dict[item], verb_id, n)
            if n == 6:
                n = 1
            else:
                n += 1

# RUN APP
if __name__ == '__main__':
    # app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)