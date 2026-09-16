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
    width: 1440,
    height: 920,
    minWidth: 1120,
    minHeight: 740,
    title: "RadiVision AI — Clinical Desktop Diagnostic Suite",
    backgroundColor: '#0B1727', // Clinical dark navy while initializing
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
    mainWindow.maximize();
    mainWindow.show();
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
