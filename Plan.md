# ClipGen Project Plan
| Status      | ID        | Aufgabe                                                                       |
|-------------|-----------|-------------------------------------------------------------------------------|
| ✅ Erledigt | DOKU:1    | `AGENTS.md` erstellen und an das Projekt anpassen.                            |
| ✅ Erledigt | DOKU:2    | `README.md` ins Deutsche übersetzen und als `README.de.md` speichern.         |
| ✅ Erledigt | FEATURE:1 | Anwendung zum Autostart von Windows hinzufügen.                               |
| ✅ Erledigt | FEATURE:2 | System-Tray-Icon mit Kontextmenü (Anzeigen/Beenden) implementieren.         |
| ✅ Erledigt | FEATURE:3 | Globale Tastenkombination zum Anzeigen/Verstecken des Fensters hinzufügen.      |
| ✅ Erledigt | FEATURE:4 | Einstellungsoption zur Änderung der Schriftgröße im Log-Bereich hinzufügen.   |

## Phase 1: Core Enhancements ( abgeschlossen)

- [x] **Intelligente, dynamische Benutzeroberfläche:** Die Benutzeroberfläche passt sich dynamisch an den ausgewählten KI-Anbieter an und zeigt nur die relevanten Einstellungsfelder. Die Schaltfläche für die Bildanalyse wird deaktiviert, wenn der Anbieter dies nicht unterstützt.

## Phase 2: Usability Improvements

- [x] **Dynamisches Neuladen der Hotkeys:** Änderungen an den Hotkeys in den Einstellungen werden sofort und ohne Neustart der Anwendung wirksam.
- [x] **Erstellung einer Standalone-Anwendung:** Eine Anleitung und möglicherweise ein Skript, um mit `auto-py-to-exe` eine `.exe`-Datei zu erstellen.
- [x] **Vollständige Cross-Platform-Kompatibilität:** Sicherstellen, dass die Anwendung auf macOS und Linux lauffähig ist.