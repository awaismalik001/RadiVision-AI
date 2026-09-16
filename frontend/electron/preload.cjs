/**
 * preload.cjs
 * -----------
 * Electron Preload Script for RadiVision AI.
 * Secure IPC Bridge exposing native desktop triggers to the React frontend.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  isElectron: true,
  platform: process.platform,
  onAutoLogout: (callback) => {
    ipcRenderer.on('app:auto-logout', (_event, value) => callback(value));
  }
});
