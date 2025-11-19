import os
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QTextBrowser, QTabWidget, QLineEdit, QTextEdit, QLabel, QScrollArea,
                          QFrame, QDialog, QColorDialog, QComboBox, QKeySequenceEdit, QMessageBox,
                          QSizeGrip, QSystemTrayIcon, QMenu)
from PyQt5.QtGui import QTextCursor, QColor, QIcon
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPoint, QSize

import pyperclip

class ClipGenView(QMainWindow):
    log_signal = pyqtSignal(str, str)  # Сигнал для логирования: сообщение, цвет
    quit_signal = pyqtSignal()
    update_models_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        # Установка иконки
        icon_path = os.path.abspath("ClipGen.ico")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            # Устанавливаем иконку для всего приложения
            from PyQt5.QtWidgets import QApplication
            QApplication.instance().setWindowIcon(app_icon)
        else:
            print(f"Иконка не найдена по пути: {icon_path}")
        self.setWindowTitle("ClipGen")
        self.setGeometry(100, 100, 554, 632)
        self.setMinimumSize(300, 200)

        # Установка иконки приложения
        icon_path = "ClipGen.ico"
        if getattr(sys, 'frozen', False):
            # Запущено как скомпилированное приложение
            icon_path = os.path.join(sys._MEIPASS, "ClipGen.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Добавляем ручки для изменения размера окна
        self.add_resize_grips()
        
        # Применяем стили
        self.apply_styles()
        
        # Изменяем флаги окна, чтобы разрешить растягивание
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Переменные для перетаскивания и изменения размера окна
        self.old_pos = None
        self.resizing = False
        self.resize_edge = None

        # Инициализация иконки в трее
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())
        self.tray_icon.setToolTip("ClipGen")

        # Erstellen des Kontextmenüs
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Anzeigen")
        show_action.triggered.connect(self.showNormal)
        quit_action = tray_menu.addAction("Beenden")
        quit_action.triggered.connect(self.quit_app)
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Haupt-Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(0)

        # Создание элементов интерфейса
        #self.setup_title_bar()
        self.setup_buttons()
        self.setup_tabs()
        
        # Логи с цветами через сигналы
        self.log_signal.connect(self.append_log)
        
        # Обновление кнопок при изменении размера
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.update_buttons)
        self.resizeEvent = self.on_resize
        
        # Применяем стили
        self.apply_styles()

    def add_resize_grips(self):
        """Добавляет ручки для изменения размера окна в четырех углах"""
        # Создаем ручки для изменения размера
        self.grip_bottom_right = QSizeGrip(self)
        self.grip_bottom_left = QSizeGrip(self)
        self.grip_top_right = QSizeGrip(self)
        self.grip_top_left = QSizeGrip(self)
        
        # Устанавливаем позиции
        self.grip_bottom_right.setGeometry(self.width() - 20, self.height() - 20, 20, 20)
        self.grip_bottom_left.setGeometry(0, self.height() - 20, 20, 20)
        self.grip_top_right.setGeometry(self.width() - 20, 0, 20, 20)
        self.grip_top_left.setGeometry(0, 0, 20, 20)
        
        # Показываем ручки
        self.grip_bottom_right.show()
        self.grip_bottom_left.show()
        self.grip_top_right.show()
        self.grip_top_left.show()
        
        # Добавляем стиль для ручек (чтобы они были прозрачными, но функциональными)
        self.grip_bottom_right.setStyleSheet("background: transparent;")
        self.grip_bottom_left.setStyleSheet("background: transparent;")
        self.grip_top_right.setStyleSheet("background: transparent;")
        self.grip_top_left.setStyleSheet("background: transparent;")

    # Переопределяем метод resizeEvent для обновления положения ручек
    def resizeEvent(self, event):
        # Обновляем положение ручек для изменения размера
        self.grip_bottom_right.setGeometry(self.width() - 20, self.height() - 20, 20, 20)
        self.grip_bottom_left.setGeometry(0, self.height() - 20, 20, 20)
        self.grip_top_right.setGeometry(self.width() - 20, 0, 20, 20)
        self.grip_top_left.setGeometry(0, 0, 20, 20)
        
        # Вызываем обработчик изменения размера для кнопок
        if hasattr(self, 'resize_timer'):
            self.resize_timer.start(200)
        QMainWindow.resizeEvent(self, event)

    def mousePressEvent(self, event):
        # Проверяем, находится ли курсор на краю окна
        edge = self.getResizeEdge(event.pos())
        if edge and event.button() == Qt.LeftButton:
            self.resizing = True
            self.resize_edge = edge
            self.setCursor(self.getResizeCursor(edge))
            self.old_pos = event.globalPos()
            return
        
        # Если клик в заголовке, готовимся к перетаскиванию
        if event.button() == Qt.LeftButton and event.pos().y() < 30 and not edge:
            self.old_pos = event.globalPos()
        
        super().mousePressEvent(event)

    def setup_title_bar(self):
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(30)
        self.title_bar.setStyleSheet("background-color: #1e1e1e; border-top-left-radius: 10px; border-top-right-radius: 10px;")
        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(10, 0, 10, 0)

        self.title_label = QLabel("ClipGen")
        self.title_label.setStyleSheet("color: #FFFFFF;")
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()

        # Кнопки в стиле Windows (справа налево): закрыть, развернуть, свернуть
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        # Кнопка закрытия (красная)
        self.close_button = QPushButton()
        self.close_button.setFixedSize(15, 15)
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #FF5F57;
                border: none;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #FF5F57;
                border: 1px solid #E14942;
            }
        """)
        
        # Кнопка разворачивания (зеленая)
        self.maximize_button = QPushButton()
        self.maximize_button.setFixedSize(15, 15)
        self.maximize_button.clicked.connect(self.toggle_maximize)
        self.maximize_button.setStyleSheet("""
            QPushButton {
                background-color: #28C940;
                border: none;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #28C940;
                border: 1px solid #1AAB29;
            }
        """)
        
        # Кнопка сворачивания (желтая)
        self.minimize_button = QPushButton()
        self.minimize_button.setFixedSize(15, 15)
        self.minimize_button.clicked.connect(self.showMinimized)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #FFBD2E;
                border: none;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #FFBD2E;
                border: 1px solid #DFA123;
            }
        """)
        
        # Добавляем кнопки в порядке Windows (слева направо)
        buttons_layout.addWidget(self.minimize_button)
        buttons_layout.addWidget(self.maximize_button)
        buttons_layout.addWidget(self.close_button)
        
        self.title_layout.addLayout(buttons_layout)
        self.layout.addWidget(self.title_bar)

    def setup_buttons(self):
        self.button_widget = QWidget()
        self.button_layout = QVBoxLayout(self.button_widget)
        self.button_layout.setAlignment(Qt.AlignTop)
        self.button_layout.setSpacing(5)
        self.layout.addWidget(self.button_widget, stretch=0)

        self.buttons = {}
        self.update_buttons()

    def setup_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                background-color: #1e1e1e; 
                border: none; 
                border-radius: 10px; 
            }
            QTabBar::tab { 
                background-color: #333333; 
                color: #FFFFFF; 
                padding: 8px 12px; 
                margin-right: 2px;
                border-top-left-radius: 5px; 
                border-top-right-radius: 5px;
                min-width: 100px;
            }
            QTabBar::tab:selected { 
                background-color: #2A2A2A;  /* Цвет активной вкладки */
                border-bottom: 2px solid #FFFFFF;
            }
            QTabBar::tab:hover:!selected { 
                background-color: #3c3c3c; 
            }
        """)
        self.layout.addWidget(self.tabs, stretch=1)

        self.setup_log_tab()
        self.setup_settings_tab()

    def setup_log_tab(self):
        self.log_tab = QWidget()
        self.log_layout = QVBoxLayout(self.log_tab)
        self.log_layout.setContentsMargins(15, 15, 15, 15)

        # Область логов
        self.log_area = QTextBrowser()
        self.log_area.setStyleSheet("""
            background-color: #252525; 
            color: #FFFFFF; 
            border: none; 
            border-radius: 10px;
            padding: 15px;
            line-height: 1.5;
            font-family: 'Consolas', 'Courier New', monospace;
            selection-background-color: #A3BFFA;
            selection-color: #1e1e1e;
        """)
        self.log_area.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard | Qt.LinksAccessibleByMouse)
        self.log_area.setCursorWidth(2)

        # Кнопки действий с логами
        log_actions = QHBoxLayout()
        clear_logs = QPushButton("Очистить логи")
        clear_logs.clicked.connect(lambda: self.log_area.clear())
        clear_logs.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border-radius: 8px;
                padding: 5px 10px;
                font-size: 12px;
                max-width: 150px;
            }
            QPushButton:hover {
                background-color: #444444;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        log_actions.addWidget(clear_logs)

        copy_logs = QPushButton("Копировать логи")
        copy_logs.clicked.connect(lambda: pyperclip.copy(self.log_area.toPlainText()))
        copy_logs.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border-radius: 8px;
                padding: 5px 10px;
                font-size: 12px;
                max-width: 150px;
            }
            QPushButton:hover {
                background-color: #444444;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        log_actions.addWidget(copy_logs)
        log_actions.addStretch()

        self.log_layout.addWidget(self.log_area)
        self.log_layout.addLayout(log_actions)
        self.tabs.addTab(self.log_tab, "Логи")

    def setup_settings_tab(self):
        self.settings_tab = QWidget()
        self.settings_tab.setStyleSheet("background-color: #1e1e1e;")
        self.settings_layout = QVBoxLayout(self.settings_tab)
        self.settings_layout.setSpacing(15)
        self.settings_layout.setContentsMargins(20, 20, 20, 20)

        # Групп API ключа
        api_key_container = QFrame()
        api_key_container.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        api_key_layout = QVBoxLayout(api_key_container)
        api_key_layout.setContentsMargins(15, 15, 15, 15)

        gemini_api_key_label = QLabel("API ключ Gemini:")
        gemini_api_key_label.setStyleSheet("margin-top: 5px;")
        api_key_layout.addWidget(gemini_api_key_label)

        gemini_api_key_input_layout = QHBoxLayout()
        self.gemini_api_key_input = QLineEdit(self.config["gemini_api_key"])
        self.gemini_api_key_input.setStyleSheet("""
            border-radius: 8px; 
            border: 1px solid #444444;
            padding: 8px;
            background-color: #2a2a2a;
        """)
        gemini_api_key_input_layout.addWidget(self.gemini_api_key_input)

        self.save_gemini_api_key_button = QPushButton("Speichern")
        self.save_gemini_api_key_button.setStyleSheet("""
            QPushButton {
                background-color: #3D8948;
                color: white;
                border-radius: 8px;
                padding: 5px 10px;
                max-width: 100px;
            }
            QPushButton:hover {
                background-color: #2A6C34;
            }
        """)
        gemini_api_key_input_layout.addWidget(self.save_gemini_api_key_button)
        api_key_layout.addLayout(gemini_api_key_input_layout)

        mistral_api_key_label = QLabel("API ключ Mistral:")
        mistral_api_key_label.setStyleSheet("margin-top: 15px;")
        api_key_layout.addWidget(mistral_api_key_label)

        mistral_api_key_input_layout = QHBoxLayout()
        self.mistral_api_key_input = QLineEdit(self.config["mistral_api_key"])
        self.mistral_api_key_input.setStyleSheet("""
            border-radius: 8px;
            border: 1px solid #444444;
            padding: 8px;
            background-color: #2a2a2a;
        """)
        mistral_api_key_input_layout.addWidget(self.mistral_api_key_input)

        self.save_mistral_api_key_button = QPushButton("Speichern")
        self.save_mistral_api_key_button.setStyleSheet("""
            QPushButton {
                background-color: #3D8948;
                color: white;
                border-radius: 8px;
                padding: 5px 10px;
                max-width: 100px;
            }
            QPushButton:hover {
                background-color: #2A6C34;
            }
        """)
        mistral_api_key_input_layout.addWidget(self.save_mistral_api_key_button)
        api_key_layout.addLayout(mistral_api_key_input_layout)

        self.settings_layout.addWidget(api_key_container)

        # Заголовок для горячих клавиш
        hotkeys_title = QLabel("Настройка горячих клавиш")
        hotkeys_title.setStyleSheet("font-size: 16px;")
        self.settings_layout.addWidget(hotkeys_title)

        # Создание карточек для каждой горячей клавиши
        self.prompt_inputs = {}
        self.name_inputs = {}
        self.color_pickers = {}
        self.hotkey_combos = {}
        self.model_combos = {}
        for i, hotkey in enumerate(self.config["hotkeys"]):
            hotkey_card = QFrame()
            hotkey_card.setStyleSheet(f"""
                QFrame {{
                    background-color: #252525;
                    border-radius: 15px;
                    padding: 10px;
                }}
            """)
            hotkey_layout = QVBoxLayout(hotkey_card)
            
            # Выбор комбинации клавиш
            hotkey_header = QHBoxLayout()
            
            # Создаем поле для записи комбинации клавиш
            hotkey_edit = QKeySequenceEdit()
            hotkey_edit.setKeySequence(hotkey["combination"])  # Устанавливаем текущую комбинацию
            hotkey_edit.setStyleSheet("""
                QKeySequenceEdit {
                    background-color: #333333;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    font-family: 'Consolas', 'Courier New', monospace;
                }
            """)
            # Добавляем обработчик изменения комбинации
            hotkey_edit.keySequenceChanged.connect(
                lambda seq, h=hotkey: self.update_hotkey_from_sequence(h, seq.toString())
            )
            # Добавляем поле в макет
            hotkey_header.addWidget(hotkey_edit)
            
            # Добавляем кнопку удаления справа
            delete_button = QPushButton("✕")
            delete_button.setFixedSize(25, 25)
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF5F57;
                    color: white;
                    border-radius: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #FF3B30;
                }
            """)
            delete_button.clicked.connect(lambda *, h=hotkey: self.delete_hotkey(h))
            hotkey_header.addWidget(delete_button)
            
            hotkey_layout.addLayout(hotkey_header)
            
            # Поле для имени действия
            name_label = QLabel("Название действия:")
            name_label.setStyleSheet("margin-top: 10px;")
            hotkey_layout.addWidget(name_label)
            
            name_input = QLineEdit(hotkey["name"])
            name_input.setStyleSheet("""
                border-radius: 8px; 
                border: 1px solid #444444;
                padding: 8px;
                background-color: #2a2a2a;
            """)
            name_input.textChanged.connect(lambda text, h=hotkey: self.update_name(h, text))
            hotkey_layout.addWidget(name_input)
            self.name_inputs[hotkey["combination"]] = name_input

            # API Provider and Model selection
            api_model_layout = QHBoxLayout()

            api_provider_combo = QComboBox()
            api_provider_combo.addItems(["Gemini", "Mistral"])
            api_provider_combo.setCurrentText(hotkey.get("api_provider", "Gemini"))
            if hotkey["name"] == "Текст с картинки":
                api_provider_combo.setEnabled(False)
            api_provider_combo.setStyleSheet("""
                QComboBox {
                    background-color: white;
                    color: red;
                    border: 1px solid #444444;
                    border-radius: 8px;
                    padding: 8px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: red;
                    selection-background-color: #f0f0f0;
                    selection-color: red;
                }
            """)
            api_provider_combo.currentTextChanged.connect(lambda text, h=hotkey: self.update_api_provider(h, text))
            api_model_layout.addWidget(api_provider_combo)

            model_combo = QComboBox()
            model_combo.setStyleSheet("""
                QComboBox {
                    background-color: white;
                    color: red;
                    border: 1px solid #444444;
                    border-radius: 8px;
                    padding: 8px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: red;
                    selection-background-color: #f0f0f0;
                    selection-color: red;
                }
            """)
            model_combo.addItem(hotkey.get("model", ""))
            model_combo.setCurrentText(hotkey.get("model", ""))
            model_combo.currentTextChanged.connect(lambda text, h=hotkey: self.update_model(h, text))
            api_model_layout.addWidget(model_combo)
            self.model_combos[hotkey["combination"]] = model_combo

            update_models_button = QPushButton("🔄")
            update_models_button.setFixedSize(35, 35)
            update_models_button.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    padding: 0px;
                    border-radius: 17px;
                }
            """)
            update_models_button.clicked.connect(lambda _, h=hotkey: self.update_models_for_hotkey(h))
            api_model_layout.addWidget(update_models_button)

            hotkey_layout.addLayout(api_model_layout)
            
            # Поле для промпта
            prompt_label = QLabel("Промпт:")
            prompt_label.setStyleSheet("margin-top: 10px;")
            hotkey_layout.addWidget(prompt_label)
            
            prompt_input = QTextEdit(hotkey["prompt"])
            prompt_input.setMinimumHeight(100)
            prompt_input.setStyleSheet("""
                border-radius: 8px; 
                border: 1px solid #444444;
                padding: 8px;
                background-color: #2a2a2a;
            """)
            prompt_input.textChanged.connect(lambda h=hotkey, pi=prompt_input: self.update_prompt(h, pi.toPlainText()))
            hotkey_layout.addWidget(prompt_input)
            self.prompt_inputs[hotkey["combination"]] = prompt_input
            
            # Выбор цвета
            color_layout = QHBoxLayout()
            
            color_label = QLabel("Цвет в логах:")
            color_label.setStyleSheet("margin-top: 10px;")
            color_layout.addWidget(color_label)
            
            color_input = QLineEdit(hotkey["log_color"].replace("#", ""))
            color_input.setFixedWidth(80)
            color_input.setStyleSheet("""
                border-radius: 8px; 
                border: 1px solid #444444;
                padding: 5px;
                background-color: #2a2a2a;
            """)
            color_input.textChanged.connect(lambda text, h=hotkey: self.update_color(h, f"#{text}"))
            
            color_preview = QPushButton()
            color_preview.setFixedSize(25, 25)
            color_preview.setStyleSheet(f"background-color: {hotkey['log_color']}; border-radius: 5px; border: none;")
            color_preview.clicked.connect(lambda checked, h=hotkey, inp=color_input: self.open_color_picker(h, inp))
            
            color_layout.addWidget(color_input)
            color_layout.addWidget(color_preview)
            color_layout.addStretch()
            
            self.color_pickers[hotkey["combination"]] = (color_input, color_preview)
            
            hotkey_layout.addLayout(color_layout)
            
            self.settings_layout.addWidget(hotkey_card)

        # Кнопки для добавления/удаления горячих клавиш
        hotkey_buttons_layout = QHBoxLayout()
        add_hotkey_button = QPushButton("Добавить новое действие")
        add_hotkey_button.setStyleSheet("""
            QPushButton {
                background-color: #3D8948;
                color: white;
                border-radius: 8px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #2A6C34;
            }
        """)
        add_hotkey_button.clicked.connect(self.add_new_hotkey)
        hotkey_buttons_layout.addWidget(add_hotkey_button)
        hotkey_buttons_layout.addStretch()
        self.settings_layout.addLayout(hotkey_buttons_layout)

        self.settings_layout.addStretch()
        self.settings_scroll = QScrollArea()
        self.settings_scroll.setWidget(self.settings_tab)
        self.settings_scroll.setWidgetResizable(True)
        self.settings_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent; 
                border: none;
            }
            QWidget#qt_scrollarea_viewport {
                background-color: transparent;
            }
        """)
        self.tabs.addTab(self.settings_scroll, "Настройки")

    def add_new_hotkey(self):
        # Создаем новую горячую клавишу
        new_hotkey = {
            "combination": "Ctrl+N",
            "name": "Новое действие",
            "log_color": "#FFFFFF",
            "prompt": "Введите промпт для нового действия..."
        }
        
        # Добавляем в конфигурацию
        self.config["hotkeys"].append(new_hotkey)
        
        # Обновляем интерфейс
        self.update_buttons()
        
        # Перезагружаем настройки
        self.reload_settings_tab()
        
        # Обновляем key_states для отслеживания новой комбинации
        self.key_states = {key["combination"].lower(): False for key in self.config["hotkeys"]}
        self.key_states["ctrl"] = False
        self.key_states["alt"] = False
        self.key_states["shift"] = False
        
        # Сохраняем настройки
        self.save_settings()
        
        # Обновляем обработчик логов с новыми цветами
        #for handler in logger.handlers:
        #    if hasattr(handler, 'action_colors'):
        #        handler.action_colors = {k["name"]: k["log_color"] for k in self.config["hotkeys"]}

    def reload_settings_tab(self):
        # Сохраняем индекс текущей активной вкладки
        current_tab_index = self.tabs.currentIndex()
        
        # Удаляем старый виджет
        self.tabs.removeTab(self.tabs.indexOf(self.settings_scroll))
        
        # Создаем заново
        self.setup_settings_tab()
        
        # Восстанавливаем активную вкладку
        self.tabs.setCurrentIndex(current_tab_index)

    def update_models_for_hotkey(self, hotkey):
        self.update_models_signal.emit(hotkey)

    def update_hotkey_from_sequence(self, hotkey, sequence):
        """Обновляет комбинацию клавиш по новой записи последовательности"""
        if not sequence:  # Если последовательность пустая
            return
            
        # Обновляем в конфигурации
        old_combo = hotkey["combination"]
        
        # Проверяем, не используется ли уже такая комбинация
        if any(h["combination"] == sequence for h in self.config["hotkeys"] if h != hotkey):
            # Показываем предупреждение
            QMessageBox.warning(self, 
                            "Дублирование комбинации", 
                            f"Комбинация {sequence} уже используется другим действием.",
                            QMessageBox.Ok)
            return
        
        # Обновляем комбинацию
        hotkey["combination"] = sequence
        
        # Обновляем key_states и интерфейс
        self.update_hotkey(old_combo, sequence)

    def delete_hotkey(self, hotkey):
        """Удаляет горячую клавишу из конфигурации"""
        # Просим подтверждение
        reply = QMessageBox.question(self, 
                                'Подтверждение удаления', 
                                f"Вы уверены, что хотите удалить действие '{hotkey['name']}'?",
                                QMessageBox.Yes | QMessageBox.No, 
                                QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Удаляем из конфигурации
            self.config["hotkeys"].remove(hotkey)
            
            # Обновляем интерфейс
            self.update_buttons()
            
            # Перезагружаем настройки
            self.reload_settings_tab()
            
            # Обновляем key_states
            self.key_states = {key["combination"].lower(): False for key in self.config["hotkeys"]}
            self.key_states["ctrl"] = False
            self.key_states["alt"] = False
            self.key_states["shift"] = False
            
            # Сохраняем настройки
            self.save_settings()

    def apply_styles(self):
        self.setStyleSheet("""
            QTabWidget::pane { 
                background-color: #1e1e1e; 
                border: none; 
                border-radius: 10px; 
            }
            QWidget {
                background-color: #1e1e1e;
            }
            QFrame {
                background-color: #252525;
            }
            QPushButton { 
                background-color: #333333; 
                border-radius: 10px; 
                padding: 8px; 
                color: #FFFFFF;
            }
            QPushButton:hover { 
                background-color: #404040; 
            }
            QPushButton:pressed { 
                background-color: #2a2a2a; 
            }
            QLineEdit, QTextEdit { 
                background-color: #2e2e2e; 
                color: #FFFFFF; 
                border: 1px solid #444444; 
                border-radius: 10px; 
                padding: 5px;
            }
            QLineEdit:focus, QTextEdit:focus { 
                border: 1px solid #A3BFFA; 
            }
            QLabel { 
                color: #FFFFFF; 
                background-color: transparent;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background: transparent;
                width: 8px;
                height: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #555555;
                min-height: 20px;
                min-width: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
                background: #666666;
            }
            QScrollBar::add-line, QScrollBar::sub-line { 
                background: none; 
                height: 0px;
                width: 0px;
            }
            QScrollBar::add-page, QScrollBar::sub-page { 
                background: none; 
            }
            QTextBrowser {
                background-color: #252525; 
                color: #FFFFFF; 
                border: none; 
                border-radius: 10px;
                padding: 10px;
                selection-background-color: #A3BFFA;
                selection-color: #1e1e1e;
            }
            QScrollArea, QScrollArea * {
                background-color: #1e1e1e;
            }
        """)

    def update_buttons(self):
        for widget in self.button_widget.findChildren(QPushButton):
            widget.deleteLater()
        self.buttons.clear()

        width = self.button_widget.width()
        if width <= 0:
            return

        buttons_per_row = max(1, width // 160)
        rows = [[] for _ in range((len(self.config["hotkeys"]) + buttons_per_row - 1) // buttons_per_row)]

        for i, hotkey in enumerate(self.config["hotkeys"]):
            row_idx = i // buttons_per_row
            btn = QPushButton(f"{hotkey['name']}")
            btn.setToolTip(f"Горячая клавиша: {hotkey['combination']}")
            btn.setFixedHeight(30)  # Уменьшенная высота кнопок
            color = hotkey['log_color']
            btn.setStyleSheet(f"""
                QPushButton {{ 
                    color: {color}; 
                    background-color: #333333;
                    border-radius: 10px;
                    padding: 5px 10px;
                }}
                QPushButton:hover {{ 
                    background-color: {color}; 
                    color: #333333;
                }}
                QPushButton:pressed {{ 
                    background-color: {color}80; 
                }}
            """)
            btn.clicked.connect(lambda checked, h=hotkey: self.queue.put(h["name"]))
            rows[row_idx].append(btn)
            self.buttons[hotkey["combination"]] = btn

        for row in rows:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(8)
            for btn in row:
                btn.setMinimumWidth(0)
                row_layout.addWidget(btn, stretch=1)
            self.button_layout.addLayout(row_layout)

    def append_log(self, msg, color):
        self.log_area.moveCursor(QTextCursor.End)
        
        # Определяем тип лога для форматирования
        if "секунд" in msg:
            # Это сообщение о времени выполнения
            self.log_area.setTextColor(QColor("#888888"))
            self.log_area.append(f"    {msg}")
        elif any(f"{hotkey['combination']}: {hotkey['name']}" in msg for hotkey in self.config["hotkeys"]):
            # Это заголовок действия
            self.log_area.setTextColor(QColor(color))
            
            # Добавляем разделитель, если это не первое сообщение
            cursor = self.log_area.textCursor()
            if not cursor.atStart():
                self.log_area.append("\n" + "─" * 40 + "\n")
                
            self.log_area.append(f"{msg}")
        elif "Ошибка:" in msg:
            # Это сообщение об ошибке
            self.log_area.setTextColor(QColor("#FF5555"))
            self.log_area.append(f"❌ {msg}")
        elif "Буфер обмена пуст" in msg:
            # Это предупреждение
            self.log_area.setTextColor(QColor("#FFDD55"))
            self.log_area.append(f"⚠️ {msg}")
        else:
            # Это результат обработки или другое сообщение
            self.log_area.setTextColor(QColor(color))
            
            # Если это результат, добавляем отступ и форматирование
            if not msg.startswith("Программа запущена"):
                self.log_area.append(f"    {msg}")
            else:
                self.log_area.append(msg)
        
        # Прокрутка вниз
        self.log_area.ensureCursorVisible()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mouseMoveEvent(self, event):
        # Если режим изменения размера
        if self.resizing and self.resize_edge and self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.resizeWindow(delta)
            self.old_pos = event.globalPos()
            return
        
        # Определяем, находится ли курсор на краю окна
        edge = self.getResizeEdge(event.pos())
        if edge:
            self.setCursor(self.getResizeCursor(edge))
        else:
            self.setCursor(Qt.ArrowCursor)
            
        # Если режим перетаскивания
        if not self.resizing and self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
        
        super().mouseMoveEvent(event)

    def getResizeEdge(self, pos):
        # Ширина краев для изменения размера
        margin = 5
        width = self.width()
        height = self.height()
        
        # Проверяем, находится ли курсор на краю окна
        left = pos.x() <= margin
        top = pos.y() <= margin
        right = pos.x() >= width - margin
        bottom = pos.y() >= height - margin
        
        if top and left:
            return "top_left"
        elif top and right:
            return "top_right"
        elif bottom and left:
            return "bottom_left"
        elif bottom and right:
            return "bottom_right"
        elif left:
            return "left"
        elif right:
            return "right"
        elif top:
            return "top"
        elif bottom:
            return "bottom"
        
        return None
    
    def getResizeCursor(self, edge):
        if edge in ["left", "right"]:
            return Qt.SizeHorCursor
        elif edge in ["top", "bottom"]:
            return Qt.SizeVerCursor
        elif edge in ["top_left", "bottom_right"]:
            return Qt.SizeFDiagCursor
        elif edge in ["top_right", "bottom_left"]:
            return Qt.SizeBDiagCursor
        return Qt.ArrowCursor
    
    def resizeWindow(self, delta):
        x, y = self.x(), self.y()
        width, height = self.width(), self.height()
        min_width, min_height = self.minimumWidth(), self.minimumHeight()
        
        if self.resize_edge in ["left", "top_left", "bottom_left"]:
            # Изменяем левый край (меняем x и ширину)
            new_x = x + delta.x()
            new_width = width - delta.x()
            
            if new_width >= min_width:
                self.setGeometry(new_x, y, new_width, height)
        
        if self.resize_edge in ["right", "top_right", "bottom_right"]:
            # Изменяем правый край (меняем только ширину)
            new_width = width + delta.x()
            
            if new_width >= min_width:
                self.setGeometry(x, y, new_width, height)
        
        if self.resize_edge in ["top", "top_left", "top_right"]:
            # Изменяем верхний край (меняем y и высоту)
            new_y = y + delta.y()
            new_height = height - delta.y()
            
            if new_height >= min_height:
                self.setGeometry(x, new_y, width, new_height)
        
        if self.resize_edge in ["bottom", "bottom_left", "bottom_right"]:
            # Изменяем нижний край (меняем только высоту)
            new_height = height + delta.y()
            
            if new_height >= min_height:
                self.setGeometry(x, y, width, new_height)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.resize_edge = None
        self.setCursor(Qt.ArrowCursor)
        self.old_pos = None
        super().mouseReleaseEvent(event)

    def on_resize(self, event):
        self.resize_timer.start(200)
        super().resizeEvent(event)

    def open_color_picker(self, hotkey, color_input):
        color = QColorDialog.getColor(QColor(hotkey["log_color"]), self, "Выберите цвет")
        if color.isValid():
            hex_color = color.name()
            color_input.setText(hex_color.replace("#", ""))
            self.update_color(hotkey, hex_color)
            # Обновляем превью
            for combo, (input_field, preview) in self.color_pickers.items():
                if combo == hotkey["combination"]:
                    preview.setStyleSheet(f"background-color: {hex_color}; border-radius: 5px; border: none;")
                    break

    def update_hotkey_combo(self, old_combo, key_type, key):
        # Формируем новую комбинацию
        new_combo = f"{key_type}+{key}"
        self.update_hotkey(old_combo, new_combo)
        
        # Обновляем словари с ссылками на элементы интерфейса
        if old_combo in self.name_inputs:
            self.name_inputs[new_combo] = self.name_inputs.pop(old_combo)
        if old_combo in self.prompt_inputs:
            self.prompt_inputs[new_combo] = self.prompt_inputs.pop(old_combo)
        if old_combo in self.color_pickers:
            self.color_pickers[new_combo] = self.color_pickers.pop(old_combo)
        if old_combo in self.hotkey_combos:
            self.hotkey_combos[new_combo] = self.hotkey_combos.pop(old_combo)
        if old_combo in self.model_combos:
            self.model_combos[new_combo] = self.model_combos.pop(old_combo)
        if old_combo in self.buttons:
            self.buttons[new_combo] = self.buttons.pop(old_combo)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Одиночный клик
            self.showNormal()
            self.activateWindow()
        elif reason == QSystemTrayIcon.DoubleClick:  # Двойной клик
            self.showNormal()
            self.activateWindow()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.show()

    def quit_app(self):
        self.tray_icon.hide()
        self.quit_signal.emit()
