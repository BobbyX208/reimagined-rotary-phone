# app.py - Complete Flask Roadmap App with Dark Theme & Advanced Footer
from flask import Flask, g, render_template_string, request, redirect, url_for, session, jsonify, flash
import os
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import random
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Configuration
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

if DEBUG:
    DATABASE_PATH = 'roadmap_app.db'
    print("🔧 Running in DEBUG mode with SQLite")
else:
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable is required in production mode")
    print("🚀 Running in PRODUCTION mode with PostgreSQL")

# Personalization
PORTFOLIO_URL = os.environ.get('PORTFOLIO_URL', 'https://yourportfolio.com')
GITHUB_URL = os.environ.get('GITHUB_URL', 'https://github.com/yourusername')
LINKEDIN_URL = os.environ.get('LINKEDIN_URL', 'https://linkedin.com/in/yourprofile')
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'hello@yourdomain.com')

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=not DEBUG,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600
)

# ---------- Template Strings ----------
TPL_BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roadmap App</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f0f23;
            --bg-secondary: #1a1a2e;
            --bg-glass: rgba(255, 255, 255, 0.05);
            --bg-glass-hover: rgba(255, 255, 255, 0.1);
            --text-primary: #ffffff;
            --text-secondary: #b0b0b0;
            --text-muted: #888888;
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --accent-success: #10b981;
            --accent-danger: #ef4444;
            --accent-warning: #f59e0b;
            --border-radius: 16px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            --shadow-hover: 0 12px 48px rgba(0, 0, 0, 0.4);
        }

        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }

        body { 
            font-family: 'Inter', sans-serif; 
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
            transition: var(--transition);
        }

        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            min-height: calc(100vh - 160px);
        }

        .glass-card {
            background: var(--bg-glass);
            backdrop-filter: blur(20px);
            border-radius: var(--border-radius);
            padding: 30px;
            box-shadow: var(--shadow);
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }

        .glass-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: var(--transition);
        }

        .glass-card:hover::before {
            left: 100%;
        }

        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-hover);
            background: var(--bg-glass-hover);
        }

        .btn {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            transition: var(--transition);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            position: relative;
            overflow: hidden;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: var(--transition);
        }

        .btn:hover::before {
            left: 100%;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
        }

        .btn-success { 
            background: linear-gradient(135deg, var(--accent-success), #059669); 
        }
        .btn-danger { 
            background: linear-gradient(135deg, var(--accent-danger), #dc2626); 
        }
        .btn-secondary { 
            background: linear-gradient(135deg, #6b7280, #4b5563); 
        }
        .btn-info { 
            background: linear-gradient(135deg, #06b6d4, #0891b2); 
        }
        .btn-small { 
            padding: 8px 16px; 
            font-size: 12px; 
        }

        .form-group { 
            margin-bottom: 20px; 
        }

        .form-control {
            width: 100%;
            padding: 14px 18px;
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            font-size: 14px;
            transition: var(--transition);
            color: var(--text-primary);
        }

        .form-control::placeholder {
            color: var(--text-muted);
        }

        .form-control:focus {
            outline: none;
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
            background: rgba(255, 255, 255, 0.08);
        }

        textarea.form-control {
            min-height: 120px;
            resize: vertical;
        }

        .alert {
            padding: 16px 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            animation: slideIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid;
            background: var(--bg-glass);
        }

        .alert-success { 
            color: #10b981; 
            border-color: rgba(16, 185, 129, 0.3); 
        }
        .alert-error { 
            color: #ef4444; 
            border-color: rgba(239, 68, 68, 0.3); 
        }
        .alert-warning { 
            color: #f59e0b; 
            border-color: rgba(245, 158, 11, 0.3); 
        }
        .alert-info { 
            color: #06b6d4; 
            border-color: rgba(6, 182, 212, 0.3); 
        }

        .task-card {
            background: var(--bg-glass);
            border-radius: var(--border-radius);
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: var(--shadow);
            transition: var(--transition);
            border-left: 4px solid var(--accent-primary);
            animation: fadeIn 0.5s ease;
            position: relative;
            overflow: hidden;
        }

        .task-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent-primary);
            transition: var(--transition);
        }

        .task-card:hover {
            transform: translateX(8px);
            box-shadow: var(--shadow-hover);
            background: var(--bg-glass-hover);
        }

        .task-card.done {
            border-left-color: var(--accent-success);
            opacity: 0.8;
        }

        .task-card.done::before {
            background: var(--accent-success);
        }

        .task-card.done .task-title {
            text-decoration: line-through;
            color: var(--text-muted);
        }

        .category-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: white;
            margin-bottom: 12px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            padding: 24px;
            border-radius: var(--border-radius);
            text-align: center;
            animation: fadeIn 1s ease;
            position: relative;
            overflow: hidden;
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: rotate 10s linear infinite;
        }

        .stat-card.success { 
            background: linear-gradient(135deg, var(--accent-success), #059669); 
        }

        .task-actions {
            display: flex;
            gap: 10px;
            margin-top: 16px;
            flex-wrap: wrap;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 24px;
        }

        .categories-sidebar {
            background: var(--bg-glass);
            border-radius: var(--border-radius);
            padding: 24px;
            height: fit-content;
            backdrop-filter: blur(20px);
        }

        .category-item {
            padding: 16px;
            margin: 12px 0;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid;
            transition: var(--transition);
        }

        .category-item:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateX(4px);
        }

        .import-example {
            background: rgba(255, 255, 255, 0.05);
            padding: 16px;
            border-radius: 12px;
            margin-top: 12px;
            font-size: 0.9em;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .import-example code {
            background: rgba(255, 255, 255, 0.1);
            padding: 4px 8px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            color: var(--accent-primary);
        }

        @keyframes slideIn {
            from { 
                transform: translateY(-20px); 
                opacity: 0; 
            }
            to { 
                transform: translateY(0); 
                opacity: 1; 
            }
        }

        @keyframes fadeIn {
            from { 
                opacity: 0; 
                transform: translateY(20px); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
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
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 20px;
        }

        .welcome-text {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }

        .subtitle {
            color: var(--text-secondary);
            margin-bottom: 20px;
            font-size: 1.1rem;
        }

        .edit-form {
            display: none;
            margin-top: 16px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .color-preview {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: inline-block;
            margin-right: 12px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            transition: var(--transition);
        }

        .color-preview:hover {
            transform: scale(1.1);
        }

        .tab-buttons {
            display: flex;
            margin-bottom: 24px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 6px;
            gap: 4px;
        }

        .tab-button {
            flex: 1;
            padding: 12px;
            text-align: center;
            background: transparent;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: var(--transition);
            color: var(--text-secondary);
            font-weight: 500;
        }

        .tab-button.active {
            background: var(--accent-primary);
            color: white;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        /* Advanced Footer */
        .app-footer {
            margin-top: 60px;
            padding: 40px 0 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .footer-content {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 40px;
            margin-bottom: 30px;
        }

        .footer-brand h3 {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 16px;
            font-size: 1.5rem;
        }

        .footer-brand p {
            color: var(--text-secondary);
            line-height: 1.6;
        }

        .footer-links h4 {
            color: var(--text-primary);
            margin-bottom: 16px;
            font-size: 1.1rem;
        }

        .footer-links ul {
            list-style: none;
        }

        .footer-links li {
            margin-bottom: 10px;
        }

        .footer-links a {
            color: var(--text-secondary);
            text-decoration: none;
            transition: var(--transition);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .footer-links a:hover {
            color: var(--accent-primary);
            transform: translateX(4px);
        }

        .footer-bottom {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        .footer-social {
            display: flex;
            gap: 16px;
        }

        .footer-social a {
            color: var(--text-secondary);
            font-size: 1.2rem;
            transition: var(--transition);
            padding: 8px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
        }

        .footer-social a:hover {
            color: var(--accent-primary);
            background: rgba(99, 102, 241, 0.1);
            transform: translateY(-2px);
        }

        .current-date {
            color: var(--accent-primary);
            font-weight: 600;
        }

        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .footer-content {
                grid-template-columns: 1fr;
                gap: 30px;
            }
            
            .footer-bottom {
                flex-direction: column;
                gap: 16px;
                text-align: center;
            }
            
            .task-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        {{content}}
    </div>

    {{footer}}

    <script>
        // Flash message auto-hide
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
            const examples = `🚀 Quick Import Formats:

📁 Category = Task1, Task2, Task3
   Web Development = HTML Basics, CSS Styling, JavaScript Fundamentals

📊 Category: Task1 | Task2 | Task3  
   Data Science: Python Basics | Pandas | Machine Learning

📝 Bullet points:
   Study Plan
   - Math Chapter 1
   - Physics Lab Report
   - Chemistry Homework

🔄 Mixed format:
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

        // Add floating animation to stats cards
        document.addEventListener('DOMContentLoaded', () => {
            const stats = document.querySelectorAll('.stat-card');
            stats.forEach((stat, index) => {
                stat.style.animationDelay = `${index * 0.2}s`;
            });
        });
    </script>
</body>
</html>
"""

TPL_FOOTER = """
<footer class="app-footer">
    <div class="footer-content">
        <div class="footer-brand">
            <h3>🚀 Roadmap App</h3>
            <p>Transform your goals into actionable roadmaps. Organize tasks, track progress, and achieve more with our intuitive planning platform.</p>
        </div>
        
        <div class="footer-links">
            <h4>Quick Links</h4>
            <ul>
                <li><a href="{{ url_for('dashboard') }}"><i class="fas fa-home"></i> Dashboard</a></li>
                <li><a href="{{ url_for('login') }}"><i class="fas fa-sign-in-alt"></i> Login</a></li>
                <li><a href="{{ url_for('register') }}"><i class="fas fa-user-plus"></i> Register</a></li>
            </ul>
        </div>
        
        <div class="footer-links">
            <h4>Connect</h4>
            <ul>
                <li><a href="{{ portfolio_url }}" target="_blank"><i class="fas fa-briefcase"></i> Portfolio</a></li>
                <li><a href="{{ github_url }}" target="_blank"><i class="fab fa-github"></i> GitHub</a></li>
                <li><a href="{{ linkedin_url }}" target="_blank"><i class="fab fa-linkedin"></i> LinkedIn</a></li>
                <li><a href="mailto:{{ contact_email }}"><i class="fas fa-envelope"></i> Contact</a></li>
            </ul>
        </div>
    </div>
    
    <div class="footer-bottom">
        <div>
            <p>© 2024 Roadmap App. Built with <i class="fas fa-heart" style="color: #ef4444;"></i> using Flask & PostgreSQL</p>
            <p>Server Time: <span class="current-date">{{ current_date }}</span></p>
        </div>
        
        <div class="footer-social">
            <a href="{{ github_url }}" target="_blank" title="GitHub">
                <i class="fab fa-github"></i>
            </a>
            <a href="{{ linkedin_url }}" target="_blank" title="LinkedIn">
                <i class="fab fa-linkedin"></i>
            </a>
            <a href="mailto:{{ contact_email }}" title="Email">
                <i class="fas fa-envelope"></i>
            </a>
        </div>
    </div>
</footer>
"""

TPL_LOGIN = """
<div class="glass-card" style="max-width: 420px; margin: 80px auto;">
    <div style="text-align: center; margin-bottom: 30px;">
        <h2 style="font-size: 2rem; margin-bottom: 8px;">Welcome Back</h2>
        <p style="color: var(--text-secondary);">Sign in to your roadmap dashboard</p>
    </div>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'warning' if category == 'warning' else 'info' }}">
                    <i class="fas fa-{% if category == 'error' %}exclamation-circle{% elif category == 'success' %}check-circle{% elif category == 'warning' %}exclamation-triangle{% else %}info-circle{% endif %}"></i>
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <form method="post">
        <div class="form-group">
            <div style="position: relative;">
                <i class="fas fa-user" style="position: absolute; left: 18px; top: 50%; transform: translateY(-50%); color: var(--text-muted);"></i>
                <input type="text" name="username" class="form-control" placeholder="Username" style="padding-left: 45px;" required>
            </div>
        </div>
        <div class="form-group">
            <div style="position: relative;">
                <i class="fas fa-lock" style="position: absolute; left: 18px; top: 50%; transform: translateY(-50%); color: var(--text-muted);"></i>
                <input type="password" name="password" class="form-control" placeholder="Password" style="padding-left: 45px;" required>
            </div>
        </div>
        <button type="submit" class="btn" style="width: 100%;">
            <i class="fas fa-sign-in-alt"></i> Sign In
        </button>
    </form>
    
    <div style="text-align: center; margin-top: 25px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
        <p style="color: var(--text-secondary); margin-bottom: 15px;">
            <a href="{{ url_for('forgot') }}" style="color: var(--accent-primary); text-decoration: none;">
                <i class="fas fa-key"></i> Forgot password?
            </a>
        </p>
        <p style="color: var(--text-secondary);">
            Don't have an account? 
            <a href="{{ url_for('register') }}" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">
                Create one here
            </a>
        </p>
    </div>
</div>
"""

TPL_REGISTER = """
<div class="glass-card" style="max-width: 420px; margin: 80px auto;">
    <div style="text-align: center; margin-bottom: 30px;">
        <h2 style="font-size: 2rem; margin-bottom: 8px;">Create Account</h2>
        <p style="color: var(--text-secondary);">Join us and start organizing your roadmaps</p>
    </div>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'warning' if category == 'warning' else 'info' }}">
                    <i class="fas fa-{% if category == 'error' %}exclamation-circle{% elif category == 'success' %}check-circle{% elif category == 'warning' %}exclamation-triangle{% else %}info-circle{% endif %}"></i>
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <form method="post">
        <div class="form-group">
            <div style="position: relative;">
                <i class="fas fa-user" style="position: absolute; left: 18px; top: 50%; transform: translateY(-50%); color: var(--text-muted);"></i>
                <input type="text" name="username" class="form-control" placeholder="Username" style="padding-left: 45px;" required>
            </div>
        </div>
        <div class="form-group">
            <div style="position: relative;">
                <i class="fas fa-lock" style="position: absolute; left: 18px; top: 50%; transform: translateY(-50%); color: var(--text-muted);"></i>
                <input type="password" name="password" class="form-control" placeholder="Password" style="padding-left: 45px;" required>
            </div>
        </div>
        <div class="form-group">
            <div style="position: relative;">
                <i class="fas fa-question-circle" style="position: absolute; left: 18px; top: 50%; transform: translateY(-50%); color: var(--text-muted);"></i>
                <input type="text" name="secret_q" class="form-control" placeholder="Secret question (e.g. Your middle name?)" style="padding-left: 45px;" required>
            </div>
        </div>
        <div class="form-group">
            <div style="position: relative;">
                <i class="fas fa-key" style="position: absolute; left: 18px; top: 50%; transform: translateY(-50%); color: var(--text-muted);"></i>
                <input type="text" name="secret_a" class="form-control" placeholder="Answer to secret question" style="padding-left: 45px;" required>
            </div>
        </div>
        <button type="submit" class="btn" style="width: 100%;">
            <i class="fas fa-user-plus"></i> Create Account
        </button>
    </form>
    
    <div style="text-align: center; margin-top: 25px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
        <p style="color: var(--text-secondary);">
            Already have an account? 
            <a href="{{ url_for('login') }}" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">
                Sign in here
            </a>
        </p>
    </div>
</div>
"""

TPL_FORGOT = """
<div class="glass-card" style="max-width: 420px; margin: 80px auto;">
    <div style="text-align: center; margin-bottom: 30px;">
        <h2 style="font-size: 2rem; margin-bottom: 8px;">Forgot Password</h2>
        <p style="color: var(--text-secondary);">Enter your username to recover your account</p>
    </div>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'warning' if category == 'warning' else 'info' }}">
                    <i class="fas fa-{% if category == 'error' %}exclamation-circle{% elif category == 'success' %}check-circle{% elif category == 'warning' %}exclamation-triangle{% else %}info-circle{% endif %}"></i>
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <form method="post">
        <div class="form-group">
            <div style="position: relative;">
                <i class="fas fa-user" style="position: absolute; left: 18px; top: 50%; transform: translateY(-50%); color: var(--text-muted);"></i>
                <input type="text" name="username" class="form-control" placeholder="Enter username" style="padding-left: 45px;" required>
            </div>
        </div>
        <button type="submit" class="btn" style="width: 100%;">
            <i class="fas fa-arrow-right"></i> Continue
        </button>
    </form>
    
    <div style="text-align: center; margin-top: 25px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
        <p style="color: var(--text-secondary);">
            Remember your password? 
            <a href="{{ url_for('login') }}" style="color: var(--accent-primary); text-decoration: none; font-weight: 600;">
                Back to login
            </a>
        </p>
    </div>
</div>
"""

TPL_FORGOT_Q = """
<div class="glass-card" style="max-width: 420px; margin: 80px auto;">
    <div style="text-align: center; margin-bottom: 30px;">
        <h2 style="font-size: 2rem; margin-bottom: 8px;">Answer Secret Question</h2>
        <p style="color: var(--text-secondary);">Please answer your security question to reset your password</p>
    </div>
    
    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin-bottom: 25px; text-align: center;">
        <h4 style="color: var(--accent-primary); margin-bottom: 10px;">Your Question:</h4>
        <p style="color: var(--text-primary); font-weight: 500;">{{ question }}</p>
    </div>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'warning' if category == 'warning' else 'info' }}">
                    <i class="fas fa-{% if category == 'error' %}exclamation-circle{% elif category == 'success' %}check-circle{% elif category == 'warning' %}exclamation-triangle{% else %}info-circle{% endif %}"></i>
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <form method="post" action="{{ url_for('reset') }}">
        <div class="form-group">
            <div style="position: relative;">
                <i class="fas fa-key" style="position: absolute; left: 18px; top: 50%; transform: translateY(-50%); color: var(--text-muted);"></i>
                <input type="text" name="answer" class="form-control" placeholder="Your answer" style="padding-left: 45px;" required>
            </div>
        </div>
        <div class="form-group">
            <div style="position: relative;">
                <i class="fas fa-lock" style="position: absolute; left: 18px; top: 50%; transform: translateY(-50%); color: var(--text-muted);"></i>
                <input type="password" name="newpass" class="form-control" placeholder="New password" style="padding-left: 45px;" required>
            </div>
        </div>
        <button type="submit" class="btn" style="width: 100%;">
            <i class="fas fa-redo"></i> Reset Password
        </button>
    </form>
</div>
"""

TPL_DASHBOARD = """
<div class="header">
    <div>
        <h1 class="welcome-text">{{ username }}'s Roadmap</h1>
        <p class="subtitle">Organize your goals and track your progress</p>
    </div>
    <a href="{{ url_for('logout') }}" class="btn btn-secondary">
        <i class="fas fa-sign-out-alt"></i> Logout
    </a>
</div>

{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="alert alert-{{ 'error' if category == 'error' else 'success' if category == 'success' else 'warning' if category == 'warning' else 'info' }}">
                <i class="fas fa-{% if category == 'error' %}exclamation-circle{% elif category == 'success' %}check-circle{% elif category == 'warning' %}exclamation-triangle{% else %}info-circle{% endif %}"></i>
                {{ message }}
            </div>
        {% endfor %}
    {% endif %}
{% endwith %}

<div class="stats-grid">
    <div class="stat-card">
        <h3>Total Tasks</h3>
        <p style="font-size: 2.5rem; font-weight: bold; margin: 10px 0;">{{ total_tasks }}</p>
        <small>All your active tasks</small>
    </div>
    <div class="stat-card success">
        <h3>Completed</h3>
        <p style="font-size: 2.5rem; font-weight: bold; margin: 10px 0;">{{ completed_tasks }}</p>
        <small>Tasks marked as done</small>
    </div>
    <div class="stat-card" style="background: linear-gradient(135deg, #f59e0b, #d97706);">
        <h3>Progress</h3>
        <p style="font-size: 2.5rem; font-weight: bold; margin: 10px 0;">
            {{ (completed_tasks / total_tasks * 100)|round|int if total_tasks > 0 else 0 }}%
        </p>
        <small>Overall completion</small>
    </div>
</div>

<div class="dashboard-grid">
    <!-- Categories Sidebar -->
    <div class="categories-sidebar">
        <h3 style="margin-bottom: 20px; color: var(--text-primary);">
            <i class="fas fa-map"></i> Your Roadmaps
        </h3>
        
        <div class="glass-card" style="margin-bottom: 20px;">
            <h4 style="margin-bottom: 15px; color: var(--text-primary);">
                <i class="fas fa-plus"></i> Add New Roadmap
            </h4>
            <form method="post" action="{{ url_for('add_category') }}">
                <div class="form-group">
                    <input type="text" name="name" class="form-control" placeholder="Roadmap name (e.g., Study Plan)" required>
                </div>
                <div class="form-group">
                    <textarea name="description" class="form-control" placeholder="Description (optional)" rows="2"></textarea>
                </div>
                <div class="form-group">
                    <label style="display: block; margin-bottom: 8px; font-weight: 500; color: var(--text-secondary);">
                        <i class="fas fa-palette"></i> Color:
                    </label>
                    <input type="color" name="color" value="#6366f1" style="width: 100%; height: 45px; border-radius: 10px; border: 2px solid rgba(255, 255, 255, 0.1); background: rgba(255, 255, 255, 0.05);">
                </div>
                <button type="submit" class="btn" style="width: 100%;">
                    <i class="fas fa-plus-circle"></i> Create Roadmap
                </button>
            </form>
        </div>

        {% if categories %}
            <h4 style="margin-bottom: 15px; color: var(--text-primary);">
                <i class="fas fa-list"></i> Your Roadmaps
            </h4>
            {% for category in categories %}
                <div class="category-item" style="border-left-color: {{ category.color }};">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="flex: 1;">
                            <strong style="color: var(--text-primary);">{{ category.name }}</strong>
                            {% if category.description %}
                                <p style="margin: 5px 0 0 0; font-size: 12px; color: var(--text-muted);">{{ category.description }}</p>
                            {% endif %}
                        </div>
                        <form method="post" action="{{ url_for('delete_category', cid=category.id) }}" style="display: inline; margin-left: 10px;">
                            <button type="submit" class="btn btn-danger btn-small" onclick="return confirm('Delete this roadmap and all its tasks?')">
                                <i class="fas fa-times"></i>
                            </button>
                        </form>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div style="text-align: center; padding: 30px; color: var(--text-muted);">
                <i class="fas fa-map-marked-alt" style="font-size: 3rem; margin-bottom: 15px; opacity: 0.5;"></i>
                <p>No roadmaps yet. Create your first one!</p>
            </div>
        {% endif %}
    </div>

    <!-- Main Content -->
    <div>
        <div class="tab-buttons">
            <button class="tab-button active" onclick="switchTab('single')">
                <i class="fas fa-plus-circle"></i> Add Single Task
            </button>
            <button class="tab-button" onclick="switchTab('bulk')">
                <i class="fas fa-bolt"></i> Bulk Import
            </button>
        </div>

        <div id="single-tab" class="tab-content active">
            <div class="glass-card">
                <h3 style="margin-bottom: 15px; color: var(--text-primary);">
                    <i class="fas fa-tasks"></i> Add New Task
                </h3>
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
                    <button type="submit" class="btn">
                        <i class="fas fa-plus"></i> Add Task
                    </button>
                </form>
            </div>
        </div>

        <div id="bulk-tab" class="tab-content">
            <div class="glass-card">
                <h3 style="margin-bottom: 15px; color: var(--text-primary);">
                    <i class="fas fa-bolt"></i> Bulk Import Tasks
                </h3>
                <form method="post" action="{{ url_for('bulk_import') }}">
                    <div class="form-group">
                        <textarea name="bulk_text" class="form-control" placeholder="Paste your roadmap here...&#10;&#10;Examples:&#10;Web Development = HTML Basics, CSS Styling, JavaScript&#10;Data Science: Python | Pandas | Machine Learning&#10;- Math Homework&#10;- Physics Lab" rows="8" required></textarea>
                    </div>
                    <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                        <button type="submit" class="btn btn-info">
                            <i class="fas fa-upload"></i> Import Roadmap
                        </button>
                        <button type="button" class="btn btn-secondary" onclick="showImportExamples()">
                            <i class="fas fa-question-circle"></i> Format Examples
                        </button>
                    </div>
                </form>
                <div class="import-example">
                    <strong><i class="fas fa-lightbulb"></i> Supported formats:</strong><br>
                    • <code>Category = Task1, Task2, Task3</code><br>
                    • <code>Category: Task1 | Task2 | Task3</code><br>
                    • Bullet points with <code>- Task</code> or <code>* Task</code>
                </div>
            </div>
        </div>

        <h2 style="margin-bottom: 20px; color: var(--text-primary); margin-top: 30px;">
            <i class="fas fa-list-check"></i> Your Tasks
        </h2>
        {% if tasks %}
            <div class="task-grid">
                {% for t in tasks %}
                    <div class="task-card {% if t['done'] %}done{% endif %}" id="task-{{ t['id'] }}">
                        {% if t['category_name'] %}
                            <div class="category-badge">
                                <i class="fas fa-tag"></i> {{ t['category_name'] }}
                            </div>
                        {% endif %}
                        <div class="task-title" style="font-weight: 600; margin-bottom: 10px; font-size: 1.1rem; color: var(--text-primary);">{{ t['title'] }}</div>
                        {% if t['notes'] %}
                            <div style="color: var(--text-secondary); margin-bottom: 12px; line-height: 1.5;">{{ t['notes'] }}</div>
                        {% endif %}
                        {% if t['done'] %}
                            <div style="color: var(--accent-success); font-size: 0.9rem; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                                <i class="fas fa-check-circle"></i>
                                {% if t.done_at %}
                                    Completed at {{ t.done_at[:16] }}
                                {% else %}
                                    Completed
                                {% endif %}
                            </div>
                        {% else %}
                            <div style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                                <i class="fas fa-clock"></i>
                                {% if t.created_at %}
                                    Created: {{ t.created_at[:16] }}
                                {% else %}
                                    Created: Recently
                                {% endif %}
                            </div>
                        {% endif %}
                        <div class="task-actions">
                            {% if t['done'] %}
                                <button onclick="undoTask({{ t['id'] }})" class="btn btn-secondary btn-small">
                                    <i class="fas fa-undo"></i> Undo
                                </button>
                            {% else %}
                                <button onclick="markTaskDone({{ t['id'] }})" class="btn btn-success btn-small">
                                    <i class="fas fa-check"></i> Mark Done
                                </button>
                                <button onclick="toggleEdit({{ t['id'] }})" class="btn btn-small">
                                    <i class="fas fa-edit"></i> Edit
                                </button>
                            {% endif %}
                            <form method="post" action="{{ url_for('delete_task', tid=t['id']) }}" style="display: inline;">
                                <button type="submit" class="btn btn-danger btn-small" onclick="return confirm('Are you sure you want to delete this task?')">
                                    <i class="fas fa-trash"></i> Delete
                                </button>
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
                                    <button type="submit" class="btn">
                                        <i class="fas fa-save"></i> Save Changes
                                    </button>
                                    <button type="button" class="btn btn-secondary" onclick="toggleEdit({{ t['id'] }})">
                                        <i class="fas fa-times"></i> Cancel
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                {% endfor %}
            </div>
        {% else %}
            <div class="glass-card" style="text-align: center; padding: 50px 30px;">
                <i class="fas fa-tasks" style="font-size: 4rem; color: var(--text-muted); margin-bottom: 20px; opacity: 0.5;"></i>
                <h3 style="color: var(--text-muted); margin-bottom: 15px;">No tasks yet</h3>
                <p style="color: var(--text-secondary);">Start by adding your first task above!</p>
            </div>
        {% endif %}
    </div>
</div>
"""

TPL_404 = """
<div class="glass-card" style="text-align: center; max-width: 500px; margin: 100px auto; padding: 50px 30px;">
    <i class="fas fa-compass" style="font-size: 4rem; color: var(--accent-primary); margin-bottom: 20px;"></i>
    <h1 style="font-size: 4rem; color: var(--accent-primary); margin-bottom: 20px;">404</h1>
    <h2 style="margin-bottom: 20px; color: var(--text-primary);">Page Not Found</h2>
    <p style="margin-bottom: 30px; color: var(--text-secondary);">The page you're looking for doesn't exist or has been moved.</p>
    <a href="{{ url_for('dashboard') }}" class="btn">
        <i class="fas fa-home"></i> Go to Dashboard
    </a>
</div>
"""

TPL_500 = """
<div class="glass-card" style="text-align: center; max-width: 500px; margin: 100px auto; padding: 50px 30px;">
    <i class="fas fa-exclamation-triangle" style="font-size: 4rem; color: var(--accent-danger); margin-bottom: 20px;"></i>
    <h1 style="font-size: 4rem; color: var(--accent-danger); margin-bottom: 20px;">500</h1>
    <h2 style="margin-bottom: 20px; color: var(--text-primary);">Internal Server Error</h2>
    <p style="margin-bottom: 30px; color: var(--text-secondary);">Something went wrong on our end. Please try again later.</p>
    <a href="{{ url_for('dashboard') }}" class="btn">
        <i class="fas fa-home"></i> Go to Dashboard
    </a>
</div>
"""

# ---------- DB Helpers ----------
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
            color TEXT DEFAULT '#6366f1',
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
            color TEXT DEFAULT '#6366f1',
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

# ---------- Auth helpers ----------
def current_user():
    if 'user_id' in session:
        user = fetch_one('SELECT * FROM users WHERE id=%s', (session['user_id'],))
        return user
    return None

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# ---------- Helper Functions ----------
def get_current_date():
    return datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

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

def render_with_footer(template, **kwargs):
    footer = TPL_FOOTER.replace('{{ current_date }}', get_current_date())\
                      .replace('{{ portfolio_url }}', PORTFOLIO_URL)\
                      .replace('{{ github_url }}', GITHUB_URL)\
                      .replace('{{ linkedin_url }}', LINKEDIN_URL)\
                      .replace('{{ contact_email }}', CONTACT_EMAIL)
    
    return render_template_string(TPL_BASE.replace('{{content}}', template).replace('{{footer}}', footer), **kwargs)

# ---------- Routes ----------
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
    
    return render_with_footer(TPL_REGISTER)

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
    
    return render_with_footer(TPL_LOGIN)

@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if current_user():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        user = fetch_one('SELECT * FROM users WHERE username=%s', (username,))
        if user:
            session['reset_user'] = user['id']
            return render_with_footer(TPL_FORGOT_Q, question=user['secret_question'])
        flash('Username not found.', 'error')
    
    return render_with_footer(TPL_FORGOT)

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
        return render_with_footer(TPL_FORGOT_Q, question=user['secret_question'])
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
    return render_with_footer(TPL_FORGOT_Q, question=user['secret_question'])

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
    
    return render_with_footer(TPL_DASHBOARD, 
                            tasks=tasks,
                            categories=categories,
                            username=user['username'],
                            total_tasks=total_tasks,
                            completed_tasks=completed_tasks)

@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name','').strip()
    description = request.form.get('description','').strip()
    color = request.form.get('color', '#6366f1')
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
        colors = ['#6366f1', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444', '#06b6d4']
        
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

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_with_footer(TPL_404), 404

@app.errorhandler(500)
def internal_error(error):
    return render_with_footer(TPL_500), 500

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)