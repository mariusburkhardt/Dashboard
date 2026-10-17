# Studien-Dashboard Projekt

Dieses Projekt dokumentiert die Planung, Architektur und prototypische Umsetzung eines Studien-Dashboards in Python.

## 1. Projektziel

Das Dashboard soll einen schnellen Überblick über den Studienfortschritt geben und dabei folgende Kernziele unterstützen:

1. Abschluss in 3 Jahren
2. Durchschnittsnote 2,0
3. Erreichte ECTS / benötigte ECTS

Weitere mögliche Kennzahlen:

- Anzahl abgeschlossener Module vs. offener Module
- Status der Prüfungsleistungen (bestanden / offen / nicht bestanden)
- Prognose für verbleibende Semester
- Trend der aktuellen Durchschnittsnote

## 2. Dashboard-Inhalte

Das Dashboard soll folgende Bereiche enthalten:

- Zielübersicht: Soll-Ist-Vergleich für Abschlussdauer und Durchschnittsnote
- Fortschrittsanzeige: Prozentualer ECTS-Fortschritt
- Modulstatus: Anzahl abgeschlossener und offener Module
- Leistungsübersicht: Liste der aktuellen Module und Prüfungsleistungen
- Visualisierung: Fortschrittsbalken, Ampelsystem oder einfache Diagramme

Die Skizze sollte so gestaltet sein, dass die Ziele aus Punkt 1 sofort sichtbar sind.

## 3. UML-Modell (Konzeptionsphase)

### Kernklassen

- `Studiengang`
- `Semester`
- `Modul`
- `Pruefungsleistung`

### Beziehungen

- `Studiengang` 1..* `Semester`
- `Semester` 1..* `Modul`
- `Modul` 1..* `Pruefungsleistung`

### Objektorientierte Konzepte

- **Klasse**: Jede Entity wird als eigene Klasse modelliert.
- **Abstraktion**: Nur relevante Eigenschaften werden aufgenommen.
- **Komposition**: `Semester` besteht aus `Modul`-Objekten; `Modul` besteht aus `Pruefungsleistung`-Objekten.
- **Aggregation**: `Studiengang` fasst Semester zusammen.
- **Vererbung**: Optional im späteren Modell, z. B. `Pruefungsleistung` als Basisklasse mit spezifischen Unterklassen wie `Klausur` oder `Hausarbeit`.

### Modellentscheidungen

- `Studiengang` enthält grundlegende Ziele (Abschlussdauer, Zielnote).
- `Semester` gruppiert Module nach Studienabschnitten.
- `Modul` fasst fachliche Inhalte zusammen und besitzt ECTS, Status und Prüfungsleistungen.
- `Pruefungsleistung` speichert konkrete Ergebnisse und kann zur Berechnung des Notendurchschnitts genutzt werden.

## 4. Python-Architektur

### Empfohlene Projektstruktur

- `src/`
  - `models.py`
  - `storage.py`
  - `dashboard.py`
  - `ui.py`
  - `main.py`
- `data/`
  - `study_data.json`
- `tests/`
  - `test_models.py`
  - `test_storage.py`
- `requirements.txt`
- `README.md`

### Module und Verantwortung

- `models.py`: Datenklassen für `StudyProgram`, `Semester`, `Module` und `Assessment`.
- `storage.py`: Lesen und Schreiben von JSON-Dateien, später ggf. SQLite.
- `dashboard.py`: Berechnung der Kennzahlen wie Durchschnittsnote, ECTS-Fortschritt, Zielerreichung.
- `ui.py`: Benutzeroberfläche für die Kommandozeile; ggf. später GUI.
- `main.py`: Startpunkt der Anwendung.

### Technologievorschlag

- Python 3.11 oder 3.12
- VS Code oder PyCharm
- `PyPDF2` für PDF-Analyse (falls benötigt)
- `matplotlib` oder `plotly` für Diagramme
- `pytest` für Tests

### Speicherentscheidung

Für den Prototypen empfehlen wir:

- Speicherung in einer JSON-Datei
- späteres Upgrade auf SQLite falls erforderlich

Begründung:

- JSON ist leicht verständlich und schnell implementierbar
- gut geeignet für einen Prototypen ohne Datenbank-Overhead

### Benutzerinteraktion

- Zuerst Kommandozeile
- GUI nur optional als Erweiterung

## 5. Aktueller Stand in diesem Ordner

- `src/`: Python-Quellcode für das Dashboard-Projekt
- `data/study_data.json`: Beispiel-Daten für das Studienprogramm
- `tests/`: Unit-Tests für Modell- und Speicherlogik
- `requirements.txt`: Testabhängigkeiten
- `README.md`: Projekt- und Architektur-Dokumentation
- `Aufgabenstellung_DLBDSOOFPP01_D.pdf`: Aufgabenstellung für das Projekt

## 6. Ausführung des aktuellen Projekts

### Schritt 1: Terminal öffnen

In PowerShell:

```powershell
cd \\DS220\Repository\development\studienprojekte\Dashboard
```

### Schritt 2: Abhängigkeiten installieren

```powershell
python -m pip install -r requirements.txt
```

### Schritt 3: Dashboard starten

```powershell
python -m src.main
```

### Schritt 4: Tests ausführen

```powershell
python -m pytest -q
```

### Alternative: Notebook ausführen

Falls du die PDF-Analyse weiter bearbeiten möchtest, öffne `pdf_project_setup_fixed.ipynb` in VS Code und führe die Zellen von oben nach unten aus.

## 7. Nächste Schritte

1. Erstelle die Dashboard-Skizze und halte sie im Konzeptdokument fest.
2. Zeichne ein erstes UML-Diagramm mit den vier Kernklassen.
3. Implementiere ein kleines Python-Testprogramm für `Semester`, `Modul` und `Pruefungsleistung`.
4. Wähle die Bibliotheken und beschreibe die Gründe im Konzept.
5. Erstelle die ersten Prototypen in Python auf Basis der vorgeschlagenen Architektur.

## 8. Hinweise für die Portfolio-Phasen

### Konzeptionsphase
- Ziele definieren
- Dashboard-Skizze erstellen
- UML-Diagramm anfertigen
- Entwicklungsumgebung und Werkzeuge begründen

### Erarbeitungs-/Reflexionsphase
- Untersuchung der OOP-Konzepte in Python
- Gesamtarchitektur entwerfen
- UML-Klassendiagramm erweitern
- Reflexionsdokument schreiben

### Finalisierungsphase
- Prototyp implementieren
- Quellcode in GitHub verwalten
- Installationsanleitung erstellen
- Projektverzeichnis strukturieren
- Abstract schreiben
