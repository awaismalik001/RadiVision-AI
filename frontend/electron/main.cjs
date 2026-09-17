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

let mainWindow = null;

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
      mainWindow.setSize(440, 620, true);
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
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
