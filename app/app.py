from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import os
import re
import html

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")

# Load from environment
# USERNAME = os.getenv("APP_USERNAME")
# PASSWORD = os.getenv("APP_PASSWORD")

def validate_search_input(search_term):
    """
    Validate search input to prevent XSS and SQL injection attacks
    Returns True if input is safe, False otherwise
    """
    if not search_term or not search_term.strip():
        return False
    
    # Check for common XSS patterns
    xss_patterns = [
        r'<script.*?>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
        r'<link',
        r'<meta',
        r'vbscript:',
        r'data:text/html'
    ]
    
    # Check for SQL injection patterns
    sql_patterns = [
        r'union\s+select',
        r'drop\s+table',
        r'delete\s+from',
        r'insert\s+into',
        r'update\s+set',
        r'exec\s*\(',
        r'execute\s*\(',
        r'sp_\w+',
        r'xp_\w+',
        r'--',
        r'/\*.*?\*/',
        r"'.*?'",
        r'".*?"',
        r';\s*\w+'
    ]
    
    search_lower = search_term.lower()
    
    # Check for XSS patterns
    for pattern in xss_patterns:
        if re.search(pattern, search_lower, re.IGNORECASE):
            return False
    
    # Check for SQL injection patterns
    for pattern in sql_patterns:
        if re.search(pattern, search_lower, re.IGNORECASE):
            return False
    
    # Additional checks for suspicious characters
    suspicious_chars = ['<', '>', '"', "'", ';', '(', ')', '{', '}']
    if any(char in search_term for char in suspicious_chars):
        return False
    
    return True

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        
        if not validate_search_input(search_term):
            flash('Invalid search term. Please enter a valid search query without special characters.', 'error')
            return render_template('home.html')
        
        # If validation passes, redirect to search results
        return redirect(url_for('search_results', query=search_term))
    
    return render_template('home.html')

@app.route('/search')
def search_results():
    query = request.args.get('query', '')
    # Escape the query for safe display
    safe_query = html.escape(query)
    return render_template('search_results.html', search_term=safe_query)

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     if data.get('username') == USERNAME and data.get('password') == PASSWORD:
#         return jsonify({"message": "Login successful"})
#     else:
#         return jsonify({"message": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)