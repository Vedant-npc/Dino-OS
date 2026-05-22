# DINO OS - Futuristic AI Desktop Assistant 🤖

A cyberpunk-inspired, fully functional AI desktop assistant with holographic interface, voice control, and real system automation.

![DINO OS](docs/screenshots/main.png)

## Features ✨

### 🎤 Voice Control
- **Voice Recognition**: Web Speech API for real-time voice commands
- **Natural Language Processing**: Understands complex commands
- **Text-to-Speech**: Responses spoken aloud using pyttsx3

### 🤖 AI Integration
- **Gemini API**: Advanced conversational AI
- **Context-Aware Responses**: Maintains conversation history
- **Multi-task AI**: Summarization, analysis, idea generation, explanation

### 🎨 Futuristic UI
- **Glassmorphism Effects**: Modern frosted glass design
- **Neon Glow**: Cyberpunk color scheme (green & cyan)
- **Smooth Animations**: Framer Motion transitions
- **Holographic Widgets**: Live system metrics display

### 🖥️ System Integration
- **App Launcher**: Open Chrome, VS Code, Settings, YouTube
- **System Commands**: Screenshots, folder creation, screen lock, shutdown
- **Coding Mode**: Automated workspace setup for developers
- **Real System Info**: Live CPU, RAM, temperature monitoring

### 💬 Interactive Dashboard
- **Chat Interface**: Real-time AI conversations
- **Floating Windows**: Draggable, movable interface windows
- **Command Console**: Terminal-style command input
- **Dynamic Widgets**: CPU, RAM, Weather, Time, AI Status

## Tech Stack

### Frontend
- **React 18**: Modern UI library
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **Electron**: Desktop application framework

### Backend
- **FastAPI**: High-performance web framework
- **Python 3.9+**: Core language
- **Gemini API**: AI capabilities
- **PyTorch/TensorFlow**: Optional ML features

### Desktop
- **Electron**: Cross-platform desktop apps
- **Node.js**: JavaScript runtime

## Installation

### Prerequisites
- Node.js 18+
- Python 3.9+
- npm or yarn
- Gemini API key (from Google AI Studio)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/dino-os.git
cd dino-os
```

### 2. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

Get your Gemini API key:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file:
```env
GEMINI_API_KEY=your_key_here
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 4. Install Backend Dependencies
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cd ..
```

### 5. Run the Application

#### Option A: Development Mode (recommended for first time)
```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Start Electron + React
cd frontend
npm start
```

#### Option B: Full Integration
```bash
npm run start-all
```

#### Option C: Build for Production
```bash
npm run build-app
```

## Usage Guide

### Voice Commands
Say "Dino" or click the microphone button to activate voice mode:

```
"Open Chrome"
"Open VS Code"
"Search Google for Python tutorials"
"Take screenshot"
"Create folder MyProject"
"Lock screen"
"Shutdown PC"
"Start coding mode"
"What is machine learning?"
"Summarize this"
"Generate project ideas"
```

### Text Commands
Press `Ctrl + `` to open the command console:

```
open chrome
search "artificial intelligence"
screenshot
info
help
```

### Keyboard Shortcuts
- `Ctrl + `` - Open/close command console
- `Escape` - Close current window/dialog
- `Enter` - Execute command
- `Arrow Up/Down` - Navigate command history

### Chat Features
Click the chat button (💬) to open the AI chat:
- Ask questions about any topic
- Get code explanations
- Brainstorm ideas
- Summarize content

## File Structure

```
dino-os/
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── InitScreen.js
│   │   │   ├── MainDashboard.js
│   │   │   ├── VoiceAssistant.js
│   │   │   ├── ChatInterface.js
│   │   │   ├── CommandConsole.js
│   │   │   ├── FloatingWindow.js
│   │   │   └── HolographicWidgets.js
│   │   ├── electron/
│   │   │   ├── main.js
│   │   │   └── preload.js
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── package.json
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── ai_engine.py
│   ├── system_commands.py
│   └── requirements.txt
├── docs/
│   └── screenshots/
├── .env.example
├── .gitignore
├── README.md
└── package.json
```

## Configuration

### Customizing Colors
Edit `frontend/tailwind.config.js`:
```js
colors: {
  'neon-green': '#00ff41',
  'neon-cyan': '#00d4ff',
  'neon-purple': '#bf00ff',
}
```

### Adding Commands
Edit `backend/system_commands.py` to add new system commands.

### Changing AI Model
Edit `backend/config.py`:
```python
AI_MODEL = "gemini-pro"  # or your preferred model
```

## Troubleshooting

### "No SpeechRecognition available"
- Voice recognition requires a Chromium-based browser
- Not available in development mode in some cases

### "API Key Error"
- Verify `.env` file has correct `GEMINI_API_KEY`
- Check API key is not expired

### Backend not responding
```bash
# Check if backend is running
curl http://localhost:8000

# Restart backend
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Frontend not starting
```bash
# Clear cache
cd frontend
rm -rf node_modules
npm install
npm start
```

## Advanced Features

### Custom Commands
Add custom voice/text commands in `backend/system_commands.py`:

```python
def _custom_command(self):
    # Your code here
    return {
        "success": True,
        "message": "Command executed"
    }
```

### Extending AI Features
Modify `backend/ai_engine.py` to add new AI capabilities:

```python
def custom_feature(self, input_text):
    prompt = f"Do something with: {input_text}"
    response = self.model.generate_content(prompt)
    return response.text
```

### Custom Widgets
Create new widgets in `frontend/src/components/HolographicWidgets.js`:

```jsx
const CustomWidget = () => (
  <motion.div className="glass-panel">
    {/* Your widget */}
  </motion.div>
);
```

## Performance Tips

1. **Disable Animations**: Edit `index.css` to reduce animation complexity
2. **Optimize Images**: Compress any custom images
3. **Use CDN**: Host large assets on CDN
4. **Cache API Responses**: Implement caching in backend

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Roadmap

- [ ] Gesture control with webcam
- [ ] PDF summarization
- [ ] Real-time music playback
- [ ] System file explorer integration
- [ ] Multi-language support
- [ ] Custom hotkeys configuration
- [ ] Dark/Light theme toggle
- [ ] Conversation memory persistence
- [ ] Integration with more AI models
- [ ] Mobile companion app

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for AI capabilities
- Framer Motion for animations
- Tailwind CSS for styling
- Electron for desktop framework
- OpenAI for inspiration

## Support

For support, email support@dinoai.com or open an issue in the repository.

## Author

Created with ❤️ by Vedant

---

**Disclaimer**: This project is for educational purposes. Ensure you have proper permissions before using system commands or accessing user data.

**Note**: Remember to add your Gemini API key before using the AI features. The application will still work without it, but AI responses won't be available.

## Citation

If you use DINO OS in your research or project, please cite:

```bibtex
@software{dino_os_2024,
  title={DINO OS: Futuristic AI Desktop Assistant},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/dino-os}
}
```
