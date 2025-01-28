from gevent import monkey
monkey.patch_all()

from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer

import os
import sys
import paramiko
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from flask_socketio import SocketIO, emit
from flask import request, jsonify, Flask
from io import StringIO

import threading


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'  # Klucz secret do Flask-SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")  # Umożliwia połączenia z dowolnego źródła

# Przechowuj połączenia SSH w słowniku (kluczem jest ID sesji)
ssh_connections = {}

@app.route('/ssh/connect', methods=['POST'])
def ssh_connect():
    print('ssh_connect')
    ssh_connection = paramiko.SSHClient()
    data = request.json
    hostname = data['hostname']
    port = data.get('port', 22)
    username = data['username']
    password = data.get('password')
    private_key = data.get('private_key')

    print('paramiko')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print('ssh')
    # ssh.connect(hostname=hostname, port=port, username=username, password=password)
    try:
        if private_key:
            key_file = StringIO(private_key)
            private_key = paramiko.RSAKey.from_private_key(key_file)
            ssh.connect(hostname, port=port, username=username, pkey=private_key)
        else:
            ssh.connect(hostname, port=port, username=username, password=password)

        print('status: connected')
        return jsonify({"status": "connected"}), 200
    except Exception as e:
        print('status: failed', e)
        return jsonify({"status": "error", "message": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected:', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected:', request.sid)
    if request.sid in ssh_connections:
        ssh_connection = ssh_connections[request.sid]
        if 'ssh' in ssh_connection:
            ssh_connection['ssh'].close()
        del ssh_connections[request.sid]

@socketio.on('ssh_connect')
def handle_ssh_connect(data):
    print('Client connected:', data)
    hostname = data['hostname']
    port = data.get('port', 22)
    username = data['username']
    password = data['password']
    private_key = data.get('private_key')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if private_key:
            key_file = StringIO(private_key)
            private_key = paramiko.RSAKey.from_private_key(key_file)
            ssh.connect(hostname, port=port, username=username, pkey=private_key)
        else:
            ssh.connect(hostname, port=port, username=username, password=password)

        # Uruchom interaktywny shell
        shell = ssh.invoke_shell()
        shell.setblocking(0)  # Ustaw tryb nieblokujący

        # Zapisz shell w słowniku
        ssh_connections[request.sid] = {'ssh': ssh, 'shell': shell}

        # Uruchom wątek do odczytywania danych z shell-a
        threading.Thread(target=read_shell_output, args=(request.sid, shell)).start()

        emit('ssh-status', {'status': 'connected'})
    except Exception as e:
        print(f"SSH connection error: {e}")
        emit('ssh-status', {'status': 'error', 'message': str(e)})
        if ssh:
            ssh.close()

def read_shell_output(sid, shell):
    """
    Funkcja do odczytywania danych z shell-a i wysyłania ich do klienta.
    """
    while True:
        if sid not in ssh_connections:
            break  # Zakończ, jeśli klient się rozłączył

        try:
            # Odczytaj dane z shell-a
            if shell.recv_ready():
                output = shell.recv(1024).decode('utf-8')
                socketio.emit('ssh_output', {'output': output}, room=sid)
        except Exception as e:
            print(f"Error reading shell output: {e}")
            if sid in ssh_connections:
                ssh_connections[sid]['ssh'].close()
                del ssh_connections[sid]
            break

@socketio.on('resize')
def handle_resize(data):
    if request.sid in ssh_connections:
        shell = ssh_connections[request.sid]['shell']
        try:
            shell.resize_pty(width=data['cols'], height=data['rows'])
        except Exception as e:
            print(f"Error resizing terminal: {e}")

@socketio.on('ssh_command')
def handle_ssh_command(data):
    print('Client connected:', data)
    command = data['command']
    ssh = ssh_connections.get(request.sid)

    if ssh:
        try:
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            emit('ssh_output', {'output': output, 'error': error})
        except Exception as e:
            emit('ssh_output', {'output': '', 'error': str(e)})
    else:
        emit('ssh_output', {'output': '', 'error': 'SSH connection not established'})

@socketio.on('ssh_input')
def handle_input_command(data):
    input_data = data['input']
    if request.sid in ssh_connections:
        shell = ssh_connections[request.sid]['shell']
        try:
            # Wyślij dane do shell-a
            shell.send(input_data)
        except Exception as e:
            emit('pty-output', {'output': '', 'error': str(e)})

socketio.init_app(app)

if __name__ == '__main__':
    # Używamy WSGIServer z gevent-websocket
    server = WSGIServer(('0.0.0.0', 5000), app,
                       handler_class=WebSocketHandler)
    server.serve_forever()