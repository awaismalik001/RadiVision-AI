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
  },
  toAuthWindow: () => ipcRenderer.send('window:to-auth'),
  authSignUp: () => ipcRenderer.send('window:auth-signup'),
  authSignIn: () => ipcRenderer.send('window:auth-signin'),
  maximizeWorkstation: () => ipcRenderer.send('window:maximize-workstation'),
  shrinkToAuthWindow: () => ipcRenderer.send('window:shrink-to-auth'),
  minimize: () => ipcRenderer.send('window:minimize'),
  maximizeToggle: () => ipcRenderer.send('window:maximize-toggle'),
  close: () => ipcRenderer.send('window:close')
});
