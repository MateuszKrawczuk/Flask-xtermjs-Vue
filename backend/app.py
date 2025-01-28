import threading
import time

from flask import Flask, Response, request, jsonify
from flask_socketio import SocketIO, emit
import paramiko
from io import StringIO
import logging 
import sys

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)

_logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'  # Klucz secret do Flask-SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")  # Umożliwia połączenia z dowolnego źródła

# Przechowuj połączenia SSH w słowniku (kluczem jest ID sesji)
ssh_connections = {}

@app.route('/ssh/connect', methods=['POST'])
def ssh_connect() -> tuple[Response, int]:
    _logger.debug('ssh_connect')
    data = request.json
    hostname = data['hostname']
    port = data.get('port', 22)
    username = data['username']
    password = data.get('password')
    private_key = data.get('private_key')

    _logger.debug('paramiko')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    _logger.debug('ssh')
    try:
        if private_key:
            key_file = StringIO(private_key)
            private_key = paramiko.RSAKey.from_private_key(key_file)
            ssh.connect(hostname, port=port, username=username, pkey=private_key)
        else:
            ssh.connect(hostname, port=port, username=username, password=password)

        _logger.info('status: connected')
        return jsonify({"status": "connected"}), 200
    except Exception as e:
        _logger.exception('status: failed')
        return jsonify({"status": "error", "message": str(e)}), 500

@socketio.on('connect')
def handle_connect() -> None:
    _logger.info(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect() -> None:
    _logger.info(f'Client disconnected: {request.sid}')
    if request.sid in ssh_connections:
        ssh_connection = ssh_connections[request.sid]
        if 'ssh' in ssh_connection:
            ssh_connection['ssh'].close()
        del ssh_connections[request.sid]

@socketio.on('ssh_connect')
def handle_ssh_connect(data) -> None:
    _logger.info(f'Client connected: {data}')
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
        _logger.exception("SSH connection error:")
        emit('ssh-status', {'status': 'error', 'message': str(e)})
        if ssh:
            ssh.close()

def read_shell_output(sid, shell) -> None:
    """
    Funkcja do odczytywania danych z shell-a i wysyłania ich do klienta.
    """
    while sid in ssh_connections: # Kontynuuj, dopóki istnieje połączenie
        try:
            # Odczytaj dane z shell-a
            if shell.recv_ready():
                output = shell.recv(1024).decode('utf-8')
                socketio.emit('ssh_output', {'output': output}, room=sid)
        except Exception as e:
            _logger.exception("Error reading shell output:")
            if sid in ssh_connections:
                ssh_connections[sid]['ssh'].close()
                del ssh_connections[sid]
            return
        
        time.sleep(0.005)  # Znacząca redukcja obciążenia CPU dzięki redukcji nadmiernej ilości iteracji

@socketio.on('resize')
def handle_resize(data) -> None:
    if request.sid in ssh_connections:
        shell = ssh_connections[request.sid]['shell']
        try:
            shell.resize_pty(width=data['cols'], height=data['rows'])
        except Exception:
            _logger.exception("Error resizing terminal:")

@socketio.on('ssh_command')
def handle_ssh_command(data) -> None:
    _logger.info(f'Client connected: {data}')
    command = data['command']
    ssh = ssh_connections.get(request.sid)

    if ssh:
        try:
            _, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            emit('ssh_output', {'output': output, 'error': error})
        except Exception as e:
            emit('ssh_output', {'output': '', 'error': str(e)})
    else:
        emit('ssh_output', {'output': '', 'error': 'SSH connection not established'})

@socketio.on('ssh_input')
def handle_input_command(data) -> None:
    input_data = data['input']
    if request.sid in ssh_connections:
        shell = ssh_connections[request.sid]['shell']
        try:
            # Wyślij dane do shell-a
            shell.send(input_data)
        except Exception as e:
            emit('pty-output', {'output': '', 'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True)