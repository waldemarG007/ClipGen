# ClipGen

<div align="center">
   <img src="https://raw.githubusercontent.com/Veta-one/clipgen/main/screenshots/clipgen-logo.png" alt="ClipGen Logo" width="200"/>
   <p><em>Ihr KI-gestützter Begleiter für die Zwischenablage. Sofortige Textkorrektur, Übersetzung und Bildanalyse mit Ihren bevorzugten KI-Modellen.</em></p>
</div>

## 🚀 Übersicht

ClipGen ist ein leistungsstarkes Desktop-Dienstprogramm, das die Art und Weise, wie Sie mit Texten und Bildern auf Ihrem Computer interagieren, revolutioniert. Durch die Anbindung an Ihre bevorzugten KI-Anbieter (einschließlich **Google Gemini**, **Groq**, **Mistral** und lokale **Ollama**-Modelle) führt ClipGen blitzschnelle KI-Operationen auf den Inhalten Ihrer Zwischenablage mit einfachen Tastenkombinationen durch.

**Geschwindigkeit ist unsere Priorität** – ClipGen verarbeitet Anfragen in Sekunden, sodass es sich wie ein nativer Teil Ihres Betriebssystems anfühlt und nicht wie ein externes Werkzeug.

![ClipGen in Aktion](https://raw.githubusercontent.com/Veta-one/clipgen/main/screenshots/clipgen-demo.gif)

## ✨ Funktionen

- 🔌 **Multi-API-Unterstützung**: Wählen Sie Ihren bevorzugten KI-Anbieter!
  - **Google Gemini**: Für leistungsstarke, kostenlose, multimodale Analysen.
  - **Groq**: Für blitzschnelle Textgenerierung.
  - **Mistral AI**: Für hochwertige Textmodelle.
  - **Ollama**: Um Ihre eigenen lokalen Modelle für maximale Privatsphäre und Anpassung zu verwenden.
- ⌨️ **Hotkey-gesteuerter Arbeitsablauf** – Kein Wechsel zwischen Anwendungen erforderlich.
- ⚙️ **System-Tray-Integration** – Läuft unauffällig im Hintergrund.
- 🚀 **Autostart-Funktion** – Startet ClipGen automatisch beim Hochfahren des Systems.
- 🖥️ **Globaler Hotkey zum Anzeigen/Verstecken** – Greifen Sie von überall auf das Fenster zu.
- ✏️ **Anpassbare Prompts und Aktionen** – Definieren Sie eigene Aktionen mit individuellen Prompts, Farben und Hotkeys.
- 🧠 **KI-gestützte Operationen**:
  - Korrektur von Grammatik, Zeichensetzung und Rechtschreibung
  - Umformulierung und Verbesserung von Texten
  - Übersetzung zwischen Sprachen
  - Erklärung komplexer Begriffe oder Konzepte
  - Beantwortung von Fragen basierend auf dem Inhalt der Zwischenablage
  - Bildanalyse (mit unterstützten Modellen wie Gemini und Ollama)

## 🛠️ Installation

### Voraussetzungen
- Python 3.8 oder höher
- Läuft unter Windows und den meisten Linux-Distributionen mit X11.

### Einrichtung

1. **Klonen Sie das Repository**
   ```bash
   git clone https://github.com/Veta-one/clipgen.git
   cd clipgen
   ```
   Alternativ können Sie die neueste Version als [ZIP-Datei herunterladen](https://github.com/Veta-one/clipgen/archive/refs/heads/main.zip).

2. **Installieren Sie die Abhängigkeiten**
   ```bash
   pip install -r requirements.txt
   ```
   *Hinweis für Linux-Nutzer:* Möglicherweise müssen Sie zusätzliche Bibliotheken für `PyQt5` und `pynput` installieren (`sudo apt-get install xclip python3-pyqt5 libx11-dev`).

3. **Konfigurieren Sie ClipGen**
   - Führen Sie die Anwendung einmal aus: `python ClipGen.py`.
   - Beim ersten Start wird automatisch eine `settings.json`-Datei erstellt.
   - Öffnen Sie die Anwendung, gehen Sie zum Tab "Einstellungen" und wählen Sie Ihren KI-Anbieter.
   - Tragen Sie die erforderlichen Daten (z. B. API-Schlüssel) für den gewählten Anbieter ein. Änderungen werden automatisch gespeichert.

## 📋 Anforderungen

Die Datei `requirements.txt` enthält alle notwendigen Python-Abhängigkeiten:
```
PyQt5==5.15.9
pyperclip==1.9.0
google-generativeai==0.8.4
pywin32==310
pynput==1.8.0
Pillow==11.1.0
groq
mistralai
ollama
```
*Anmerkung: `pywin32` ist nur für Windows erforderlich und wird auf anderen Betriebssystemen ignoriert.*

## 🔥 Wie man es benutzt

1. **Starten Sie ClipGen** – Führen Sie `python ClipGen.py` aus. Die Anwendung wird in den System-Tray minimiert.
2. **Wählen Sie Inhalte aus** – Bei Text einfach markieren; bei Bildern einen Screenshot machen oder das Bild in die Zwischenablage kopieren.
3. **Verwenden Sie Hotkeys** – Drücken Sie die entsprechende Tastenkombination, um eine Aktion auszuführen (z.B. `Strg+F1` für Korrektur).
4. **Sehen Sie die Ergebnisse** – Der verarbeitete Inhalt wird automatisch wieder in die Zwischenablage kopiert und eingefügt.

## ⚙️ Anpassung & KI-Anbieter

Sie können ClipGen umfassend über den "Einstellungen"-Tab in der Anwendung anpassen.

### Allgemeine Einstellungen
- **KI-Anbieter**: Wählen Sie den aktiven KI-Dienst (`Gemini`, `Groq`, `Mistral`, `Ollama`).

### Anbieter-Einstellungen
Im entsprechenden Bereich können Sie jeden Dienst konfigurieren:
- **Gemini**:
  - `api_key`: Ihr Google AI Studio API-Schlüssel.
- **Groq**:
  - `api_key`: Ihr GroqCloud API-Schlüssel.
  - `model`: Das zu verwendende Modell (z. B. `llama3-8b-8192`).
- **Mistral**:
  - `api_key`: Ihr Mistral AI API-Schlüssel.
  - `model`: Das zu verwendende Modell (z. B. `mistral-small-latest`).
- **Ollama**:
  - `host`: Die URL Ihres lokalen Ollama-Servers (z. B. `http://localhost:11434`).
  - `model`: Der Name des lokalen Modells, das Sie verwenden möchten (z. B. `llama3`).

### Hotkeys
Passen Sie die KI-Aktionen direkt in der Oberfläche an:
- **Tastenkombination**: Klicken Sie auf das Feld und geben Sie eine neue Kombination ein.
- **Aktionsname**: Der Anzeigename in der Benutzeroberfläche.
- **Prompt**: Die Anweisung, die an die KI gesendet wird.
- **Farbe in Logs**: Die Farbe für die Darstellung im Log-Fenster der Anwendung.

## 🚀 Warum ClipGen?

ClipGen transformiert Ihren Arbeitsablauf am Computer, indem es Kontextwechsel eliminiert. Anstatt zwischen Anwendungen und Websites hin- und her zu kopieren, wählen Sie einfach Inhalte aus, drücken eine Tastenkombination und erhalten sofort das Ergebnis. Diese nahtlose Integration schafft ein neues Computererlebnis, bei dem sich die KI-Unterstützung wie eine natürliche Erweiterung Ihrer Tastatur anfühlt.

## 🔒 Datenschutz

Bei der Verwendung von Cloud-basierten Anbietern (Gemini, Groq, Mistral) werden Ihre Zwischenablage-Inhalte zur Verarbeitung an deren Server gesendet. Bei der Verwendung von **Ollama** erfolgt die gesamte Verarbeitung auf Ihrem lokalen Rechner, und es verlassen keine Daten Ihr Netzwerk. ClipGen selbst speichert oder protokolliert Ihre Daten nicht über die aktuelle Sitzung hinaus.

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

## 👨‍💻 Über den Autor

**Vitalii Kalistratov**
- Website: [vetaone.site](https://vetaone.site)
- Wenn Sie dieses Projekt unterstützen oder sich bedanken möchten:
  - USDT TRC20: `TEJw2gRrW5Z6Drowk7icjp5DhZvAEPwCYY`

## 🙏 Danksagung

- [Google Generative AI](https://github.com/google/generative-ai-python), [Groq](https://groq.com/), [Mistral AI](https://mistral.ai/) und [Ollama](https://ollama.com/) für ihre leistungsstarken APIs und Modelle.
- [PyQt5](https://riverbankcomputing.com/software/pyqt/intro) für die UI-Komponenten.
