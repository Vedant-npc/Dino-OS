const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  executeCommand: (command, argument) => ipcRenderer.invoke('execute-command', command, argument),
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  onToggleVoiceAssistant: (callback) => ipcRenderer.on('toggle-voice-assistant', callback),
  onToggleCommandConsole: (callback) => ipcRenderer.on('toggle-command-console', callback),
  onVoiceCommand: (callback) => ipcRenderer.on('voice-command', callback),
});

contextBridge.exposeInMainWorld('api', {
  callBackend: async (endpoint, method = 'GET', data = null) => {
    try {
      const options = {
        method,
        headers: {
          'Content-Type': 'application/json'
        }
      };
      if (data) options.body = JSON.stringify(data);
      
      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, options);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      return { error: error.message, success: false };
    }
  }
});

