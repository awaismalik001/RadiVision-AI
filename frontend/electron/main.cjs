/**
 * main.cjs
 * --------
 * Electron Main Process for RadiVision AI Native Desktop Application.
 * Wraps the React + Vite frontend into a native medical desktop workstation with
 * window management, auto-logout hooks upon window close, and hardware acceleration.
 */

const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');
const { spawn, exec } = require('child_process');

let mainWindow = null;
let backendProcess = null;

/**
 * Health check to verify if the FastAPI server is responding on port 8000.
 */
function checkBackendHealth(timeoutMs = 1200) {
  return new Promise((resolve) => {
    const req = http.get('http://127.0.0.1:8000/api/health', (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(timeoutMs, () => {
      req.destroy();
      resolve(false);
    });
  });
}

/**
 * Polls the backend health endpoint until it is online.
 */
async function waitForBackend(maxAttempts = 50, intervalMs = 600) {
  for (let i = 0; i < maxAttempts; i++) {
    const isUp = await checkBackendHealth();
    if (isUp) return true;
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  return false;
}

/**
 * Automatically launches the RadiVision AI backend in the background.
 */
function startBackend() {
  return new Promise(async (resolve) => {
    try {
      const alreadyRunning = await checkBackendHealth(800);
      if (alreadyRunning) {
        console.log('[Electron] RadiVision AI backend is already active on port 8000.');
        return resolve(true);
      }

      let executablePath = '';
      let args = [];
      let cwd = '';
      let env = { ...process.env };

      if (app.isPackaged) {
        // Packaged desktop app: search in process.resourcesPath
        const candidates = [
          path.join(process.resourcesPath, 'backend', 'server', 'server.exe'),
          path.join(process.resourcesPath, 'backend', 'server.exe'),
          path.join(process.resourcesPath, 'server', 'server.exe')
        ];
        for (const cand of candidates) {
          if (fs.existsSync(cand)) {
            executablePath = cand;
            cwd = path.dirname(cand);
            break;
          }
        }
        env.RADIVISION_ROOT = process.resourcesPath;
      } else {
        // Development mode: check if standalone binary exists, else fallback to python
        const devBinary = path.join(__dirname, '..', '..', 'dist-server', 'server', 'server.exe');
        const projectRoot = path.join(__dirname, '..', '..');

        if (fs.existsSync(devBinary)) {
          executablePath = devBinary;
          cwd = path.dirname(devBinary);
          env.RADIVISION_ROOT = projectRoot;
        } else {
          executablePath = 'python';
          args = ['server.py'];
          cwd = projectRoot;
        }
      }

      if (!executablePath) {
        console.warn('[Electron] Could not locate backend executable. Relying on existing service.');
        return resolve(false);
      }

      console.log(`[Electron] Spawning background AI backend: ${executablePath} (CWD: ${cwd})`);
      backendProcess = spawn(executablePath, args, {
        cwd: cwd,
        env: env,
        windowsHide: true,
        stdio: ['ignore', 'pipe', 'pipe']
      });

      backendProcess.stdout.on('data', (data) => {
        console.log(`[Backend] ${data.toString().trim()}`);
      });

      backendProcess.stderr.on('data', (data) => {
        console.warn(`[Backend ERR] ${data.toString().trim()}`);
      });

      backendProcess.on('error', (err) => {
        console.error('[Electron] Backend process error:', err);
      });

      backendProcess.on('exit', (code, signal) => {
        console.log(`[Electron] Backend process terminated with code ${code}, signal ${signal}`);
        backendProcess = null;
      });

      // Wait for backend to finish warming up
      const ready = await waitForBackend();
      if (ready) {
        console.log('[Electron] RadiVision AI backend is ready and listening.');
      } else {
        console.warn('[Electron] Timed out waiting for backend. UI will continue loading.');
      }
      resolve(ready);
    } catch (err) {
      console.error('[Electron] Exception during backend launch:', err);
      resolve(false);
    }
  });
}

/**
 * Cleanly terminates the background backend process upon app exit.
 */
function stopBackend() {
  if (backendProcess && backendProcess.pid) {
    console.log('[Electron] Terminating background AI engine...');
    try {
      if (process.platform === 'win32') {
        exec(`taskkill /pid ${backendProcess.pid} /T /F`, (err) => {
          if (err) console.warn('[Electron] taskkill warning:', err.message);
        });
      } else {
        backendProcess.kill();
      }
    } catch (e) {
      console.error('[Electron] Error stopping backend:', e);
    }
    backendProcess = null;
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 580,
    height: 440,
    center: true,
    resizable: false,
    frame: false,
    transparent: true,
    hasShadow: false,
    backgroundColor: '#00000000',
    title: "RadiVision AI — Professional Medical X-Ray Diagnostic Suite",
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false
    },
    show: false
  });

  // Completely remove the default application menu bar (File, Edit, View, Window, Help)
  Menu.setApplicationMenu(null);
  mainWindow.setMenuBarVisibility(false);

  const devUrl = process.env.ELECTRON_START_URL || 'http://localhost:5173';
  const prodPath = path.join(__dirname, '..', 'dist', 'index.html');

  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL(devUrl).catch(() => {
      if (fs.existsSync(prodPath)) {
        mainWindow.loadFile(prodPath);
      }
    });
  } else if (fs.existsSync(prodPath)) {
    mainWindow.loadFile(prodPath);
  } else {
    mainWindow.loadURL(devUrl);
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Window management IPC listeners for compact splash & auth windows
  ipcMain.on('window:to-auth', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.setResizable(true);
      mainWindow.setSize(390, 460, true);
      mainWindow.setResizable(false);
      mainWindow.center();
    }
  });

  // Option 3: Adaptive Height Resizing for Sign Up vs Sign In
  ipcMain.on('window:auth-signup', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.setResizable(true);
      mainWindow.setSize(470, 750, true);
      mainWindow.setResizable(false);
      mainWindow.center();
    }
  });

  ipcMain.on('window:auth-signin', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.setResizable(true);
      mainWindow.setSize(390, 460, true);
      mainWindow.setResizable(false);
      mainWindow.center();
    }
  });

  ipcMain.on('window:maximize-workstation', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.setResizable(true);
      mainWindow.setMinimumSize(1120, 740);
      mainWindow.maximize();
    }
  });

  ipcMain.on('window:shrink-to-auth', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.unmaximize();
      mainWindow.setMinimumSize(360, 420);
      mainWindow.setSize(390, 460, true);
      mainWindow.setResizable(false);
      mainWindow.center();
    }
  });

  // Native window control actions (Minimize, Maximize/Restore, Close)
  ipcMain.on('window:minimize', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.minimize();
    }
  });

  ipcMain.on('window:maximize-toggle', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
      } else {
        mainWindow.maximize();
      }
    }
  });

  ipcMain.on('window:close', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.close();
    }
  });

  // Forward renderer console logs to terminal for easy diagnosis
  mainWindow.webContents.on('console-message', (event) => {
    const msg = event.message || event;
    console.log(`[Renderer] ${msg}`);
  });

  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    console.error(`[Electron] Failed to load ${validatedURL}: ${errorDescription} (${errorCode})`);
  });

  // Allow F12 or Ctrl+Shift+I to toggle DevTools
  mainWindow.webContents.on('before-input-event', (event, input) => {
    if (input.key === 'F12' || (input.control && input.shift && input.key.toLowerCase() === 'i')) {
      mainWindow.webContents.toggleDevTools();
      event.preventDefault();
    }
  });

  // Phase 5 Access Control: Auto-logout trigger when application window is closed
  mainWindow.on('close', (e) => {
    try {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('app:auto-logout');
      }
    } catch (err) {
      console.error('[Electron] Auto-logout dispatch error:', err);
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  // Concurrently initiate silent background backend launch and render UI window
  startBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('before-quit', () => {
  stopBackend();
});

app.on('will-quit', () => {
  stopBackend();
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
