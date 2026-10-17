# Studien-Dashboard

Ein Python-Prototyp zur Übersicht des Studienfortschritts im Studiengang
Cyber Security. Die Architektur orientiert sich am Phase-1-Fachmodell und am
Schichtenmodell aus Phase 2.

## Funktionen

- zeigt aktuelles und geplantes Semester sowie verbleibende Semester
- berechnet bestandene ECTS, den ECTS-Fortschritt und den Notendurchschnitt
- vergleicht ECTS-Fortschritt und Notendurchschnitt mit den gesetzten Zielen
- stellt Module, Prüfungsarten, Prüfungsstatus und Noten in einer Tkinter-GUI dar
- speichert einen Studiengang mit Semestern, Modulen und Prüfungsleistungen in
  einer SQLite-Datenbank

Beim ersten Start wird ein ausdrücklich als Beispiel gekennzeichneter
Cyber-Security-Studiengang angelegt. Das Dashboard ist derzeit eine
Leseansicht. Der Beispieldatensatz kann über `StudyProgramRepository.save()`
durch eigene Daten ersetzt werden; die Datenbank liegt unter
`data/study_dashboard.sqlite3`.

## Architektur

| Schicht | Klasse/Modul | Zuständigkeit |
| --- | --- | --- |
| Domain | `models.py` | Studiengang, Semester, Modul, Prüfungsleistung und Prüfungs-Enums |
| Service | `dashboard.py` | ECTS-, Noten-, Zeit- und Zielberechnungen |
| Repository-Abstraktion | `repositories.py` | Vertrag zum Laden und Speichern eines Studiengangs |
| Repository-Implementierung | `storage.py` | SQLite-Schema und persistente Speicherung |
| DTO | `dto.py` | Typisierte, für die Anzeige vorbereitete Daten |
| Controller | `controller.py` | Verbindet Repository und Service |
| View | `ui.py` | Darstellung in Tkinter, ohne Berechnungslogik |
| Application | `application.py`, `main.py` | Erzeugt und verbindet die Schichten; Programmeinstieg |

Das UML-Klassendiagramm der Gesamtarchitektur liegt in
[`docs/architecture.puml`](docs/architecture.puml).

### OOP- und Modellierungsentscheidungen

- `StudyProgram`, `Semester`, `Module` und `Assessment` sind `dataclass`-
  Fachklassen. Ihre Beziehung ist bewusst als Studiengang-Aggregation und
  Semester-/Modul-Komposition modelliert.
- Ein Modul besitzt genau eine Prüfungsleistung. `AssessmentStatus` und
  `AssessmentType` sind Enums; eine bestandene Prüfung muss eine gültige Note
  haben. Getter/Setter sind für die einfachen Datenträger nicht erforderlich.
- Prüfungsarten bleiben Werte eines Enums statt Unterklassen von `Assessment`.
  Für unterschiedliche Prüfungsverhalten gibt es im Fachmodell derzeit keine
  Regel, die eine Vererbungshierarchie rechtfertigen würde.
- Mehrere Fachobjekte betreffende Berechnungen liegen im `DashboardService`.
  Der `DashboardController` hängt vom Repository-Protokoll und nicht von der
  SQLite-Implementierung ab. Damit kann die Speicherung ausgetauscht und der
  Controller mit einem Test-Repository geprüft werden.

### Berechnungs- und Ampellogik

- Ein Studiensemester umfasst sechs Monate ab dem Studienstart.
- Das ECTS-Soll steigt pro abgeschlossenem Plansemester gleichmäßig bis zur
  Gesamtzahl der erforderlichen ECTS.
- Erreichte ECTS zählen nur für bestandene Prüfungsleistungen.
- Der Notendurchschnitt ist das arithmetische Mittel der bestandenen
  Prüfungsleistungen. Eine bestandene Leistung benötigt eine Note zwischen
  1,0 und 4,0.
- Der Gesamtstatus ist **Im Plan**, wenn ECTS- und Notenziel erfüllt und die
  geplante Studiendauer nicht überschritten ist. Ein verfehltes Leistungsziel
  oder ein noch nicht vorhandener Notendurchschnitt führt zu
  **Aufmerksamkeit erforderlich**. Nach Überschreiten der geplanten Dauer
  lautet der Status **Geplante Studiendauer überschritten**.

Diese Schwellen sind explizite Prototypregeln und können bei Bedarf fachlich
angepasst werden.

## Projektstruktur

```text
Dashboard/
├── data/                 # SQLite-Datenbank (wird beim Start angelegt)
├── docs/architecture.puml
├── src/
│   ├── application.py
│   ├── controller.py
│   ├── dashboard.py
│   ├── dto.py
│   ├── main.py
│   ├── models.py
│   ├── repositories.py
│   ├── sample_data.py
│   ├── storage.py
│   └── ui.py
├── tests/
└── requirements.txt
```

## Starten

Voraussetzung: Python 3.11 oder neuer mit Tkinter-Unterstützung.

```powershell
cd .\Dashboard
python -m src.main
```

Runtime-Abhängigkeiten außerhalb der Python-Standardbibliothek gibt es nicht.

## Tests

```powershell
cd .\Dashboard
python -m pip install -r requirements.txt
python -m pytest -q
```
