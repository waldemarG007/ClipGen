# -*- coding: utf-8 -*-
"""
View-Komponente für die ClipGen-Anwendung.

Diese Datei definiert die grafische Benutzeroberfläche (GUI) der Anwendung mit PyQt5.
Sie ist verantwortlich für die Darstellung aller Fenster, Schaltflächen, Tabs und
Eingabefelder und kommuniziert über Signale mit dem Controller (`ClipGen.py`).
"""
import os
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QTextBrowser, QTabWidget, QLineEdit, QTextEdit, QLabel, QScrollArea,
                          QFrame, QDialog, QColorDialog, QComboBox, QKeySequenceEdit, QMessageBox,
                          QSizeGrip, QStackedLayout)
from PyQt5.QtGui import QTextCursor, QColor, QIcon
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPoint, QSize

import pyperclip

class ClipGenView(QMainWindow):
    log_signal = pyqtSignal(str, str)  # Signal für die Protokollierung: Nachricht, Farbe
    setting_changed = pyqtSignal(list)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.config = controller.config
        # Icon setzen
        icon_path = os.path.abspath("ClipGen.ico")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            # Icon für die gesamte Anwendung setzen
            from PyQt5.QtWidgets import QApplication
            QApplication.instance().setWindowIcon(app_icon)
        else:
            print(f"Icon unter dem Pfad nicht gefunden: {icon_path}")
        self.setWindowTitle("ClipGen")
        self.setGeometry(100, 100, 554, 632)
        self.setMinimumSize(300, 200)

        # Anwendungsicon setzen
        icon_path = "ClipGen.ico"
        if getattr(sys, 'frozen', False):
            # Als kompilierte Anwendung gestartet
            icon_path = os.path.join(sys._MEIPASS, "ClipGen.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Griffe zum Ändern der Fenstergröße hinzufügen
        self.add_resize_grips()

        # Stile anwenden
        self.apply_styles()

        # Fensterflags ändern, um Größenänderung zu ermöglichen
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Variablen zum Ziehen und Ändern der Fenstergröße
        self.old_pos = None
        self.resizing = False
        self.resize_edge = None

        # Haupt-Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(0)

        # UI-Elemente erstellen
        self.setup_buttons()
        self.setup_tabs()

        # Protokolle mit Farben über Signale
        self.log_signal.connect(self.append_log)

        # Buttons bei Größenänderung aktualisieren
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.update_buttons)
        self.resizeEvent = self.on_resize

        # Stile anwenden
        self.apply_styles()

    def add_resize_grips(self):
        """Fügt Griffe zum Ändern der Fenstergröße an den vier Ecken hinzu."""
        # Griffe zum Ändern der Größe erstellen
        self.grip_bottom_right = QSizeGrip(self)
        self.grip_bottom_left = QSizeGrip(self)
        self.grip_top_right = QSizeGrip(self)
        self.grip_top_left = QSizeGrip(self)

        # Positionen festlegen
        self.grip_bottom_right.setGeometry(self.width() - 20, self.height() - 20, 20, 20)
        self.grip_bottom_left.setGeometry(0, self.height() - 20, 20, 20)
        self.grip_top_right.setGeometry(self.width() - 20, 0, 20, 20)
        self.grip_top_left.setGeometry(0, 0, 20, 20)

        # Griffe anzeigen
        self.grip_bottom_right.show()
        self.grip_bottom_left.show()
        self.grip_top_right.show()
        self.grip_top_left.show()

        # Stil für die Griffe hinzufügen (damit sie transparent, aber funktional sind)
        self.grip_bottom_right.setStyleSheet("background: transparent;")
        self.grip_bottom_left.setStyleSheet("background: transparent;")
        self.grip_top_right.setStyleSheet("background: transparent;")
        self.grip_top_left.setStyleSheet("background: transparent;")

    def resizeEvent(self, event):
        """resizeEvent-Methode überschreiben, um die Position der Griffe zu aktualisieren."""
        # Position der Griffe zum Ändern der Größe aktualisieren
        self.grip_bottom_right.setGeometry(self.width() - 20, self.height() - 20, 20, 20)
        self.grip_bottom_left.setGeometry(0, self.height() - 20, 20, 20)
        self.grip_top_right.setGeometry(self.width() - 20, 0, 20, 20)
        self.grip_top_left.setGeometry(0, 0, 20, 20)

        # Größenänderungs-Handler für die Buttons aufrufen
        if hasattr(self, 'resize_timer'):
            self.resize_timer.start(200)
        QMainWindow.resizeEvent(self, event)

    def mousePressEvent(self, event):
        # Prüfen, ob sich der Cursor am Fensterrand befindet
        edge = self.getResizeEdge(event.pos())
        if edge and event.button() == Qt.LeftButton:
            self.resizing = True
            self.resize_edge = edge
            self.setCursor(self.getResizeCursor(edge))
            self.old_pos = event.globalPos()
            return

        # Wenn im Titelbereich geklickt wird, zum Ziehen vorbereiten
        if event.button() == Qt.LeftButton and event.pos().y() < 30 and not edge:
            self.old_pos = event.globalPos()

        super().mousePressEvent(event)

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
                background-color: #2A2A2A;  /* Farbe des aktiven Tabs */
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

        # Log-Bereich
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

        # Log-Aktionsbuttons
        log_actions = QHBoxLayout()
        clear_logs = QPushButton("Logs löschen")
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

        copy_logs = QPushButton("Logs kopieren")
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
        self.tabs.addTab(self.log_tab, "Logs")

    def setup_settings_tab(self):
        self.settings_tab = QWidget()
        self.settings_tab.setStyleSheet("background-color: #1e1e1e;")
        self.settings_layout = QVBoxLayout(self.settings_tab)
        self.settings_layout.setSpacing(15)
        self.settings_layout.setContentsMargins(20, 20, 20, 20)

        # Provider-Auswahl
        provider_container = QFrame()
        provider_container.setStyleSheet("background-color: #252525; border-radius: 15px; padding: 10px;")
        provider_layout = QVBoxLayout(provider_container)

        provider_label = QLabel("KI-Anbieter:")
        provider_layout.addWidget(provider_label)

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Gemini", "Groq", "Mistral", "Ollama"])
        self.provider_combo.setStyleSheet("""
            QComboBox {
                border-radius: 8px;
                border: 1px solid #444444;
                padding: 8px;
                background-color: #2a2a2a;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.provider_combo.currentIndexChanged.connect(self._update_ui_for_provider)
        self.provider_combo.currentTextChanged.connect(
            lambda text: self.setting_changed.emit(["general", "provider", text])
        )
        provider_layout.addWidget(self.provider_combo)
        self.settings_layout.addWidget(provider_container)

        # --- Anbieterspezifische Einstellungen ---
        self.provider_settings_container = QWidget()
        self.provider_settings_layout = QStackedLayout(self.provider_settings_container)
        self.settings_layout.addWidget(self.provider_settings_container)

        self.provider_settings_frames = {}

        # Gemini-Einstellungen
        gemini_frame = QFrame()
        gemini_frame.setLayout(QVBoxLayout())
        self.gemini_api_key_input = QLineEdit(self.config.get("providers", {}).get("gemini", {}).get("api_key", ""))
        gemini_frame.layout().addWidget(QLabel("Gemini API-Schlüssel:"))
        gemini_frame.layout().addWidget(self.gemini_api_key_input)
        self.provider_settings_layout.addWidget(gemini_frame)
        self.provider_settings_frames["Gemini"] = gemini_frame

        # Groq-Einstellungen
        groq_frame = QFrame()
        groq_frame.setLayout(QVBoxLayout())
        self.groq_api_key_input = QLineEdit(self.config.get("providers", {}).get("groq", {}).get("api_key", ""))
        self.groq_model_input = QLineEdit(self.config.get("providers", {}).get("groq", {}).get("model", "llama3-8b-8192"))
        groq_frame.layout().addWidget(QLabel("Groq API-Schlüssel:"))
        groq_frame.layout().addWidget(self.groq_api_key_input)
        groq_frame.layout().addWidget(QLabel("Groq Modell:"))
        groq_frame.layout().addWidget(self.groq_model_input)
        self.provider_settings_layout.addWidget(groq_frame)
        self.provider_settings_frames["Groq"] = groq_frame

        # Mistral-Einstellungen
        mistral_frame = QFrame()
        mistral_frame.setLayout(QVBoxLayout())
        self.mistral_api_key_input = QLineEdit(self.config.get("providers", {}).get("mistral", {}).get("api_key", ""))
        self.mistral_model_input = QLineEdit(self.config.get("providers", {}).get("mistral", {}).get("model", "mistral-large-latest"))
        mistral_frame.layout().addWidget(QLabel("Mistral API-Schlüssel:"))
        mistral_frame.layout().addWidget(self.mistral_api_key_input)
        mistral_frame.layout().addWidget(QLabel("Mistral Modell:"))
        mistral_frame.layout().addWidget(self.mistral_model_input)
        self.provider_settings_layout.addWidget(mistral_frame)
        self.provider_settings_frames["Mistral"] = mistral_frame

        # Ollama-Einstellungen
        ollama_frame = QFrame()
        ollama_frame.setLayout(QVBoxLayout())
        self.ollama_host_input = QLineEdit(self.config.get("providers", {}).get("ollama", {}).get("host", "http://localhost:11434"))
        self.ollama_model_input = QLineEdit(self.config.get("providers", {}).get("ollama", {}).get("model", "llama3"))
        ollama_frame.layout().addWidget(QLabel("Ollama Host:"))
        ollama_frame.layout().addWidget(self.ollama_host_input)
        ollama_frame.layout().addWidget(QLabel("Ollama Modell:"))
        ollama_frame.layout().addWidget(self.ollama_model_input)
        self.provider_settings_layout.addWidget(ollama_frame)
        self.provider_settings_frames["Ollama"] = ollama_frame

        # Signale für Anbieter-Einstellungen verbinden
        self.gemini_api_key_input.textChanged.connect(
            lambda text: self.setting_changed.emit(["providers", "gemini", "api_key", text])
        )
        self.groq_api_key_input.textChanged.connect(
            lambda text: self.setting_changed.emit(["providers", "groq", "api_key", text])
        )
        self.groq_model_input.textChanged.connect(
            lambda text: self.setting_changed.emit(["providers", "groq", "model", text])
        )
        self.mistral_api_key_input.textChanged.connect(
            lambda text: self.setting_changed.emit(["providers", "mistral", "api_key", text])
        )
        self.mistral_model_input.textChanged.connect(
            lambda text: self.setting_changed.emit(["providers", "mistral", "model", text])
        )
        self.ollama_host_input.textChanged.connect(
            lambda text: self.setting_changed.emit(["providers", "ollama", "host", text])
        )
        self.ollama_model_input.textChanged.connect(
            lambda text: self.setting_changed.emit(["providers", "ollama", "model", text])
        )

        # Anfangszustand setzen
        current_provider = self.config.get("general", {}).get("provider", "Gemini")
        self.provider_combo.setCurrentText(current_provider)
        self._update_ui_for_provider()

    def _update_ui_for_provider(self):
        selected_provider = self.provider_combo.currentText()
        self.provider_settings_layout.setCurrentWidget(self.provider_settings_frames[selected_provider])

        # Hotkey für Bildanalyse aktivieren/deaktivieren
        vision_providers = ["Gemini", "Ollama"]
        image_hotkey_name = "Bildanalyse"

        for hotkey in self.config["hotkeys"]:
            if hotkey["name"] == image_hotkey_name:
                hotkey_combo = hotkey["combination"]
                if hotkey_combo in self.buttons:
                    self.buttons[hotkey_combo].setEnabled(selected_provider in vision_providers)
                break

        # Titel für Hotkeys
        hotkeys_title = QLabel("Hotkey-Einstellungen")
        hotkeys_title.setStyleSheet("font-size: 16px;")
        self.settings_layout.addWidget(hotkeys_title)

        # Karten für jeden Hotkey erstellen
        self.prompt_inputs = {}
        self.name_inputs = {}
        self.color_pickers = {}
        self.hotkey_combos = {}
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

            # Tastenkombination auswählen
            hotkey_header = QHBoxLayout()

            # Feld zum Aufzeichnen der Tastenkombination erstellen
            hotkey_edit = QKeySequenceEdit()
            hotkey_edit.setKeySequence(hotkey["combination"])  # Aktuelle Kombination festlegen
            hotkey_edit.setStyleSheet("""
                QKeySequenceEdit {
                    background-color: #333333;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    font-family: 'Consolas', 'Courier New', monospace;
                }
            """)
            # Handler für Kombinationsänderung hinzufügen
            hotkey_edit.keySequenceChanged.connect(
                lambda seq, h=hotkey: self.update_hotkey_from_sequence(h, seq.toString())
            )
            # Feld zum Layout hinzufügen
            hotkey_header.addWidget(hotkey_edit)

            # Löschen-Button rechts hinzufügen
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

            # Feld für Aktionsnamen
            name_label = QLabel("Aktionsname:")
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

            # Feld für Prompt
            prompt_label = QLabel("Prompt:")
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

            # Farbauswahl
            color_layout = QHBoxLayout()

            color_label = QLabel("Farbe in Logs:")
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

        # Buttons zum Hinzufügen/Entfernen von Hotkeys
        hotkey_buttons_layout = QHBoxLayout()
        add_hotkey_button = QPushButton("Neue Aktion hinzufügen")
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
        self.tabs.addTab(self.settings_scroll, "Einstellungen")

    def add_new_hotkey(self):
        # Neuen Hotkey erstellen
        new_hotkey = {
            "combination": "Ctrl+N",
            "name": "Neue Aktion",
            "log_color": "#FFFFFF",
            "prompt": "Geben Sie den Prompt für die neue Aktion ein..."
        }

        # Zur Konfiguration hinzufügen
        self.config["hotkeys"].append(new_hotkey)

        # Oberfläche aktualisieren
        self.update_buttons()

        # Einstellungen neu laden
        self.reload_settings_tab()

        # key_states für die neue Kombination aktualisieren
        self.key_states = {key["combination"].lower(): False for key in self.config["hotkeys"]}
        self.key_states["ctrl"] = False
        self.key_states["alt"] = False
        self.key_states["shift"] = False

        # Einstellungen speichern
        self.save_settings()

    def reload_settings_tab(self):
        # Index des aktuell aktiven Tabs speichern
        current_tab_index = self.tabs.currentIndex()

        # Altes Widget entfernen
        self.tabs.removeTab(self.tabs.indexOf(self.settings_scroll))

        # Neu erstellen
        self.setup_settings_tab()

        # Aktiven Tab wiederherstellen
        self.tabs.setCurrentIndex(current_tab_index)

    def update_hotkey_from_sequence(self, hotkey, sequence):
        """Aktualisiert die Tastenkombination gemäß der neuen Sequenzaufzeichnung."""
        if not sequence:  # Wenn die Sequenz leer ist
            return

        # In der Konfiguration aktualisieren
        old_combo = hotkey["combination"]

        # Prüfen, ob diese Kombination bereits verwendet wird
        if any(h["combination"] == sequence for h in self.config["hotkeys"] if h != hotkey):
            # Warnung anzeigen
            QMessageBox.warning(self,
                            "Doppelte Kombination",
                            f"Die Kombination {sequence} wird bereits von einer anderen Aktion verwendet.",
                            QMessageBox.Ok)
            return

        # Kombination aktualisieren
        hotkey["combination"] = sequence

        # key_states und Oberfläche aktualisieren
        self.update_hotkey(old_combo, sequence)

    def delete_hotkey(self, hotkey):
        """Entfernt einen Hotkey aus der Konfiguration."""
        # Um Bestätigung bitten
        reply = QMessageBox.question(self,
                                'Löschbestätigung',
                                f"Sind Sie sicher, dass Sie die Aktion '{hotkey['name']}' löschen möchten?",
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Aus der Konfiguration entfernen
            self.config["hotkeys"].remove(hotkey)

            # Oberfläche aktualisieren
            self.update_buttons()

            # Einstellungen neu laden
            self.reload_settings_tab()

            # key_states aktualisieren
            self.key_states = {key["combination"].lower(): False for key in self.config["hotkeys"]}
            self.key_states["ctrl"] = False
            self.key_states["alt"] = False
            self.key_states["shift"] = False

            # Einstellungen speichern
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
            btn.setToolTip(f"Hotkey: {hotkey['combination']}")
            btn.setFixedHeight(30)  # Reduzierte Button-Höhe
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

        # Log-Typ für die Formatierung bestimmen
        if "Sekunden" in msg:
            # Dies ist die Nachricht über die Ausführungszeit
            self.log_area.setTextColor(QColor("#888888"))
            self.log_area.append(f"    {msg}")
        elif any(f"{hotkey['combination']}: {hotkey['name']}" in msg for hotkey in self.config["hotkeys"]):
            # Dies ist der Aktionstitel
            self.log_area.setTextColor(QColor(color))

            # Trennzeichen hinzufügen, wenn es nicht die erste Nachricht ist
            cursor = self.log_area.textCursor()
            if not cursor.atStart():
                self.log_area.append("\n" + "─" * 40 + "\n")

            self.log_area.append(f"{msg}")
        elif "Fehler:" in msg:
            # Dies ist eine Fehlermeldung
            self.log_area.setTextColor(QColor("#FF5555"))
            self.log_area.append(f"❌ {msg}")
        elif "Zwischenablage" in msg and "leer" in msg:
            # Dies ist eine Warnung
            self.log_area.setTextColor(QColor("#FFDD55"))
            self.log_area.append(f"⚠️ {msg}")
        else:
            # Dies ist ein Verarbeitungsergebnis oder eine andere Nachricht
            self.log_area.setTextColor(QColor(color))

            # Wenn es sich um ein Ergebnis handelt, Einzug und Formatierung hinzufügen
            if not msg.startswith("ClipGen gestartet"):
                self.log_area.append(f"    {msg}")
            else:
                self.log_area.append(msg)

        # Nach unten scrollen
        self.log_area.ensureCursorVisible()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mouseMoveEvent(self, event):
        # Wenn im Größenänderungsmodus
        if self.resizing and self.resize_edge and self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.resizeWindow(delta)
            self.old_pos = event.globalPos()
            return

        # Bestimmen, ob sich der Cursor am Fensterrand befindet
        edge = self.getResizeEdge(event.pos())
        if edge:
            self.setCursor(self.getResizeCursor(edge))
        else:
            self.setCursor(Qt.ArrowCursor)

        # Wenn im Ziehmodus
        if not self.resizing and self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

        super().mouseMoveEvent(event)

    def getResizeEdge(self, pos):
        # Breite der Ränder zum Ändern der Größe
        margin = 5
        width = self.width()
        height = self.height()

        # Prüfen, ob sich der Cursor am Fensterrand befindet
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
            # Linken Rand ändern (x und Breite ändern)
            new_x = x + delta.x()
            new_width = width - delta.x()

            if new_width >= min_width:
                self.setGeometry(new_x, y, new_width, height)

        if self.resize_edge in ["right", "top_right", "bottom_right"]:
            # Rechten Rand ändern (nur Breite ändern)
            new_width = width + delta.x()

            if new_width >= min_width:
                self.setGeometry(x, y, new_width, height)

        if self.resize_edge in ["top", "top_left", "top_right"]:
            # Oberen Rand ändern (y und Höhe ändern)
            new_y = y + delta.y()
            new_height = height - delta.y()

            if new_height >= min_height:
                self.setGeometry(x, new_y, width, new_height)

        if self.resize_edge in ["bottom", "bottom_left", "bottom_right"]:
            # Unteren Rand ändern (nur Höhe ändern)
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
        color = QColorDialog.getColor(QColor(hotkey["log_color"]), self, "Farbe auswählen")
        if color.isValid():
            hex_color = color.name()
            color_input.setText(hex_color.replace("#", ""))
            self.update_color(hotkey, hex_color)
            # Vorschau aktualisieren
            for combo, (input_field, preview) in self.color_pickers.items():
                if combo == hotkey["combination"]:
                    preview.setStyleSheet(f"background-color: {hex_color}; border-radius: 5px; border: none;")
                    break

    def update_hotkey_combo(self, old_combo, key_type, key):
        # Neue Kombination erstellen
        new_combo = f"{key_type}+{key}"
        self.update_hotkey(old_combo, new_combo)

        # Wörterbücher mit Verweisen auf UI-Elemente aktualisieren
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
