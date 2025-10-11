# ClipGen

<div align="center">
   <img src="screenshots/clipgen-logo.png" alt="ClipGen Logo" width="200"/>
   <p><em>Ihr KI-gestützter Begleiter für die Zwischenablage. Sofortige Textkorrektur, Übersetzung und Bildanalyse mit Ihren bevorzugten KI-Modellen.</em></p>
</div>

## 🚀 Übersicht

ClipGen ist ein leistungsstarkes Desktop-Dienstprogramm, das die Art und Weise, wie Sie mit Texten und Bildern auf Ihrem Computer interagieren, revolutioniert. Durch die Anbindung an Ihre bevorzugten KI-Anbieter (einschließlich **Google Gemini**, **Groq**, **Mistral** und lokale **Ollama**-Modelle) führt ClipGen blitzschnelle KI-Operationen auf den Inhalten Ihrer Zwischenablage mit einfachen Tastenkombinationen durch.

**Geschwindigkeit ist unsere Priorität** – ClipGen verarbeitet Anfragen in Sekunden, sodass es sich wie ein nativer Teil Ihres Betriebssystems anfühlt und nicht wie ein externes Werkzeug.

![ClipGen in Aktion](screenshots/clipgen-demo.gif)
**[Laden Sie ClipGen hier herunter](http://vetaone.site/ClipGen/ClipGen.zip)**
*Wichtig: Vergessen Sie nicht, Ihre API-Schlüssel in der `settings.json`-Datei zu konfigurieren!*

## ✨ Funktionen

- 🔌 **Multi-API-Unterstützung**: Wählen Sie Ihren bevorzugten KI-Anbieter!
  - **Google Gemini**: Für leistungsstarke, kostenlose, multimodale Analysen.
  - **Groq**: Für blitzschnelle Textgenerierung.
  - **Mistral AI**: Für hochwertige Textmodelle.
  - **Ollama**: Um Ihre eigenen lokalen Modelle für maximale Privatsphäre und Anpassung zu verwenden.
- ⌨️ **Hotkey-gesteuerter Arbeitsablauf** – Kein Wechsel zwischen Anwendungen erforderlich.
- ⚙️ **System-Tray-Integration** – Läuft unauffällig im Hintergrund.
- 🚀 **Autostart mit Windows** – Startet ClipGen automatisch beim Hochfahren.
- 🖥️ **Globaler Hotkey zum Anzeigen/Verstecken** – Greifen Sie von überall auf das Fenster zu.
- ✏️ **Anpassbare Schriftgröße** – Passen Sie die Schriftgröße für eine bessere Lesbarkeit an.
- 🧠 **KI-gestützte Operationen**:
  - Korrektur von Grammatik, Zeichensetzung und Rechtschreibung
  - Umformulierung und Verbesserung von Texten
  - Übersetzung zwischen mehr als 140 Sprachen
  - Erklärung komplexer Begriffe oder Konzepte
  - Beantwortung von Fragen basierend auf dem Inhalt der Zwischenablage
  - Bildanalyse (mit unterstützten Modellen wie Gemini und Ollama)
  - Benutzerdefinierte Anfragen
  - Generierung humorvoller Kommentare – vollständig anpassbare Prompts, die zu Ihrem Stil passen

## 🛠️ Installation

### Voraussetzungen
- Python 3.8 oder höher
- Windows-Betriebssystem (derzeit nur für Windows)

### Einrichtung

1. **Klonen Sie das Repository**
   ```
   git clone https://github.com/Veta-one/clipgen.git
   cd clipgen
   ```

2. **Installieren Sie die Abhängigkeiten**
   ```
   pip install -r requirements.txt
   ```

3. **Konfigurieren Sie ClipGen**
   - Führen Sie die Anwendung einmal aus, um die Datei `settings.json` zu generieren.
   - Öffnen Sie `settings.json` in einem Texteditor.
   - Wählen Sie in der Einstellungs-UI Ihren gewünschten KI-Anbieter aus dem Dropdown-Menü.
   - Füllen Sie die erforderlichen Details (wie API-Schlüssel oder Modellnamen) für Ihren gewählten Anbieter aus.

### Anwendung ausführen und Autostart
Damit die Anwendung korrekt funktioniert, insbesondere die Autostart-Funktion, befolgen Sie bitte diese Schritte:

1.  **Projektordner an einen festen Ort verschieben.** Bevor Sie die Anwendung zum ersten Mal ausführen, verschieben Sie den gesamten `ClipGen`-Ordner an einen Ort, an dem er dauerhaft verbleiben soll. Gute Beispiele sind `C:\Programme\ClipGen` oder `C:\Benutzer\IhrName\Anwendungen\ClipGen`.
    > **Warnung:** Führen Sie die Anwendung nicht aus Ihrem `Downloads`-Ordner aus, wenn Sie die Autostart-Funktion verwenden möchten, da dieser Ordner möglicherweise verschoben oder geleert wird.

2.  **Anwendung ausführen**, indem Sie `ClipGen.py` von seinem neuen, festen Speicherort aus starten.

3.  **Autostart aktivieren (Optional).** Um ClipGen automatisch mit Windows zu starten:
    - Öffnen Sie das Hauptfenster (standardmäßig mit `Strg+Umschalt+C` oder durch Klicken auf das Tray-Icon).
    - Gehen Sie zum Reiter "Einstellungen".
    - Aktivieren Sie das Kontrollkästchen **"Mit Windows starten"**.

Die Anwendung registriert ihren aktuellen Pfad für den Autostart. Wenn Sie den Ordner verschieben, *nachdem* Sie diese Option aktiviert haben, kann sie nicht mehr gestartet werden. Sie müssen dann zu den Einstellungen zurückkehren, den Autostart deaktivieren und wieder aktivieren, um den Pfad zu aktualisieren.

## 📋 Anforderungen

Die Datei `requirements.txt` enthält alle notwendigen Abhängigkeiten:
```
PyQt5==5.15.9
pyperclip==1.9.0
google-generativeai==0.8.4
pywin32==310
pynput==1.8.0
Pillow==11.1.0
groq==0.9.0
mistralai==0.4.1
ollama==0.3.0
```

## 🔥 Wie man es benutzt

1. **Starten Sie ClipGen** – Führen Sie die Anwendung aus. Sie wird in den System-Tray minimiert.
2. **Fenster umschalten** – Verwenden Sie den globalen Hotkey (`Strg+Umschalt+C` standardmäßig) oder klicken Sie auf das Tray-Icon, um das Fenster anzuzeigen/zu verstecken.
3. **Wählen Sie Inhalte aus** – Bei Text einfach markieren; bei Bildern einen Screenshot machen oder das Bild in die Zwischenablage kopieren.
4. **Verwenden Sie Hotkeys** – Drücken Sie die entsprechende Tastenkombination, um eine Aktion auszuführen.
5. **Sehen Sie die Ergebnisse** – Der verarbeitete Inhalt wird automatisch wieder eingefügt.

## ⚙️ Anpassung & KI-Anbieter

Sie können ClipGen umfassend anpassen, indem Sie die Datei `settings.json` bearbeiten oder die Benutzeroberfläche verwenden.

### Allgemeine Einstellungen
- `provider`: Der aktive KI-Anbieter (`gemini`, `groq`, `mistral`, `ollama`).
- `autostart`: Setzen Sie dies auf `true`, damit ClipGen beim Windows-Start gestartet wird.
- `show_hide_hotkey`: Der globale Hotkey zum Anzeigen oder Verstecken des Anwendungsfensters.
- `font_size`: Die Schriftgröße für den Log-Textbereich.

### Anbieter-Einstellungen
Im Abschnitt `providers` können Sie jeden Dienst konfigurieren:
- **Gemini**:
  - `api_key`: Ihr Google AI Studio API-Schlüssel.
  - `model`: Das zu verwendende Modell (z. B. `gemini-1.5-flash-latest`).
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
Passen Sie die KI-Aktionen in der `hotkeys`-Liste an:
- `combination`: Die Tastenkombination.
- `name`: Anzeigename in der Benutzeroberfläche.
- `log_color`: Farbe im Anwendungsprotokoll.
- `prompt`: Die Anweisung, die an die KI gesendet wird.

## 🚀 Warum ClipGen?

ClipGen transformiert Ihren Arbeitsablauf am Computer, indem es Kontextwechsel eliminiert. Anstatt zwischen Anwendungen und Websites hin- und her zu kopieren, wählen Sie einfach Inhalte aus, drücken eine Tastenkombination und erhalten sofort das Ergebnis. Diese nahtlose Integration schafft ein neues Computererlebnis, bei dem sich die KI-Unterstützung wie eine natürliche Erweiterung Ihrer Tastatur anfühlt.

## 🔒 Datenschutz

Bei der Verwendung von Cloud-basierten Anbietern (Gemini, Groq, Mistral) werden Ihre Zwischenablage-Inhalte zur Verarbeitung an deren Server gesendet. Bei der Verwendung von **Ollama** erfolgt die gesamte Verarbeitung auf Ihrem lokalen Rechner, und es verlassen keine Daten Ihr Netzwerk. ClipGen selbst speichert oder protokolliert Ihre Daten nicht über die aktuelle Sitzung hinaus.

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert – siehe die LIZENZ-Datei für Details.

## 👨‍💻 Über den Autor

**Vitalii Kalistratov**
- Website: [vetaone.site](https://vetaone.site)
- Wenn Sie dieses Projekt unterstützen oder sich bedanken möchten:
  - USDT TRC20: `TEJw2gRrW5Z6Drowk7icjp5DhZvAEPwCYY`

## 🙏 Danksagung

- [Google Generative AI](https://github.com/google/generative-ai-python), [Groq](https://groq.com/), [Mistral AI](https://mistral.ai/) und [Ollama](https://ollama.com/) für ihre leistungsstarken APIs und Modelle.
- [PyQt5](https://riverbankcomputing.com/software/pyqt/intro) für die UI-Komponenten.