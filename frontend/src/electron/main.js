const { app, BrowserWindow, ipcMain, globalShortcut, session } = require('electron');
const path = require('path');
const http = require('http');

let mainWindow;
const BACKEND_URL = 'http://127.0.0.1:8000';
const isDev = !app.isPackaged;

// Helper function to make HTTP requests
function makeRequest(url, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: method,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          resolve({ error: body });
        }
      });
    });

    req.on('error', reject);
    if (data) req.write(JSON.stringify(data));
    req.end();
  });
}

function createWindow() {
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    callback(permission === 'media');
  });

  session.defaultSession.setPermissionCheckHandler((webContents, permission) => {
    return permission === 'media';
  });

  mainWindow = new BrowserWindow({
    width: 1920,
    height: 1080,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      sandbox: true
    },
    icon: path.join(__dirname, '../../assets/dino-icon.png'),
    backgroundColor: '#020712',
    show: true
  });

  const startUrl = isDev 
    ? 'http://localhost:3001' 
    : `file://${path.join(__dirname, '../../build/index.html')}`;

  mainWindow.loadURL(startUrl);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.webContents.on('did-fail-load', (_event, errorCode, errorDescription, validatedURL) => {
    console.error(`Failed to load ${validatedURL}: ${errorCode} ${errorDescription}`);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Register global hotkeys
  registerGlobalHotkeys();
}

function registerGlobalHotkeys() {
  const showMainWindow = () => {
    if (!mainWindow) return;
    if (mainWindow.isMinimized()) {
      mainWindow.restore();
    }
    mainWindow.show();
    mainWindow.focus();
    mainWindow.setAlwaysOnTop(true);
    mainWindow.setAlwaysOnTop(false);
  };

  const sendToRenderer = (channel) => {
    showMainWindow();
    if (!mainWindow) return;
    mainWindow.webContents.send(channel);
    const domEvent = channel === 'toggle-voice-assistant'
      ? 'dino-toggle-voice'
      : 'dino-toggle-console';
    mainWindow.webContents.executeJavaScript(
      `window.dispatchEvent(new CustomEvent('${domEvent}'))`
    ).catch((error) => {
      console.error(`Failed to dispatch ${domEvent}:`, error);
    });
  };

  try {
    // Ctrl+Shift+V to toggle voice assistant
    const voiceRegistered = globalShortcut.register('CommandOrControl+Shift+V', () => {
      console.log('Hotkey triggered: CommandOrControl+Shift+V');
      sendToRenderer('toggle-voice-assistant');
    });
    const voiceAltRegistered = globalShortcut.register('CommandOrControl+Alt+V', () => {
      console.log('Hotkey triggered: CommandOrControl+Alt+V');
      sendToRenderer('toggle-voice-assistant');
    });
    const voiceF8Registered = globalShortcut.register('F8', () => {
      console.log('Hotkey triggered: F8');
      sendToRenderer('toggle-voice-assistant');
    });

    // Ctrl+` to open command console
    const consoleRegistered = globalShortcut.register('CommandOrControl+`', () => {
      console.log('Hotkey triggered: CommandOrControl+`');
      sendToRenderer('toggle-command-console');
    });
    const consoleAltRegistered = globalShortcut.register('CommandOrControl+Shift+C', () => {
      console.log('Hotkey triggered: CommandOrControl+Shift+C');
      sendToRenderer('toggle-command-console');
    });

    console.log(`Global hotkeys registered: voice=${voiceRegistered}, voiceAlt=${voiceAltRegistered}, voiceF8=${voiceF8Registered}, console=${consoleRegistered}, consoleAlt=${consoleAltRegistered}`);
  } catch (e) {
    console.error('Failed to register global hotkeys:', e);
  }
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

// IPC Handlers for system commands
ipcMain.handle('execute-command', async (event, command, argument) => {
  try {
    const result = await makeRequest(
      `${BACKEND_URL}/execute`,
      'POST',
      { command, argument }
    );
    return result;
  } catch (error) {
    console.error('Command execution error:', error);
    return { success: false, message: error.message };
  }
});

ipcMain.handle('get-system-info', async (event) => {
  try {
    const data = await makeRequest(`${BACKEND_URL}/system/info`);
    return data;
  } catch (error) {
    console.error('Failed to get system info:', error);
    return { error: error.message };
  }
});
