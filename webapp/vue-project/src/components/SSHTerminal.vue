<template>
  <div>
    <!-- Formularz do nawiązywania połączenia -->
    <div v-if="!isConnected">
      <div>
        <label for="hostname">Adres:</label>
        <input v-model="hostname" id="hostname" type="text" placeholder="np. 192.168.1.1" />
      </div>
      <div>
        <label for="username">Nazwa użytkownika:</label>
        <input v-model="username" id="username" type="text" placeholder="np. root" />
      </div>
      <div>
        <label for="password">Hasło:</label>
        <input v-model="password" id="password" type="password" placeholder="********" />
      </div>
      <button @click="connect">Połącz</button>
    </div>

    <!-- Terminal (widoczny tylko po nawiązaniu połączenia) -->
    <div ref="terminal" class="terminal"></div>
  </div>
</template>

<script>
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import io from "socket.io-client"
import 'xterm/css/xterm.css'

export default {
  name: 'SSHTerminal',
  data() {
    return {
      term: null,
      fitAddon: null,
      ws: null,
      isConnected: false,
      hostname: '',
      username: '',
      password: '',
    }
  },
  methods: {
    initializeTerminal() {
      if (this.term) {
        this.term.dispose(); // Zniszcz poprzedni terminal, jeśli istnieje
      }

      this.term = new Terminal();
      this.fitAddon = new FitAddon();
      this.term.loadAddon(this.fitAddon);

      // Użyj nextTick, aby poczekać na renderowanie DOM
      this.$nextTick(() => {
        this.term.open(this.$refs.terminal);
        this.fitAddon.fit();

        this.term.onData((data) => {
          if (this.ws) {
            this.ws.emit('ssh_input', { input: data });
          }
        });

        window.addEventListener('resize', () => {
          this.fitAddon.fit();
        });
      });
    },
    connect() {
      // Nawiąż połączenie WebSocket
      this.isConnected = true
      this.ws = io.connect('http://localhost:5000');

      // Wyślij dane do nawiązania połączenia SSH
      this.ws.emit('ssh_connect', {
        hostname: this.hostname,
        username: this.username,
        password: this.password,
      });

      // Obsługa zdarzeń WebSocket
      this.ws.on('ssh-status', (event) => {
        if (event.status === 'connected') {
          this.isConnected = true; // Połączenie nawiązane
          this.initializeTerminal(); // Inicjalizuj terminal po nawiązaniu połączenia
          if (this.term) {
            this.term.write('SSH Status: Connected\r\n');
          }
        } else {
          if (this.term) {
            this.term.write('SSH Status: Error - ' + event.message + '\r\n');
          }
        }
      });

      this.ws.on('ssh_output', (event) => {
        if (this.term) {
          this.term.write(event.output);
        }
      });

      this.ws.on('connect_error', (error) => {
        console.error('Connection error:', error);
        if (this.term) {
          this.term.write('\r\nConnection error. Please try again.\r\n');
        }
      });

      this.ws.on('disconnect', () => {
        this.isConnected = false;
        if (this.term) {
          this.term.write('\r\nSSH connection closed.\r\n');
          this.term.dispose();
          this.term = null;
        }
      });
    },
  },
  beforeDestroy() {
    if (this.ws) {
      this.ws.close();
    }
    if (this.term) {
      this.term.dispose();
    }
  },
}
</script>

<style scoped>
.terminal {
  width: 100%;
  height: 500px;
}

input {
  margin: 5px;
  padding: 5px;
}

button {
  margin: 10px;
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}
</style>
