from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import os
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr
    return ip

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/collect', methods=['POST'])
def collect():
    device_id = request.form['device_id']
    log_data = request.form['log_data']
    ip_address = get_client_ip()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"{LOG_DIR}/{device_id}_{timestamp}.log"
    with open(log_filename, 'w') as log_file:
        log_file.write(f"IP Address: {ip_address}\n{log_data}")
    socketio.emit('new_log', {'filename': log_filename, 'content': log_data, 'ip': ip_address})
    return jsonify({"status": "success", "message": "Log received", "ip": ip_address})

@app.route('/logs')
def logs():
    logs = []
    for log_file in os.listdir(LOG_DIR):
        with open(os.path.join(LOG_DIR, log_file), 'r') as file:
            content = file.read()
            ip_address = content.split('\n')[0].replace('IP Address: ', '')
            logs.append({'filename': log_file, 'content': content, 'ip': ip_address})
    return jsonify(logs)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

