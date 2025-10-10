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
from groq import Groq
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import ollama
import win32api
import win32con
from pynput import keyboard as pkb
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPoint
from PyQt5.QtWidgets import QApplication
import ctypes
from ctypes import windll, c_bool, c_int, byref, POINTER, Structure
import winreg
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from libs.ClipGen_view import ClipGenView

# Настройка логирования
logger = logging.getLogger('ClipGen')
logger.setLevel(logging.INFO)

# Консольный обработчик только для ошибок
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(console_handler)

# Начальная конфигурация
DEFAULT_CONFIG = {
    "general": {
        "provider": "gemini",
        "autostart": False,
        "show_hide_hotkey": "Ctrl+Shift+C",
        "font_size": 10
    },
    "providers": {
        "gemini": {
            "api_key": "YOUR_GEMINI_API_KEY_HERE",
            "model": "gemini-2.5-flash"
        },
        "groq": {
            "api_key": "YOUR_GROQ_API_KEY_HERE",
            "model": "groq/compound"
        },
        "mistral": {
            "api_key": "YOUR_MISTRAL_API_KEY_HERE",
            "model": "mistral-small-latest"
        },
        "ollama": {
            "host": "http://localhost:11434",
            "model": "llama3"
        }
    },
    "hotkeys": [
        {"combination": "Ctrl+F1", "name": "Коррекция", "log_color": "#FFFFFF", "prompt": "Пожалуйста, исправь следующий текст..."},
        {"combination": "Ctrl+F2", "name": "Переписать", "log_color": "#A3BFFA", "prompt": "Пожалуйста, исправь следующий текст, если нужно..."},
        {"combination": "Ctrl+F3", "name": "Перевод", "log_color": "#FBB6CE", "prompt": "Пожалуйста, переведи следующий текст на русский язык..."},
        {"combination": "Ctrl+F6", "name": "Объяснение", "log_color": "#FAF089", "prompt": "Пожалуйста, объясни следующий текст простыми словами..."},
        {"combination": "Ctrl+F7", "name": "Ответ на вопрос", "log_color": "#FBD38D", "prompt": "Пожалуйста, ответь на следующий вопрос..."},
        {"combination": "Ctrl+F8", "name": "Просьба", "log_color": "#B5EAD7", "prompt": "Выполни просьбу пользователя..."},
        {"combination": "Ctrl+F9", "name": "Комментарий", "log_color": "#D6BCFA", "prompt": "Генерируй саркастичные комментарии..."},
        {"combination": "Ctrl+F10", "name": "Анализ изображения", "log_color": "#A1CFF9", "prompt": "Анализируй изображение..."}
    ]
}

class ClipGen(ClipGenView):
    def __init__(self):
        # Загрузка настроек перед инициализацией GUI
        self.load_settings()
        
        # Инициализируем представление
        super().__init__()
        
        # Инициализация API клиентов
        self.initialize_clients()

        self.queue = Queue()
        self.stop_event = threading.Event()

        # Настройка System Tray
        self.setup_tray_icon()

        # Перехват горячих клавиш
        self.key_states = {key["combination"].lower(): False for key in self.config["hotkeys"]}
        self.key_states["ctrl"] = False
        self.key_states["alt"] = False
        self.key_states["shift"] = False
        self.listener_thread = threading.Thread(target=self.hotkey_listener, args=(self.queue,), daemon=True)
        self.listener_thread.start()
        self.check_queue()

        # Глобальный listener для показать/скрыть
        self.global_hotkey_thread = threading.Thread(target=self.global_hotkey_listener, daemon=True)
        self.global_hotkey_thread.start()
        
        # Настройка обработчика логов
        gui_handler = self.create_log_handler()
        gui_handler.setLevel(logging.INFO)
        gui_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(gui_handler)

        # Тестовое сообщение
        self.log_signal.emit("ClipGen запущен", "#FFFFFF")
        
        # Применяем размер шрифта при запуске
        self.update_font_size(self.config["general"].get("font_size", 10))

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("ClipGen.ico"))

        show_action = QAction("Показать", self)
        quit_action = QAction("Выход", self)
        show_action.triggered.connect(self.toggle_visibility)
        quit_action.triggered.connect(self.quit_application)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Одиночный клик
            self.toggle_visibility()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()

    def quit_application(self):
        self.stop_event.set()
        if self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1.0)
        QApplication.instance().quit()

    def global_hotkey_listener(self):
        # Этот listener будет проще, так как он отслеживает только одну комбинацию
        def on_press(key):
            try:
                # Проверяем, нажата ли наша комбинация для показать/скрыть
                with pkb.GlobalHotKeys({
                    self.config["general"].get("show_hide_hotkey", "<ctrl>+<shift>+c"): self.toggle_visibility
                }) as h:
                    h.join()
            except Exception as e:
                logger.error(f"Global hotkey error: {e}")

        # Запускаем listener в отдельном потоке
        # Korrekte Syntax für pynput
        hotkey_str = self.config["general"].get("show_hide_hotkey", "<ctrl>+<shift>+c")
        
        # Sicherstellen, dass der Hotkey im richtigen Format ist
        if not hotkey_str.startswith("<"):
            # Konvertiere von "Ctrl+Shift+C" zu "<ctrl>+<shift>+c"
            hotkey_parts = hotkey_str.split("+")
            hotkey_str = "+".join([f"<{part.lower()}>" for part in hotkey_parts])
        else:
            # Konvertiere "<ctrl>+<shift>+c" zu "<ctrl>+<shift>+c"
            hotkey_parts = hotkey_str.split("+")
            formatted_parts = []
            for part in hotkey_parts:
                if part.startswith("<") and part.endswith(">"):
                    formatted_parts.append(part)
                else:
                    formatted_parts.append(f"<{part.lower()}>")
            hotkey_str = "+".join(formatted_parts)
            
        # Spezielle Behandlung für den letzten Teil (Buchstabe)
        hotkey_parts = hotkey_str.split("+")
        if len(hotkey_parts) > 0:
            last_part = hotkey_parts[-1]
            if len(last_part) == 3 and last_part.startswith("<") and last_part.endswith(">") and last_part[1].isalpha():
                # Ersetze "<c>" mit "c"
                hotkey_parts[-1] = last_part[1]
                hotkey_str = "+".join(hotkey_parts)
        
        listener = pkb.GlobalHotKeys({
            hotkey_str: self.toggle_visibility
        })
        listener.start()

    # В файле ClipGen.py замените метод create_log_handler следующим кодом:

    def create_log_handler(self):
        class LogHandler(logging.Handler):
            def __init__(self, log_signal, action_colors, config):
                super().__init__()
                self.log_signal = log_signal
                self.action_colors = {k["combination"]: k["log_color"] for k in action_colors}
                self.start_times = {}
                self.config = config
                self.processed_activations = set()  # Для отслеживания обработанных активаций
                
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

    def initialize_clients(self):
        """Инициализирует API клиенты на основе конфигурации."""
        provider_config = self.config.get("providers", {})

        # Gemini
        gemini_config = provider_config.get("gemini", {})
        if gemini_config.get("api_key") and gemini_config["api_key"] != "YOUR_GEMINI_API_KEY_HERE":
            try:
                genai.configure(api_key=gemini_config["api_key"])
            except Exception as e:
                logger.error(f"Failed to configure Gemini: {e}")

        # Groq
        groq_config = provider_config.get("groq", {})
        try:
            self.groq_client = Groq(api_key=groq_config.get("api_key")) if groq_config.get("api_key") and groq_config.get("api_key") != "YOUR_GROQ_API_KEY_HERE" else None
        except Exception as e:
            logger.error(f"Failed to initialize Groq: {e}")
            self.groq_client = None

        # Mistral
        mistral_config = provider_config.get("mistral", {})
        try:
            self.mistral_client = MistralClient(api_key=mistral_config.get("api_key")) if mistral_config.get("api_key") and mistral_config.get("api_key") != "YOUR_MISTRAL_API_KEY_HERE" else None
        except Exception as e:
            logger.error(f"Failed to initialize Mistral: {e}")
            self.mistral_client = None

        # Ollama
        ollama_config = provider_config.get("ollama", {})
        try:
            self.ollama_client = ollama.Client(host=ollama_config.get("host", "http://localhost:11434"))
            self.ollama_client.list() # Test connection
        except Exception:
            logger.warning(f"Could not connect to Ollama at {ollama_config.get('host')}. Ollama will be unavailable.")
            self.ollama_client = None

    def load_settings(self):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                loaded_config = json.load(f)
        except FileNotFoundError:
            self.config = DEFAULT_CONFIG.copy()
            self.save_settings()
            return

        # Migration from old format
        if "api_key" in loaded_config:
            logger.info("Old config format detected. Migrating to new format.")
            new_config = DEFAULT_CONFIG.copy()
            new_config["general"]["autostart"] = loaded_config.get("autostart", False)
            new_config["general"]["show_hide_hotkey"] = loaded_config.get("show_hide_hotkey", "Ctrl+Shift+C")
            new_config["general"]["font_size"] = loaded_config.get("font_size", 10)
            new_config["providers"]["gemini"]["api_key"] = loaded_config.get("api_key", "YOUR_GEMINI_API_KEY_HERE")
            new_config["hotkeys"] = loaded_config.get("hotkeys", DEFAULT_CONFIG["hotkeys"])
            self.config = new_config
            self.save_settings()
            logger.info("Configuration migrated successfully.")
        else:
            self.config = loaded_config

        # Ensure all keys are present (deep merge)
        def deep_update(source, overrides):
            for key, value in overrides.items():
                if isinstance(value, dict):
                    source[key] = deep_update(source.get(key, {}), value)
                elif key not in source:
                    source[key] = value
            return source

        self.config = deep_update(self.config, DEFAULT_CONFIG.copy())
        self.set_autostart(self.config["general"].get("autostart", False))


    def save_settings(self):
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    # Добавьте этот новый метод здесь
    def update_logger_colors(self):
        """Обновляет цвета в логгере после изменения настроек горячих клавиш"""
        for handler in logger.handlers:
            if hasattr(handler, 'action_colors'):
                handler.action_colors = {k["name"]: k["log_color"] for k in self.config["hotkeys"]}

    def update_provider_config(self, provider, key, value):
        """Обновляет конфигурацию для конкретного провайдера."""
        if provider in self.config["providers"]:
            self.config["providers"][provider][key] = value
            self.save_settings()
            self.initialize_clients() # Re-initialize clients with new settings
        else:
            logger.error(f"Attempted to update config for unknown provider: {provider}")

    def update_prompt(self, hotkey, text):
        for h in self.config["hotkeys"]:
            if h["combination"] == hotkey["combination"]:
                h["prompt"] = text
                break
        self.save_settings()

    def update_name(self, hotkey, text):
        for h in self.config["hotkeys"]:
            if h["combination"] == hotkey["combination"]:
                h["name"] = text
                self.update_buttons()
                # Обновляем цвета в логгере
                self.update_logger_colors()
                break
        self.save_settings()

    # В файле ClipGen.py, изменим метод update_color:

    def update_color(self, hotkey, color):
        for h in self.config["hotkeys"]:
            if h["combination"] == hotkey["combination"]:
                h["log_color"] = color
                self.update_buttons()
                
                # Обновляем цвета в логгере
                self.update_logger_colors()
                
                break
        self.save_settings()
        
    def update_hotkey(self, old_combo, new_combo):
        for h in self.config["hotkeys"]:
            if h["combination"] == old_combo:
                h["combination"] = new_combo
                # Обновляем key_states для отслеживания новой комбинации
                self.key_states = {key["combination"].lower(): False for key in self.config["hotkeys"]}
                self.key_states["ctrl"] = False
                self.key_states["alt"] = False
                self.update_buttons()
                break
        self.save_settings()

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

    def process_text(self, text, action, prompt, is_image=False):
        provider = self.config["general"].get("provider", "gemini")
        logger.info(f"Using provider: {provider}")

        if provider == "gemini":
            return self._process_gemini(text, action, prompt, is_image)
        elif provider == "groq":
            return self._process_groq(text, action, prompt, is_image)
        elif provider == "mistral":
            return self._process_mistral(text, action, prompt, is_image)
        elif provider == "ollama":
            return self._process_ollama(text, action, prompt, is_image)
        else:
            logger.error(f"Unknown provider: {provider}")
            return ""

    def _process_gemini(self, text, action, prompt, is_image):
        try:
            hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
            combo = hotkey["combination"] if hotkey else ""
            provider_config = self.config["providers"]["gemini"]
            model_name = provider_config.get("model", "gemini-1.5-flash-latest")
            model = genai.GenerativeModel(model_name)

            if is_image:
                image = ImageGrab.grabclipboard()
                if not image:
                    logger.warning(f"[{combo}: {action}] Clipboard is empty")
                    return ""
                contents = [prompt, image]
            else:
                contents = [prompt + text]
            
            response = model.generate_content(contents, generation_config=GenerationConfig(temperature=0.7, max_output_tokens=2048))
            result = response.text.strip() if response and response.text else ""
            logger.info(f"[{combo}: {action}] Processed: {result}")
            return result
        except Exception as e:
            logger.error(f"Error with Gemini API: {e}")
            return ""

    def _process_groq(self, text, action, prompt, is_image):
        if is_image:
            logger.warning("Groq does not support image analysis. Please switch to another provider.")
            return ""
        if not self.groq_client:
            logger.error("Groq client not initialized. Check your API key.")
            return ""
        try:
            hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
            combo = hotkey["combination"] if hotkey else ""
            provider_config = self.config["providers"]["groq"]
            model_name = provider_config.get("model", "llama3-8b-8192")

            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                model=model_name,
            )
            result = chat_completion.choices[0].message.content
            logger.info(f"[{combo}: {action}] Processed: {result}")
            return result
        except Exception as e:
            logger.error(f"Error with Groq API: {e}")
            return ""

    def _process_mistral(self, text, action, prompt, is_image):
        if is_image:
            logger.warning("Mistral does not support image analysis. Please switch to another provider.")
            return ""
        if not self.mistral_client:
            logger.error("Mistral client not initialized. Check your API key.")
            return ""
        try:
            hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
            combo = hotkey["combination"] if hotkey else ""
            provider_config = self.config["providers"]["mistral"]
            model_name = provider_config.get("model", "mistral-small-latest")

            messages = [
                ChatMessage(role="system", content=prompt),
                ChatMessage(role="user", content=text)
            ]
            chat_response = self.mistral_client.chat(model=model_name, messages=messages)
            result = chat_response.choices[0].message.content
            logger.info(f"[{combo}: {action}] Processed: {result}")
            return result
        except Exception as e:
            logger.error(f"Error with Mistral API: {e}")
            return ""

    def _process_ollama(self, text, action, prompt, is_image):
        if not self.ollama_client:
            logger.error("Ollama client not available. Check if Ollama is running.")
            return ""
        try:
            hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
            combo = hotkey["combination"] if hotkey else ""
            provider_config = self.config["providers"]["ollama"]
            model_name = provider_config.get("model", "llama3")

            images = []
            if is_image:
                from io import BytesIO
                image = ImageGrab.grabclipboard()
                if not image:
                    logger.warning(f"[{combo}: {action}] Clipboard is empty")
                    return ""
                # Convert PIL image to bytes
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                images = [buffered.getvalue()]

            response = self.ollama_client.generate(
                model=model_name,
                prompt=f"{prompt}\n\n{text}",
                images=images,
                stream=False
            )
            result = response['response']
            logger.info(f"[{combo}: {action}] Processed: {result}")
            return result
        except Exception as e:
            logger.error(f"Error with Ollama: {e}")
            return ""

    def handle_text_operation(self, action, prompt):
        # Находим hotkey для данного действия
        hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
        combo = hotkey["combination"] if hotkey else ""
        
        try:
            # Логируем активацию действия
            logger.info(f"[{combo}: {action}] Activated")
            
            # Копируем текст из буфера
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('C'), 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)

            is_image = action == "Анализ изображения"
            if is_image:
                processed_text = self.process_text("", action, prompt, is_image=True)
            else:
                text = pyperclip.paste()
                if not text.strip():
                    # Пробуем снова скопировать
                    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                    win32api.keybd_event(ord('C'), 0, 0, 0)
                    time.sleep(0.5)
                    win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
                    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(0.5)
                    text = pyperclip.paste()
                    if not text.strip():
                        logger.warning(f"[{combo}: {action}] Буфер обмена пуст после двух попыток копирования")
                        return
                processed_text = self.process_text(text, action, prompt)

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
                    logger.info(f"Received event from queue: {event}")
                    for hotkey in self.config["hotkeys"]:
                        if hotkey["name"] == event:
                            threading.Thread(target=self.handle_text_operation, args=(hotkey["name"], hotkey["prompt"]), daemon=True).start()
                            break
                except Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error processing queue: {e}")

        threading.Thread(target=queue_worker, daemon=True).start()

    def set_autostart(self, enable):
        """Включает или отключает автозапуск приложения через реестр Windows."""
        app_name = "ClipGen"
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        try:
            registry_key = winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE)
            if enable:
                # Получаем путь к исполняемому файлу
                app_path = os.path.realpath(sys.argv[0])
                # Если это скрипт, нужно найти python.exe
                if app_path.endswith(".py"):
                    python_exe = sys.executable
                    app_path = f'"{python_exe}" "{app_path}"'
                winreg.SetValueEx(registry_key, app_name, 0, winreg.REG_SZ, app_path)
            else:
                winreg.DeleteValue(registry_key, app_name)
            winreg.CloseKey(registry_key)
        except FileNotFoundError:
            # Если значение не найдено при удалении, это не ошибка
            if not enable:
                pass
            else:
                logger.error("Не удалось найти ключ реестра для автозапуска.")
        except Exception as e:
            logger.error(f"Ошибка при настройке автозапуска: {e}")

    def update_autostart(self, state):
        self.config["general"]["autostart"] = bool(state)
        self.set_autostart(self.config["general"]["autostart"])
        self.save_settings()

    def update_font_size(self, size):
        self.config["general"]["font_size"] = size
        self.log_area.setStyleSheet(f"""
            background-color: #252525;
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 15px;
            font-size: {size}pt;
            font-family: 'Consolas', 'Courier New', monospace;
            selection-background-color: #A3BFFA;
            selection-color: #1e1e1e;
        """)
        self.save_settings()

    def update_show_hide_hotkey(self, hotkey):
        self.config["general"]["show_hide_hotkey"] = hotkey
        # Перезапускаем глобальный listener
        # (Это может быть сложно, проще попросить перезапустить приложение)
        logger.warning("Для применения нового глобального хоткея перезапустите приложение.")
        self.save_settings()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "ClipGen",
                "Приложение свернуто в трей.",
                QIcon("ClipGen.ico"),
                2000
            )

# Добавить новую функцию перед функцией main:
def set_dark_titlebar(hwnd):
    """Установка темной темы для стандартного заголовка Windows"""
    try:
        # Константы для Windows API
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        
        # Включение темной темы для заголовка окна
        windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 
            byref(c_int(1)), ctypes.sizeof(c_int)
        )
    except Exception as e:
        print(f"Не удалось установить темную тему для заголовка: {e}")

# Изменить блок main:
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClipGen()
    
    # Применяем темную тему для заголовка Windows
    set_dark_titlebar(int(window.winId()))
    
    window.show()
    sys.exit(app.exec_())