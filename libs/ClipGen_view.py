import os
import sys
import json
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

        # Erstellen des Kontextmenюs
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
        """Einrichtung der Einstellungen-Registerkarte"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(15, 15, 15, 15)
        settings_layout.setSpacing(10)
        
        # === API-KEYS SECTION ===
        api_section = QLabel("🔑 API-Schlüssel")
        api_section.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFFFFF;")
        settings_layout.addWidget(api_section)
        
        # Gemini API Key
        gemini_label = QLabel("Gemini API-Schlüssel:")
        gemini_label.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        gemini_layout = QHBoxLayout()
        gemini_layout.setSpacing(5)
        
        self.gemini_input = QLineEdit(self.config.get("gemini_api_key", ""))
        self.gemini_input.setEchoMode(QLineEdit.Password)
        self.gemini_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #FFFFFF;
                border-radius: 5px;
                border: 1px solid #444444;
                padding: 6px;
                font-size: 11px;
            }
        """)
        
        self.gemini_toggle_btn = QPushButton("👁️")
        self.gemini_toggle_btn.setMaximumWidth(35)
        self.gemini_toggle_btn.setMaximumHeight(28)
        self.gemini_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.gemini_toggle_btn.clicked.connect(lambda: self.toggle_api_visibility(self.gemini_input, self.gemini_toggle_btn))
        
        gemini_save_btn = QPushButton("💾")
        gemini_save_btn.setMaximumWidth(35)
        gemini_save_btn.setMaximumHeight(28)
        gemini_save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a8a2a;
                color: #FFFFFF;
                border: 1px solid #3a9a3a;
                border-radius: 5px;
                padding: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3a9a3a;
            }
        """)
        gemini_save_btn.clicked.connect(lambda: self.save_single_api_key("gemini_api_key", self.gemini_input, "Gemini"))
        
        gemini_layout.addWidget(self.gemini_input)
        gemini_layout.addWidget(self.gemini_toggle_btn)
        gemini_layout.addWidget(gemini_save_btn)
        
        settings_layout.addWidget(gemini_label)
        settings_layout.addLayout(gemini_layout)
        
        # Mistral API Key
        mistral_label = QLabel("Mistral API-Schlüssel:")
        mistral_label.setStyleSheet("color: #CCCCCC; font-size: 12px; margin-top: 8px;")
        mistral_layout = QHBoxLayout()
        mistral_layout.setSpacing(5)
        
        self.mistral_input = QLineEdit(self.config.get("mistral_api_key", ""))
        self.mistral_input.setEchoMode(QLineEdit.Password)
        self.mistral_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #FFFFFF;
                border-radius: 5px;
                border: 1px solid #444444;
                padding: 6px;
                font-size: 11px;
            }
        """)
        
        self.mistral_toggle_btn = QPushButton("👁️")
        self.mistral_toggle_btn.setMaximumWidth(35)
        self.mistral_toggle_btn.setMaximumHeight(28)
        self.mistral_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.mistral_toggle_btn.clicked.connect(lambda: self.toggle_api_visibility(self.mistral_input, self.mistral_toggle_btn))
        
        mistral_save_btn = QPushButton("💾")
        mistral_save_btn.setMaximumWidth(35)
        mistral_save_btn.setMaximumHeight(28)
        mistral_save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a8a2a;
                color: #FFFFFF;
                border: 1px solid #3a9a3a;
                border-radius: 5px;
                padding: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3a9a3a;
            }
        """)
        mistral_save_btn.clicked.connect(lambda: self.save_single_api_key("mistral_api_key", self.mistral_input, "Mistral"))
        
        mistral_layout.addWidget(self.mistral_input)
        mistral_layout.addWidget(self.mistral_toggle_btn)
        mistral_layout.addWidget(mistral_save_btn)
        
        settings_layout.addWidget(mistral_label)
        settings_layout.addLayout(mistral_layout)
        
        # Groq API Key
        groq_label = QLabel("Groq API-Schlüssel:")
        groq_label.setStyleSheet("color: #CCCCCC; font-size: 12px; margin-top: 8px;")
        groq_layout = QHBoxLayout()
        groq_layout.setSpacing(5)
        
        self.groq_input = QLineEdit(self.config.get("groq_api_key", ""))
        self.groq_input.setEchoMode(QLineEdit.Password)
        self.groq_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #FFFFFF;
                border-radius: 5px;
                border: 1px solid #444444;
                padding: 6px;
                font-size: 11px;
            }
        """)
        
        self.groq_toggle_btn = QPushButton("👁️")
        self.groq_toggle_btn.setMaximumWidth(35)
        self.groq_toggle_btn.setMaximumHeight(28)
        self.groq_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.groq_toggle_btn.clicked.connect(lambda: self.toggle_api_visibility(self.groq_input, self.groq_toggle_btn))
        
        groq_save_btn = QPushButton("💾")
        groq_save_btn.setMaximumWidth(35)
        groq_save_btn.setMaximumHeight(28)
        groq_save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a8a2a;
                color: #FFFFFF;
                border: 1px solid #3a9a3a;
                border-radius: 5px;
                padding: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3a9a3a;
            }
        """)
        groq_save_btn.clicked.connect(lambda: self.save_single_api_key("groq_api_key", self.groq_input, "Groq"))
        
        groq_layout.addWidget(self.groq_input)
        groq_layout.addWidget(self.groq_toggle_btn)
        groq_layout.addWidget(groq_save_btn)
        
        settings_layout.addWidget(groq_label)
        settings_layout.addLayout(groq_layout)
        
        # Status Label für API Feedback
        self.api_status_label = QLabel("")
        self.api_status_label.setStyleSheet("color: #88FF88; font-size: 11px; font-weight: bold; margin-top: 5px;")
        settings_layout.addWidget(self.api_status_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #444444; margin: 10px 0px;")
        settings_layout.addWidget(separator)
        
        # === HOTKEYS SECTION ===
        hotkeys_label = QLabel("⌨️ Hotkeys konfigurieren")
        hotkeys_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFFFFF; margin-top: 10px;")
        settings_layout.addWidget(hotkeys_label)
        
        # Scrollable area für Hotkeys (ohне double-window Effekt)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget {
                background-color: transparent;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(8)
        
        # Für jeden Hotkey ein Eingabefeld
        self.hotkey_inputs = {}
        self.provider_combos = {}
        self.model_combos = {}
        
        for i, hotkey in enumerate(self.config.get("hotkeys", [])):
            # Container für jeden Hotkey (ohne визуальный Rahmen)
            hotkey_layout = QVBoxLayout()
            hotkey_layout.setSpacing(5)
            
            # === HOTKEY NAME + COMBINATION (in einer Zeile) ===
            header_layout = QHBoxLayout()
            header_layout.setSpacing(8)
            
            name_label = QLabel(f"#{i+1}")
            name_label.setStyleSheet("color: #AAAAAA; font-size: 11px; font-weight: bold; min-width: 25px;")
            
            name_input = QLineEdit(hotkey.get("name", ""))
            name_input.setPlaceholderText("Name der Aktion")
            name_input.setMaximumHeight(28)
            name_input.setStyleSheet("""
                QLineEdit {
                    background-color: #2a2a2a;
                    color: #FFFFFF;
                    border: 1px solid #444444;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 11px;
                }
            """)
            
            combo_input = QKeySequenceEdit()
            combo_input.setKeySequence(hotkey.get("combination", ""))
            combo_input.setMaximumHeight(28)
            combo_input.setMaximumWidth(150)
            combo_input.setStyleSheet("""
                QKeySequenceEdit {
                    background-color: #2a2a2a;
                    color: #FFFFFF;
                    border: 1px solid #444444;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 11px;
                }
            """)
            
            header_layout.addWidget(name_label)
            header_layout.addWidget(name_input, stretch=1)
            header_layout.addWidget(combo_input)
            
            hotkey_layout.addLayout(header_layout)
            self.hotkey_inputs[f"name_{i}"] = name_input
            self.hotkey_inputs[f"combination_{i}"] = combo_input
            
            # === PROVIDER + MODEL (in einer Zeile) ===
            provider_model_layout = QHBoxLayout()
            provider_model_layout.setSpacing(8)
            
            provider_combo = QComboBox()
            provider_combo.addItems(["Gemini", "Mistral", "Groq"])
            provider_combo.setCurrentText(hotkey.get("api_provider", "Gemini"))
            provider_combo.setMaximumHeight(28)
            provider_combo.setMaximumWidth(120)
            provider_combo.setStyleSheet("""
                QComboBox {
                    background-color: #2a2a2a;
                    color: #FFFFFF;
                    border: 1px solid #444444;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 11px;
                }
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView {
                    background-color: #2a2a2a;
                    color: #FFFFFF;
                    selection-background-color: #444444;
                }
            """)
            
            model_combo = QComboBox()
            available_models = self.config.get("available_models", {})
            current_provider = hotkey.get("api_provider", "Gemini")
            models_list = available_models.get(current_provider, [])
            
            model_combo.addItems(models_list)
            current_model = hotkey.get("model", "")
            if current_model and current_model in models_list:
                model_combo.setCurrentText(current_model)
            
            model_combo.setMaximumHeight(28)
            model_combo.setStyleSheet("""
                QComboBox {
                    background-color: #2a2a2a;
                    color: #FFFFFF;
                    border: 1px solid #444444;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 11px;
                }
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView {
                    background-color: #2a2a2a;
                    color: #FFFFFF;
                    selection-background-color: #444444;
                }
            """)
            
            def update_models(provider_name, idx=i):
                available = self.config.get("available_models", {})
                models = available.get(provider_name, [])
                self.model_combos[f"model_{idx}"].clear()
                self.model_combos[f"model_{idx}"].addItems(models)
            
            provider_combo.currentTextChanged.connect(update_models)
            
            provider_model_layout.addWidget(QLabel("Provider:"), 0)
            provider_model_layout.addWidget(provider_combo, 0)
            provider_model_layout.addWidget(QLabel("Modell:"), 0)
            provider_model_layout.addWidget(model_combo, 1)
            
            hotkey_layout.addLayout(provider_model_layout)
            self.provider_combos[f"provider_{i}"] = provider_combo
            self.model_combos[f"model_{i}"] = model_combo
            
            # === PROMPT ===
            prompt_label = QLabel("Prompt:")
            prompt_label.setStyleSheet("color: #AAAAAA; font-size: 11px;")
            
            prompt_input = QTextEdit(hotkey.get("prompt", ""))
            prompt_input.setMaximumHeight(60)
            prompt_input.setStyleSheet("""
                QTextEdit {
                    background-color: #2a2a2a;
                    color: #FFFFFF;
                    border: 1px solid #444444;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 11px;
                }
            """)
            
            hotkey_layout.addWidget(prompt_label)
            hotkey_layout.addWidget(prompt_input)
            self.hotkey_inputs[f"prompt_{i}"] = prompt_input
            
            # === TYPE + COLOR + DELETE (in einer Zeile) ===
            footer_layout = QHBoxLayout()
            footer_layout.setSpacing(8)
            
            type_combo = QComboBox()
            type_combo.addItems(["text", "image"])
            type_combo.setCurrentText(hotkey.get("type", "text"))
            type_combo.setMaximumHeight(28)
            type_combo.setMaximumWidth(100)
            type_combo.setStyleSheet("""
                QComboBox {
                    background-color: #2a2a2a;
                    color: #FFFFFF;
                    border: 1px solid #444444;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 11px;
                }
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView {
                    background-color: #2a2a2a;
                    color: #FFFFFF;
                    selection-background-color: #444444;
                }
            """)
            
            color_input = QLineEdit(hotkey.get("log_color", "#FFFFFF"))
            color_input.setMaximumHeight(28)
            color_input.setMaximumWidth(100)
            color_input.setStyleSheet("""
                QLineEdit {
                    background-color: #2a2a2a;
                    color: #FFFFFF;
                    border: 1px solid #444444;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 11px;
                }
            """)
            
            def open_color_dialog(idx=i):
                color = QColorDialog.getColor(QColor(self.hotkey_inputs[f"color_{idx}"].text()))
                if color.isValid():
                    self.hotkey_inputs[f"color_{idx}"].setText(color.name())
            
            color_btn = QPushButton("🎨")
            color_btn.setMaximumWidth(35)
            color_btn.setMaximumHeight(28)
            color_btn.setStyleSheet("""
                QPushButton {
                    background-color: #444444;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    padding: 4px;
                    font-size: 11px;
                }
                QPushButton:hover { background-color: #555555; }
            """)
            color_btn.clicked.connect(lambda: open_color_dialog())
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(35)
            delete_btn.setMaximumHeight(28)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #8B0000;
                    color: #FFFFFF;
                    border: 1px solid #A00000;
                    border-radius: 5px;
                    padding: 4px;
                    font-size: 11px;
                }
                QPushButton:hover { background-color: #A00000; }
            """)
            delete_btn.clicked.connect(lambda: self.delete_hotkey(i))
            
            footer_layout.addWidget(QLabel("Typ:"), 0)
            footer_layout.addWidget(type_combo, 0)
            footer_layout.addWidget(QLabel("Farbe:"), 0)
            footer_layout.addWidget(color_input, 0)
            footer_layout.addWidget(color_btn, 0)
            footer_layout.addStretch()
            footer_layout.addWidget(delete_btn, 0)
            
            hotkey_layout.addLayout(footer_layout)
            self.hotkey_inputs[f"type_{i}"] = type_combo
            self.hotkey_inputs[f"color_{i}"] = color_input
            
            # Add separator between hotkeys
            hotkey_container = QWidget()
            hotkey_container.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    border-bottom: 1px solid #333333;
                    padding-bottom: 8px;
                }
            """)
            hotkey_container.setLayout(hotkey_layout)
            scroll_layout.addWidget(hotkey_container)
        
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        settings_layout.addWidget(scroll_area, stretch=1)
        
        # === BUTTONS ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        add_hotkey_btn = QPushButton("➕ Neuer Hotkey")
        add_hotkey_btn.setMaximumHeight(32)
        add_hotkey_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a8a2a;
                color: #FFFFFF;
                border: 1px solid #3a9a3a;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #3a9a3a; }
        """)
        add_hotkey_btn.clicked.connect(self.add_new_hotkey)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setMaximumHeight(32)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a5a8a;
                color: #FFFFFF;
                border: 1px solid #2a6a9a;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #2a6a9a; }
        """)
        save_btn.clicked.connect(self.save_settings_from_ui)
        
        button_layout.addWidget(add_hotkey_btn)
        button_layout.addWidget(save_btn)
        button_layout.addStretch()
        
        settings_layout.addLayout(button_layout)
        
        settings_widget.setLayout(settings_layout)
        self.tabs.addTab(settings_widget, "⚙️ Einstellungen")

    def toggle_api_visibility(self, input_field, button):
        """Wechselt zwischen Anzeige und Verbergen des API-Schlüssels"""
        if input_field.echoMode() == QLineEdit.Password:
            input_field.setEchoMode(QLineEdit.Normal)
            button.setText("🙈")
        else:
            input_field.setEchoMode(QLineEdit.Password)
            button.setText("👁️")

    def save_single_api_key(self, key_name, input_field, provider_name):
        """Speichert einen einzelnen API-Schlüssel mit Feedback"""
        try:
            api_key = input_field.text().strip()
            
            if not api_key:
                QMessageBox.warning(self, "Warnung", f"{provider_name} API-Schlüssel darf nicht leer sein!")
                self.api_status_label.setText(f"❌ {provider_name}: Leerer Schlüssel nicht gespeichert")
                return
            
            # Speichern в config
            self.config[key_name] = api_key
            
            # Speichern в settings.json
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            
            # Feedback geben
            self.api_status_label.setText(f"✅ {provider_name} API-Schlüssel erfolgreich gespeichert!")
            
            # Feedback nach 3 Sekunden ausblenden
            QTimer.singleShot(3000, lambda: self.api_status_label.setText(""))
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")
            self.api_status_label.setText(f"❌ Fehler beim Speichern von {provider_name}")

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

    def save_settings_from_ui(self):
        """Speichert die Einstellungen aus der UI in settings.json"""
        try:
            # API-Keys speichern
            self.config["gemini_api_key"] = self.findChild(QLineEdit, "gemini_input").text() if self.findChild(QLineEdit, "gemini_input") else ""
            self.config["mistral_api_key"] = self.findChild(QLineEdit, "mistral_input").text() if self.findChild(QLineEdit, "mistral_input") else ""
            self.config["groq_api_key"] = self.findChild(QLineEdit, "groq_input").text() if self.findChild(QLineEdit, "groq_input") else ""
            
            # Hotkeys speichern
            self.config["hotkeys"] = []
            i = 0
            while f"name_{i}" in self.hotkey_inputs:
                hotkey = {
                    "name": self.hotkey_inputs[f"name_{i}"].text(),
                    "combination": self.hotkey_inputs[f"combination_{i}"].keySequence().toString(),
                    "prompt": self.hotkey_inputs[f"prompt_{i}"].toPlainText(),
                    "api_provider": self.provider_combos[f"provider_{i}"].currentText(),
                    "model": self.model_combos[f"model_{i}"].currentText(),
                    "type": self.hotkey_inputs[f"type_{i}"].currentText(),
                    "log_color": self.hotkey_inputs[f"color_{i}"].text()
                }
                self.config["hotkeys"].append(hotkey)
                i += 1
            
            # Einstellungen speichern
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            
            QMessageBox.information(self, "Erfolg", "Einstellungen gespeichert!")
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")
