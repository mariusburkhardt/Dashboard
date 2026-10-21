# Studien-Dashboard

Ein Python-Prototyp zur Übersicht des Studienfortschritts im Studiengang
Cyber Security. Die Architektur orientiert sich am Phase-1-Fachmodell und am
Schichtenmodell aus Phase 2.

## Funktionen

- zeigt aktuelles, geplantes und verbleibendes Semester sowie den Gesamtstatus
- berechnet bestandene ECTS, den ECTS-Fortschritt und den Notendurchschnitt
- vergleicht ECTS-Fortschritt und Notendurchschnitt mit den gesetzten Zielen
- zeigt Module, ECTS, Noten und farbige Prüfungsstatus in der Übersicht; im
  Moduldialog lassen sich Prüfungsart und Status auswählen
- speichert einen Studiengang mit Semestern, Modulen und Prüfungsleistungen in
  einer SQLite-Datenbank
- ermöglicht das Bearbeiten der Kerndaten sowie das Hinzufügen und Bearbeiten
  von Modulen einschließlich Prüfungsstatus und Note
- importiert und exportiert vollständige JSON-Sicherungen

Beim ersten Start wird eine leere Datenbank angelegt. Solange noch kein
Studiengang gespeichert ist, zeigen die Kerndaten den Hinweis
**Kerndaten anpassen**; über die gleichnamige Schaltfläche lassen sich die
erforderlichen Angaben erfassen. Module können im jeweils vorhandenen
Semester ergänzt werden. Falls noch kein Semester vorhanden ist, wird beim
ersten Modul das erste Semester ab dem Studienstart angelegt. **Importieren**
und **Exportieren** verwenden JSON-Sicherungsdateien. Ein Import ersetzt
gespeicherte Studiengangsdaten unmittelbar. Die Datenbank liegt unter
`data/study_dashboard.sqlite3`.
Zum Ausprobieren kann die Datei
[`examples/beispielstudiengang.json`](examples/beispielstudiengang.json) über
**Importieren** geladen werden.

## Architektur

| Schicht | Klasse/Modul | Zuständigkeit |
| --- | --- | --- |
| Domainklassen | `src/domain/` | Je eine Datei für Studiengang, Semester, Modul und Prüfungsleistung |
| Service | `dashboard.py` | ECTS-, Noten-, Zeit- und Zielberechnungen |
| Repository-Abstraktion | `repositories.py` | Vertrag zum Laden und Speichern eines Studiengangs |
| Repository-Implementierung | `storage.py` | SQLite-Schema und persistente Speicherung |
| DTO | `dto.py` | Typisierte, für die Anzeige vorbereitete Daten |
| Controller | `controller.py` | Verbindet Repository und Service |
| Datentransfer | `transfer.py` | Validierter Import und Export vollständiger JSON-Sicherungen |
| View | `ui.py` | Darstellung und Benutzereingaben in Tkinter |
| Application | `application.py`, `main.py` | Erzeugt und verbindet die Schichten; Programmeinstieg |

Das UML-Klassendiagramm der Gesamtarchitektur liegt in
[`docs/architecture.puml`](docs/architecture.puml).
Eine bearbeitbare draw.io-Version liegt unter
[`docs/architecture.drawio`](docs/architecture.drawio).
Die View spricht den Controller an. Dieser koordiniert Dashboard-Service,
Repository und JSON-Transfer. Nur die Application kennt die konkrete SQLite-
Implementierung und verdrahtet die Komponenten.
Das Diagramm zeigt die technische Gesamtarchitektur der Umsetzung. Es ergänzt
das sprachunabhängige Entity-Modell aus Phase 1 um Service, Controller,
Repository, DTOs, Oberfläche und Programmeinstieg.

### OOP- und Modellierungsentscheidungen

- `StudyProgram`, `Semester`, `Module` und `Assessment` sind `dataclass`-
  Fachklassen. Ein Studiengang besitzt seine Semester, ein Semester seine
  Module und ein Modul genau eine Prüfungsleistung. Die SQLite-Fremdschlüssel
  bilden diese Kompositionen mit Löschweitergabe ab.
- Ein Modul besitzt genau eine Prüfungsleistung. `AssessmentStatus` und
  `AssessmentType` sind Enums; eine bestandene Prüfung muss eine gültige Note
  haben. Getter/Setter sind für die einfachen Datenträger nicht erforderlich.
- Prüfungsarten bleiben Werte eines Enums statt Unterklassen von `Assessment`.
  Für unterschiedliche Prüfungsverhalten gibt es im Fachmodell derzeit keine
  Regel, die eine Vererbungshierarchie rechtfertigen würde.
- Mehrere Fachobjekte betreffende Berechnungen liegen im `DashboardService`.
  Der `DashboardController` hängt vom Repository-Protokoll und nicht von der
  SQLite-Implementierung ab. Damit kann die Speicherung ausgetauscht und der
  Controller mit einem Test-Repository geprüft werden. Der JSON-Transfer ist
  als Funktionsmodul umgesetzt, nicht als zusätzliche Fachklasse.

### Berechnungs- und Ampellogik

- Ein Studiensemester umfasst sechs Monate ab dem Studienstart.
- Das ECTS-Soll steigt pro abgeschlossenem Plansemester gleichmäßig bis zur
  Gesamtzahl der erforderlichen ECTS. Der jeweilige Sollwert wird auf den
  nächsten ganzen ECTS-Punkt aufgerundet.
- Modul-ECTS und die erforderliche Gesamtzahl werden als positive ganze Zahlen
  gespeichert und eingegeben.
- Erreichte ECTS zählen nur für bestandene Prüfungsleistungen.
- Der Notendurchschnitt ist das arithmetische Mittel der bestandenen
  Prüfungsleistungen. Eine bestandene Leistung benötigt eine Note zwischen
  1,0 und 4,0.
- Der Gesamtstatus ist **Im Plan**, wenn ECTS- und Notenziel erfüllt und die
  geplante Studiendauer nicht überschritten ist. Ein verfehltes Leistungsziel
  oder ein noch nicht vorhandener Notendurchschnitt führt zu
  **Aufmerksamkeit erforderlich**. Nach Überschreiten der geplanten Dauer
  lautet der Status **Geplante Studiendauer überschritten**. Dieser
  Gesamtstatus wird als einzige Text-Ampel für Zeit und ECTS angezeigt. Die
  farbigen Fortschrittsbalken zeigen weiterhin deren jeweiligen Fortschritt;
  ein separates Statusfeld pro Kennzahl gibt es nicht.

Diese Schwellen sind explizite Prototypregeln und können bei Bedarf fachlich
angepasst werden.

## Projektstruktur

```text
Dashboard/
├── .gitignore
├── agents.md
├── data/                         # SQLite-Datenbank (wird beim Start angelegt)
├── docs/
│   ├── Installationsanleitung.html
│   ├── Installationsanleitung.pdf
│   └── architecture.puml
├── examples/
│   └── beispielstudiengang.json
├── requirements.txt
├── src/
│   ├── application.py
│   ├── __init__.py
│   ├── controller.py
│   ├── dashboard.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── pruefungsleistung.py
│   │   ├── modul.py
│   │   ├── semester.py
│   │   └── studiengang.py
│   ├── dto.py
│   ├── main.py
│   ├── repositories.py
│   ├── storage.py
│   ├── transfer.py
│   └── ui.py
├── tests/
│   ├── test_dashboard.py
│   ├── test_domain.py
│   ├── test_storage.py
│   └── test_transfer.py
└── README.md
```

## Starten

Voraussetzung: Python 3.11 oder neuer mit Tkinter-Unterstützung.

```powershell
cd .\Dashboard
python -m src.main
```

Runtime-Abhängigkeiten außerhalb der Python-Standardbibliothek gibt es nicht.

Eine schrittweise Windows-Anleitung zum Klonen, Prüfen und Starten des Projekts
steht in der [Installationsanleitung (PDF)](docs/Installationsanleitung.pdf).
Die bearbeitbare [HTML-Quelle](docs/Installationsanleitung.html) liegt daneben.
Repository: <https://github.com/mariusburkhardt/Dashboard>

## Tests

```powershell
cd .\Dashboard
python -m pip install -r requirements.txt
python -m pytest -q
```
