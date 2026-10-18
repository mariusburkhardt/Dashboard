# General Development Rules

## Sprache
- Alle Kommentare und Docstrings auf Deutsch.
- Kommentare für nicht offensichtliche Logik und fachliche Entscheidungen.
- Variablen und Funktionen auf Englisch.

## Qualität
- Clean Code.
- DRY beachten.
- Keine unnötigen Bibliotheken.

## Sicherheit
- Keine Passwörter im Code.
- Secrets nur über .env.
- Eingaben validieren.

## Dokumentation
- README aktuell halten.
- Falls keine Readme im aktuellen Ordner erhalten ist, eine erstellen
- Docstrings für alle Funktionen.
- Änderungen dokumentieren.

## Python
- PEP 8
- Type Hints
- Logging statt print()
- verwende `snake_case` für Funktionen und Variablen und `PascalCase` für Klassen.
- verwende Python Standard-Bibliotheken für runtime functionality außer eine Abhängigkeit ist notwendig und Frage vorher.

## Git
- Kleine Commits
- Aussagekräftige Commit-Messages

## Tests
- Neue Funktionen nach Möglichkeit mit Unit-Tests versehen.
- Starte die relevanten Tests mit `python -m pytest -q`.