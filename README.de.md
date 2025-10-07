# ClipGen

<div align="center">
   <img src="screenshots/clipgen-logo.png" alt="ClipGen Logo" width="200"/>
   <p><em>KI-gestütztes Dienstprogramm zur Erweiterung der Zwischenablage mit Hotkeys für sofortige Textkorrektur, Übersetzung, Umformulierung und Bildanalyse über die Google Gemini API.</em></p>
</div>

## 🚀 Übersicht

ClipGen ist ein leistungsstarkes Desktop-Dienstprogramm, das die Art und Weise, wie Sie mit Texten und Bildern auf Ihrem Computer interagieren, revolutioniert. Mit der Google Gemini API führt ClipGen blitzschnelle KI-Operationen auf den Inhalten Ihrer Zwischenablage mit einfachen Tastenkombinationen durch.

**Geschwindigkeit ist unsere Priorität** – ClipGen verarbeitet kurze Texte in weniger als 0,5 Sekunden und längere Texte in nur wenigen Sekunden. Dadurch fühlt es sich wie ein nativer Teil Ihres Betriebssystems an und nicht wie ein externes Werkzeug.

![ClipGen in Aktion](screenshots/clipgen-demo.gif)
**[Laden Sie ClipGen hier herunter](http://vetaone.site/ClipGen/ClipGen.zip)**
*Wichtig: Vergessen Sie nicht, den API-Schlüssel in den Konfigurationsdateien (`settings.json`) durch Ihren eigenen zu ersetzen! Sie können einen kostenlosen API-Schlüssel im [Google AI Studio](https://aistudio.google.com/u/0/apikey) erhalten.*

## 💰 Völlig KOSTENLOS!

ClipGen verwendet das Modell **models/gemini-2.0-flash-exp** von Google, das **1.000 KOSTENLOSE Anfragen pro Tag** über die Google Gemini API beinhaltet! Das bedeutet:

- ✅ **Keine Abonnementgebühren**
- ✅ **Keine Nutzungsgebühren**
- ✅ **Keine Kreditkarte erforderlich**
- ✅ **Leistungsstarke KI völlig kostenlos**

Mit 1.000 täglichen Anfragen können Sie Hunderte von Texten verarbeiten und Informationen aus Bildern extrahieren, ohne einen Cent zu bezahlen. Das Modell bietet eine hervorragende Balance zwischen Intelligenz und Geschwindigkeit und ermöglicht alle leistungsstarken Funktionen von ClipGen zum Nulltarif.

## ✨ Funktionen

- 🆓 **Völlig kostenlos** – 1.000 Anfragen pro Tag ohne Kosten
- 🔄 **Ultraschnelle Verarbeitung** – Ergebnisse für kurze Texte in Millisekunden und für längere Texte in Sekunden
- ⌨️ **Hotkey-gesteuerter Arbeitsablauf** – Kein Wechsel zwischen Anwendungen erforderlich
- 🧠 **KI-gestützte Operationen**:
  - Korrektur von Grammatik, Zeichensetzung und Rechtschreibung
  - Umformulierung und Verbesserung von Texten
  - Übersetzung zwischen mehr als 140 Sprachen
  - Erklärung komplexer Begriffe oder Konzepte
  - Beantwortung von Fragen basierend auf dem Inhalt der Zwischenablage
  - Bildanalyse, Textextraktion und Erklärung
  - Benutzerdefinierte Anfragen
  - Generierung humorvoller Kommentare – vollständig anpassbare Prompts, die zu Ihrem Stil passen

## 📸 Screenshots

### Hauptoberfläche
![Hauptoberfläche](screenshots/main-interface.png)

### Beispiel für Grammatikkorrektur
![Grammatikkorrektur](screenshots/correction-example.png)

### Beispiel für Bildanalyse
![Bildanalyse](screenshots/image-analysis.png)

## 🛠️ Installation

### Voraussetzungen
- Python 3.8 oder höher
- Windows-Betriebssystem (derzeit nur für Windows)
- Google Gemini API-Schlüssel (kostenlos erhältlich)

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

3. **Holen Sie sich einen KOSTENLOSEN Google Gemini API-Schlüssel**
   - Besuchen Sie direkt das [Google AI Studio](https://aistudio.google.com/u/0/apikey)
   - Erstellen Sie einen neuen API-Schlüssel (keine Kreditkarte erforderlich)
   - Kopieren Sie Ihren API-Schlüssel
   - Mit diesem Schlüssel erhalten Sie 1.000 kostenlose Anfragen pro Tag!

4. **Konfigurieren Sie ClipGen**
   - Öffnen Sie `settings.json` in einem Texteditor.
   - Ersetzen Sie den Platzhalter-API-Schlüssel durch Ihren eigenen:
     ```json
     {
         "api_key": "YOUR_API_KEY_HERE",
         "hotkeys": [
             ...
         ]
     }
     ```

5. **Führen Sie die Anwendung aus**
   ```
   python ClipGen.py
   ```

## 📋 Anforderungen

Erstellen Sie eine Datei namens `requirements.txt` mit folgendem Inhalt:

```
pillow
pyperclip
google-generativeai
pywin32
pynput
PyQt5
```

## 🔥 Wie man es benutzt

1. **Starten Sie ClipGen** – Führen Sie die Anwendung aus, um sie im Hintergrund bereitzuhalten.
2. **Wählen Sie Inhalte aus** – Bei Text einfach markieren (kein Kopieren nötig); bei Bildern einen Screenshot machen oder das Bild in die Zwischenablage kopieren.
3. **Verwenden Sie Hotkeys** – Drücken Sie die entsprechende Tastenkombination, um eine Aktion auszuführen.
4. **Sehen Sie die Ergebnisse** – Der verarbeitete Inhalt wird automatisch wieder eingefügt.

### Hotkey-Referenz

| Hotkey  | Funktion          | Beschreibung                                    |
|---------|-------------------|-------------------------------------------------|
| Strg+F1 | Korrektur         | Korrigiert Grammatik, Zeichensetzung und Rechtschreibung |
| Strg+F2 | Umschreiben       | Verbessert die Klarheit und Lesbarkeit von Texten |
| Strg+F3 | Übersetzung       | Übersetzt Text zwischen über 140 Sprachen      |
| Strg+F6 | Erklärung         | Erklärt komplexe Konzepte in einfachen Worten   |
| Strg+F7 | Antwort           | Beantwortet Fragen in der Zwischenablage        |
| Strg+F8 | Eigene Anfrage    | Führt die angegebene Aufgabe aus                |
| Strg+F9 | Kommentar         | Generiert humorvolle Kommentare                 |
| Strg+F10| Bildanalyse       | Analysiert Bilder, extrahiert Text und erklärt Inhalte |

## 💡 Anwendungsfälle

- **Autoren/Redakteure**: Sätze sofort verbessern, ohne zu Grammatik-Tools zu wechseln.
- **Mehrsprachige Kommunikation**: Nachrichten schnell zwischen beliebigen Sprachen übersetzen.
- **Studenten**: Erklärungen für komplexe Begriffe oder Konzepte erhalten.
- **Entwickler**: Fehlermeldungen bereinigen oder Text aus Screenshots extrahieren.
- **Soziale Medien**: Memes oder Bilder verstehen, wenn der Kontext unklar ist.
- **Alltäglicher Gebrauch**: Tippfehler in jedem Textfeld in allen Anwendungen korrigieren.

## ⚙️ Anpassung

Sie können ClipGen umfassend anpassen, indem Sie die Konfigurationsdatei `settings.json` bearbeiten:

```json
{
    "api_key": "DEIN_API_SCHLÜSSEL",
    "hotkeys": [
        {
            "combination": "Ctrl+F1",
            "name": "Korrektur",
            "log_color": "#FFFFFF",
            "prompt": "Bitte korrigiere den folgenden Text..."
        },
        ...
    ]
}
```

Jeder Aspekt kann angepasst werden:
- `combination`: Die Tastenkombination
- `name`: Anzeigename in der Benutzeroberfläche
- `log_color`: Farbe im Anwendungsprotokoll
- `prompt`: Die Anweisung, die an Gemini AI gesendet wird

## 🚀 Warum ClipGen?

ClipGen transformiert Ihren Arbeitsablauf am Computer, indem es Kontextwechsel eliminiert. Anstatt:

1. Text in einer Anwendung zu schreiben
2. Ein Grammatik-Tool oder einen Übersetzer in einem anderen Fenster zu öffnen
3. Text in das neue Tool zu kopieren
4. Auf die Verarbeitung zu warten
5. Das Ergebnis zu kopieren
6. Zurück zu Ihrer ursprünglichen Anwendung zu wechseln
7. Das Ergebnis einzufügen

Mit ClipGen wird der Prozess zu:
1. Text in einer beliebigen Anwendung schreiben
2. Eine Tastenkombination drücken
3. Mit dem korrigierten Text weiterarbeiten

Diese nahtlose Integration schafft ein neues Computererlebnis, bei dem sich die KI-Unterstützung wie eine natürliche Erweiterung Ihrer Tastatur anfühlt.

## 🧠 Über das KI-Modell

ClipGen verwendet das leistungsstarke Modell **models/gemini-2.0-flash-exp** von Google, das Folgendes bietet:

- **Schnelle Antwortzeiten** – Perfekt für die Echtzeit-Textverarbeitung
- **Hohe Genauigkeit** – Hervorragende Ergebnisse für Grammatik-, Übersetzungs- und Analyseaufgaben
- **Multimodale Fähigkeiten** – Analysiert mühelos sowohl Text als auch Bilder
- **1.000 kostenlose API-Aufrufe täglich** – Mehr als genug für den persönlichen und beruflichen Gebrauch

## 🔒 Datenschutz

ClipGen verarbeitet Text lokal und sendet Inhalte nur dann an die Google Gemini API, wenn eine Tastenkombination gedrückt wird. Es werden keine Daten über die aktuelle Sitzung hinaus gespeichert oder protokolliert.

## 📅 Geplant
- Unterstützung für macOS und Linux hinzufügen.
- Funktionalität erweitern, um mit anderen APIs zu arbeiten.
- Verbesserung der Benutzeroberfläche und Hinzufügen von Hotkey-Einstellungen.

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert – siehe die LIZENZ-Datei für Details.

## 👨‍💻 Über den Autor

**Vitalii Kalistratov**
- Website: [vetaone.site](https://vetaone.site)
- Wenn Sie dieses Projekt unterstützen oder sich bedanken möchten:
  - USDT TRC20: `TEJw2gRrW5Z6Drowk7icjp5DhZvAEPwCYY`

## 🙏 Danksagung

- [Google Generative AI](https://github.com/google/generative-ai-python) für die Gemini API und den kostenlosen Zugang
- [PyQt5](https://riverbankcomputing.com/software/pyqt/intro) für die UI-Komponenten