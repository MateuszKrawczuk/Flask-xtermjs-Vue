<template>

  <div ref="terminal" class="terminal"></div>
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
      })
    },
    connectWebSocket() {
      this.ws = io.connect('http://localhost:5000')

        this.ws.emit(
            'ssh_connect', JSON.stringify({
            hostname: 'hostname',
            username: 'username',
            password: 'password',
    }))

      this.ws.on('ssh_status', (event) => {
        console.log(event)
        // const data = JSON.parse(event)
        this.term.write('SSH Status: ' + event['status'] + '\r\n')
        // this.term.write(data)
      })

      this.ws.on('ssh_output', (event) => {
        this.term.write('' + event['output'])
      })

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.output) {
          this.term.write(data.output)
        }
        if (data.error) {
          this.term.write(data.error)
        }
      }

      this.ws.onclose = () => {
        this.term.write('\r\nSSH connection closed.\r\n')
      }
    },
  },
  beforeDestroy() {
    if (this.ws) {
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
