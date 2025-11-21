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
from mistralai import Mistral
from groq import Groq
import win32api
import win32con
from pynput import keyboard as pkb
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPoint
from PyQt5.QtWidgets import QApplication, QMessageBox
import ctypes
from ctypes import windll, c_bool, c_int, byref, POINTER, Structure
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
    "gemini_api_key": "YOUR_API_KEY_HERE",
    "mistral_api_key": "YOUR_API_KEY_HERE",
    "groq_api_key": "YOUR_API_KEY_HERE",
    "available_models": {
        "Gemini": ["gemini-1.5-flash", "gemini-pro", "gemini-pro-vision"],
        "Mistral": ["mistral-large-latest", "mistral-small-latest"],
        "Groq": []
    },
    "hotkeys": [
        {"combination": "Ctrl+F1", "name": "Коррекция", "log_color": "#FFFFFF", "prompt": "Пожалуйста, исправь следующий текст...", "api_provider": "Gemini", "model": "gemini-1.5-flash", "type": "text"},
        {"combination": "Ctrl+F2", "name": "Переписать", "log_color": "#A3BFFA", "prompt": "Пожалуйста, исправь следующий текст, если нужно...", "api_provider": "Gemini", "model": "gemini-1.5-flash", "type": "text"},
        {"combination": "Ctrl+F3", "name": "Перевод", "log_color": "#FBB6CE", "prompt": "Пожалуйста, переведи следующий текст на русский язык...", "api_provider": "Gemini", "model": "gemini-1.5-flash", "type": "text"},
        {"combination": "Ctrl+F6", "name": "Объяснение", "log_color": "#FAF089", "prompt": "Пожалуйста, объясни следующий текст простыми словами...", "api_provider": "Gemini", "model": "gemini-1.5-flash", "type": "text"},
        {"combination": "Ctrl+F7", "name": "Ответ на вопрос", "log_color": "#FBD38D", "prompt": "Пожалуйста, ответь на следующий вопрос...", "api_provider": "Gemini", "model": "gemini-1.5-flash", "type": "text"},
        {"combination": "Ctrl+F8", "name": "Просьба", "log_color": "#B5EAD7", "prompt": "Выполни просьбу пользователя...", "api_provider": "Gemini", "model": "gemini-1.5-flash", "type": "text"},
        {"combination": "Ctrl+F9", "name": "Комментарий", "log_color": "#D6BCFA", "prompt": "Генерируй саркастичные комментарии...", "api_provider": "Gemini", "model": "gemini-1.5-flash", "type": "text"},
        {"combination": "Ctrl+F10", "name": "Анализ изображения", "log_color": "#A1CFF9", "prompt": "Анализируй изображение...", "api_provider": "Gemini", "model": "gemini-pro-vision", "type": "image"},
        {"combination": "Ctrl+F11", "name": "Текст с картинки", "log_color": "#DAF7A6", "prompt": "Extrahiere den gesamten Text aus diesem Bild. Gib ausschließlich den transkribierten Text zurück, ohne zusätzliche Kommentare oder Formatierungen.", "api_provider": "Gemini", "model": "gemini-pro-vision", "type": "image"}
    ]
}

class ClipGen(ClipGenView):
    def __init__(self):
        # Загрузка настроек перед инициализацией GUI
        self.load_settings()
        
        # Инициализируем представление
        super().__init__()
        
        # Инициализация Gemini
        genai.configure(api_key=self.config["gemini_api_key"])
        self.mistral_client = Mistral(api_key=self.config["mistral_api_key"])
        self.groq_client = Groq(api_key=self.config.get("groq_api_key"))
        self.queue = Queue()
        self.stop_event = threading.Event()
        
        # Перехват горячих клавиш
        self.key_states = {key["combination"].lower(): False for key in self.config["hotkeys"]}
        self.key_states["ctrl"] = False
        self.key_states["alt"] = False
        self.key_states["shift"] = False
        self.listener_thread = threading.Thread(target=self.hotkey_listener, args=(self.queue,), daemon=True)
        self.listener_thread.start()
        self.check_queue()
        
        # Настройка обработчика логов
        gui_handler = self.create_log_handler()
        gui_handler.setLevel(logging.INFO)
        gui_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(gui_handler)

        # Тестовое сообщение
        self.log_signal.emit("ClipGen запущен", "#FFFFFF")
        self.quit_signal.connect(self.real_closeEvent)
        self.save_gemini_api_key_button.clicked.connect(self.update_gemini_api_key)
        self.save_mistral_api_key_button.clicked.connect(self.update_mistral_api_key)
        self.save_groq_api_key_button.clicked.connect(self.update_groq_api_key)
        self.update_models_signal.connect(self.update_models_for_hotkey)

        # Füllen der Modell-Dropdowns beim Start
        for hotkey in self.config["hotkeys"]:
            self.update_model_combobox_for_hotkey(hotkey)
        
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

    def load_settings(self):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                self.config = json.load(f)
            if "gemini_api_key" not in self.config:
                self.config["gemini_api_key"] = self.config.get("api_key", "YOUR_API_KEY_HERE")
            if "mistral_api_key" not in self.config:
                self.config["mistral_api_key"] = "YOUR_API_KEY_HERE"
            if "groq_api_key" not in self.config:
                self.config["groq_api_key"] = "YOUR_API_KEY_HERE"
            if "api_key" in self.config:
                del self.config["api_key"]
            if "available_models" not in self.config:
                self.config["available_models"] = {
                    "Gemini": ["gemini-1.5-flash", "gemini-pro"],
                    "Mistral": ["mistral-large-latest", "mistral-small-latest"],
                    "Groq": []
                }
            elif "Groq" not in self.config["available_models"]:
                self.config["available_models"]["Groq"] = []

            for hotkey in self.config["hotkeys"]:
                if "api_provider" not in hotkey:
                    hotkey["api_provider"] = "Gemini"
                if "model" not in hotkey:
                    hotkey["model"] = "gemini-1.5-flash"

            # Migration, um den 'type' für Hotkeys hinzuzufügen
            default_hotkey_types = {h["combination"]: h["type"] for h in DEFAULT_CONFIG["hotkeys"]}
            for hotkey in self.config["hotkeys"]:
                if "type" not in hotkey:
                    # Weisen Sie den Typ basierend auf der Standardkombination zu oder standardmäßig auf 'text'
                    hotkey["type"] = default_hotkey_types.get(hotkey["combination"], "text")

            # Migration für neue Hotkeys
            existing_hotkey_names = {h["name"] for h in self.config["hotkeys"]}
            for default_hotkey in DEFAULT_CONFIG["hotkeys"]:
                if default_hotkey["name"] not in existing_hotkey_names:
                    self.config["hotkeys"].append(default_hotkey)

            # Migration für das Modell der Bilderkennungs-Hotkeys
            for hotkey in self.config["hotkeys"]:
                if hotkey["name"] in ["Анализ изображения", "Текст с картинки"]:
                    if hotkey["model"] == "gemini-1.5-flash":
                        hotkey["model"] = "gemini-pro-vision"

            self.save_settings()
        except FileNotFoundError:
            self.config = DEFAULT_CONFIG.copy()
            self.save_settings()

    def save_settings(self):
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    # Добавьте этот новый метод здесь
    def update_logger_colors(self):
        """Обновляет цвета в логгере после изменения настроек горячих клавиш"""
        for handler in logger.handlers:
            if hasattr(handler, 'action_colors'):
                handler.action_colors = {k["name"]: k["log_color"] for k in self.config["hotkeys"]}

    def update_gemini_api_key(self):
        new_api_key = self.gemini_api_key_input.text()
        self.config["gemini_api_key"] = new_api_key
        genai.configure(api_key=new_api_key)
        self.save_settings()
        self.log_signal.emit("Gemini API-Schlüssel gespeichert.", "#FFFFFF")
        QMessageBox.information(self, "Erfolg", "Der Gemini API-Schlüssel wurde erfolgreich gespeichert.")

    def update_mistral_api_key(self):
        new_api_key = self.mistral_api_key_input.text()
        self.config["mistral_api_key"] = new_api_key
        self.mistral_client = Mistral(api_key=new_api_key)
        self.save_settings()
        self.log_signal.emit("Mistral API-Schlüssel gespeichert.", "#FFFFFF")
        QMessageBox.information(self, "Erfolg", "Der Mistral API-Schlüssel wurde erfolgreich gespeichert.")

    def update_groq_api_key(self):
        new_api_key = self.groq_api_key_input.text()
        self.config["groq_api_key"] = new_api_key
        self.groq_client = Groq(api_key=new_api_key)
        self.save_settings()
        self.log_signal.emit("Groq API-Schlüssel gespeichert.", "#FFFFFF")
        QMessageBox.information(self, "Erfolg", "Der Groq API-Schlüssel wurde erfolgreich gespeichert.")

    def update_prompt(self, hotkey, text):
        for h in self.config["hotkeys"]:
            if h["combination"] == hotkey["combination"]:
                h["prompt"] = text
                break
        self.save_settings()

    def update_api_provider(self, hotkey, provider):
        for h in self.config["hotkeys"]:
            if h["combination"] == hotkey["combination"]:
                h["api_provider"] = provider
                self.update_model_combobox_for_hotkey(h)
                break
        self.save_settings()

    def update_model(self, hotkey, model):
        for h in self.config["hotkeys"]:
            if h["combination"] == hotkey["combination"]:
                h["model"] = model
                break
        self.save_settings()

    def update_model_combobox_for_hotkey(self, hotkey):
        provider = hotkey.get("api_provider", "Gemini")
        models = self.config.get("available_models", {}).get(provider, [])

        # Finde das QComboBox-Widget für das spezifische Hotkey
        if hotkey["combination"] in self.model_combos:
            combo_box = self.model_combos[hotkey["combination"]]

            # Blockiere Signale, um Endlosschleifen zu vermeiden
            combo_box.blockSignals(True)

            current_model = combo_box.currentText()
            combo_box.clear()
            combo_box.addItems(models)

            # Versuche, das zuvor ausgewählte Modell wiederherzustellen
            if current_model in models:
                combo_box.setCurrentText(current_model)
            elif models:
                # Wähle das erste Modell in der Liste als Standard
                combo_box.setCurrentIndex(0)

            # Entblockiere Signale
            combo_box.blockSignals(False)

    def update_models_for_hotkey(self, hotkey):
        provider = hotkey.get("api_provider", "Gemini")
        new_models = []
        try:
            if provider == "Gemini":
                # Korrekter Aufruf für Gemini API
                all_models = genai.list_models()
                new_models = sorted([m.name for m in all_models if 'generateContent' in m.supported_generation_methods])

            elif provider == "Mistral":
                res = self.mistral_client.models.list()
                new_models = sorted([model.id for model in res.data])

            elif provider == "Groq":
                res = self.groq_client.models.list()
                new_models = sorted([model.id for model in res.data])

            if new_models:
                self.config["available_models"][provider] = new_models
                self.save_settings()
                self.update_model_combobox_for_hotkey(hotkey)
                QMessageBox.information(self, "Erfolg", f"Modellliste für {provider} erfolgreich aktualisiert.")
            else:
                QMessageBox.warning(self, "Fehler", f"Keine Modelle für {provider} gefunden.")

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Modelle für {provider}: {e}")
            QMessageBox.critical(self, "API Fehler", f"Konnte Modelle für {provider} nicht abrufen. Bitte überprüfen Sie Ihren API-Schlüssel und Ihre Internetverbindung.")

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

    def process_text_with_gemini(self, text, model, prompt, action, is_image=False):
        hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
        combo = hotkey["combination"] if hotkey else ""
        try:
            if is_image:
                image = ImageGrab.grabclipboard()
                if not image:
                    logger.warning(f"[{combo}: {action}] Clipboard is empty")
                    return ""
                response = genai.GenerativeModel(model).generate_content(
                    contents=[prompt, image], generation_config=GenerationConfig(temperature=0.7, max_output_tokens=2048)
                )
            else:
                full_prompt = prompt + text
                response = genai.GenerativeModel(model).generate_content(
                    full_prompt, generation_config=GenerationConfig(temperature=0.7, max_output_tokens=2048)
                )
            
            result = response.text.strip() if response and response.text else ""
            logger.info(f"[{combo}: {action}] Processed: {result}")
            return result
        except Exception as e:
            logger.error(f"[{combo}: {action}] Error requesting Gemini: {e}")
            return ""

    def process_text_with_mistral(self, text, model, prompt, action):
        hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
        combo = hotkey["combination"] if hotkey else ""
        try:
            messages = [
                {"role": "user", "content": prompt + text}
            ]
            chat_response = self.mistral_client.chat.complete(
                model=model,
                messages=messages,
            )
            result = chat_response.choices[0].message.content.strip()
            logger.info(f"[{combo}: {action}] Processed: {result}")
            return result
        except Exception as e:
            logger.error(f"[{combo}: {action}] Error requesting Mistral: {e}")
            return ""

    def process_with_groq(self, text, model, prompt, action, is_image=False):
        hotkey = next((h for h in self.config["hotkeys"] if h["name"] == action), None)
        combo = hotkey["combination"] if hotkey else ""
        try:
            if is_image:
                image = ImageGrab.grabclipboard()
                if not image:
                    logger.warning(f"[{combo}: {action}] Clipboard is empty")
                    return ""

                # Konvertieren Sie das Bild in ein Format, das Groq akzeptiert (Base64)
                from io import BytesIO
                import base64
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ]
            else:
                 messages=[
                    {
                        "role": "user",
                        "content": prompt + text,
                    }
                ]

            chat_completion = self.groq_client.chat.completions.create(
                messages=messages,
                model=model,
            )
            result = chat_completion.choices[0].message.content.strip()
            logger.info(f"[{combo}: {action}] Processed: {result}")
            return result
        except Exception as e:
            logger.error(f"[{combo}: {action}] Error requesting Groq: {e}")
            return ""

    def handle_text_operation(self, hotkey):
        action = hotkey["name"]
        prompt = hotkey["prompt"]
        api_provider = hotkey["api_provider"]
        model = hotkey["model"]
        hotkey_type = hotkey.get("type", "text")
        combo = hotkey["combination"]
        
        try:
            logger.info(f"[{combo}: {action}] Activated")
            
            is_image_action = hotkey_type == "image"
            processed_text = ""

            if is_image_action:
                if api_provider == "Mistral":
                    logger.warning(f"[{combo}: {action}] Image analysis is not supported by Mistral.")
                    return
                # Для операций с изображениями не симулируем Ctrl+C, предполагаем, что изображение уже в буфере обмена.
                if api_provider == "Gemini":
                    processed_text = self.process_text_with_gemini("", model, prompt, action, is_image=True)
                elif api_provider == "Groq":
                    processed_text = self.process_with_groq("", model, prompt, action, is_image=True)
            else:
                # Для текстовых операций сначала симулируем Ctrl+C, чтобы скопировать выделенный текст.
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(ord('C'), 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)

                text = pyperclip.paste()
                if not text.strip():
                    time.sleep(0.5) # Даем время буферу обновиться
                    text = pyperclip.paste()
                    if not text.strip():
                        logger.warning(f"[{combo}: {action}] Clipboard is empty after two retries.")
                        return

                if api_provider == "Gemini":
                    processed_text = self.process_text_with_gemini(text, model, prompt, action)
                elif api_provider == "Mistral":
                    processed_text = self.process_text_with_mistral(text, model, prompt, action)
                elif api_provider == "Groq":
                    processed_text = self.process_with_groq(text, model, prompt, action)

            if processed_text:
                pyperclip.copy(processed_text)

                time.sleep(0.3)
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(ord('V'), 0, 0, 0)
                time.sleep(0.2)
                win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        except Exception as e:
            logger.error(f"[{combo}: {action}] Error: {e}")

    def check_queue(self):
        def queue_worker():
            while not self.stop_event.is_set():
                try:
                    event = self.queue.get(timeout=0.5)
                    logger.info(f"Received event from queue: {event}")
                    for hotkey in self.config["hotkeys"]:
                        if hotkey["name"] == event:
                            threading.Thread(target=self.handle_text_operation, args=(hotkey,), daemon=True).start()
                            break
                except Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error processing queue: {e}")

        threading.Thread(target=queue_worker, daemon=True).start()

    def real_closeEvent(self):
        self.save_settings()
        self.stop_event.set()
        if self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1.0)
        QApplication.instance().quit()

    def closeEvent(self, event):
        super().closeEvent(event)

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
    
    window.hide()
    window.tray_icon.show()
    sys.exit(app.exec_())
