import time

import speech_recognition as sr

from system_commands import SystemCommandExecutor


def main():
    executor = SystemCommandExecutor()
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8

    print("[VOICE] DINO voice listener started", flush=True)
    print("[VOICE] Press Ctrl+C in this terminal to stop", flush=True)

    try:
        with sr.Microphone() as source:
            print("[VOICE] Calibrating microphone noise...", flush=True)
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[VOICE] Listening...", flush=True)

            while True:
                try:
                    audio = recognizer.listen(source, timeout=8, phrase_time_limit=5)
                except sr.WaitTimeoutError:
                    print("[VOICE] No speech heard. Listening again...", flush=True)
                    continue

                try:
                    text = recognizer.recognize_google(audio).strip()
                except sr.UnknownValueError:
                    print("[VOICE] Could not understand audio", flush=True)
                    continue
                except sr.RequestError as error:
                    print(f"[VOICE] Speech recognition service error: {error}", flush=True)
                    time.sleep(2)
                    continue

                print(f"[VOICE] Heard: {text}", flush=True)
                parsed = executor.parse_voice_command(text)

                if not parsed.get("success"):
                    print(f"[VOICE] Could not parse command: {text}", flush=True)
                    continue

                result = executor.execute(parsed["command"], parsed.get("argument"))
                print(f"[VOICE] {result.get('message', result)}", flush=True)

    except KeyboardInterrupt:
        print("\n[VOICE] DINO voice listener stopped", flush=True)
    except Exception as error:
        print(f"[VOICE] Microphone error: {error}", flush=True)


if __name__ == "__main__":
    main()
