from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import random
import os
from datetime import datetime
import json

app = Flask(__name__)
# Use a filesystem-friendly secret or fallback to a simple value for development
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-please-change')

# Initialize database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Define models
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    keys = db.Column(db.Text, nullable=False)  # JSON list of question keys
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()


# --- QUESTIONS: 30 items across Python, Java, DBMS ---
questions = {
    'q1': {
        'question': 'What is the output of: print(type([1,2,3])) in Python?',
        'options': ['<class "list">', '<class "tuple">', '<class "dict">', '<class "set">'],
        'answer': '<class "list">'
    },
    'q2': {
        'question': 'Which keyword is used to define a function in Python?',
        'options': ['func', 'def', 'function', 'lambda'],
        'answer': 'def'
    },
    'q3': {
        'question': 'Which of these is immutable in Python?',
        'options': ['list', 'set', 'tuple', 'dict'],
        'answer': 'tuple'
    },
    'q4': {
        'question': 'What does PEP stand for in Python community?',
        'options': ['Python Enhancement Proposal', 'Python Enterprise Plan', 'Program Execution Protocol', 'Partial Eval Proposal'],
        'answer': 'Python Enhancement Proposal'
    },
    'q5': {
        'question': 'Which method adds an item to the end of a Python list?',
        'options': ['append()', 'add()', 'push()', 'insert()'],
        'answer': 'append()'
    },
    'q6': {
        'question': 'What is the correct file extension for Python files?',
        'options': ['.py', '.pt', '.p', '.python'],
        'answer': '.py'
    },
    'q7': {
        'question': 'Which statement is used to handle exceptions in Python?',
        'options': ['try/except', 'catch/except', 'handle/onerror', 'try/catch'],
        'answer': 'try/except'
    },
    'q8': {
        'question': 'Which built-in type is used for key-value pairs?',
        'options': ['list', 'dict', 'tuple', 'set'],
        'answer': 'dict'
    },
    'q9': {
        'question': 'What does the len() function return when called on a string?',
        'options': ['Number of words', 'Number of characters', 'Number of bytes', 'Memory size'],
        'answer': 'Number of characters'
    },
    'q10': {
        'question': 'Which operator is used for string concatenation in Python?',
        'options': ['&', '+', '.', 'concat()'],
        'answer': '+'
    },

    'q11': {
        'question': 'Which of these is not a Java keyword?',
        'options': ['static', 'Boolean', 'class', 'if'],
        'answer': 'Boolean'
    },
    'q12': {
        'question': 'Which method is the entry point of a Java application?',
        'options': ['public static void main(String[] args)', 'start()', 'main() without args', 'run()'],
        'answer': 'public static void main(String[] args)'
    },
    'q13': {
        'question': 'Which keyword is used to inherit a class in Java?',
        'options': ['implements', 'extends', 'inherits', 'uses'],
        'answer': 'extends'
    },
    'q14': {
        'question': 'Which collection allows duplicate elements in Java?',
        'options': ['Set', 'Map', 'List', 'None of these'],
        'answer': 'List'
    },
    'q15': {
        'question': 'Which package contains the Scanner class?',
        'options': ['java.io', 'java.util', 'java.net', 'java.lang'],
        'answer': 'java.util'
    },
    'q16': {
        'question': 'Which keyword declares a constant in Java?',
        'options': ['static', 'final', 'const', 'immutable'],
        'answer': 'final'
    },
    'q17': {
        'question': 'Which of these is a checked exception?',
        'options': ['NullPointerException', 'IOException', 'ArrayIndexOutOfBoundsException', 'RuntimeException'],
        'answer': 'IOException'
    },
    'q18': {
        'question': 'What is the default value of a boolean member variable in Java?',
        'options': ['true', 'false', 'null', '0'],
        'answer': 'false'
    },
    'q19': {
        'question': 'Which access modifier makes a member visible only within its own class?',
        'options': ['public', 'protected', 'private', 'package'],
        'answer': 'private'
    },
    'q20': {
        'question': 'Which keyword is used to create a new object in Java?',
        'options': ['create', 'new', 'instantiate', 'build'],
        'answer': 'new'
    },

    'q21': {
        'question': 'Which command is used to remove a table named students in SQL?',
        'options': ['DELETE TABLE students;', 'DROP TABLE students;', 'REMOVE TABLE students;', 'TRUNCATE TABLE students;'],
        'answer': 'DROP TABLE students;'
    },
    'q22': {
        'question': 'Which SQL clause is used to filter results?',
        'options': ['ORDER BY', 'GROUP BY', 'WHERE', 'HAVING'],
        'answer': 'WHERE'
    },
    'q23': {
        'question': 'Which normal form removes repeating groups from a relation?',
        'options': ['1NF', '2NF', '3NF', 'BCNF'],
        'answer': '1NF'
    },
    'q24': {
        'question': 'Which SQL keyword is used to sort results?',
        'options': ['FILTER BY', 'ORDER BY', 'SORT BY', 'GROUP BY'],
        'answer': 'ORDER BY'
    },
    'q25': {
        'question': 'Which of these is a NoSQL database?',
        'options': ['MySQL', 'PostgreSQL', 'MongoDB', 'SQLite'],
        'answer': 'MongoDB'
    },
    'q26': {
        'question': 'Which join returns all rows from both tables, matching where possible?',
        'options': ['INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL OUTER JOIN'],
        'answer': 'FULL OUTER JOIN'
    },
    'q27': {
        'question': 'What does ACID stand for (in databases)?',
        'options': ['Atomicity, Consistency, Isolation, Durability', 'Accuracy, Consistency, Integrity, Durability', 'Atomicity, Concurrency, Isolation, Durability', 'Atomicity, Consistency, Isolation, Distribution'],
        'answer': 'Atomicity, Consistency, Isolation, Durability'
    },
    'q28': {
        'question': 'Which statement is used to add a row into a table?',
        'options': ['ADD INTO', 'INSERT INTO', 'CREATE ROW', 'UPDATE INTO'],
        'answer': 'INSERT INTO'
    },
    'q29': {
        'question': 'Which index type enforces uniqueness of the indexed column?',
        'options': ['NON-UNIQUE INDEX', 'UNIQUE INDEX', 'CLUSTERED INDEX', 'BITMAP INDEX'],
        'answer': 'UNIQUE INDEX'
    },
    'q30': {
        'question': 'Which SQL function returns the number of rows in a result set?',
        'options': ['COUNT()', 'SUM()', 'TOTAL()', 'LENGTH()'],
        'answer': 'COUNT()'
    }
}


def generate_captcha():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    return (a, b, a + b)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        captcha_answer = request.form.get('captcha', '').strip()
        # optional quiz options
        quiz_size = int(request.form.get('quiz_size', 30))
        categories = request.form.getlist('category')  # list of chosen categories

        expected = session.get('captcha_expected')

        error = None
        if not username or not password:
            error = 'Please enter username and password.'
        elif expected is None or str(expected) != captcha_answer:
            error = 'Captcha answer is incorrect.'
        else:
            # Validate username and password
            user = User.query.filter_by(username=username).first()
            if not user or not check_password_hash(user.password, password):
                # Skip setting the error message
                a, b, s = generate_captcha()
                session['captcha_expected'] = s
                return render_template('login.html', a=a, b=b, username=username, quiz_size=quiz_size, categories=categories)

        if error:
            # regenerate captcha and re-render
            a, b, s = generate_captcha()
            session['captcha_expected'] = s
            return render_template('login.html', error=error, a=a, b=b, username=username, quiz_size=quiz_size, categories=categories)

        # login success
        session['logged_in'] = True
        session['username'] = username
        # store chosen options in session
        session['quiz_size'] = quiz_size
        session['categories'] = categories
        # clear captcha
        session.pop('captcha_expected', None)
        return redirect(url_for('quiz'))

    # GET
    a, b, s = generate_captcha()
    session['captcha_expected'] = s
    # defaults
    return render_template('login.html', a=a, b=b, quiz_size=30, categories=['python','java','dbms'])


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return render_template('signup.html', error='Username already exists')

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Log the user in and redirect to quiz
        session['user_id'] = new_user.id
        return redirect('/quiz')

    return render_template('signup.html')


@app.route('/quiz', methods=['GET'])
def quiz():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Choose a random subset of questions for this attempt
    quiz_size = session.get('quiz_size', 30)
    chosen_categories = session.get('categories') or ['python', 'java', 'dbms']

    # map category name to question keys (we use ranges: q1-10 python, q11-20 java, q21-30 dbms)
    all_keys = list(questions.keys())
    cat_map = {
        'python': all_keys[0:10],
        'java': all_keys[10:20],
        'dbms': all_keys[20:30]
    }

    pool = []
    for c in chosen_categories:
        pool.extend(cat_map.get(c, []))

    if not pool:
        pool = all_keys

    selected = random.sample(pool, min(quiz_size, len(pool)))

    # Persist attempt server-side
    attempt = Attempt(username=session['username'], keys=json.dumps(selected))
    db.session.add(attempt)
    db.session.commit()
    session['attempt_id'] = attempt.id

    # store selected keys in session for template convenience too
    session['quiz_keys'] = selected
    selected_questions = {k: questions[k] for k in selected}
    return render_template('quiz.html', questions=selected_questions)


@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Use the quiz_keys from the stored attempt for accuracy
    attempt_id = session.get('attempt_id')
    if attempt_id:
        attempt = Attempt.query.get(attempt_id)
        selected = json.loads(attempt.keys) if attempt else (session.get('quiz_keys') or list(questions.keys()))
    else:
        selected = session.get('quiz_keys') or list(questions.keys())

    user_answers = {}
    score = 0
    total = len(selected)

    for key in selected:
        q = questions.get(key)
        ans = request.form.get(key)
        user_answers[key] = ans
        if ans is not None and q and ans == q['answer']:
            score += 1

    # update attempt record if available
    if attempt_id and attempt:
        attempt.score = score
        db.session.commit()

    # Save score to database
    new_score = Score(username=session['username'], score=score)
    db.session.add(new_score)
    db.session.commit()

    return render_template('result.html', score=score, total=total, questions=questions, user_answers=user_answers)


@app.route('/leaderboard')
def leaderboard():
    top_scores = Score.query.order_by(Score.score.desc()).limit(10).all()
    return render_template('leaderboard.html', scores=top_scores)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    # Only for development. Use a proper server for production.
    print('Starting Flask dev server...')
    print(' - open http://127.0.0.1:5000 or http://localhost:5000 in your browser')
    print(' - health check available at http://127.0.0.1:5000/health')
    app.run(host='0.0.0.0', port=5000, debug=True)



@app.route('/health')
def health():
    return 'OK', 200