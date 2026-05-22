import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Settings
DEBUG = os.getenv("DEBUG", "False") == "True"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dino.db")

# Voice
VOICE_ENABLED = os.getenv("VOICE_ENABLED", "True") == "True"
TEXT_TO_SPEECH_ENABLED = os.getenv("TTS_ENABLED", "True") == "True"

# System
MAX_COMMAND_TIMEOUT = int(os.getenv("MAX_COMMAND_TIMEOUT", 30))
DEFAULT_ALLOWED_COMMANDS = [
    "open",
    "close",
    "search",
    "screenshot",
    "create-folder",
    "read-text",
    "lock",
    "shutdown",
    "restart",
    "coding-mode",
    "open-project",
]
CONFIGURED_ALLOWED_COMMANDS = [
    command.strip()
    for command in os.getenv(
        "ALLOWED_COMMANDS",
        ",".join(DEFAULT_ALLOWED_COMMANDS),
    ).split(",")
    if command.strip()
]
ALLOWED_COMMANDS = list(dict.fromkeys(DEFAULT_ALLOWED_COMMANDS + CONFIGURED_ALLOWED_COMMANDS))
ENABLE_SHELL_COMMANDS = os.getenv("ENABLE_SHELL_COMMANDS", "False") == "True"

# AI Model
AI_MODEL = os.getenv("AI_MODEL", "gemini-pro")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))

print("[CONFIG] DINO OS Configuration loaded")
print(f"[CONFIG] Debug mode: {DEBUG}")
print(f"[CONFIG] Voice enabled: {VOICE_ENABLED}")
print(f"[CONFIG] TTS enabled: {TEXT_TO_SPEECH_ENABLED}")
print(f"[CONFIG] AI Model: {AI_MODEL}")
