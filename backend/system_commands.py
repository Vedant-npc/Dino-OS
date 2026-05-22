import subprocess
import os
import sys
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import platform
import json
import re
import shutil
import webbrowser
from urllib.parse import quote_plus

from config import ALLOWED_COMMANDS, ENABLE_SHELL_COMMANDS, MAX_COMMAND_TIMEOUT

logger = logging.getLogger(__name__)

class SystemCommandExecutor:
    """Handles execution of system commands and application launches"""
    
    def __init__(self):
        self.platform = platform.system()
        self.app_paths = self._load_app_paths()
        for name, path in self._discover_installed_apps().items():
            if name not in self.app_paths or self._known_app_path_is_missing(self.app_paths[name]):
                self.app_paths[name] = path
    
    def _load_app_paths(self) -> dict:
        """Load paths to common applications"""
        if self.platform == "Windows":
            return {
                "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "edge": "msedge",
                "code": "C:\\Program Files\\Microsoft VS Code\\Code.exe",
                "vscode": "C:\\Program Files\\Microsoft VS Code\\Code.exe",
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "calc": "calc.exe",
                "paint": "mspaint.exe",
                "explorer": "explorer.exe",
                "terminal": "wt.exe",
                "cmd": "cmd.exe",
                "powershell": "powershell.exe",
                "settings": "ms-settings:",
                "youtube": "https://youtube.com",
                "github": "https://github.com",
                "chatgpt": "https://chatgpt.com",
                "hotstar": "https://www.hotstar.com/in/home",
            }
        elif self.platform == "Darwin":  # macOS
            return {
                "chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "code": "/Applications/Visual Studio Code.app/Contents/MacOS/code",
                "vscode": "/Applications/Visual Studio Code.app/Contents/MacOS/code",
                "settings": "open /System/Library/PreferencePanes/System\\ Preferences.prefPane",
                "youtube": "open https://youtube.com",
                "github": "open https://github.com",
                "chatgpt": "open https://chat.openai.com",
                "hotstar": "open https://www.hotstar.com/in/home",
            }
        else:  # Linux
            return {
                "chrome": "google-chrome",
                "code": "code",
                "vscode": "code",
                "settings": "gnome-control-center",
                "youtube": "https://youtube.com",
                "github": "https://github.com",
                "chatgpt": "https://chatgpt.com/",
                "hotstar": "https://www.hotstar.com/in/home",
            }

    def _app_key(self, app_name: str) -> str:
        """Return a loose lookup key for app names from speech or shortcuts."""
        key = app_name.lower().strip()
        key = re.sub(r"[&+]", " and ", key)
        key = re.sub(r"[\(\[].*?[\)\]]", " ", key)
        key = re.sub(r"\b(app|application|desktop|shortcut)\b", " ", key)
        key = re.sub(r"\.(exe|lnk|url|app)$", "", key)
        key = re.sub(r"[^a-z0-9]+", " ", key)
        return re.sub(r"\s+", " ", key).strip()

    def _register_discovered_app(self, apps: Dict[str, str], name: str, path: str) -> None:
        """Register an app under a few predictable spoken-name variants."""
        if not name or not path:
            return

        key = self._app_key(name)
        keys = {
            key,
            self._app_key(Path(name).stem),
        }

        spoken_aliases = {
            "visual studio code": "vscode",
            "microsoft teams": "teams",
            "microsoft edge": "edge",
            "google chrome": "chrome",
        }
        if key in spoken_aliases:
            keys.add(spoken_aliases[key])

        for key in keys:
            if key:
                apps.setdefault(key, path)

    def _known_app_path_is_missing(self, app_path: str) -> bool:
        """Return True when a built-in path is stale and discovery found a better one."""
        if app_path.startswith(("http://", "https://", "shell:AppsFolder\\")):
            return False
        if app_path == "ms-settings:":
            return False
        if shutil.which(app_path):
            return False
        if os.path.isabs(app_path):
            return not os.path.exists(app_path)
        return False

    def _discover_installed_apps(self) -> Dict[str, str]:
        """Discover installed applications from OS app launch locations."""
        if self.platform == "Windows":
            return self._discover_windows_apps()
        if self.platform == "Darwin":
            return self._discover_macos_apps()
        return self._discover_linux_apps()

    def _discover_windows_apps(self) -> Dict[str, str]:
        """Discover Windows desktop and Store apps."""
        apps: Dict[str, str] = {}

        start_menu_dirs = [
            Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
            Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        ]
        for start_menu_dir in start_menu_dirs:
            if not start_menu_dir.exists():
                continue
            for shortcut in start_menu_dir.rglob("*"):
                if shortcut.suffix.lower() not in {".lnk", ".url"}:
                    continue
                if shortcut.stem.lower().startswith(("uninstall", "readme")):
                    continue
                self._register_discovered_app(apps, shortcut.stem, str(shortcut))

        self._discover_windows_app_paths(apps)
        self._discover_windows_store_apps(apps)
        return apps

    def _discover_windows_app_paths(self, apps: Dict[str, str]) -> None:
        """Discover apps registered in the Windows App Paths registry."""
        try:
            import winreg
        except Exception:
            return

        roots = [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"

        for root in roots:
            try:
                with winreg.OpenKey(root, registry_path) as app_paths_key:
                    index = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(app_paths_key, index)
                            index += 1
                        except OSError:
                            break

                        try:
                            with winreg.OpenKey(app_paths_key, subkey_name) as subkey:
                                executable, _ = winreg.QueryValueEx(subkey, "")
                        except OSError:
                            continue

                        if executable:
                            self._register_discovered_app(apps, subkey_name, executable)
                            self._register_discovered_app(apps, Path(subkey_name).stem, executable)
            except OSError:
                continue

    def _discover_windows_store_apps(self, apps: Dict[str, str]) -> None:
        """Discover Microsoft Store apps exposed through the Start menu."""
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "Get-StartApps | Select-Object Name,AppID | ConvertTo-Json -Compress",
                ],
                capture_output=True,
                text=True,
                timeout=8,
            )
        except Exception:
            return

        if result.returncode != 0 or not result.stdout.strip():
            return

        try:
            start_apps = json.loads(result.stdout)
        except json.JSONDecodeError:
            return

        if isinstance(start_apps, dict):
            start_apps = [start_apps]

        for app in start_apps:
            name = app.get("Name")
            app_id = app.get("AppID")
            if name and app_id:
                self._register_discovered_app(apps, name, f"shell:AppsFolder\\{app_id}")

    def _discover_macos_apps(self) -> Dict[str, str]:
        """Discover macOS apps from common Applications folders."""
        apps: Dict[str, str] = {}
        app_dirs = [Path("/Applications"), Path.home() / "Applications"]
        for app_dir in app_dirs:
            if not app_dir.exists():
                continue
            for app in app_dir.glob("*.app"):
                self._register_discovered_app(apps, app.stem, str(app))
        return apps

    def _discover_linux_apps(self) -> Dict[str, str]:
        """Discover Linux desktop apps from .desktop files."""
        apps: Dict[str, str] = {}
        desktop_dirs = [
            Path("/usr/share/applications"),
            Path("/usr/local/share/applications"),
            Path.home() / ".local" / "share" / "applications",
        ]

        for desktop_dir in desktop_dirs:
            if not desktop_dir.exists():
                continue
            for desktop_file in desktop_dir.glob("*.desktop"):
                try:
                    contents = desktop_file.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue

                name_match = re.search(r"^Name=(.+)$", contents, re.MULTILINE)
                exec_match = re.search(r"^Exec=(.+)$", contents, re.MULTILINE)
                if not name_match or not exec_match:
                    continue

                command = re.sub(r"\s+%[a-zA-Z]", "", exec_match.group(1)).strip()
                self._register_discovered_app(apps, name_match.group(1), command)

        return apps

    def _normalize_app_name(self, app_name: str) -> str:
        """Normalize common speech-recognition variants for app names."""
        normalized = re.sub(r"\s+", " ", app_name.lower().strip())
        normalized = re.sub(r"^(please|can you|could you)\s+", "", normalized)
        normalized = re.sub(r"\s+(please|for me|app)$", "", normalized).strip()
        aliases = {
            "google chrome": "chrome",
            "chrome browser": "chrome",
            "browser": "chrome",
            "note pad": "notepad",
            "notes pad": "notepad",
            "notepad app": "notepad",
            "calculator app": "calculator",
            "calculate": "calculator",
            "vs code": "vscode",
            "visual studio code": "vscode",
            "file explorer": "explorer",
            "windows explorer": "explorer",
            "command prompt": "cmd",
            "power shell": "powershell",
            "chat gpt": "chatgpt",
            "chat gbt": "chatgpt",
            "chat open ai": "chatgpt",
            "open ai chat": "chatgpt",
        }
        return aliases.get(normalized, normalized)

    def _lookup_app_path(self, app_name: str) -> Optional[str]:
        """Find an app path using aliases, discovered names, and executable lookup."""
        candidates = [
            app_name,
            self._app_key(app_name),
            self._app_key(Path(app_name).stem),
        ]

        for candidate in candidates:
            if candidate in self.app_paths:
                return self.app_paths[candidate]

        return shutil.which(app_name)
    
    def execute(self, command: str, argument: Optional[str] = None) -> Dict[str, Any]:
        """Execute a system command"""
        command = command.lower().strip()

        if command not in ALLOWED_COMMANDS:
            return {
                "success": False,
                "message": f"Command '{command}' is not allowed"
            }
        
        if command == "open":
            return self._open_application(argument)
        elif command == "close":
            return self._close_application(argument)
        elif command == "search":
            return self._search_google(argument)
        elif command == "screenshot":
            return self._take_screenshot()
        elif command == "create-folder":
            return self._create_folder(argument)
        elif command == "read-text":
            return self._read_text()
        elif command == "lock":
            return self._lock_screen()
        elif command == "shutdown":
            return self._shutdown_pc()
        elif command == "restart":
            return self._restart_pc()
        elif command == "coding-mode":
            return self._start_coding_mode()
        elif command == "open-project":
            return self._open_project_folder()
        elif command == "run-shell":
            return self._run_shell_command(argument)
        else:
            return {
                "success": False,
                "message": f"Unknown command: {command}"
            }

    def listen_and_execute(self, timeout: int = 5, phrase_time_limit: int = 4) -> Dict[str, Any]:
        """Listen to the default microphone, recognize speech, and execute it."""
        try:
            import speech_recognition as sr
        except Exception as e:
            return {
                "success": False,
                "message": f"SpeechRecognition is not available: {str(e)}"
            }

        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True

        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(
                    source,
                    timeout=max(1, int(timeout or 5)),
                    phrase_time_limit=max(1, int(phrase_time_limit or 4)),
                )
        except sr.WaitTimeoutError:
            return {
                "success": False,
                "message": "No speech heard",
                "text": ""
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Microphone error: {str(e)}",
                "text": ""
            }

        try:
            text = recognizer.recognize_google(audio).strip()
        except sr.UnknownValueError:
            return {
                "success": False,
                "message": "Could not understand audio",
                "text": ""
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "message": f"Speech recognition service error: {str(e)}",
                "text": ""
            }

        command_result = self.parse_voice_command(text)
        if not command_result["success"]:
            return {
                "success": False,
                "message": command_result.get("error", "Could not parse command"),
                "text": text
            }

        execution = self.execute(
            command_result["command"],
            command_result.get("argument")
        )
        return {
            "success": execution.get("success", False),
            "text": text,
            "parsed_command": command_result["command"],
            "execution": execution,
            "message": execution.get("message", "")
        }
    
    def _open_application(self, app_name: Optional[str]) -> Dict[str, Any]:
        """Open an application"""
        if not app_name:
            return {"success": False, "message": "Application name required"}
        
        app_name = self._normalize_app_name(app_name)
        
        app_path = self._lookup_app_path(app_name)
        if app_name.startswith(("http://", "https://")):
            return self._open_url(app_name)

        if app_path and app_path.startswith(("http://", "https://")):
            return self._open_url(app_path)

        if not app_path:
            app_path = app_name
        
        try:
            if self.platform == "Windows":
                if app_path == "ms-settings:":
                    os.startfile(app_path)
                elif app_path.startswith("shell:AppsFolder\\"):
                    subprocess.Popen(["explorer.exe", app_path])
                elif app_path.lower().endswith((".lnk", ".url")):
                    os.startfile(app_path)
                elif os.path.exists(app_path):
                    subprocess.Popen([app_path])
                else:
                    subprocess.Popen([app_path])
            elif self.platform == "Darwin":
                subprocess.Popen(["open", "-a", app_path])
            else:  # Linux
                subprocess.Popen([app_path])
            
            logger.info(f"Opened application: {app_name}")
            return {
                "success": True,
                "message": f"Opening {app_name}..."
            }
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
            return {
                "success": False,
                "message": f"Failed to open {app_name}: {str(e)}"
            }
    
    def _open_url(self, url: str) -> Dict[str, Any]:
        """Open a URL in default browser"""
        try:
            if self.platform == "Windows":
                os.startfile(url)
            else:
                webbrowser.open(url)
            
            return {"success": True, "message": f"Opening {url}..."}
        except Exception as e:
            return {"success": False, "message": f"Failed to open URL: {str(e)}"}

    def _send_windows_keys(self, keys: str) -> None:
        """Send Windows hotkeys without launching a new PowerShell process when possible."""
        try:
            import win32com.client

            win32com.client.Dispatch("WScript.Shell").SendKeys(keys)
            return
        except Exception:
            pass

        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"$wshell = New-Object -ComObject WScript.Shell; $wshell.SendKeys('{keys}')",
            ],
            timeout=3,
            check=True,
        )

    def _send_hotkey(self, action: str) -> Dict[str, Any]:
        """Send a common close hotkey to the active app."""
        hotkeys = {
            "tab": {
                "Windows": "^w",
                "Darwin": "command-w",
                "Linux": ["ctrl+w"],
            },
            "window": {
                "Windows": "%{F4}",
                "Darwin": "command-w",
                "Linux": ["alt+F4"],
            },
        }
        try:
            if self.platform == "Windows":
                self._send_windows_keys(hotkeys[action]["Windows"])
            elif self.platform == "Darwin":
                key = hotkeys[action]["Darwin"]
                key_name, modifier = key.split("-")
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        f'tell application "System Events" to keystroke "{key_name}" using {{{modifier} down}}',
                    ],
                    timeout=5,
                    check=True,
                )
            else:
                subprocess.run(["xdotool", "key", *hotkeys[action]["Linux"]], timeout=5, check=True)

            return {"success": True, "message": f"Closing active {action}"}
        except Exception as e:
            return {"success": False, "message": f"Failed to close active {action}: {str(e)}"}

    def _process_name_candidates(self, app_name: str) -> set:
        """Build likely process names for a spoken app name."""
        normalized = self._normalize_app_name(app_name)
        candidates = {normalized, self._app_key(normalized)}

        process_aliases = {
            "chrome": {"chrome", "chrome.exe"},
            "edge": {"msedge", "msedge.exe"},
            "vscode": {"code", "code.exe"},
            "code": {"code", "code.exe"},
            "notepad": {"notepad", "notepad.exe"},
            "calculator": {"calculator", "calculator.exe", "calc", "calc.exe"},
            "calc": {"calculator", "calculator.exe", "calc", "calc.exe"},
            "paint": {"mspaint", "mspaint.exe"},
            "explorer": {"explorer", "explorer.exe"},
            "terminal": {"windowsterminal", "windowsterminal.exe", "wt", "wt.exe"},
            "cmd": {"cmd", "cmd.exe"},
            "powershell": {"powershell", "powershell.exe", "pwsh", "pwsh.exe"},
        }
        candidates.update(process_aliases.get(normalized, set()))

        app_path = self._lookup_app_path(normalized)
        if app_path and not app_path.startswith(("http://", "https://", "shell:AppsFolder\\")):
            candidates.add(Path(app_path).stem.lower())
            candidates.add(Path(app_path).name.lower())

        return {candidate.lower() for candidate in candidates if candidate}

    def _close_application(self, target: Optional[str]) -> Dict[str, Any]:
        """Close an active tab/window or terminate an application by name."""
        if not target:
            return self._send_hotkey("window")

        target = self._normalize_app_name(target)
        target_key = self._app_key(target)

        tab_targets = {"tab", "current tab", "active tab", "browser tab", "this tab"}
        window_targets = {
            "window",
            "current window",
            "active window",
            "this window",
            "app",
            "application",
            "program",
            "current",
            "active",
            "this",
        }
        if target_key in tab_targets:
            return self._send_hotkey("tab")
        if target_key in window_targets:
            return self._send_hotkey("window")

        try:
            import psutil
        except Exception as e:
            return {"success": False, "message": f"psutil is required to close apps: {str(e)}"}

        candidates = self._process_name_candidates(target)
        closed = []
        denied = []

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                proc_name = (proc.info.get("name") or "").lower()
                proc_stem = Path(proc_name).stem.lower()
                if proc_name not in candidates and proc_stem not in candidates:
                    continue
                proc.terminate()
                closed.append(proc.info.get("name") or str(proc.pid))
            except psutil.AccessDenied:
                denied.append(proc.info.get("name") or str(proc.pid))
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                continue

        if closed:
            return {
                "success": True,
                "message": f"Closing {target}...",
                "data": {"processes": sorted(set(closed))},
            }
        if denied:
            return {
                "success": False,
                "message": f"Found {target}, but permission was denied while closing it.",
                "data": {"processes": sorted(set(denied))},
            }
        return {"success": False, "message": f"No running app found for {target}"}
    
    def _search_google(self, query: Optional[str]) -> Dict[str, Any]:
        """Search Google"""
        if not query:
            return {"success": False, "message": "Search query required"}
        
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        return self._open_url(url)
    
    def _take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot"""
        try:
            from PIL import ImageGrab
            import time
            
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(os.path.expanduser("~"), "Pictures", filename)
            
            # Create Pictures directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            return {
                "success": True,
                "message": f"Screenshot saved: {filepath}",
                "data": {"path": filepath}
            }
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {
                "success": False,
                "message": f"Failed to take screenshot: {str(e)}"
            }
    
    def _create_folder(self, folder_name: Optional[str]) -> Dict[str, Any]:
        """Create a new folder"""
        if not folder_name:
            return {"success": False, "message": "Folder name required"}
        
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", folder_name)
            os.makedirs(desktop_path, exist_ok=True)
            
            return {
                "success": True,
                "message": f"Folder created: {desktop_path}",
                "data": {"path": desktop_path}
            }
        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            return {
                "success": False,
                "message": f"Failed to create folder: {str(e)}"
            }
    
    def _read_text(self) -> Dict[str, Any]:
        """Read selected text (clipboard)"""
        try:
            import subprocess
            if self.platform == "Windows":
                result = subprocess.run(
                    ['powershell', '-Command', 'Get-Clipboard'],
                    capture_output=True,
                    text=True
                )
                text = result.stdout
            elif self.platform == "Darwin":
                result = subprocess.run(
                    ['pbpaste'],
                    capture_output=True,
                    text=True
                )
                text = result.stdout
            else:  # Linux
                result = subprocess.run(
                    ['xclip', '-selection', 'clipboard', '-o'],
                    capture_output=True,
                    text=True
                )
                text = result.stdout
            
            return {
                "success": True,
                "message": "Text read from clipboard",
                "data": {"text": text}
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to read text: {str(e)}"
            }
    
    def _lock_screen(self) -> Dict[str, Any]:
        """Lock the screen"""
        try:
            if self.platform == "Windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            elif self.platform == "Darwin":
                subprocess.run([
                    "osascript",
                    "-e",
                    "tell application \"System Events\" to keystroke \"q\" using {command down, control down}"
                ])
            else:  # Linux
                subprocess.run(["loginctl", "lock-session"])
            
            return {"success": True, "message": "Screen locked"}
        except Exception as e:
            return {"success": False, "message": f"Failed to lock screen: {str(e)}"}
    
    def _shutdown_pc(self) -> Dict[str, Any]:
        """Shutdown the PC"""
        try:
            if self.platform == "Windows":
                subprocess.run(["shutdown", "/s", "/t", "60"])
            elif self.platform == "Darwin":
                subprocess.run(["osascript", "-e", "tell application \"System Events\" to shut down"])
            else:  # Linux
                subprocess.run(["sudo", "shutdown", "-h", "+1"])
            
            return {"success": True, "message": "Shutdown initiated"}
        except Exception as e:
            return {"success": False, "message": f"Failed to shutdown: {str(e)}"}

    def _restart_pc(self) -> Dict[str, Any]:
        """Restart the PC"""
        try:
            if self.platform == "Windows":
                subprocess.run(["shutdown", "/r", "/t", "60"])
            elif self.platform == "Darwin":
                subprocess.run(["osascript", "-e", "tell application \"System Events\" to restart"])
            else:  # Linux
                subprocess.run(["sudo", "shutdown", "-r", "+1"])

            return {"success": True, "message": "Restart initiated"}
        except Exception as e:
            return {"success": False, "message": f"Failed to restart: {str(e)}"}

    def _run_shell_command(self, shell_command: Optional[str]) -> Dict[str, Any]:
        """Run an explicit shell command when enabled by configuration."""
        if not ENABLE_SHELL_COMMANDS:
            return {
                "success": False,
                "message": "Shell commands are disabled. Set ENABLE_SHELL_COMMANDS=True in .env to enable them."
            }

        if not shell_command:
            return {"success": False, "message": "Shell command required"}

        blocked_patterns = [
            r"\brm\b",
            r"\bdel\b",
            r"\brmdir\b",
            r"\bformat\b",
            r"\bdiskpart\b",
            r"\breg\s+delete\b",
            r"\bshutdown\b",
            r"\bRemove-Item\b",
            r"\bgit\s+reset\b",
        ]
        if any(re.search(pattern, shell_command, re.IGNORECASE) for pattern in blocked_patterns):
            return {
                "success": False,
                "message": "That shell command is blocked for safety."
            }

        try:
            result = subprocess.run(
                shell_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=MAX_COMMAND_TIMEOUT,
            )
            output = (result.stdout or result.stderr or "").strip()
            return {
                "success": result.returncode == 0,
                "message": output or f"Command finished with exit code {result.returncode}",
                "data": {"returncode": result.returncode, "output": output}
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Shell command timed out"}
        except Exception as e:
            return {"success": False, "message": f"Failed to run shell command: {str(e)}"}
    
    def _start_coding_mode(self) -> Dict[str, Any]:
        """Start coding mode - open VS Code, Chrome, GitHub"""
        try:
            # Open VS Code
            self._open_application("vscode")
            
            # Open Chrome
            self._open_application("chrome")
            
            # Open GitHub
            self._open_url(self.app_paths.get("github", "https://github.com"))
            
            return {
                "success": True,
                "message": "Coding mode activated! Opening VS Code, Chrome, and GitHub..."
            }
        except Exception as e:
            logger.error(f"Failed to start coding mode: {e}")
            return {
                "success": False,
                "message": f"Failed to start coding mode: {str(e)}"
            }
    
    def _open_project_folder(self) -> Dict[str, Any]:
        """Open project folder"""
        try:
            projects_path = os.path.join(os.path.expanduser("~"), "My_Projects")
            if os.path.exists(projects_path):
                if self.platform == "Windows":
                    os.startfile(projects_path)
                elif self.platform == "Darwin":
                    subprocess.Popen(["open", projects_path])
                else:
                    subprocess.Popen(["xdg-open", projects_path])
                
                return {"success": True, "message": f"Opening {projects_path}"}
            else:
                return {
                    "success": False,
                    "message": "Project folder not found"
                }
        except Exception as e:
            return {"success": False, "message": f"Failed to open project: {str(e)}"}
    
    def parse_voice_command(self, text: str) -> Dict[str, Any]:
        """Parse voice command text and extract command"""
        original_text = text.strip()
        text_lower = original_text.lower().strip()

        phrase_commands = [
            (["take screenshot", "capture screen", "screenshot"], "screenshot", None),
            (["lock screen", "lock my pc", "lock computer", "lock"], "lock", None),
            (["shutdown pc", "shutdown computer", "shut down pc", "shut down computer", "shutdown", "shut down", "turn off computer", "turn off pc"], "shutdown", None),
            (["restart pc", "restart computer", "reboot pc", "reboot computer", "restart", "reboot"], "restart", None),
            (["close current tab", "close active tab", "close browser tab", "close tab"], "close", "tab"),
            (["close current window", "close active window", "close this window", "close window"], "close", "window"),
            (["start coding mode", "coding mode"], "coding-mode", None),
            (["read selected text", "read clipboard", "read text"], "read-text", None),
            (["open project folder", "open projects folder"], "open-project", None),
        ]

        for phrases, command, arg in phrase_commands:
            single_word_power_phrases = {"shutdown", "shut down", "restart", "reboot"}
            if command in {"shutdown", "restart"}:
                matched = False
                for phrase in phrases:
                    if phrase in single_word_power_phrases:
                        polite_forms = {
                            phrase,
                            f"please {phrase}",
                            f"{phrase} please",
                            f"please {phrase} my pc",
                            f"please {phrase} my computer",
                        }
                        matched = text_lower in polite_forms
                    else:
                        matched = phrase in text_lower
                    if matched:
                        break
            else:
                matched = any(phrase in text_lower for phrase in phrases)

            if matched:
                return {"success": True, "command": command, "argument": arg}

        for prefix in ["search google for ", "google search ", "search google ", "search for ", "search "]:
            if text_lower.startswith(prefix):
                return {
                    "success": True,
                    "command": "search",
                    "argument": original_text[len(prefix):].strip()
                }
            marker = f" {prefix}"
            if marker in text_lower:
                start = text_lower.index(marker) + len(marker)
                return {
                    "success": True,
                    "command": "search",
                    "argument": original_text[start:].strip()
                }

        for prefix in ["create folder named ", "make folder named ", "create folder ", "make folder "]:
            if text_lower.startswith(prefix):
                return {
                    "success": True,
                    "command": "create-folder",
                    "argument": original_text[len(prefix):].strip()
                }
            marker = f" {prefix}"
            if marker in text_lower:
                start = text_lower.index(marker) + len(marker)
                return {
                    "success": True,
                    "command": "create-folder",
                    "argument": original_text[start:].strip()
                }

        for prefix in ["run command ", "execute command ", "run shell "]:
            if text_lower.startswith(prefix):
                return {
                    "success": True,
                    "command": "run-shell",
                    "argument": original_text[len(prefix):].strip()
                }
            marker = f" {prefix}"
            if marker in text_lower:
                start = text_lower.index(marker) + len(marker)
                return {
                    "success": True,
                    "command": "run-shell",
                    "argument": original_text[start:].strip()
                }

        for prefix in ["close ", "quit ", "exit "]:
            if text_lower.startswith(prefix):
                return {
                    "success": True,
                    "command": "close",
                    "argument": original_text[len(prefix):].strip()
                }
            marker = f" {prefix}"
            if marker in text_lower:
                start = text_lower.index(marker) + len(marker)
                return {
                    "success": True,
                    "command": "close",
                    "argument": original_text[start:].strip()
                }

        for prefix in ["open ", "launch ", "start "]:
            if text_lower.startswith(prefix):
                return {
                    "success": True,
                    "command": "open",
                    "argument": original_text[len(prefix):].strip()
                }
            marker = f" {prefix}"
            if marker in text_lower:
                start = text_lower.index(marker) + len(marker)
                return {
                    "success": True,
                    "command": "open",
                    "argument": original_text[start:].strip()
                }
        
        return {
            "success": False,
            "error": f"Could not parse command: {text}"
        }
