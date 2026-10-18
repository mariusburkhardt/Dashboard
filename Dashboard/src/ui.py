from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path
import sqlite3
from typing import Callable
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .controller import DashboardController
from .dto import DashboardData, TargetStatus
from .domain import (
    Assessment,
    AssessmentStatus,
    AssessmentType,
    Module,
    StudyProgram,
)


class ProgressBar(tk.Canvas):
    """Zeichnet einen typisierten, farbigen Fortschrittsbalken."""

    def __init__(self, parent: tk.Widget, background: str, fill: str) -> None:
        """Initialisiert den Hintergrund und den leeren Fortschrittsbalken."""
        super().__init__(
            parent,
            height=12,
            bg=background,
            highlightthickness=0,
        )
        self.fraction = 0.0
        self.fill_color = fill
        self.create_rectangle(
            0, 0, 0, 12, fill=fill, outline="", tags="fill"
        )


class DashboardView:
    """Stellt Studienfortschritt und Modulübersicht grafisch dar."""

    _COLORS = {
        "navy": "#143B5D",
        "teal": "#168F8A",
        "light_blue": "#E8F2F7",
        "panel": "#F1F6F9",
        "border": "#D7E1E8",
        "text": "#213547",
        "muted": "#62798A",
        "green": "#2C9B73",
        "amber": "#D18B25",
        "red": "#C34D4D",
        "white": "#FFFFFF",
    }

    def __init__(self, root: tk.Tk, controller: DashboardController) -> None:
        """Initialisiert das Fenster und verbindet es mit dem Controller."""
        self._root = root
        self._controller = controller
        self._root.title("Studienfortschritt-Dashboard")
        self._root.geometry("1240x760")
        self._root.minsize(1050, 650)
        self._configure_styles()
        self._build_widgets()
        self._refresh()

    def run(self) -> None:
        """Startet die Ereignisschleife von Tkinter."""
        self._root.mainloop()

    def _configure_styles(self) -> None:
        """Legt Farben und Schriftarten der Tabellenansicht fest."""
        style = ttk.Style(self._root)
        style.theme_use("clam")
        style.configure(
            "Dashboard.Treeview",
            background=self._COLORS["white"],
            fieldbackground=self._COLORS["white"],
            foreground=self._COLORS["text"],
            rowheight=36,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Dashboard.Treeview.Heading",
            background=self._COLORS["navy"],
            foreground=self._COLORS["white"],
            font=("Segoe UI", 9, "bold"),
            padding=(8, 10),
        )
        style.map(
            "Dashboard.Treeview",
            background=[("selected", "#D5E9F2")],
            foreground=[("selected", self._COLORS["text"])],
        )

    def _build_widgets(self) -> None:
        """Erstellt Kopfbereich, Fortschrittskarten, Tabelle und Aktionen."""
        self._root.configure(bg=self._COLORS["white"])
        self._root.grid_columnconfigure(0, weight=1)
        self._root.grid_rowconfigure(1, weight=1)

        header = tk.Frame(self._root, bg=self._COLORS["white"], padx=22, pady=14)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        tk.Label(
            header,
            text="Studienfortschritt-Dashboard",
            bg=self._COLORS["white"],
            fg=self._COLORS["navy"],
            font=("Segoe UI", 20, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        self._build_profile_card(header)

        content = tk.Frame(
            self._root, bg=self._COLORS["white"], padx=22, pady=12
        )
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=11, uniform="content")
        content.grid_columnconfigure(1, weight=10, uniform="content")
        self._build_progress_panel(content)
        self._build_modules_panel(content)
        self._build_action_bar()

    def _build_profile_card(self, parent: tk.Widget) -> None:
        """Erstellt den Profil- und Studiengangsbereich."""
        card = tk.Frame(
            parent,
            bg=self._COLORS["panel"],
            highlightbackground=self._COLORS["border"],
            highlightthickness=1,
            padx=16,
            pady=12,
        )
        card.grid(row=1, column=0, columnspan=2, sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(3, weight=1)
        avatar = tk.Canvas(
            card,
            width=58,
            height=58,
            bg=self._COLORS["panel"],
            highlightthickness=0,
        )
        avatar.create_oval(
            3, 3, 55, 55, fill=self._COLORS["teal"], outline=""
        )
        self._avatar_text_id = avatar.create_text(
            29,
            29,
            text="",
            fill=self._COLORS["white"],
            font=("Segoe UI", 17, "bold"),
        )
        avatar.grid(row=0, column=0, rowspan=2, padx=(0, 14))

        self._profile_name = tk.Label(
            card,
            bg=self._COLORS["panel"],
            fg=self._COLORS["navy"],
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        self._profile_name.grid(row=0, column=1, sticky="w", pady=(2, 7))
        self._profile_program = tk.Label(
            card,
            bg=self._COLORS["panel"],
            fg=self._COLORS["text"],
            font=("Segoe UI", 10),
            anchor="w",
        )
        self._profile_program.grid(row=1, column=1, sticky="w")
        self._profile_start = tk.Label(
            card,
            bg=self._COLORS["panel"],
            fg=self._COLORS["muted"],
            font=("Segoe UI", 10),
            anchor="w",
        )
        self._profile_start.grid(row=0, column=2, sticky="w", padx=(28, 8))
        self._profile_plan = tk.Label(
            card,
            bg=self._COLORS["panel"],
            fg=self._COLORS["muted"],
            font=("Segoe UI", 10),
            anchor="w",
        )
        self._profile_plan.grid(row=1, column=2, sticky="w", padx=(28, 8))
        self._profile_goal = tk.Label(
            card,
            bg=self._COLORS["panel"],
            fg=self._COLORS["muted"],
            font=("Segoe UI", 10),
            anchor="w",
        )
        self._profile_goal.grid(row=0, column=3, sticky="w", padx=(12, 8))
        self._profile_ects = tk.Label(
            card,
            bg=self._COLORS["panel"],
            fg=self._COLORS["muted"],
            font=("Segoe UI", 10),
            anchor="w",
        )
        self._profile_ects.grid(row=1, column=3, sticky="w", padx=(12, 8))
        self._button(
            card, "Kerndaten ändern", self._open_core_data_dialog
        ).grid(row=0, column=4, rowspan=2, padx=(12, 0), sticky="e")
        self._avatar = avatar

    def _build_progress_panel(self, parent: tk.Widget) -> None:
        """Erstellt Notenziel-Ampel und Zeit-/ECTS-Fortschritt."""
        panel = self._panel(parent, "Fortschritt")
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        grade_card = tk.Frame(
            panel,
            bg=self._COLORS["white"],
            highlightbackground=self._COLORS["border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        grade_card.grid(row=1, column=0, sticky="ew", pady=(2, 12))
        grade_card.grid_columnconfigure(0, weight=1)
        tk.Label(
            grade_card,
            text="Notenziel-Ampel",
            bg=self._COLORS["white"],
            fg=self._COLORS["navy"],
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        tk.Label(
            grade_card,
            text="Aktueller Schnitt",
            bg=self._COLORS["white"],
            fg=self._COLORS["muted"],
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w")
        self._average_grade = tk.Label(
            grade_card,
            bg=self._COLORS["white"],
            fg=self._COLORS["navy"],
            font=("Segoe UI", 26, "bold"),
        )
        self._average_grade.grid(row=2, column=0, sticky="w")
        self._grade_target = tk.Label(
            grade_card,
            bg=self._COLORS["white"],
            fg=self._COLORS["muted"],
            font=("Segoe UI", 10),
        )
        self._grade_target.grid(row=3, column=0, sticky="w", pady=(4, 0))
        self._grade_badge = self._badge(grade_card)
        self._grade_badge.grid(row=2, column=1, rowspan=2, padx=10)

        progress_card = tk.Frame(
            panel,
            bg=self._COLORS["white"],
            highlightbackground=self._COLORS["border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        progress_card.grid(row=2, column=0, sticky="nsew")
        progress_card.grid_columnconfigure(0, weight=1)
        tk.Label(
            progress_card,
            text="ZEIT- / ECTS-AMPEL",
            bg=self._COLORS["white"],
            fg=self._COLORS["navy"],
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))
        self._time_label = tk.Label(
            progress_card,
            bg=self._COLORS["white"],
            fg=self._COLORS["text"],
            font=("Segoe UI", 10),
        )
        self._time_label.grid(row=1, column=0, sticky="w")
        self._time_badge = self._badge(progress_card)
        self._time_badge.grid(row=1, column=2, sticky="e")
        self._time_bar = self._progress_bar(progress_card)
        self._time_bar.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(5, 12))
        self._ects_label = tk.Label(
            progress_card,
            bg=self._COLORS["white"],
            fg=self._COLORS["text"],
            font=("Segoe UI", 10),
        )
        self._ects_label.grid(row=3, column=0, sticky="w")
        self._ects_badge = self._badge(progress_card)
        self._ects_badge.grid(row=3, column=2, sticky="e")
        self._ects_bar = self._progress_bar(progress_card)
        self._ects_bar.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(5, 0))

    def _build_modules_panel(self, parent: tk.Widget) -> None:
        """Erstellt die kompakte Modulübersicht aus der Entwurfsvorlage."""
        panel = self._panel(parent, "Modulübersicht")
        panel.grid(row=0, column=1, sticky="nsew", padx=(9, 0))
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        add_button = self._button(
            panel, "＋  Modul hinzufügen", self._open_module_dialog
        )
        add_button.grid(row=0, column=0, sticky="e", pady=(0, 8))

        table_frame = tk.Frame(
            panel,
            bg=self._COLORS["white"],
            highlightbackground=self._COLORS["border"],
            highlightthickness=1,
        )
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        columns = ("module", "ects", "grade", "status")
        self._module_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Dashboard.Treeview",
            selectmode="browse",
        )
        for column, label, width, anchor in [
            ("module", "MODULNAME", 230, tk.W),
            ("ects", "ECTS", 58, tk.CENTER),
            ("grade", "NOTE", 58, tk.CENTER),
            ("status", "STATUS", 130, tk.CENTER),
        ]:
            self._module_table.heading(column, text=label)
            self._module_table.column(
                column,
                width=width,
                minwidth=45,
                stretch=column == "module",
                anchor=anchor,
            )
        self._module_table.tag_configure(
            "passed", foreground=self._COLORS["green"]
        )
        self._module_table.tag_configure(
            "in_progress", foreground=self._COLORS["amber"]
        )
        self._module_table.tag_configure(
            "failed", foreground=self._COLORS["red"]
        )
        self._module_table.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self._module_table.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._module_table.configure(yscrollcommand=scrollbar.set)

    def _build_action_bar(self) -> None:
        """Erstellt die Aktionen zum Importieren, Exportieren und Beenden."""
        actions = tk.Frame(self._root, bg=self._COLORS["white"], padx=22, pady=12)
        actions.grid(row=2, column=0, sticky="ew")
        self._button(actions, "Importieren", self._import_data).pack(
            side=tk.RIGHT, padx=(10, 0)
        )
        self._button(actions, "Exportieren", self._export_data).pack(
            side=tk.RIGHT, padx=(10, 0)
        )
        self._button(actions, "Beenden", self._root.destroy).pack(side=tk.RIGHT)

    def _panel(self, parent: tk.Widget, title: str) -> tk.Frame:
        """Erstellt eine einheitlich gestaltete Inhaltskarte."""
        panel = tk.Frame(
            parent,
            bg=self._COLORS["panel"],
            highlightbackground=self._COLORS["border"],
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        tk.Label(
            panel,
            text=title,
            bg=self._COLORS["panel"],
            fg=self._COLORS["navy"],
            font=("Segoe UI", 15, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 9))
        return panel

    def _button(
        self, parent: tk.Widget, text: str, command: Callable[[], None]
    ) -> tk.Button:
        """Erstellt eine Schaltfläche im Stil der Entwurfsvorlage."""
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=self._COLORS["light_blue"],
            fg=self._COLORS["navy"],
            activebackground="#D4E5EF",
            activeforeground=self._COLORS["navy"],
            relief=tk.FLAT,
            borderwidth=0,
            padx=13,
            pady=8,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )

    def _badge(self, parent: tk.Widget) -> tk.Label:
        """Erstellt ein Statusfeld mit neutralem Anfangswert."""
        return tk.Label(
            parent,
            text="",
            bg=self._COLORS["border"],
            fg=self._COLORS["text"],
            padx=12,
            pady=8,
            font=("Segoe UI", 9, "bold"),
        )

    def _progress_bar(self, parent: tk.Widget) -> ProgressBar:
        """Erstellt eine leere Fortschrittsleiste."""
        bar = ProgressBar(
            parent,
            background=self._COLORS["border"],
            fill=self._COLORS["teal"],
        )
        bar.bind(
            "<Configure>",
            lambda event, progress_bar=bar: self._draw_progress_bar(
                event, progress_bar
            ),
        )
        return bar

    def _refresh(self) -> None:
        """Lädt Studiengang und Kennzahlen und aktualisiert alle Ansichten."""
        data = self._controller.load_dashboard_data()
        program = self._controller.load_study_program()
        self._display_profile(program, data)
        self._display_progress(data)
        self._display_modules(data)

    def _display_profile(
        self, program: StudyProgram, data: DashboardData
    ) -> None:
        """Zeigt Person, Studiengang und gesetzte Studienziele an."""
        self._profile_name.configure(
            text=program.student_name or "Studierende/r"
        )
        self._profile_program.configure(text=program.name)
        self._profile_start.configure(
            text=f"Studienstart   {program.start_date:%d.%m.%Y}"
        )
        self._profile_plan.configure(
            text=f"Geplante Semester   {program.planned_semesters}"
        )
        self._profile_goal.configure(
            text=f"Zielnote   ≤ {program.target_grade:.1f}"
        )
        self._profile_ects.configure(
            text=f"Anzahl ECTS   {program.required_ects:g}"
        )
        initials = "".join(
            part[0].upper()
            for part in program.student_name.split()
            if part
        )[:2]
        self._avatar.itemconfigure(self._avatar_text_id, text=initials or "S")

    def _display_progress(self, data: DashboardData) -> None:
        """Zeigt Notenschnitt, Zeitplan und ECTS-Fortschritt mit Ampeln."""
        average = (
            f"{data.average_grade:.1f}".replace(".", ",")
            if data.average_grade is not None
            else "–"
        )
        self._average_grade.configure(text=average)
        self._grade_target.configure(
            text=f"Zielnote   ≤ {data.target_grade:.1f}".replace(".", ",")
        )
        self._set_badge(self._grade_badge, data.grade_status)
        time_fraction = min(
            1.0, max(0.0, data.current_semester / data.planned_semesters)
        )
        self._time_label.configure(
            text=(
                f"Semester     {data.current_semester} von "
                f"{data.planned_semesters}"
            )
        )
        self._set_badge(self._time_badge, data.time_status)
        self._set_progress_bar(self._time_bar, time_fraction, data.time_status)
        self._ects_label.configure(
            text=(
                f"ECTS     {data.completed_ects:g} von "
                f"{data.required_ects:g}"
            )
        )
        self._set_badge(self._ects_badge, data.ects_status)
        self._set_progress_bar(
            self._ects_bar, data.progress_percentage / 100, data.ects_status
        )

    def _set_badge(
        self, badge: tk.Label, status: TargetStatus
    ) -> None:
        """Setzt Text und Ampelfarbe eines Statusfelds."""
        if status is TargetStatus.ON_TRACK:
            text, color = "Ziel erreicht", self._COLORS["green"]
        elif status is TargetStatus.BEHIND:
            text, color = "Im Rückstand", self._COLORS["red"]
        else:
            text, color = "Noch keine Daten", self._COLORS["muted"]
        badge.configure(text=text, bg=color, fg=self._COLORS["white"])

    def _set_progress_bar(
        self,
        bar: ProgressBar,
        fraction: float,
        status: TargetStatus,
    ) -> None:
        """Aktualisiert Füllstand und Farbe einer Fortschrittsleiste."""
        color = (
            self._COLORS["green"]
            if status is TargetStatus.ON_TRACK
            else self._COLORS["red"]
            if status is TargetStatus.BEHIND
            else self._COLORS["muted"]
        )
        bar.fraction = min(1.0, max(0.0, fraction))
        bar.fill_color = color
        bar.update_idletasks()
        bar.delete("fill")
        bar.create_rectangle(
            0,
            0,
            int(bar.winfo_width() * bar.fraction),
            12,
            fill=bar.fill_color,
            outline="",
            tags="fill",
        )

    def _draw_progress_bar(
        self, event: tk.Event, bar: ProgressBar
    ) -> None:
        """Zeichnet die Füllung nach einer Größenänderung neu."""
        bar.delete("fill")
        bar.create_rectangle(
            0,
            0,
            int(event.width * bar.fraction),
            12,
            fill=bar.fill_color,
            outline="",
            tags="fill",
        )

    def _display_modules(self, data: DashboardData) -> None:
        """Füllt die Tabelle mit Modulen, Noten und Prüfungsstatus."""
        self._module_table.delete(*self._module_table.get_children())
        for module in data.modules:
            status = self._module_status(module.assessment_status)
            grade = (
                f"{module.grade:.1f}".replace(".", ",")
                if module.grade is not None
                else "–"
            )
            tag = {
                "Bestanden": "passed",
                "In Bearbeitung": "in_progress",
                "Nicht bestanden": "failed",
            }.get(status, "")
            self._module_table.insert(
                "",
                tk.END,
                values=(module.module_name, f"{module.ects:g}", grade, status),
                tags=(tag,),
            )

    def _module_status(self, raw_status: str) -> str:
        """Übersetzt einen Prüfungsstatus in eine kompakte Anzeige."""
        labels = {
            AssessmentStatus.OPEN.value: "Geplant",
            AssessmentStatus.IN_PROGRESS.value: "In Bearbeitung",
            AssessmentStatus.PASSED.value: "Abgeschlossen",
            AssessmentStatus.FAILED.value: "Nicht bestanden",
        }
        return labels[raw_status]

    def _open_core_data_dialog(self) -> None:
        """Öffnet ein Formular zum Ändern der Studiengang-Kerndaten."""
        program = self._controller.load_study_program()
        fields = [
            ("Name", program.student_name),
            ("Studiengang", program.name),
            ("Studienstart (JJJJ-MM-TT)", program.start_date.isoformat()),
            ("Geplante Semester", str(program.planned_semesters)),
            ("Anzahl ECTS", str(program.required_ects)),
            ("Zielnote", str(program.target_grade)),
        ]
        dialog, entries = self._form_dialog("Kerndaten ändern", fields)

        def save() -> None:
            """Prüft und speichert die geänderten Kerndaten."""
            try:
                updated = replace(
                    program,
                    student_name=entries[0].get().strip(),
                    name=entries[1].get().strip(),
                    start_date=date.fromisoformat(entries[2].get().strip()),
                    planned_semesters=int(entries[3].get()),
                    required_ects=float(entries[4].get().replace(",", ".")),
                    target_grade=float(entries[5].get().replace(",", ".")),
                )
                self._controller.save_study_program(updated)
            except (OSError, RuntimeError, sqlite3.Error, ValueError) as error:
                messagebox.showerror(
                    "Eingabe nicht übernommen", str(error), parent=dialog
                )
                return
            dialog.destroy()
            self._refresh()

        self._form_buttons(dialog, save)

    def _open_module_dialog(self) -> None:
        """Öffnet ein Formular zum Anlegen eines Moduls."""
        program = self._controller.load_study_program()
        dialog = tk.Toplevel(self._root)
        dialog.title("Modul hinzufügen")
        dialog.configure(bg=self._COLORS["white"])
        dialog.transient(self._root)
        dialog.grab_set()
        form = tk.Frame(dialog, bg=self._COLORS["white"], padx=20, pady=16)
        form.pack(fill=tk.BOTH, expand=True)
        variables: dict[str, tk.StringVar] = {}

        def add_field(
            row: int,
            key: str,
            label: str,
            value: str = "",
            choices: tuple[str, ...] | None = None,
        ) -> None:
            """Fügt dem Moduldialog ein Eingabefeld hinzu."""
            tk.Label(
                form,
                text=label,
                bg=self._COLORS["white"],
                fg=self._COLORS["text"],
                font=("Segoe UI", 10),
            ).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=6)
            variable = tk.StringVar(value=value)
            variables[key] = variable
            if choices:
                widget: tk.Widget = ttk.Combobox(
                    form,
                    textvariable=variable,
                    values=choices,
                    state="readonly",
                    width=30,
                )
            else:
                widget = ttk.Entry(form, textvariable=variable, width=33)
            widget.grid(row=row, column=1, sticky="ew", pady=6)

        semester_numbers = tuple(
            str(semester.number) for semester in program.semesters
        ) or ("1",)
        assessment_types = tuple(
            assessment_type.value for assessment_type in AssessmentType
        )
        statuses = tuple(status.value for status in AssessmentStatus)
        add_field(0, "name", "Modulname")
        add_field(1, "semester", "Semester", semester_numbers[0], semester_numbers)
        add_field(2, "ects", "ECTS", "5")
        add_field(
            3, "assessment_type", "Prüfungsart", assessment_types[0], assessment_types
        )
        add_field(4, "status", "Status", statuses[0], statuses)
        add_field(5, "grade", "Note (nur bei bestanden)")
        form.grid_columnconfigure(1, weight=1)

        def save() -> None:
            """Validiert das Modul und speichert es im gewählten Semester."""
            try:
                status = next(
                    item
                    for item in AssessmentStatus
                    if item.value == variables["status"].get()
                )
                assessment_type = next(
                    item
                    for item in AssessmentType
                    if item.value == variables["assessment_type"].get()
                )
                grade_text = variables["grade"].get().strip()
                module = Module(
                    name=variables["name"].get().strip(),
                    ects=float(variables["ects"].get().replace(",", ".")),
                    assessment=Assessment(
                        assessment_type=assessment_type,
                        status=status,
                        grade=(
                            float(grade_text.replace(",", "."))
                            if grade_text
                            else None
                        ),
                    ),
                )
                self._controller.add_module(
                    int(variables["semester"].get()), module
                )
            except (
                OSError,
                RuntimeError,
                sqlite3.Error,
                StopIteration,
                ValueError,
            ) as error:
                messagebox.showerror(
                    "Eingabe nicht übernommen", str(error), parent=dialog
                )
                return
            dialog.destroy()
            self._refresh()

        self._form_buttons(dialog, save)

    def _form_dialog(
        self, title: str, fields: list[tuple[str, str]]
    ) -> tuple[tk.Toplevel, list[ttk.Entry]]:
        """Erstellt ein modales Eingabeformular mit beschrifteten Textfeldern."""
        dialog = tk.Toplevel(self._root)
        dialog.title(title)
        dialog.configure(bg=self._COLORS["white"])
        dialog.transient(self._root)
        dialog.grab_set()
        form = tk.Frame(dialog, bg=self._COLORS["white"], padx=20, pady=16)
        form.pack(fill=tk.BOTH, expand=True)
        entries = []
        for row, (label, value) in enumerate(fields):
            tk.Label(
                form,
                text=label,
                bg=self._COLORS["white"],
                fg=self._COLORS["text"],
                font=("Segoe UI", 10),
            ).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=6)
            entry = ttk.Entry(form, width=34)
            entry.insert(0, value)
            entry.grid(row=row, column=1, sticky="ew", pady=6)
            entries.append(entry)
        form.grid_columnconfigure(1, weight=1)
        return dialog, entries

    def _form_buttons(
        self, dialog: tk.Toplevel, save: Callable[[], None]
    ) -> None:
        """Fügt Formularaktionen zum Speichern oder Abbrechen hinzu."""
        actions = tk.Frame(dialog, bg=self._COLORS["white"], padx=20, pady=12)
        actions.pack(fill=tk.X)
        self._button(actions, "Abbrechen", dialog.destroy).pack(side=tk.RIGHT)
        self._button(actions, "Speichern", save).pack(
            side=tk.RIGHT, padx=(0, 8)
        )
        dialog.bind("<Return>", lambda _event: save())
        dialog.bind("<Escape>", lambda _event: dialog.destroy())

    def _import_data(self) -> None:
        """Importiert einen Studiengang aus einer JSON-Sicherungsdatei."""
        filename = filedialog.askopenfilename(
            parent=self._root,
            title="Dashboard-Daten importieren",
            filetypes=(("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")),
        )
        if not filename:
            return
        if not messagebox.askyesno(
            "Daten ersetzen?",
            "Beim Import werden die aktuell gespeicherten "
            "Studiengangsdaten ersetzt.",
            parent=self._root,
        ):
            return
        try:
            self._controller.import_study_program(Path(filename))
        except (OSError, RuntimeError, sqlite3.Error, ValueError) as error:
            messagebox.showerror(
                "Import fehlgeschlagen", str(error), parent=self._root
            )
            return
        self._refresh()
        messagebox.showinfo(
            "Import abgeschlossen",
            "Die Studiengangsdaten wurden importiert.",
            parent=self._root,
        )

    def _export_data(self) -> None:
        """Exportiert einen Studiengang in eine JSON-Sicherungsdatei."""
        filename = filedialog.asksaveasfilename(
            parent=self._root,
            title="Dashboard-Daten exportieren",
            defaultextension=".json",
            filetypes=(("JSON-Dateien", "*.json"),),
        )
        if not filename:
            return
        try:
            self._controller.export_study_program(Path(filename))
        except (OSError, RuntimeError, sqlite3.Error, ValueError) as error:
            messagebox.showerror(
                "Export fehlgeschlagen", str(error), parent=self._root
            )
            return
        messagebox.showinfo(
            "Export abgeschlossen",
            "Die Studiengangsdaten wurden exportiert.",
            parent=self._root,
        )
