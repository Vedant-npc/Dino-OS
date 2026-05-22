from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import os
import sys
from typing import Optional
import subprocess
import json
from datetime import datetime

# Import local modules
from config import GEMINI_API_KEY
from ai_engine import AIEngine
from system_commands import SystemCommandExecutor

app = FastAPI(title="DINO OS Backend", version="1.0.0")

# Enable CORS for Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
ai_engine = AIEngine(api_key=GEMINI_API_KEY)
command_executor = SystemCommandExecutor()

# Models
class CommandRequest(BaseModel):
    command: str
    argument: Optional[str] = None
    text: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

class VoiceCommandRequest(BaseModel):
    text: str

class ListenCommandRequest(BaseModel):
    timeout: Optional[int] = 5
    phrase_time_limit: Optional[int] = 4

class CommandResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None

# Routes
@app.get("/")
async def root():
    return {
        "status": "DINO OS Backend Online",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_engine": "online" if ai_engine else "offline",
        "system_commands": "ready"
    }

@app.post("/execute", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """Execute system commands"""
    try:
        result = command_executor.execute(request.command, request.argument)
        return CommandResponse(
            success=result["success"],
            message=result["message"],
            data=result.get("data")
        )
    except Exception as e:
        return CommandResponse(
            success=False,
            message="Command execution failed",
            error=str(e)
        )

@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle AI chat requests"""
    try:
        response = ai_engine.chat(request.message, request.context)
        return {
            "success": True,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice-command")
async def voice_command(request: VoiceCommandRequest):
    """Process voice commands"""
    try:
        # Parse command from text
        command_result = command_executor.parse_voice_command(request.text)
        
        if command_result["success"]:
            # Execute the command
            exec_result = command_executor.execute(
                command_result["command"],
                command_result.get("argument")
            )
            return {
                "success": True,
                "parsed_command": command_result["command"],
                "execution": exec_result
            }
        else:
            return {
                "success": False,
                "error": command_result.get("error")
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/listen-command")
async def listen_command(request: ListenCommandRequest):
    """Listen through the backend microphone and execute a voice command"""
    try:
        result = await run_in_threadpool(
            command_executor.listen_and_execute,
            request.timeout,
            request.phrase_time_limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/info")
async def system_info():
    """Get system information"""
    try:
        import psutil
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "available": psutil.virtual_memory().available
            },
            "disk": {
                "percent": psutil.disk_usage("/").percent,
                "total": psutil.disk_usage("/").total
            },
            "platform": sys.platform
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/processes")
async def system_processes():
    """Get running processes"""
    try:
        import psutil
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                processes.append({
                    "pid": proc.pid,
                    "name": proc.name(),
                    "memory": proc.memory_percent()
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {"processes": sorted(processes, key=lambda x: x["memory"], reverse=True)[:10]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/analyze")
async def analyze_text(request: dict):
    """Analyze text using AI"""
    try:
        text = request.get("text", "")
        task = request.get("task", "analyze")
        
        result = ai_engine.analyze(text, task)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/summarize")
async def summarize_text(request: dict):
    """Summarize text using AI"""
    try:
        text = request.get("text", "")
        result = ai_engine.summarize(text)
        return {
            "success": True,
            "summary": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
