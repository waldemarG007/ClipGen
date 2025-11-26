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
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import GenerationConfig
from mistralai import Mistral
from groq import Groq
import win32api
import win32con
from pynput import keyboard as pkb
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPoint
from PyQt5.QtWidgets import QApplication
import ctypes
from ctypes import windll, c_int, byref
from libs.ClipGen_view import ClipGenView

# Load .env variables
load_dotenv()

# Logging setup
logger = logging.getLogger('ClipGen')
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(console_handler)

DEFAULT_CONFIG = {
    "gemini_api_key": os.getenv("Gemini_api_key", ""),
    "mistral_api_key": os.getenv("Mistral_api_key", ""),
    "groq_api_key": os.getenv("groq_api_key", ""),
    "hotkeys": [
        {
            "combination": "Ctrl+F1",
            "name": "Коррекция",
            "log_color": "#FFFFFF",
            "prompt": "Пожалуйста, исправь следующий текст...",
            "api_provider": "Gemini",
            "model": "gemini-2.0-flash-exp",
            "type": "text"
        }
    ]
}

class ClipGen(ClipGenView):
    def __init__(self):
        self.load_settings()
        super().__init__()  # Zuerst Elternklasse initialisieren
        
        # Initialize API clients
        self.init_api_clients()
        
        self.queue = Queue()
        self.stop_event = threading.Event()
        
        # Hotkey tracking
        self.key_states = {key["combination"].lower(): False for key in self.config["hotkeys"]}
        self.key_states["ctrl"] = False
        self.key_states["alt"] = False
        self.key_states["shift"] = False
        
        self.listener_thread = threading.Thread(target=self.hotkey_listener, args=(self.queue,), daemon=True)
        self.listener_thread.start()
        self.check_queue()
        
        gui_handler = self.create_log_handler()
        gui_handler.setLevel(logging.INFO)
        gui_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(gui_handler)
        
        self.log_signal.emit("ClipGen запущен", "#FFFFFF")
        self.quit_signal.connect(self.real_closeEvent)

    def apply_styles(self):
            """Ruft die apply_styles-Methode der Elternklasse auf"""
            
    def init_api_clients(self):
        """Initialize API clients for all providers"""
        # Gemini
        if self.config.get("gemini_api_key"):
            genai.configure(api_key=self.config["gemini_api_key"])
        
        # Mistral
        self.mistral_client = None
        if self.config.get("mistral_api_key"):
            self.mistral_client = Mistral(api_key=self.config["mistral_api_key"])
        
        # Groq
        self.groq_client = None
        if self.config.get("groq_api_key"):
            self.groq_client = Groq(api_key=self.config["groq_api_key"])

    def load_settings(self):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = DEFAULT_CONFIG.copy()
            self.save_settings()

    def save_settings(self):
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def process_text_with_provider(self, text, action, prompt, is_image=False, provider=None, model=None):
        """Process text with selected provider"""
        try:
            hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
            combo = hotkey["combination"] if hotkey else ""
            
            provider = provider or hotkey.get("api_provider", "Gemini")
            model = model or hotkey.get("model", "gemini-2.0-flash-exp")
            
            if provider == "Gemini":
                return self._process_with_gemini(text, action, prompt, is_image, model)
            elif provider == "Mistral":
                return self._process_with_mistral(text, action, prompt, model)
            elif provider == "Groq":
                return self._process_with_groq(text, action, prompt, model)
            else:
                logger.error(f"[{combo}: {action}] Ungültiger Provider: {provider}")
                return ""
        except Exception as e:
            logger.error(f"[{combo}: {action}] Fehler: {e}")
            return ""

    def _process_with_gemini(self, text, action, prompt, is_image, model):
        """Process with Google Gemini"""
        hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
        combo = hotkey["combination"] if hotkey else ""
        
        try:
            if is_image:
                image = ImageGrab.grabclipboard()
                if not image:
                    logger.warning(f"[{combo}: {action}] Буфер обмена пуст")
                    return ""
                response = genai.GenerativeModel(model).generate_content(
                    contents=[prompt, image],
                    generation_config=GenerationConfig(temperature=0.7, max_output_tokens=2048)
                )
            else:
                full_prompt = prompt + text
                response = genai.GenerativeModel(model).generate_content(
                    full_prompt,
                    generation_config=GenerationConfig(temperature=0.7, max_output_tokens=2048)
                )
            
            result = response.text.strip() if response and response.text else ""
            logger.info(f"[{combo}: {action}] Processed: {result}")
            return result
        except Exception as e:
            logger.error(f"[{combo}: {action}] Gemini Error: {e}")
            return ""

    def _process_with_mistral(self, text, action, prompt, model):
        """Process with Mistral"""
        if not self.mistral_client:
            logger.error("Mistral client not initialized")
            return ""
        
        hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
        combo = hotkey["combination"] if hotkey else ""
        
        try:
            full_prompt = prompt + text
            response = self.mistral_client.chat.complete(
                model=model,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.7,
                max_tokens=2048
            )
            result = response.choices[0].message.content.strip() if response else ""
            logger.info(f"[{combo}: {action}] Processed: {result}")
            return result
        except Exception as e:
            logger.error(f"[{combo}: {action}] Mistral Error: {e}")
            return ""

    def _process_with_groq(self, text, action, prompt, model):
        """Process with Groq"""
        if not self.groq_client:
            logger.error("Groq client not initialized")
            return ""
        
        hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
        combo = hotkey["combination"] if hotkey else ""
        
        try:
            full_prompt = prompt + text
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.7,
                max_tokens=2048
            )
            result = response.choices[0].message.content.strip() if response else ""
            logger.info(f"[{combo}: {action}] Processed: {result}")
            return result
        except Exception as e:
            logger.error(f"[{combo}: {action}] Groq Error: {e}")
            return ""

    def handle_text_operation(self, action, prompt, provider, model):
        """Handle text operation with specified provider"""
        hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
        combo = hotkey["combination"] if hotkey else ""
        
        try:
            logger.info(f"[{combo}: {action}] Activated")
            
            # Copy text from clipboard
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('C'), 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            
            is_image = hotkey.get("type") == "image"
            if is_image:
                processed_text = self.process_text_with_provider("", action, prompt, is_image=True, provider=provider, model=model)
            else:
                text = pyperclip.paste()
                if not text.strip():
                    logger.warning(f"[{combo}: {action}] Буфер обмена пуст")
                    return
                processed_text = self.process_text_with_provider(text, action, prompt, provider=provider, model=model)
            
            if processed_text:
                pyperclip.copy(processed_text)
                time.sleep(0.3)
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(ord('V'), 0, 0, 0)
                time.sleep(0.2)
                win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        except Exception as e:
            logger.error(f"[{combo}: {action}] Ошибка: {e}")

    def check_queue(self):
        def queue_worker():
            while not self.stop_event.is_set():
                try:
                    event = self.queue.get(timeout=0.5)
                    for hotkey in self.config["hotkeys"]:
                        if hotkey["name"] == event:
                            threading.Thread(
                                target=self.handle_text_operation,
                                args=(
                                    hotkey["name"],
                                    hotkey["prompt"],
                                    hotkey.get("api_provider", "Gemini"),
                                    hotkey.get("model", "gemini-2.0-flash-exp")
                                ),
                                daemon=True
                            ).start()
                            break
                except Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error processing queue: {e}")
        
        threading.Thread(target=queue_worker, daemon=True).start()

    # В файле ClipGen.py замените метод create_log_handler следующим кодом:

    def create_log_handler(self):
        class LogHandler(logging.Handler):
            def __init__(self, log_signal, action_colors, config):
                super().__init__()
                self.log_signal = log_signal
                # Модифицируем словарь цветов, используя имя действия вместо комбинации клавиш
                self.action_colors = {k["name"]: k["log_color"] for k in action_colors}
                self.start_times = {}
                self.config = config
                self.processed_activations = set()  # Для отслеживания обработанных активаций
                
            def emit(self, record):
                try:
                    msg = self.format(record)
                    
                    # Пропускаем дублирующие сообщения о событиях из очереди
                    if "Received event from queue" in msg:
                        return
                        
                    # Обрабатываем активацию действий
                    if "Activated" in msg:
                        # Извлекаем название действия из сообщения
                        for combo, name in [(h["combination"], h["name"]) for h in self.config["hotkeys"]]:
                            if name in msg:
                                # Формируем уникальный идентификатор для активации
                                timestamp = time.strftime('%H:%M:%S')
                                activation_id = f"{combo}:{name}:{timestamp}"
                                
                                # Пропускаем, если такая активация уже была обработана
                                if activation_id in self.processed_activations:
                                    return
                                    
                                self.processed_activations.add(activation_id)
                                self.start_times[name] = time.time()
                                
                                # Находим цвет для действия по его имени
                                color = self.action_colors.get(name, "#FFFFFF")
                                
                                # Отправляем сообщение о действии
                                formatted_msg = f"{combo}: {name} - {timestamp}"
                                self.log_signal.emit(formatted_msg, color)
                                return
                    
                    # Форматируем сообщения о завершении
                    if "Processed:" in msg:
                        for name, start_time in list(self.start_times.items()):
                            if name in msg:
                                elapsed = time.time() - self.start_times.pop(name)
                                # Находим цвет для действия по его имени
                                color = self.action_colors.get(name, "#FFFFFF")
                                
                                # Сначала отправляем сообщение о времени выполнения
                                self.log_signal.emit(f"Выполнено за {elapsed:.2f} секунд", "#888888")
                                
                                # Затем отправляем результат
                                result = msg.split("Processed:")[1].strip()
                                self.log_signal.emit(result, color)
                                return
                                
                    # Обрабатываем ошибки
                    if record.levelno >= logging.ERROR:
                        self.log_signal.emit(f"Ошибка: {msg}", "#FF5555")
                        return
                    
                    # Обрабатываем предупреждения
                    if record.levelno == logging.WARNING:
                        self.log_signal.emit(msg, "#FFDD55")
                        return
                        
                    # Остальные информационные сообщения
                    self.log_signal.emit(msg, "#FFFFFF")
                    
                except Exception as e:
                    print(f"Ошибка в обработчике логов: {e}")
        
        return LogHandler(self.log_signal, self.config["hotkeys"], self.config)

    def hotkey_listener(self, queue):
        def on_press(key, queue):
            try:
                # Преобразуем ключ в строку для сравнения
                key_str = str(key).lower().replace("key.", "").replace("'", "")
                
                # Отслеживаем нажатия модификаторов
                if key_str in ("ctrl_l", "ctrl_r"):
                    self.key_states["ctrl"] = True
                    return
                if key_str in ("alt_l", "alt_r"):
                    self.key_states["alt"] = True
                    return
                if key_str in ("shift_l", "shift_r"):
                    self.key_states["shift"] = True
                    return
                
                # Логируем для отладки состояние клавиш
                logger.debug(f"Key pressed: {key_str}, Modifiers: Ctrl={self.key_states['ctrl']}, Alt={self.key_states['alt']}, Shift={self.key_states['shift']}")
                
                # Проверяем комбинации клавиш
                for hotkey in self.config["hotkeys"]:
                    combo_lower = hotkey["combination"].lower()
                    
                    # Преобразуем последний ключ в комбинации (после последнего '+')
                    if "+" in combo_lower:
                        combo_parts = combo_lower.split("+")
                        last_key = combo_parts[-1].strip()
                        
                        # Проверяем модификаторы
                        has_ctrl = "ctrl" in combo_lower
                        has_alt = "alt" in combo_lower
                        has_shift = "shift" in combo_lower
                        
                        # Для цифровых клавиш и клавиш F1-F12
                        if (last_key == key_str or 
                            (last_key.startswith("f") and key_str.startswith("f") and last_key == key_str) or
                            (last_key.isdigit() and key_str.isdigit() and last_key == key_str)):
                            
                            # Проверяем, что все требуемые модификаторы нажаты и нет лишних
                            if ((has_ctrl == self.key_states["ctrl"]) and 
                                (has_alt == self.key_states["alt"]) and 
                                (has_shift == self.key_states["shift"])):
                                
                                logger.info(f"[{hotkey['combination']}: {hotkey['name']}] Activated")
                                queue.put(hotkey["name"])
                                
                                # Сбрасываем состояния
                                self.key_states["ctrl"] = False
                                self.key_states["alt"] = False
                                self.key_states["shift"] = False
                                return
                    else:
                        # Обработка одиночных клавиш (без модификаторов)
                        if combo_lower == key_str:
                            logger.info(f"[{hotkey['combination']}: {hotkey['name']}] Activated")
                            queue.put(hotkey["name"])
                            return
                            
            except Exception as e:
                logger.error(f"Error in on_press: {e}")

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
                logger.error(f"Error in on_release: {e}")

        with pkb.Listener(on_press=lambda k: on_press(k, queue), on_release=lambda k: on_release(k, queue)) as listener:
            self.stop_event.wait()
            listener.stop()

    def real_closeEvent(self):
        self.save_settings()
        self.stop_event.set()
        if self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1.0)
        QApplication.instance().quit()

    def closeEvent(self, event):
        super().closeEvent(event)

def set_dark_titlebar(hwnd):
    try:
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
            byref(c_int(1)), ctypes.sizeof(c_int)
        )
    except Exception as e:
        print(f"Не удалось установить темную тему для заголовка: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClipGen()
    set_dark_titlebar(int(window.winId()))
    window.hide()
    window.tray_icon.show()
    sys.exit(app.exec_())
