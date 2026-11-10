/**
 * QUANTUM//OPS - Main Frontend Entry Point
 * Orchestrates terminal lifecycle, telemetry HUD updates, and module chips.
 */

import { QuantumTerminal } from './terminal.js';

document.addEventListener('DOMContentLoaded', async () => {
  const terminal = new QuantumTerminal('terminal-container');
  await terminal.init();

  // Wire up quick command pills
  document.querySelectorAll('.cmd-pill').forEach((btn) => {
    btn.addEventListener('click', () => {
      const cmd = btn.getAttribute('data-cmd');
      if (cmd) {
        terminal.executeExternal(cmd);
      }
    });
  });

  // Wire clear button
  const clearBtn = document.getElementById('btn-clear');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      terminal.executeExternal('clear');
    });
  }

  // Wire help button
  const helpBtn = document.getElementById('btn-help');
  if (helpBtn) {
    helpBtn.addEventListener('click', () => {
      terminal.executeExternal('help');
    });
  }

  // Periodic telemetry refresh
  async function refreshTelemetry() {
    try {
      const [sysRes, modRes] = await Promise.all([
        fetch('/api/system/info'),
        fetch('/api/modules'),
      ]);

      if (sysRes.ok) {
        const sys = await sysRes.json();
        const modeEl = document.getElementById('telemetry-mode');
        const cpuEl = document.getElementById('telemetry-cpu');
        const connDot = document.getElementById('backend-status-dot');
        const connText = document.getElementById('backend-status-text');

        if (connDot) {
          connDot.className = 'status-dot';
        }
        if (connText) {
          connText.textContent = 'ONLINE';
        }
        if (modeEl) {
          modeEl.textContent = sys.active_execution_mode.toUpperCase();
        }
        if (cpuEl) {
          cpuEl.textContent = `${sys.cpu_cores}C CPU | ${sys.ram_gb} GB`;
        }
      }

      if (modRes.ok) {
        const mods = await modRes.json();
        updateModuleChips(mods);
      }
    } catch (e) {
      const connDot = document.getElementById('backend-status-dot');
      const connText = document.getElementById('backend-status-text');
      if (connDot) connDot.className = 'status-dot error pulse';
      if (connText) connText.textContent = 'OFFLINE';
    }
  }

  function updateModuleChips(mods) {
    const chipKeys = ['cudaq', 'qiskit', 'nvqlink', 'shor'];
    chipKeys.forEach((key) => {
      const mod = mods[key];
      if (!mod) return;
      const tagEl = document.getElementById(`tag-${key}`);
      if (tagEl) {
        tagEl.textContent = mod.status.toUpperCase();
        tagEl.className = `chip-tag ${mod.status}`;
      }
    });
  }

  // Click on module chips to query their status
  document.querySelectorAll('.module-chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      const cmd = chip.getAttribute('data-cmd');
      if (cmd) {
        terminal.executeExternal(cmd);
      }
    });
  });

  // Listen for command executions to refresh status
  window.addEventListener('quantum-command-executed', () => {
    setTimeout(refreshTelemetry, 500);
  });

  // Initial telemetry load
  refreshTelemetry();
  setInterval(refreshTelemetry, 15000);
});
