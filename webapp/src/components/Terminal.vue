<template>
  <div ref="terminal" class="terminal"></div>
</template>

<script>
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import io from 'socket.io-client'
import 'xterm/css/xterm.css'

export default {
  name: 'SSHTerminal',
  data() {
    return {
      term: null,
      fitAddon: null,
      ws: null,
    }
  },
  mounted() {
    this.initializeTerminal()
    this.connectWebSocket()
  },
  methods: {
    initializeTerminal() {
      this.term = new Terminal()
      this.fitAddon = new FitAddon()
      this.term.loadAddon(this.fitAddon)
      this.term.open(this.$refs.terminal)
      this.fitAddon.fit()

      this.term.onData((data) => {
        if (this.ws) {
          this.ws.emit('ssh_input', { input: data })
        }
      })

      window.addEventListener('resize', () => {
        this.fitAddon.fit()
        this.ws.emit('resize', { cols: this.term.cols, rows: this.term.rows })
      })
    },
    connectWebSocket() {
      this.ws = io.connect('http://localhost:5000')

      this.ws.emit('ssh_connect', {
        hostname: 'hostname',
        username: 'username',
        password: 'password',
      })

      this.ws.on('ssh_status', (event) => {
        console.log(event)
        this.term.write('SSH Status: ' + event.status + '\r\n')
      })

      this.ws.on('ssh_output', (event) => {
        this.term.write(event.output)
      })

      this.ws.on('connect_error', (error) => {
        console.error('Connection error:', error)
        this.term.write('\r\nConnection error. Please try again.\r\n')
      })

      this.ws.on('disconnect', () => {
        this.term.write('\r\nSSH connection closed.\r\n')
      })
    },
  },
  beforeDestroy() {
    if (this.ws && this.ws.connected) {
      this.ws.close()
    }
  },
}
</script>

<style scoped>
.terminal {
  width: 100%;
  height: 100%;
}
</style>
