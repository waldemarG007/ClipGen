# -*- coding: utf-8 -*-
"""
Haupt-Controller für die ClipGen-Anwendung.

Diese Datei enthält die Hauptlogik der Anwendung, einschließlich der Initialisierung,
der Hotkey-Verwaltung, der Einstellungsverwaltung und der Kommunikation mit den
verschiedenen KI-Anbietern.
"""
import sys
import os
import json
import logging
import time
from multiprocessing import Queue
from multiprocessing.queues import Empty
import threading
import pyperclip
from PIL import ImageGrab
import google.generativeai as genai
from google.generativeai import GenerationConfig
from pynput import keyboard as pkb
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPoint
from PyQt5.QtWidgets import QApplication
from groq import Groq
from mistralai.client import MistralClient
import ollama
from libs.ClipGen_view import ClipGenView

# Logging-Konfiguration
logger = logging.getLogger('ClipGen')
logger.setLevel(logging.INFO)

# Konsolen-Handler nur für Fehler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(console_handler)

# Standardkonfiguration
DEFAULT_CONFIG = {
    "api_key": "DEIN_API_SCHLÜSSEL_HIER",
    "hotkeys": [
        {"combination": "Ctrl+F1", "name": "Korrektur", "log_color": "#FFFFFF", "prompt": "Bitte korrigiere den folgenden Text..."},
        {"combination": "Ctrl+F2", "name": "Umschreiben", "log_color": "#A3BFFA", "prompt": "Bitte schreibe den folgenden Text bei Bedarf um..."},
        {"combination": "Ctrl+F3", "name": "Übersetzung", "log_color": "#FBB6CE", "prompt": "Bitte übersetze den folgenden Text auf Deutsch..."},
        {"combination": "Ctrl+F6", "name": "Erklärung", "log_color": "#FAF089", "prompt": "Bitte erkläre den folgenden Text in einfachen Worten..."},
        {"combination": "Ctrl+F7", "name": "Frage beantworten", "log_color": "#FBD38D", "prompt": "Bitte beantworte die folgende Frage..."},
        {"combination": "Ctrl+F8", "name": "Anfrage", "log_color": "#B5EAD7", "prompt": "Führe die Anfrage des Benutzers aus..."},
        {"combination": "Ctrl+F9", "name": "Kommentar", "log_color": "#D6BCFA", "prompt": "Generiere einen sarkastischen Kommentar..."},
        {"combination": "Ctrl+F10", "name": "Bildanalyse", "log_color": "#A1CFF9", "prompt": "Analysiere das Bild..."}
    ]
}

class ClipGen(ClipGenView):
    """
    Die Hauptklasse für die ClipGen-Anwendung. Erbt von der View-Klasse
    und steuert die gesamte Anwendungslogik.
    """
    def __init__(self):
        # Einstellungen vor der GUI-Initialisierung laden
        self.load_settings()

        # Ansicht initialisieren
        super().__init__(self)
        self.setting_changed.connect(self.update_setting)

        # KI-Anbieter initialisieren
        self.configure_ai_provider()
        self.queue = Queue()
        self.stop_event = threading.Event()
        try:
            self.keyboard = pkb.Controller()
        except Exception as e:
            logger.warning(f"Tastatur-Controller konnte nicht initialisiert werden: {e}")
            self.keyboard = None

        # Hotkeys abfangen
        self.key_states = {key["combination"].lower(): False for key in self.config["hotkeys"]}
        self.key_states["ctrl"] = False
        self.key_states["alt"] = False
        self.key_states["shift"] = False
        try:
            self.listener_thread = threading.Thread(target=self.hotkey_listener, args=(self.queue,), daemon=True)
            self.listener_thread.start()
        except Exception as e:
            logger.error(f"Hotkey-Listener konnte nicht gestartet werden: {e}")
            self.listener_thread = None

        self.check_queue()

        # Log-Handler einrichten
        gui_handler = self.create_log_handler()
        gui_handler.setLevel(logging.INFO)
        gui_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(gui_handler)

        # Startnachricht
        self.log_signal.emit("ClipGen gestartet", "#FFFFFF")

    def create_log_handler(self):
        """Erstellt einen benutzerdefinierten Log-Handler, der Nachrichten an die GUI sendet."""
        class LogHandler(logging.Handler):
            def __init__(self, log_signal, action_colors, config):
                super().__init__()
                self.log_signal = log_signal
                # Farb-Wörterbuch anpassen, Aktionsnamen anstelle von Tastenkombinationen verwenden
                self.action_colors = {k["name"]: k["log_color"] for k in action_colors}
                self.start_times = {}
                self.config = config
                self.processed_activations = set()  # Um bereits verarbeitete Aktivierungen zu verfolgen

            def emit(self, record):
                try:
                    msg = self.format(record)

                    # Doppelte Nachrichten aus der Warteschlange überspringen
                    if "Received event from queue" in msg:
                        return

                    # Aktivierung von Aktionen verarbeiten
                    if "Activated" in msg:
                        # Aktionsnamen aus der Nachricht extrahieren
                        for combo, name in [(h["combination"], h["name"]) for h in self.config["hotkeys"]]:
                            if name in msg:
                                # Eindeutige ID für die Aktivierung erstellen
                                timestamp = time.strftime('%H:%M:%S')
                                activation_id = f"{combo}:{name}:{timestamp}"

                                # Überspringen, falls diese Aktivierung bereits verarbeitet wurde
                                if activation_id in self.processed_activations:
                                    return

                                self.processed_activations.add(activation_id)
                                self.start_times[name] = time.time()

                                # Farbe für die Aktion anhand ihres Namens finden
                                color = self.action_colors.get(name, "#FFFFFF")

                                # Nachricht über die Aktion senden
                                formatted_msg = f"{combo}: {name} - {timestamp}"
                                self.log_signal.emit(formatted_msg, color)
                                return

                    # Abschlussnachrichten formatieren
                    if "Processed:" in msg:
                        for name, start_time in list(self.start_times.items()):
                            if name in msg:
                                elapsed = time.time() - self.start_times.pop(name)
                                # Farbe für die Aktion anhand ihres Namens finden
                                color = self.action_colors.get(name, "#FFFFFF")

                                # Zuerst die Nachricht über die Ausführungszeit senden
                                self.log_signal.emit(f"Abgeschlossen in {elapsed:.2f} Sekunden", "#888888")

                                # Dann das Ergebnis senden
                                result = msg.split("Processed:")[1].strip()
                                self.log_signal.emit(result, color)
                                return

                    # Fehler verarbeiten
                    if record.levelno >= logging.ERROR:
                        self.log_signal.emit(f"Fehler: {msg}", "#FF5555")
                        return

                    # Warnungen verarbeiten
                    if record.levelno == logging.WARNING:
                        self.log_signal.emit(msg, "#FFDD55")
                        return

                    # Andere Informationsnachrichten
                    self.log_signal.emit(msg, "#FFFFFF")

                except Exception as e:
                    print(f"Fehler im Log-Handler: {e}")

        return LogHandler(self.log_signal, self.config["hotkeys"], self.config)

    def load_settings(self):
        """Lädt die Einstellungen aus der settings.json-Datei."""
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = DEFAULT_CONFIG.copy()
            self.save_settings()

    def save_settings(self):
        """Speichert die aktuellen Einstellungen in der settings.json-Datei."""
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def update_logger_colors(self):
        """Aktualisiert die Farben im Logger nach einer Änderung der Hotkey-Einstellungen."""
        for handler in logger.handlers:
            if hasattr(handler, 'action_colors'):
                handler.action_colors = {k["name"]: k["log_color"] for k in self.config["hotkeys"]}

    def update_prompt(self, hotkey, text):
        """Aktualisiert den Prompt-Text für einen bestimmten Hotkey."""
        for h in self.config["hotkeys"]:
            if h["combination"] == hotkey["combination"]:
                h["prompt"] = text
                break
        self.save_settings()
        self.restart_hotkey_listener()

    def update_name(self, hotkey, text):
        """Aktualisiert den Namen für einen bestimmten Hotkey."""
        for h in self.config["hotkeys"]:
            if h["combination"] == hotkey["combination"]:
                h["name"] = text
                self.update_buttons()
                # Farben im Logger aktualisieren
                self.update_logger_colors()
                break
        self.save_settings()
        self.restart_hotkey_listener()

    def update_color(self, hotkey, color):
        """Aktualisiert die Log-Farbe für einen bestimmten Hotkey."""
        for h in self.config["hotkeys"]:
            if h["combination"] == hotkey["combination"]:
                h["log_color"] = color
                self.update_buttons()

                # Farben im Logger aktualisieren
                self.update_logger_colors()

                break
        self.save_settings()
        self.restart_hotkey_listener()

    def update_hotkey(self, old_combo, new_combo):
        """Aktualisiert die Tastenkombination für einen Hotkey."""
        for h in self.config["hotkeys"]:
            if h["combination"] == old_combo:
                h["combination"] = new_combo
                # key_states für die neue Kombination aktualisieren
                self.key_states = {key["combination"].lower(): False for key in self.config["hotkeys"]}
                self.key_states["ctrl"] = False
                self.key_states["alt"] = False
                self.update_buttons()
                break
        self.save_settings()
        self.restart_hotkey_listener()

    def restart_hotkey_listener(self):
        """Startet den Hotkey-Listener-Thread neu."""
        if self.listener_thread is None:
            return
        self.stop_event.set()
        self.listener_thread.join()
        self.stop_event = threading.Event()
        try:
            self.listener_thread = threading.Thread(target=self.hotkey_listener, args=(self.queue,), daemon=True)
            self.listener_thread.start()
        except Exception as e:
            logger.error(f"Hotkey-Listener konnte nicht neu gestartet werden: {e}")
            self.listener_thread = None


    def hotkey_listener(self, queue):
        """Überwacht globale Tastendrücke auf Hotkey-Kombinationen."""
        def on_press(key, queue):
            try:
                # Taste zum Vergleich in einen String umwandeln
                key_str = str(key).lower().replace("key.", "").replace("'", "")

                # Modifikatortasten-Drücke verfolgen
                if key_str in ("ctrl_l", "ctrl_r"):
                    self.key_states["ctrl"] = True
                    return
                if key_str in ("alt_l", "alt_r"):
                    self.key_states["alt"] = True
                    return
                if key_str in ("shift_l", "shift_r"):
                    self.key_states["shift"] = True
                    return

                # Tastenstatus für das Debugging protokollieren
                logger.debug(f"Taste gedrückt: {key_str}, Modifikatoren: Ctrl={self.key_states['ctrl']}, Alt={self.key_states['alt']}, Shift={self.key_states['shift']}")

                # Tastenkombinationen prüfen
                for hotkey in self.config["hotkeys"]:
                    combo_lower = hotkey["combination"].lower()

                    # Letzte Taste in der Kombination umwandeln (nach dem letzten '+')
                    if "+" in combo_lower:
                        combo_parts = combo_lower.split("+")
                        last_key = combo_parts[-1].strip()

                        # Modifikatoren prüfen
                        has_ctrl = "ctrl" in combo_lower
                        has_alt = "alt" in combo_lower
                        has_shift = "shift" in combo_lower

                        # Für Zifferntasten und F1-F12-Tasten
                        if (last_key == key_str or
                            (last_key.startswith("f") and key_str.startswith("f") and last_key == key_str) or
                            (last_key.isdigit() and key_str.isdigit() and last_key == key_str)):

                            # Prüfen, ob alle erforderlichen Modifikatoren gedrückt und keine überflüssigen vorhanden sind
                            if ((has_ctrl == self.key_states["ctrl"]) and
                                (has_alt == self.key_states["alt"]) and
                                (has_shift == self.key_states["shift"])):

                                logger.info(f"[{hotkey['combination']}: {hotkey['name']}] Aktiviert")
                                queue.put(hotkey["name"])

                                # Status zurücksetzen
                                self.key_states["ctrl"] = False
                                self.key_states["alt"] = False
                                self.key_states["shift"] = False
                                return
                    else:
                        # Verarbeitung einzelner Tasten (ohne Modifikatoren)
                        if combo_lower == key_str:
                            logger.info(f"[{hotkey['combination']}: {hotkey['name']}] Aktiviert")
                            queue.put(hotkey["name"])
                            return

            except Exception as e:
                logger.error(f"Fehler in on_press: {e}")

        def on_release(key, queue):
            try:
                key_str = str(key).lower().replace("key.", "").replace("'", "")
                if key_str in ("ctrl_l", "ctrl_r"):
                    self.key_states["ctrl"] = False
                if key_str in ("alt_l", "alt_r"):
                    self.key_states["alt"] = False
                if key_str in ("shift_l", "shift_r"):
                    self.key_states["shift"] = False
            except Exception as e:
                logger.error(f"Fehler in on_release: {e}")

        with pkb.Listener(on_press=lambda k: on_press(k, queue), on_release=lambda k: on_release(k, queue)) as listener:
            self.stop_event.wait()
            listener.stop()

    def update_setting(self, keys):
        """Aktualisiert eine verschachtelte Einstellung in der Konfiguration."""
        value = keys.pop()
        d = self.config
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
        self.save_settings()
        self.configure_ai_provider()

    def configure_ai_provider(self):
        """Konfiguriert den ausgewählten KI-Anbieter mit den entsprechenden Anmeldeinformationen."""
        provider = self.config.get("general", {}).get("provider", "Gemini")

        if provider == "Gemini":
            api_key = self.config.get("providers", {}).get("gemini", {}).get("api_key")
            if api_key:
                genai.configure(api_key=api_key)
        elif provider == "Groq":
            api_key = self.config.get("providers", {}).get("groq", {}).get("api_key")
            self.groq_client = Groq(api_key=api_key)
        elif provider == "Mistral":
            api_key = self.config.get("providers", {}).get("mistral", {}).get("api_key")
            self.mistral_client = MistralClient(api_key=api_key)
        elif provider == "Ollama":
            host = self.config.get("providers", {}).get("ollama", {}).get("host", "http://localhost:11434")
            self.ollama_client = ollama.Client(host=host)

    def process_text(self, text, action, prompt, is_image=False):
        """Verarbeitet den Text mit dem ausgewählten KI-Anbieter."""
        provider = self.config.get("general", {}).get("provider", "Gemini")
        try:
            if provider == "Gemini":
                return self._process_gemini(text, action, prompt, is_image)
            elif provider == "Groq":
                return self._process_groq(text, action, prompt)
            elif provider == "Mistral":
                return self._process_mistral(text, action, prompt)
            elif provider == "Ollama":
                return self._process_ollama(text, action, prompt, is_image)
            else:
                logger.error(f"Unbekannter Anbieter: {provider}")
                return ""
        except Exception as e:
            logger.error(f"Fehler bei der Textverarbeitung mit {provider}: {e}")
            return ""

    def _process_groq(self, text, action, prompt):
        hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
        combo = hotkey["combination"] if hotkey else ""
        full_prompt = prompt + text
        chat_completion = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model=self.config.get("providers", {}).get("groq", {}).get("model", "llama3-8b-8192"),
        )
        result = chat_completion.choices[0].message.content
        logger.info(f"[{combo}: {action}] Verarbeitet: {result}")
        return result

    def _process_mistral(self, text, action, prompt):
        hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
        combo = hotkey["combination"] if hotkey else ""
        full_prompt = prompt + text
        messages = [{"role": "user", "content": full_prompt}]
        chat_response = self.mistral_client.chat(
            model=self.config.get("providers", {}).get("mistral", {}).get("model", "mistral-large-latest"),
            messages=messages,
        )
        result = chat_response.choices[0].message.content
        logger.info(f"[{combo}: {action}] Verarbeitet: {result}")
        return result

    def _process_ollama(self, text, action, prompt, is_image=False):
        hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
        combo = hotkey["combination"] if hotkey else ""
        full_prompt = prompt + text

        request_data = {
            "model": self.config.get("providers", {}).get("ollama", {}).get("model", "llama3"),
            "prompt": full_prompt,
            "stream": False
        }

        if is_image:
            image = ImageGrab.grabclipboard()
            if not image:
                logger.warning(f"[{combo}: {action}] Zwischenablage ist leer")
                return ""
            request_data["images"] = [image]

        response = self.ollama_client.generate(**request_data)
        result = response['response']
        logger.info(f"[{combo}: {action}] Verarbeitet: {result}")
        return result

    def _process_gemini(self, text, action, prompt, is_image=False):
        try:
            # Hotkey für diese Aktion finden
            hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
            combo = hotkey["combination"] if hotkey else ""

            if is_image:
                image = ImageGrab.grabclipboard()
                if not image:
                    logger.warning(f"[{combo}: {action}] Zwischenablage ist leer")
                    return ""
                response = genai.GenerativeModel("models/gemini-2.0-flash-exp").generate_content(
                    contents=[prompt, image], generation_config=GenerationConfig(temperature=0.7, max_output_tokens=2048)
                )
            else:
                full_prompt = prompt + text
                response = genai.GenerativeModel("models/gemini-2.0-flash-exp").generate_content(
                    full_prompt, generation_config=GenerationConfig(temperature=0.7, max_output_tokens=2048)
                )

            result = response.text.strip() if response and response.text else ""
            logger.info(f"[{combo}: {action}] Verarbeitet: {result}")
            return result
        except Exception as e:
            logger.error(f"[{combo}: {action}] Fehler bei der Anfrage an Gemini: {e}")
            return ""

    def handle_text_operation(self, action, prompt):
        # Hotkey für diese Aktion finden
        hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
        combo = hotkey["combination"] if hotkey else ""

        try:
            # Aktivierung der Aktion protokollieren
            logger.info(f"[{combo}: {action}] Aktiviert")

            # Text aus der Zwischenablage kopieren
            if self.keyboard:
                with self.keyboard.pressed(pkb.Key.ctrl):
                    self.keyboard.press('c')
                    self.keyboard.release('c')
                time.sleep(0.1)

            is_image = action == "Bildanalyse"
            if is_image:
                processed_text = self.process_text("", action, prompt, is_image=True)
            else:
                text = pyperclip.paste()
                if not text.strip():
                    # Erneut versuchen zu kopieren
                    if self.keyboard:
                        with self.keyboard.pressed(pkb.Key.ctrl):
                            self.keyboard.press('c')
                            self.keyboard.release('c')
                        time.sleep(0.5)
                    text = pyperclip.paste()
                    if not text.strip():
                        logger.warning(f"[{combo}: {action}] Zwischenablage nach zwei Kopierversuchen leer")
                        return
                processed_text = self.process_text(text, action, prompt)

            if processed_text:
                pyperclip.copy(processed_text)

                time.sleep(0.3)
                if self.keyboard:
                    with self.keyboard.pressed(pkb.Key.ctrl):
                        self.keyboard.press('v')
                        self.keyboard.release('v')
        except Exception as e:
            logger.error(f"[{combo}: {action}] Fehler: {e}")

    def check_queue(self):
        """Überprüft die Warteschlange auf neue Hotkey-Ereignisse."""
        def queue_worker():
            while not self.stop_event.is_set():
                try:
                    event = self.queue.get(timeout=0.5)
                    logger.info(f"Ereignis aus Warteschlange empfangen: {event}")
                    for hotkey in self.config["hotkeys"]:
                        if hotkey["name"] == event:
                            threading.Thread(target=self.handle_text_operation, args=(hotkey["name"], hotkey["prompt"]), daemon=True).start()
                            break
                except Empty:
                    continue
                except Exception as e:
                    logger.error(f"Fehler bei der Warteschlangenverarbeitung: {e}")

        threading.Thread(target=queue_worker, daemon=True).start()

    def closeEvent(self, event):
        """Behandelt das Schließen des Fensters."""
        self.save_settings()
        self.stop_event.set()
        if self.listener_thread is not None and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1.0)
        event.accept()
        os._exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClipGen()
    window.show()
    sys.exit(app.exec_())
