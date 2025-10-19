# app.py
from flask import Flask, g, render_template_string, request, redirect, url_for, session, jsonify, flash
import os
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

if DEBUG:
    DATABASE_PATH = 'roadmap_app.db'
else:
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable is required in production mode")

BACKGROUND_THEMES = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
]

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=not DEBUG,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600
)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        if DEBUG:
            db = g._database = sqlite3.connect(DATABASE_PATH)
            db.row_factory = sqlite3.Row
        else:
            db = g._database = psycopg2.connect(DATABASE_URL)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cur = db.cursor()
    
    if DEBUG:
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            secret_question TEXT,
            secret_answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            color TEXT DEFAULT '#667eea',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER,
            title TEXT NOT NULL,
            notes TEXT,
            done BOOLEAN DEFAULT FALSE,
            done_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL
        )''')
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            secret_question TEXT,
            secret_answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            color TEXT DEFAULT '#667eea',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            category_id INTEGER,
            title TEXT NOT NULL,
            notes TEXT,
            done BOOLEAN DEFAULT FALSE,
            done_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL
        )''')
    
    db.commit()

def execute_query(query, params=()):
    db = get_db()
    if DEBUG:
        cur = db.cursor()
        cur.execute(query, params)
        return cur
    else:
        return db.cursor(cursor_factory=RealDictCursor)

def fetch_all(query, params=()):
    cur = execute_query(query, params)
    result = cur.fetchall()
    cur.close()
    return result

def fetch_one(query, params=()):
    cur = execute_query(query, params)
    result = cur.fetchone()
    cur.close()
    return result

def current_user():
    if 'user_id' in session:
        user = fetch_one('SELECT * FROM users WHERE id=%s', (session['user_id'],))
        return user
    return None

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def get_random_background():
    return random.choice(BACKGROUND_THEMES)

def parse_bulk_import(text):
    categories = []
    current_category = None
    
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if '=' in line:
            parts = line.split('=', 1)
            category_name = parts[0].strip()
            tasks_text = parts[1].strip()
            
            if category_name and tasks_text:
                current_category = {
                    'name': category_name,
                    'tasks': [task.strip() for task in tasks_text.split(',') if task.strip()]
                }
                categories.append(current_category)
                
        elif ':' in line:
            parts = line.split(':', 1)
            category_name = parts[0].strip()
            tasks_text = parts[1].strip()
            
            if category_name and tasks_text:
                current_category = {
                    'name': category_name,
                    'tasks': [task.strip() for task in tasks_text.split('|') if task.strip()]
                }
                categories.append(current_category)
                
        elif line.startswith(('-', '*')):
            task_title = line[1:].strip()
            if current_category and task_title:
                current_category['tasks'].append(task_title)
                
        elif current_category:
            current_category['tasks'].append(line)
        else:
            categories.append({
                'name': 'General',
                'tasks': [line]
            })
    
    return categories

@app.route('/')
def home():
    if current_user():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        secret_q = request.form['secret_q'].strip()
        secret_a = request.form['secret_a'].strip()
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
        elif not secret_q or not secret_a:
            flash('All fields are required.', 'error')
        else:
            db = get_db()
            cur = db.cursor()
            try:
                cur.execute('INSERT INTO users(username,password,secret_question,secret_answer) VALUES(%s,%s,%s,%s)',
                           (username, generate_password_hash(password), secret_q, generate_password_hash(secret_a.lower())))
                db.commit()
                flash('Account created successfully! You can now log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash('Username already taken.', 'error')
    background = get_random_background()
    return render_template_string(TPL_BASE.replace('{{background}}', background).replace('{{content}}', TPL_REGISTER))

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = fetch_one('SELECT * FROM users WHERE username=%s', (username,))
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session.permanent = True
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'error')
    background = get_random_background()
    return render_template_string(TPL_BASE.replace('{{background}}', background).replace('{{content}}', TPL_LOGIN))

@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if current_user():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        user = fetch_one('SELECT * FROM users WHERE username=%s', (username,))
        if user:
            session['reset_user'] = user['id']
            background = get_random_background()
            content = TPL_FORGOT_Q.replace('{{ question }}', user['secret_question'])
            return render_template_string(TPL_BASE.replace('{{background}}', background).replace('{{content}}', content))
        flash('Username not found.', 'error')
    background = get_random_background()
    return render_template_string(TPL_BASE.replace('{{background}}', background).replace('{{content}}', TPL_FORGOT))

@app.route('/reset', methods=['POST'])
def reset():
    if current_user():
        return redirect(url_for('dashboard'))
    answer = request.form['answer'].strip().lower()
    newpass = request.form['newpass']
    uid = session.get('reset_user')
    if not uid:
        return redirect(url_for('forgot'))
    if len(newpass) < 6:
        flash('Password must be at least 6 characters long.', 'error')
        user = fetch_one('SELECT * FROM users WHERE id=%s', (uid,))
        background = get_random_background()
        content = TPL_FORGOT_Q.replace('{{ question }}', user['secret_question'])
        return render_template_string(TPL_BASE.replace('{{background}}', background).replace('{{content}}', content))
    user = fetch_one('SELECT * FROM users WHERE id=%s', (uid,))
    if user and check_password_hash(user['secret_answer'], answer):
        db = get_db()
        cur = db.cursor()
        cur.execute('UPDATE users SET password=%s WHERE id=%s', (generate_password_hash(newpass), uid))
        db.commit()
        session.pop('reset_user', None)
        flash('Password reset successful. Please log in.', 'success')
        return redirect(url_for('login'))
    flash('Incorrect answer.', 'error')
    background = get_random_background()
    content = TPL_FORGOT_Q.replace('{{ question }}', user['secret_question'])
    return render_template_string(TPL_BASE.replace('{{background}}', background).replace('{{content}}', content))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    categories = fetch_all('SELECT * FROM categories WHERE user_id=%s ORDER BY name', (user['id'],))
    tasks = fetch_all('''SELECT t.*, c.name as category_name, c.color as category_color 
                       FROM tasks t 
                       LEFT JOIN categories c ON t.category_id = c.id 
                       WHERE t.user_id=%s 
                       ORDER BY t.done, t.created_at DESC''', (user['id'],))
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task['done'])
    
    background = get_random_background()
    dashboard_content = TPL_DASHBOARD.replace('{{username}}', user['username'])\
                                    .replace('{{total_tasks}}', str(total_tasks))\
                                    .replace('{{completed_tasks}}', str(completed_tasks))
    
    return render_template_string(TPL_BASE.replace('{{background}}', background)\
                                        .replace('{{content}}', dashboard_content))

@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name','').strip()
    description = request.form.get('description','').strip()
    color = request.form.get('color', '#667eea')
    if name:
        db = get_db()
        cur = db.cursor()
        cur.execute('INSERT INTO categories(user_id,name,description,color) VALUES(%s,%s,%s,%s)', 
                   (session['user_id'], name, description, color))
        db.commit()
        flash('Roadmap added successfully!', 'success')
    else:
        flash('Roadmap name cannot be empty.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('title','').strip()
    notes = request.form.get('notes','').strip()
    category_id = request.form.get('category_id')
    if title:
        db = get_db()
        cur = db.cursor()
        cur.execute('INSERT INTO tasks(user_id,title,notes,category_id) VALUES(%s,%s,%s,%s)', 
                   (session['user_id'], title, notes, category_id if category_id else None))
        db.commit()
        flash('Task added successfully!', 'success')
    else:
        flash('Task title cannot be empty.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/bulk_import', methods=['POST'])
@login_required
def bulk_import():
    bulk_text = request.form.get('bulk_text', '').strip()
    if not bulk_text:
        flash('Please enter some content to import.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        categories_data = parse_bulk_import(bulk_text)
        db = get_db()
        cur = db.cursor()
        
        imported_count = 0
        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7']
        
        for category_data in categories_data:
            color = random.choice(colors)
            cur.execute('INSERT INTO categories(user_id,name,color) VALUES(%s,%s,%s) RETURNING id', 
                       (session['user_id'], category_data['name'], color))
            
            if DEBUG:
                category_id = cur.lastrowid
            else:
                category_id = cur.fetchone()[0]
            
            for task_title in category_data['tasks']:
                cur.execute('INSERT INTO tasks(user_id,title,category_id) VALUES(%s,%s,%s)', 
                           (session['user_id'], task_title, category_id))
                imported_count += 1
        
        db.commit()
        flash(f'Successfully imported {imported_count} tasks across {len(categories_data)} roadmaps!', 'success')
        
    except Exception as e:
        flash(f'Error importing data: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/mark_done', methods=['POST'])
@login_required
def mark_done():
    data = request.get_json()
    tid = data.get('id')
    db = get_db()
    cur = db.cursor()
    cur.execute('UPDATE tasks SET done=TRUE, done_at=%s WHERE id=%s AND user_id=%s',
               (datetime.now(timezone.utc), tid, session['user_id']))
    db.commit()
    return jsonify({'ok': True})

@app.route('/unset_done', methods=['POST'])
@login_required
def unset_done():
    data = request.get_json()
    tid = data.get('id')
    db = get_db()
    cur = db.cursor()
    cur.execute('UPDATE tasks SET done=FALSE, done_at=NULL WHERE id=%s AND user_id=%s', 
               (tid, session['user_id']))
    db.commit()
    return jsonify({'ok': True})

@app.route('/delete_category/<int:cid>', methods=['POST'])
@login_required
def delete_category(cid):
    db = get_db()
    cur = db.cursor()
    cur.execute('DELETE FROM categories WHERE id=%s AND user_id=%s', (cid, session['user_id']))
    db.commit()
    flash('Roadmap deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_task/<int:tid>', methods=['POST'])
@login_required
def delete_task(tid):
    db = get_db()
    cur = db.cursor()
    cur.execute('DELETE FROM tasks WHERE id=%s AND user_id=%s', (tid, session['user_id']))
    db.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/edit_task/<int:tid>', methods=['POST'])
@login_required
def edit_task(tid):
    title = request.form.get('title','').strip()
    notes = request.form.get('notes','').strip()
    category_id = request.form.get('category_id')
    if title:
        db = get_db()
        cur = db.cursor()
        cur.execute('UPDATE tasks SET title=%s, notes=%s, category_id=%s WHERE id=%s AND user_id=%s', 
                   (title, notes, category_id if category_id else None, tid, session['user_id']))
        db.commit()
        flash('Task updated successfully!', 'success')
    else:
        flash('Task title cannot be empty.', 'error')
    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def not_found(error):
    background = get_random_background()
    return render_template_string(TPL_BASE.replace('{{background}}', background).replace('{{content}}', TPL_404)), 404

@app.errorhandler(500)
def internal_error(error):
    background = get_random_background()
    return render_template_string(TPL_BASE.replace('{{background}}', background).replace('{{content}}', TPL_500)), 500

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)