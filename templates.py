# templates.py
TPL_BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roadmap App</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Inter', sans-serif; 
            background: {{background}};
            min-height: 100vh;
            padding: 20px;
            transition: background 0.5s ease;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        .btn-success { background: linear-gradient(135deg, #28a745, #20c997); }
        .btn-danger { background: linear-gradient(135deg, #dc3545, #e83e8c); }
        .btn-secondary { background: linear-gradient(135deg, #6c757d, #868e96); }
        .btn-info { background: linear-gradient(135deg, #17a2b8, #6f42c1); }
        .btn-small { padding: 6px 12px; font-size: 12px; }
        .form-group { margin-bottom: 15px; }
        .form-control {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        .form-control:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        textarea.form-control {
            min-height: 100px;
            resize: vertical;
        }
        .alert {
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 20px;
            animation: slideIn 0.5s ease;
        }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .alert-info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .task-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border-left: 5px solid #667eea;
            animation: fadeIn 0.5s ease;
        }
        .task-card:hover {
            transform: translateX(5px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }
        .task-card.done {
            border-left-color: #28a745;
            opacity: 0.8;
        }
        .task-card.done .task-title {
            text-decoration: line-through;
            color: #6c757d;
        }
        .category-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            color: white;
            margin-bottom: 8px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            animation: fadeIn 1s ease;
        }
        .stat-card.success { background: linear-gradient(135deg, #28a745, #20c997); }
        .task-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
        }
        .categories-sidebar {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 20px;
            height: fit-content;
        }
        .category-item {
            padding: 10px;
            margin: 8px 0;
            border-radius: 10px;
            background: #f8f9fa;
            border-left: 4px solid;
        }
        .bulk-import-section {
            margin: 20px 0;
        }
        .import-example {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            font-size: 0.9em;
        }
        .import-example code {
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
        @keyframes slideIn {
            from { transform: translateY(-20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .pulse { animation: pulse 2s infinite; }
        .header { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 20px;
        }
        .task-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        .welcome-text {
            font-size: 1.5rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #718096;
            margin-bottom: 20px;
        }
        .edit-form {
            display: none;
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .color-preview {
            width: 30px;
            height: 30px;
            border-radius: 6px;
            display: inline-block;
            margin-right: 10px;
            border: 2px solid #e1e5e9;
        }
        .tab-buttons {
            display: flex;
            margin-bottom: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 5px;
        }
        .tab-button {
            flex: 1;
            padding: 10px;
            text-align: center;
            background: transparent;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .tab-button.active {
            background: white;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        {{content}}
    </div>
    <script>
        setTimeout(() => {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                alert.style.transition = 'all 0.5s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                setTimeout(() => alert.remove(), 500);
            });
        }, 5000);

        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }

        function showImportExamples() {
            const examples = `Quick Import Formats:

1. Category = Task1, Task2, Task3
   Web Development = HTML Basics, CSS Styling, JavaScript Fundamentals

2. Category: Task1 | Task2 | Task3  
   Data Science: Python Basics | Pandas | Machine Learning

3. Bullet points:
   Study Plan
   - Math Chapter 1
   - Physics Lab Report
   - Chemistry Homework

4. Mixed format:
   Fitness = Morning Run, Gym Session
   Fitness: Yoga | Meditation
   - Healthy Cooking`;
            alert(examples);
        }

        async function markTaskDone(taskId) {
            try {
                const response = await fetch('/mark_done', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: taskId })
                });
                const result = await response.json();
                if (result.ok) {
                    const taskCard = document.getElementById('task-' + taskId);
                    taskCard.style.animation = 'pulse 0.5s ease';
                    setTimeout(() => {
                        location.reload();
                    }, 500);
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('An error occurred. Please try again.');
            }
        }

        async function undoTask(taskId) {
            try {
                const response = await fetch('/unset_done', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: taskId })
                });
                if (response.ok) {
                    const taskCard = document.getElementById('task-' + taskId);
                    taskCard.style.animation = 'pulse 0.5s ease';
                    setTimeout(() => {
                        location.reload();
                    }, 500);
                }
            } catch (error) {
                alert('An error occurred. Please try again.');
            }
        }

        function toggleEdit(taskId) {
            const editForm = document.getElementById('edit-form-' + taskId);
            if (editForm.style.display === 'block') {
                editForm.style.display = 'none';
            } else {
                editForm.style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""

TPL_LOGIN = """
<div class="glass-card" style="max-width: 400px; margin: 50px auto;">
    <h2 style="text-align: center; margin-bottom: 30px; color: #2d3748;">Welcome Back</h2>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'warning' if category == 'warning' else 'info' }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    <form method="post">
        <div class="form-group">
            <input type="text" name="username" class="form-control" placeholder="Username" required>
        </div>
        <div class="form-group">
            <input type="password" name="password" class="form-control" placeholder="Password" required>
        </div>
        <button type="submit" class="btn" style="width: 100%;">Login</button>
    </form>
    <div style="text-align: center; margin-top: 20px;">
        <p>Forgot password? <a href="{{ url_for('forgot') }}" style="color: #667eea; text-decoration: none;">Recover</a></p>
        <p>Don't have an account? <a href="{{ url_for('register') }}" style="color: #667eea; text-decoration: none;">Register</a></p>
    </div>
</div>
"""

TPL_REGISTER = """
<div class="glass-card" style="max-width: 400px; margin: 50px auto;">
    <h2 style="text-align: center; margin-bottom: 30px; color: #2d3748;">Create Account</h2>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'warning' if category == 'warning' else 'info' }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    <form method="post">
        <div class="form-group">
            <input type="text" name="username" class="form-control" placeholder="Username" required>
        </div>
        <div class="form-group">
            <input type="password" name="password" class="form-control" placeholder="Password" required>
        </div>
        <div class="form-group">
            <input type="text" name="secret_q" class="form-control" placeholder="Secret question (e.g. Your middle name?)" required>
        </div>
        <div class="form-group">
            <input type="text" name="secret_a" class="form-control" placeholder="Answer to secret question" required>
        </div>
        <button type="submit" class="btn" style="width: 100%;">Register</button>
    </form>
    <div style="text-align: center; margin-top: 20px;">
        <p>Already have an account? <a href="{{ url_for('login') }}" style="color: #667eea; text-decoration: none;">Login</a></p>
    </div>
</div>
"""

TPL_FORGOT = """
<div class="glass-card" style="max-width: 400px; margin: 50px auto;">
    <h2 style="text-align: center; margin-bottom: 30px; color: #2d3748;">Forgot Password</h2>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'warning' if category == 'warning' else 'info' }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    <form method="post">
        <div class="form-group">
            <input type="text" name="username" class="form-control" placeholder="Enter username" required>
        </div>
        <button type="submit" class="btn" style="width: 100%;">Next</button>
    </form>
</div>
"""

TPL_FORGOT_Q = """
<div class="glass-card" style="max-width: 400px; margin: 50px auto;">
    <h2 style="text-align: center; margin-bottom: 30px; color: #2d3748;">Answer Secret Question</h2>
    <p style="text-align: center; margin-bottom: 20px; font-weight: 500;">{{ question }}</p>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'warning' if category == 'warning' else 'info' }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    <form method="post" action="{{ url_for('reset') }}">
        <div class="form-group">
            <input type="text" name="answer" class="form-control" placeholder="Your answer" required>
        </div>
        <div class="form-group">
            <input type="password" name="newpass" class="form-control" placeholder="New password" required>
        </div>
        <button type="submit" class="btn" style="width: 100%;">Reset Password</button>
    </form>
</div>
"""

TPL_404 = """
<div class="glass-card" style="text-align: center; max-width: 500px; margin: 100px auto;">
    <h1 style="font-size: 4rem; color: #667eea; margin-bottom: 20px;">404</h1>
    <h2 style="margin-bottom: 20px;">Page Not Found</h2>
    <p style="margin-bottom: 30px;">The page you're looking for doesn't exist.</p>
    <a href="{{ url_for('dashboard') }}" class="btn">Go to Dashboard</a>
</div>
"""

TPL_500 = """
<div class="glass-card" style="text-align: center; max-width: 500px; margin: 100px auto;">
    <h1 style="font-size: 4rem; color: #f5576c; margin-bottom: 20px;">500</h1>
    <h2 style="margin-bottom: 20px;">Internal Server Error</h2>
    <p style="margin-bottom: 30px;">Something went wrong on our end. Please try again later.</p>
    <a href="{{ url_for('dashboard') }}" class="btn">Go to Dashboard</a>
</div>
"""

TPL_DASHBOARD = """
<div class="header">
    <div>
        <h1 class="welcome-text">{{username}}'s Roadmap</h1>
        <p class="subtitle">Organize your life with categories and tasks</p>
    </div>
    <a href="{{ url_for('logout') }}" class="btn btn-secondary">Logout</a>
</div>
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'warning' if category == 'warning' else 'info' }}">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}

<div class="stats-grid">
    <div class="stat-card">
        <h3>Total Tasks</h3>
        <p style="font-size: 2rem; font-weight: bold;">{{total_tasks}}</p>
    </div>
    <div class="stat-card success">
        <h3>Completed</h3>
        <p style="font-size: 2rem; font-weight: bold;">{{completed_tasks}}</p>
    </div>
    <div class="stat-card" style="background: linear-gradient(135deg, #ffd89b, #19547b);">
        <h3>Progress</h3>
        <p style="font-size: 2rem; font-weight: bold;">
            {{ (completed_tasks / total_tasks * 100)|round|int if total_tasks > 0 else 0 }}%
        </p>
    </div>
</div>

<div class="dashboard-grid">
    <div class="categories-sidebar">
        <h3 style="margin-bottom: 20px;">Your Roadmaps</h3>
        
        <div class="glass-card" style="margin-bottom: 20px;">
            <h4 style="margin-bottom: 15px;">Add New Roadmap</h4>
            <form method="post" action="{{ url_for('add_category') }}">
                <div class="form-group">
                    <input type="text" name="name" class="form-control" placeholder="Roadmap name (e.g., Study Plan)" required>
                </div>
                <div class="form-group">
                    <textarea name="description" class="form-control" placeholder="Description (optional)" rows="2"></textarea>
                </div>
                <div class="form-group">
                    <label style="display: block; margin-bottom: 8px; font-weight: 500;">Color:</label>
                    <input type="color" name="color" value="#667eea" style="width: 100%; height: 40px; border-radius: 8px; border: 2px solid #e1e5e9;">
                </div>
                <button type="submit" class="btn" style="width: 100%;">Create Roadmap</button>
            </form>
        </div>

        {% if categories %}
            <h4 style="margin-bottom: 15px;">Your Roadmaps</h4>
            {% for category in categories %}
                <div class="category-item" style="border-left-color: {{ category.color }};">
                    <div style="display: flex; justify-content: between; align-items: center;">
                        <div>
                            <strong>{{ category.name }}</strong>
                            {% if category.description %}
                                <p style="margin: 5px 0 0 0; font-size: 12px; color: #6c757d;">{{ category.description }}</p>
                            {% endif %}
                        </div>
                        <form method="post" action="{{ url_for('delete_category', cid=category.id) }}" style="display: inline;">
                            <button type="submit" class="btn btn-danger btn-small" onclick="return confirm('Delete this roadmap and all its tasks?')">×</button>
                        </form>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div style="text-align: center; padding: 20px; color: #6c757d;">
                <p>No roadmaps yet. Create your first one!</p>
            </div>
        {% endif %}
    </div>

    <div>
        <div class="tab-buttons">
            <button class="tab-button active" onclick="switchTab('single')">Add Single Task</button>
            <button class="tab-button" onclick="switchTab('bulk')">Bulk Import</button>
        </div>

        <div id="single-tab" class="tab-content active">
            <div class="glass-card">
                <h3 style="margin-bottom: 15px;">Add New Task</h3>
                <form method="post" action="{{ url_for('add_task') }}">
                    <div class="form-group">
                        <input type="text" name="title" class="form-control" placeholder="Task title" required>
                    </div>
                    <div class="form-group">
                        <textarea name="notes" class="form-control" placeholder="Notes (optional)" rows="3"></textarea>
                    </div>
                    <div class="form-group">
                        <select name="category_id" class="form-control">
                            <option value="">No Roadmap (General)</option>
                            {% for category in categories %}
                                <option value="{{ category.id }}">{{ category.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <button type="submit" class="btn">Add Task</button>
                </form>
            </div>
        </div>

        <div id="bulk-tab" class="tab-content">
            <div class="glass-card">
                <h3 style="margin-bottom: 15px;">Bulk Import Tasks</h3>
                <form method="post" action="{{ url_for('bulk_import') }}">
                    <div class="form-group">
                        <textarea name="bulk_text" class="form-control" placeholder="Paste your roadmap here..." rows="8" required></textarea>
                    </div>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <button type="submit" class="btn btn-info">Import Roadmap</button>
                        <button type="button" class="btn btn-secondary" onclick="showImportExamples()">Show Format Examples</button>
                    </div>
                </form>
                <div class="import-example">
                    <strong>Supported formats:</strong><br>
                    • <code>Category = Task1, Task2, Task3</code><br>
                    • <code>Category: Task1 | Task2 | Task3</code><br>
                    • Bullet points with <code>- Task</code> or <code>* Task</code>
                </div>
            </div>
        </div>

        <h2 style="margin-bottom: 20px; color: white;">Your Tasks</h2>
        {% if tasks %}
            <div class="task-grid">
                {% for t in tasks %}
                    <div class="task-card {% if t['done'] %}done{% endif %}" id="task-{{ t['id'] }}">
                        {% if t['category_name'] %}
                            <div class="category-badge" style="background-color: {{ t['category_color'] }};">
                                {{ t['category_name'] }}
                            </div>
                        {% endif %}
                        <div class="task-title" style="font-weight: 600; margin-bottom: 10px;">{{ t['title'] }}</div>
                        {% if t['notes'] %}
                            <div style="color: #718096; margin-bottom: 10px;">{{ t['notes'] }}</div>
                        {% endif %}
                        {% if t['done'] %}
                            <div style="color: #28a745; font-size: 0.9rem; margin-bottom: 10px;">
                                {% if t.done_at %}
                                    ✓ Completed at {{ t.done_at[:16] }}
                                {% else %}
                                    ✓ Completed
                                {% endif %}
                            </div>
                        {% else %}
                            <div style="color: #6c757d; font-size: 0.9rem; margin-bottom: 10px;">
                                {% if t.created_at %}
                                    Created: {{ t.created_at[:16] }}
                                {% else %}
                                    Created: Recently
                                {% endif %}
                            </div>
                        {% endif %}
                        <div class="task-actions">
                            {% if t['done'] %}
                                <button onclick="undoTask({{ t['id'] }})" class="btn btn-secondary">Undo</button>
                            {% else %}
                                <button onclick="markTaskDone({{ t['id'] }})" class="btn btn-success">Mark Done</button>
                                <button onclick="toggleEdit({{ t['id'] }})" class="btn">Edit</button>
                            {% endif %}
                            <form method="post" action="{{ url_for('delete_task', tid=t['id']) }}" style="display: inline;">
                                <button type="submit" class="btn btn-danger" onclick="return confirm('Are you sure you want to delete this task?')">Delete</button>
                            </form>
                        </div>
                        <div id="edit-form-{{ t['id'] }}" class="edit-form">
                            <form method="post" action="{{ url_for('edit_task', tid=t['id']) }}">
                                <div class="form-group">
                                    <input type="text" name="title" class="form-control" value="{{ t['title'] }}" required>
                                </div>
                                <div class="form-group">
                                    <textarea name="notes" class="form-control" rows="3">{{ t['notes'] or '' }}</textarea>
                                </div>
                                <div class="form-group">
                                    <select name="category_id" class="form-control">
                                        <option value="">No Roadmap (General)</option>
                                        {% for category in categories %}
                                            <option value="{{ category.id }}" {% if t.category_id == category.id %}selected{% endif %}>
                                                {{ category.name }}
                                            </option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div style="display: flex; gap: 10px;">
                                    <button type="submit" class="btn">Save Changes</button>
                                    <button type="button" class="btn btn-secondary" onclick="toggleEdit({{ t['id'] }})">Cancel</button>
                                </div>
                            </form>
                        </div>
                    </div>
                {% endfor %}
            </div>
        {% else %}
            <div class="glass-card" style="text-align: center;">
                <h3 style="color: #6c757d; margin-bottom: 15px;">No tasks yet</h3>
                <p style="color: #868e96;">Start by adding your first task above!</p>
            </div>
        {% endif %}
    </div>
</div>
"""