from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

HTML_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Instagram Follow Requests</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f3f4f6;
      margin: 0;
      padding: 20px;
    }
    .container {
      max-width: 700px;
      margin: auto;
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    h1 {
      text-align: center;
    }
    .search-bar {
      width: 100%;
      padding: 10px;
      margin-bottom: 15px;
    }
    .request {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #eee;
      padding: 10px 0;
    }
    .actions button {
      padding: 6px 10px;
      margin-left: 5px;
      border: none;
      border-radius: 6px;
      color: white;
      cursor: pointer;
    }
    .accept { background: #10b981; }
    .decline { background: #ef4444; }
    .status { font-weight: bold; }
  </style>
</head>
<body>
  <div class="container">
    <h1>📸 Instagram Follow Requests</h1>
    <input class="search-bar" placeholder="🔍 Search..." oninput="filterRequests(this.value)" />
    <div id="requests"></div>
  </div>

<script>
let requests = [];

function fetchRequests() {
  fetch('/api/requests')
    .then(res => res.json())
    .then(data => {
      requests = data;
      render();
    });
}

function render() {
  const container = document.getElementById('requests');
  container.innerHTML = '';
  requests.forEach(req => {
    const div = document.createElement('div');
    div.className = 'request';
    div.dataset.user = req.username.toLowerCase();
    div.innerHTML = `
      <div>
        <strong>${req.fullName}</strong> (@${req.username})<br>
        <small>${req.time}</small>
      </div>
      <div>
        ${req.status === 'pending' ? `
          <button class="accept" onclick="act('${req.username}', 'accept')">Accept</button>
          <button class="decline" onclick="act('${req.username}', 'decline')">Decline</button>
        ` : `<span class="status">${req.status.toUpperCase()}</span>`}
      </div>
    `;
    container.appendChild(div);
  });
}

function act(username, action) {
  fetch(`/api/requests/${username}/${action}`, { method: 'POST' })
    .then(() => fetchRequests());
}

function filterRequests(query) {
  document.querySelectorAll('.request').forEach(r => {
    r.style.display = r.dataset.user.includes(query.toLowerCase()) ? '' : 'none';
  });
}

fetchRequests();
</script>
</body>
</html>
'''

# ------------------------
# DATABASE SETUP
# ------------------------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS follow_requests (
            username TEXT PRIMARY KEY,
            full_name TEXT,
            time TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')
    # Prepopulate if empty
    c.execute("SELECT COUNT(*) FROM follow_requests")
    if c.fetchone()[0] == 0:
        sample_data = [
            ('travelgirl_23', 'Aisha Khan', '2 mins ago'),
            ('coder_boy', 'Rohan Das', '5 mins ago'),
            ('art_life', 'Neha Mehta', '10 mins ago'),
            ('moto_dude', 'Sarthak Verma', '15 mins ago'),
            ('bookworm101', 'Anjali Sharma', '20 mins ago')
        ]
        c.executemany('INSERT INTO follow_requests (username, full_name, time) VALUES (?, ?, ?)', sample_data)
    conn.commit()
    conn.close()

# ------------------------
# ROUTES
# ------------------------
@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/requests')
def get_requests():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT username, full_name, time, status FROM follow_requests')
    rows = c.fetchall()
    conn.close()
    return jsonify([
        {'username': u, 'fullName': n, 'time': t, 'status': s} for u, n, t, s in rows
    ])

@app.route('/api/requests/<username>/<action>', methods=['POST'])
def update_status(username, action):
    if action not in ['accept', 'decline']:
        return jsonify({'error': 'Invalid action'}), 400
    status = 'accepted' if action == 'accept' else 'declined'
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE follow_requests SET status = ? WHERE username = ?', (status, username))
    conn.commit()
    conn.close()
    return jsonify({'status': 'updated'})

# ------------------------
# WSGI ENTRY POINT
# ------------------------
init_db()  # Ensures DB is ready

if __name__ == '__main__':
    app.run(debug=True)
