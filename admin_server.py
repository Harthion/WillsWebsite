from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import os

app = Flask(__name__)

PASSCODE = 'letmein'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper to read index.html
with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    INDEX_TEMPLATE = f.read()

ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Editor - William Kazimir Jurek</title>
    <style>
        body { background: #0a0a0a; color: #fff; font-family: 'Helvetica', Arial, sans-serif; }
        .container { max-width: 1200px; margin: 40px auto; background: #181818; border-radius: 20px; padding: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { text-align: center; margin-bottom: 2rem; }
        .tabs { display: flex; gap: 1rem; margin-bottom: 2rem; }
        .tab-btn { background: #222; color: #fff; border: none; padding: 1rem 2rem; border-radius: 10px 10px 0 0; cursor: pointer; font-weight: 600; }
        .tab-btn.active { background: linear-gradient(45deg, #ff6b6b, #ff8e8e); color: #fff; }
        .tab-content { display: none; background: #222; border-radius: 0 0 10px 10px; padding: 2rem; }
        .tab-content.active { display: block; }
        .editable { background: #333; border: 1px dashed #ff6b6b; border-radius: 8px; padding: 1rem; min-height: 2rem; margin-bottom: 1rem; color: #fff; }
        .img-list { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
        .img-list img { max-width: 180px; border-radius: 10px; background: #111; }
        .img-list .img-wrap { position: relative; }
        .img-list .remove-img { position: absolute; top: 5px; right: 5px; background: #ff4444; color: #fff; border: none; border-radius: 5px; padding: 2px 8px; cursor: pointer; }
        .save-btn { background: linear-gradient(45deg, #ff6b6b, #ff8e8e); color: #fff; border: none; padding: 1rem 2.5rem; border-radius: 50px; font-weight: 700; cursor: pointer; font-size: 1.1rem; margin-top: 2rem; display: block; margin-left: auto; }
        .logout-btn { background: #444; color: #fff; border: none; padding: 0.7rem 2rem; border-radius: 8px; font-weight: 600; cursor: pointer; float: right; }
        .upload-input { margin-bottom: 1rem; }
        .msg { color: #ff6b6b; text-align: center; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <button class="logout-btn" onclick="window.location.href='/admin_logout'">Logout</button>
        <h1>Admin Editor</h1>
        {% if msg %}<div class="msg">{{ msg }}</div>{% endif %}
        <form method="POST" enctype="multipart/form-data">
            <div class="tabs">
                <button type="button" class="tab-btn active" onclick="showTab('home')">Home</button>
                <button type="button" class="tab-btn" onclick="showTab('about')">About</button>
                <button type="button" class="tab-btn" onclick="showTab('photography')">Photography</button>
                <button type="button" class="tab-btn" onclick="showTab('cinematography')">Cinematography</button>
                <button type="button" class="tab-btn" onclick="showTab('music')">Music</button>
                <button type="button" class="tab-btn" onclick="showTab('contact')">Contact</button>
            </div>
            <div id="home" class="tab-content active">
                <h2>Home Section</h2>
                <div>Title:</div>
                <div class="editable" contenteditable="true" name="home_title">{{ home_title }}</div>
                <div>Subtitle:</div>
                <div class="editable" contenteditable="true" name="home_subtitle">{{ home_subtitle }}</div>
            </div>
            <div id="about" class="tab-content">
                <h2>About Section</h2>
                <div>About Text:</div>
                <div class="editable" contenteditable="true" name="about_text">{{ about_text }}</div>
            </div>
            <div id="photography" class="tab-content">
                <h2>Photography Section</h2>
                <div>Photography Description:</div>
                <div class="editable" contenteditable="true" name="photography_text">{{ photography_text }}</div>
                <div>Images:</div>
                <div class="img-list" id="photography_imgs">
                    {% for img in photography_imgs %}
                    <div class="img-wrap"><img src="/static/uploads/{{ img }}"><button type="button" class="remove-img" onclick="removeImg(this, '{{ img }}', 'photography')">x</button></div>
                    {% endfor %}
                </div>
                <input class="upload-input" type="file" name="photography_uploads" accept="image/*" multiple>
            </div>
            <div id="cinematography" class="tab-content">
                <h2>Cinematography Section</h2>
                <div>Cinematography Description:</div>
                <div class="editable" contenteditable="true" name="cinematography_text">{{ cinematography_text }}</div>
            </div>
            <div id="music" class="tab-content">
                <h2>Music Section</h2>
                <div>Music Description:</div>
                <div class="editable" contenteditable="true" name="music_text">{{ music_text }}</div>
                <div>Music Files:</div>
                <div class="img-list" id="music_files">
                    {% for music in music_files %}
                    <div class="img-wrap"><a href="/static/uploads/{{ music }}" target="_blank">{{ music }}</a><button type="button" class="remove-img" onclick="removeImg(this, '{{ music }}', 'music')">x</button></div>
                    {% endfor %}
                </div>
                <input class="upload-input" type="file" name="music_uploads" accept="audio/*" multiple>
            </div>
            <div id="contact" class="tab-content">
                <h2>Contact Section</h2>
                <div>Contact Info:</div>
                <div class="editable" contenteditable="true" name="contact_text">{{ contact_text }}</div>
            </div>
            <input type="hidden" name="section_data" id="section_data">
            <button class="save-btn" type="submit">Save Changes</button>
        </form>
    </div>
    <script>
        function showTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(tabC => tabC.classList.remove('active'));
            document.querySelector('.tab-btn[onclick*="'+tab+'"]').classList.add('active');
            document.getElementById(tab).classList.add('active');
        }
        // Before submit, collect all editable content
        document.querySelector('form').addEventListener('submit', function(e) {
            let data = {};
            document.querySelectorAll('.editable').forEach(el => {
                data[el.getAttribute('name')] = el.innerHTML;
            });
            document.getElementById('section_data').value = JSON.stringify(data);
        });
        // Remove image/music (AJAX)
        function removeImg(btn, filename, section) {
            fetch('/admin_remove_file', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename, section })
            }).then(() => btn.parentElement.remove());
        }
    </script>
</body>
</html>
'''

# Helper to extract and update editable content from index.html
EDIT_MARKERS = {
    'home_title': ('<h1>', '</h1>'),
    'home_subtitle': ('<p>', '</p>'),
    'about_h2': ('<h2>', '</h2>'),
    'about_p1': ('<p>', '</p>'),
    'about_p2': ('<p>', '</p>'),
    'about_p3': ('<p>', '</p>'),
    # Add more markers as needed for other sections
}

def extract_content(html):
    content = {}
    idx = 0
    for key, (start_tag, end_tag) in EDIT_MARKERS.items():
        start = html.find(start_tag, idx)
        if start == -1:
            content[key] = ''
            continue
        start += len(start_tag)
        end = html.find(end_tag, start)
        content[key] = html[start:end].strip()
        idx = end + len(end_tag)
    return content

def update_content(html, updates):
    idx = 0
    for key, (start_tag, end_tag) in EDIT_MARKERS.items():
        if key in updates:
            start = html.find(start_tag, idx)
            if start == -1:
                continue
            start += len(start_tag)
            end = html.find(end_tag, start)
            html = html[:start] + updates[key] + html[end:]
            idx = start + len(updates[key]) + len(end_tag)
    return html

from flask import session
app.secret_key = 'supersecretkey'

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    msg = ''
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
    content = extract_content(html)
    if request.method == 'POST':
        updates = {}
        for key in EDIT_MARKERS:
            updates[key] = request.form.get(key, '')
        new_html = update_content(html, updates)
        with open(INDEX_PATH, 'w', encoding='utf-8') as f:
            f.write(new_html)
        msg = 'Changes saved!'
        content = extract_content(new_html)
    # Use the same CSS and structure as index.html, but make fields editable
    admin_html = html
    # Replace editable fields with contenteditable divs inside a form
    for key, (start_tag, end_tag) in EDIT_MARKERS.items():
        value = content[key]
        editable = f'<div contenteditable="true" class="admin-edit" id="{key}">{value}</div>'
        admin_html = admin_html.replace(f'{start_tag}{value}{end_tag}', f'{start_tag}{editable}{end_tag}')
    # Add save button and script to collect edits
    admin_html = admin_html.replace('</body>', '''
    <form id="adminForm" method="POST" style="position:fixed;bottom:30px;right:30px;z-index:3000;background:#222;padding:20px;border-radius:20px;">
        <button type="submit" style="background:linear-gradient(45deg,#ff6b6b,#ff8e8e);color:#fff;border:none;padding:14px 28px;border-radius:50px;font-weight:700;cursor:pointer;font-size:1rem;">Save Changes</button>
        <span style="color:#ff6b6b;margin-left:20px;">''' + msg + '''</span>
    </form>
    <script>
    document.getElementById('adminForm').addEventListener('submit', function(e) {
        e.preventDefault();
        var form = this;
        var data = {};
        document.querySelectorAll('.admin-edit').forEach(function(div) {
            data[div.id] = div.innerHTML;
        });
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onload = function() { if (xhr.status == 200) location.reload(); };
        xhr.send(Object.keys(data).map(function(k){return encodeURIComponent(k)+'='+encodeURIComponent(data[k]);}).join('&'));
    });
    </script>
    </body>''')
    # Remove the floating admin button if present
    admin_html = admin_html.replace('<a href="admin.html" class="admin-link-btn" style="position:fixed;bottom:30px;right:30px;z-index:2000;text-decoration:none;">\n        <button style="background:linear-gradient(45deg,#ff6b6b,#ff8e8e);color:#fff;border:none;padding:14px 28px;border-radius:50px;font-weight:700;box-shadow:0 4px 16px rgba(0,0,0,0.2);cursor:pointer;font-size:1rem;transition:all 0.2s;">Admin</button>\n    </a>', '')
    return admin_html

def is_admin_logged_in():
    return session.get('admin_logged_in')

@app.route('/')
def index():
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
    content = extract_content(html)
    return render_template_string(html, **content)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSCODE:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
    return '''
    <form method="POST" style="background:#222;padding:2rem;border-radius:10px;max-width:400px;margin:100px auto;color:#fff;">
        <h2 style="text-align:center;">Admin Login</h2>
        <div style="margin-bottom:1rem;">
            <label for="password" style="display:block;margin-bottom:0.5rem;">Password:</label>
            <input type="password" name="password" id="password" required style="width:100%;padding:0.7rem;border:none;border-radius:5px;background:#333;color:#fff;">
        </div>
        <button type="submit" style="width:100%;padding:0.7rem;border:none;border-radius:5px;background:linear-gradient(45deg,#ff6b6b,#ff8e8e);color:#fff;font-weight:bold;cursor:pointer;">Login</button>
    </form>
    '''

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/admin_remove_file', methods=['POST'])
def admin_remove_file():
    data = request.get_json()
    filename = data.get('filename')
    section = data.get('section')
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
        return ('', 204)
    return ('', 404)

if __name__ == '__main__':
    app.run(debug=True)
