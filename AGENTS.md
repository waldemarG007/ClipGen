# Regeln für die Zusammenarbeit mit dem KI-Agenten

Dieses Dokument definiert die grundlegenden Regeln, Arbeitsweisen und Standards für die Zusammenarbeit mit einem KI-Agenten in diesem Projekt.

## 1. Allgemeine Prinzipien

- **Kritischer Freund:** Der Agent agiert als "kritischer Freund". Er würdigt gute Ideen, zeigt aber auch konstruktiv potenzielle Herausforderungen, technische Auswirkungen und Alternativen auf.
- **Klarheit bei Unsicherheit:** Wenn der Agent sich bei einer Aussage unsicher ist oder keine verlässlichen Informationen hat, kommuniziert er dies klar (z.B. mit "Ich weiß es nicht") und stellt Rückfragen.
- **Sprache:** Die primäre Kommunikationssprache in diesem Projekt ist Deutsch.

## 2. Sicherheit

- **Keine sensiblen Daten im Repository:** Es dürfen unter keinen Umständen sensible Daten wie API-Schlüssel in das Git-Repository committet werden.
- **Konfigurationsdateien nutzen:** Alle sensiblen Daten werden ausschließlich über eine lokale Konfigurationsdatei (`settings.json`) geladen.
- **`.gitignore` verwenden:** Die lokale Konfigurationsdatei (`settings.json`) muss in der `.gitignore`-Datei aufgeführt sein, um ein versehentliches Committen zu verhindern.
- **Vorlagen-Datei:** Eine Vorlagen-Datei (`settings.example.json`) sollte im Repository vorhanden sein, um die benötigten Variablen zu dokumentieren.

## 3. Code-Qualität und Stil

- **Lesbarkeit:** Der Code sollte sauber, gut strukturiert und verständlich sein. Zu jeder angelegten Datei wird oben eine kurze Zusammenfassung hinzugefügt, was die Datei beinhaltet und die Funktionen erklärt. Dieses soll auch aktualisiert werden, wenn sich die Funktionalität ändert.
- **PEP 8:** Für Python-Projekte ist der PEP 8-Styleguide zu befolgen.
- **Sinnvolle Kommentare:** Komplexe Logik, wichtige Design-Entscheidungen oder unoffensichtliche Code-Abschnitte sollten kommentiert werden. Es sollte darauf geachtet werden, dass die Kommentare aktuell und ausführlich genug sind, damit andere Entwickler den Code verstehen können.
- **Deskriptive Namen:** Variablen, Funktionen und Klassen erhalten klare und aussagekräftige Namen.
- **Keine temporären Dateien:** Temporäre Test- oder Debug-Dateien (z.B. `test.py`, `temp_*.py`) müssen vor einem Commit gelöscht werden.
- **Code-Review:** Jeder Code-Commit wird vom Agenten überprüft, bevor er in das Repository committet wird.
- **Code-Formatierung:** Der Code wird automatisch formatiert, um eine konsistente Darstellung zu gewährleisten.
- **Code-Tests:** Jeder Code-Commit wird mit Tests überprüft, um sicherzustellen, dass keine Regressionen aufgetreten sind.
- **Code-Refactoring:** Der Agent kann Code-Refactoring vornehmen, um den Code zu verbessern und zu optimieren.

## 4. Abhängigkeitsmanagement

- **Anforderungen definieren:** Alle Projekt-Abhängigkeiten müssen in einer `requirements.txt`-Datei deklariert sein. Die Anforderungsdatei sollte regelmäßig aktualisiert werden.
- **Virtuelle Umgebung:** Die Entwicklung und Ausführung des Projekts sollte innerhalb einer virtuellen Umgebung stattfinden, um Konflikte zu vermeiden.

## 5. Testen

- **Tests ausführen:** Vor dem Einreichen von Änderungen müssen alle vorhandenen Tests ausgeführt werden, um Regressionen zu vermeiden.
- **Neue Tests schreiben:** Für neue Funktionen sollten nach Möglichkeit auch neue Tests erstellt werden, um die Korrektheit zu gewährleisten.
- **Manuelles Testen:** Falls keine automatisierten Tests vorhanden sind, müssen Änderungen manuell durch Ausführen der Anwendung überprüft werden.

## 6. Arbeitsweise und Commits

- **Branches:** Änderungen werden in separaten Feature-Branches entwickelt, nicht direkt im `main`-Branch.
- **Eigenständige Commits:** Der Agent darf abgeschlossene Aufgaben eigenständig committen und hochladen, ohne auf eine explizite Aufforderung zu warten.

## 7. Projektspezifische Anweisungen

- Der Haupteinstiegspunkt der Anwendung ist `ClipGen.py`.
- Die UI-Logik (View) befindet sich in `libs/ClipGen_view.py`.
- Die Konfiguration, einschließlich des API-Schlüssels und der Hotkeys, wird in `settings.json` gespeichert.
- Das Projekt ist eine Desktop-Anwendung, die mit PyQt5 erstellt wurde.