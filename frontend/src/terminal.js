/**
 * QUANTUM//OPS - Interactive Terminal Engine (xterm.js)
 * Implements cyberpunk shell, command history, tab completion,
 * and live REST connection to the FastAPI backend.
 */

import { COMMAND_LIST, getTabCompletions } from './commands.js';

export class QuantumTerminal {
  constructor(containerId, apiBase = '') {
    this.container = document.getElementById(containerId);
    this.apiBase = apiBase;
    this.term = null;
    this.fitAddon = null;

    // Shell state
    this.promptStr = '\x1b[38;2;0;255;255mQUANTUM//OPS\x1b[0m:\x1b[38;2;0;255;65m~$\x1b[0m ';
    this.currentLine = '';
    this.cursorPos = 0;
    this.history = [];
    this.historyIndex = -1;
    this.isExecuting = false;

    // ASCII Boot Banner (Clean technical header, no marketing tagline)
    this.bootBanner = [
      '\x1b[38;2;0;255;65m ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗██╗   ██╗███╗   ███╗    ██████╗ ██████╗ ███████╗\x1b[0m',
      '\x1b[38;2;0;255;65m██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██║   ██║████╗ ████║   ██╔═══██╗██╔══██╗██╔════╝\x1b[0m',
      '\x1b[38;2;0;255;65m██║   ██║██║   ██║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║   ██║   ██║██████╔╝███████╗\x1b[0m',
      '\x1b[38;2;0;255;65m██║▄▄ ██║██║   ██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║   ██║   ██║██╔═══╝ ╚════██║\x1b[0m',
      '\x1b[38;2;0;255;65m╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║██╗╚██████╔╝██║     ███████║\x1b[0m',
      '\x1b[38;2;0;255;65m ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚══════╝\x1b[0m',
      '\x1b[38;2;0;255;255m       QUANTUM HYBRID COMPUTING WORKBENCH  ::  v1.0.0-PROD\x1b[0m',
      '\x1b[38;2;70;70;70m--------------------------------------------------------------------------------\x1b[0m',
    ];
  }

  async init() {
    const TerminalClass = window.Terminal;
    const FitAddonClass = window.FitAddon?.FitAddon;

    if (!TerminalClass) {
      console.error('xterm.js library not loaded');
      this.container.innerHTML = '<div style="color:red;padding:20px;">Error: xterm.js not loaded.</div>';
      return;
    }

    this.term = new TerminalClass({
      cursorBlink: true,
      cursorStyle: 'block',
      fontFamily: "'JetBrains Mono', 'Fira Code', 'Courier New', monospace",
      fontSize: 13,
      lineHeight: 1.25,
      theme: {
        background: '#050505',
        foreground: '#00FF41',
        cursor: '#00FF41',
        cursorAccent: '#050505',
        selectionBackground: 'rgba(0, 255, 65, 0.3)',
        black: '#050505',
        red: '#FF3333',
        green: '#00FF41',
        yellow: '#FFD700',
        blue: '#00BFFF',
        magenta: '#FF00FF',
        cyan: '#00FFFF',
        white: '#E0FFE0',
        brightGreen: '#39FF14',
        brightCyan: '#70FFFF',
      },
    });

    if (FitAddonClass) {
      this.fitAddon = new FitAddonClass();
      this.term.loadAddon(this.fitAddon);
    }

    this.term.open(this.container);

    if (this.fitAddon) {
      this.fitAddon.fit();
      window.addEventListener('resize', () => {
        try { this.fitAddon.fit(); } catch (e) {}
      });
    }

    this.setupKeyHandlers();
    await this.runBootSequence();
  }

  async runBootSequence() {
    for (const line of this.bootBanner) {
      this.term.writeln(line);
      await this.sleep(20);
    }

    this.term.writeln('');
    this.term.writeln('\x1b[38;2;0;255;65m[ OK ]\x1b[0m Loading core system kernel');
    await this.sleep(40);
    this.term.writeln('\x1b[38;2;0;255;65m[ OK ]\x1b[0m Initializing execution environment');
    await this.sleep(40);

    // Dynamic initial checks against live API
    try {
      const resp = await fetch(`${this.apiBase}/api/modules`);
      const modules = await resp.json();

      const tagMap = {
        success: '\x1b[38;2;0;255;65m[ OK ]\x1b[0m',
        simulated: '\x1b[38;2;0;255;255m[ SIM ]\x1b[0m',
        unavailable: '\x1b[38;2;255;80;80m[ FAIL ]\x1b[0m',
      };

      const cStatus = modules.cudaq?.status || 'unavailable';
      const qStatus = modules.qiskit?.status || 'unavailable';
      const nStatus = modules.nvqlink?.status || 'unavailable';
      const sStatus = modules.shor?.status || 'unavailable';

      this.term.writeln(`${tagMap[cStatus] || '[ OK ]'} Module 01: CUDA-Q Engine (${cStatus.toUpperCase()})`);
      await this.sleep(35);
      this.term.writeln(`${tagMap[qStatus] || '[ OK ]'} Module 02: Qiskit Connectivity (${qStatus.toUpperCase()})`);
      await this.sleep(35);
      this.term.writeln(`${tagMap[nStatus] || '[ OK ]'} Module 03: NVQLink Architecture (${nStatus.toUpperCase()})`);
      await this.sleep(35);
      this.term.writeln(`${tagMap[sStatus] || '[ OK ]'} Module 04: Shor Algorithm (${sStatus.toUpperCase()})`);
      await this.sleep(35);
    } catch (e) {
      this.term.writeln('\x1b[38;2;255;180;0m[ WARN ]\x1b[0m Probing local FastAPI backend...');
    }

    this.term.writeln('');
    this.term.writeln('\x1b[38;2;0;255;65;1mSYSTEM READY.\x1b[0m Type \x1b[38;2;0;255;255mhelp\x1b[0m for available commands.');
    this.term.writeln('');
    this.prompt();
  }

  prompt() {
    this.currentLine = '';
    this.cursorPos = 0;
    this.term.write(this.promptStr);
  }

  setupKeyHandlers() {
    this.term.onData((data) => {
      if (this.isExecuting) return;

      const code = data.charCodeAt(0);

      // Enter key (CR or LF)
      if (data === '\r' || data === '\n') {
        this.term.write('\r\n');
        this.handleCommand(this.currentLine.trim());
      }
      // Backspace
      else if (code === 127 || code === 8) {
        if (this.cursorPos > 0) {
          this.currentLine =
            this.currentLine.slice(0, this.cursorPos - 1) +
            this.currentLine.slice(this.cursorPos);
          this.cursorPos--;
          this.redrawLine();
        }
      }
      // Arrow Keys & Escape sequences
      else if (data === '\x1b[A') {
        // Arrow Up: history back
        if (this.history.length > 0 && this.historyIndex < this.history.length - 1) {
          this.historyIndex++;
          this.currentLine = this.history[this.history.length - 1 - this.historyIndex];
          this.cursorPos = this.currentLine.length;
          this.redrawLine();
        }
      } else if (data === '\x1b[B') {
        // Arrow Down: history forward
        if (this.historyIndex > 0) {
          this.historyIndex--;
          this.currentLine = this.history[this.history.length - 1 - this.historyIndex];
          this.cursorPos = this.currentLine.length;
          this.redrawLine();
        } else if (this.historyIndex === 0) {
          this.historyIndex = -1;
          this.currentLine = '';
          this.cursorPos = 0;
          this.redrawLine();
        }
      } else if (data === '\x1b[D') {
        // Arrow Left
        if (this.cursorPos > 0) {
          this.cursorPos--;
          this.term.write(data);
        }
      } else if (data === '\x1b[C') {
        // Arrow Right
        if (this.cursorPos < this.currentLine.length) {
          this.cursorPos++;
          this.term.write(data);
        }
      }
      // Tab completion
      else if (code === 9) {
        const matches = getTabCompletions(this.currentLine);
        if (matches.length === 1) {
          this.currentLine = matches[0];
          this.cursorPos = this.currentLine.length;
          this.redrawLine();
        } else if (matches.length > 1) {
          this.term.write('\r\n');
          this.term.writeln('\x1b[38;2;85;122;95m' + matches.join('   ') + '\x1b[0m');
          this.term.write(this.promptStr + this.currentLine);
        }
      }
      // Ctrl+C
      else if (code === 3) {
        this.term.writeln('^C');
        this.prompt();
      }
      // Ctrl+L (Clear)
      else if (code === 12) {
        this.term.clear();
        this.term.write(this.promptStr + this.currentLine);
      }
      // Normal printable characters
      else if (code >= 32) {
        this.currentLine =
          this.currentLine.slice(0, this.cursorPos) +
          data +
          this.currentLine.slice(this.cursorPos);
        this.cursorPos += data.length;
        this.redrawLine();
      }
    });
  }

  redrawLine() {
    this.term.write('\r\x1b[K');
    this.term.write(this.promptStr + this.currentLine);
    const offset = this.currentLine.length - this.cursorPos;
    if (offset > 0) {
      this.term.write(`\x1b[${offset}D`);
    }
  }

  async handleCommand(cmdStr) {
    if (!cmdStr) {
      this.prompt();
      return;
    }

    this.history.push(cmdStr);
    this.historyIndex = -1;

    if (cmdStr === 'clear' || cmdStr === 'cls') {
      this.term.clear();
      this.prompt();
      return;
    }

    this.isExecuting = true;

    try {
      const response = await fetch(`${this.apiBase}/api/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmdStr, raw_input: cmdStr }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.output) {
        const formatted = data.output.replace(/\r?\n/g, '\r\n');
        this.term.write(formatted);
      }

      window.dispatchEvent(new CustomEvent('quantum-command-executed', { detail: data }));
    } catch (err) {
      this.term.writeln(`\x1b[38;2;255;75;75m[ERROR] Connection failed: ${err.message}\x1b[0m`);
      this.term.writeln('\x1b[38;2;85;122;95mEnsure the FastAPI server is running on http://localhost:8000\x1b[0m\r\n');
    } finally {
      this.isExecuting = false;
      this.prompt();
    }
  }

  executeExternal(cmd) {
    if (this.isExecuting) return;
    this.currentLine = cmd;
    this.term.write(cmd + '\r\n');
    this.handleCommand(cmd);
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
