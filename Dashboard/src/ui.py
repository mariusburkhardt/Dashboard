from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .controller import DashboardController
from .dto import DashboardData, OverallStatus


class DashboardView:
    """Render dashboard data in a read-only Tkinter window."""

    def __init__(self, root: tk.Tk, controller: DashboardController) -> None:
        self._root = root
        self._controller = controller
        self._root.title("Studien-Dashboard")
        self._root.geometry("900x620")
        self._build_widgets()

    def run(self) -> None:
        """Start the Tkinter event loop."""
        self._root.mainloop()

    def _build_widgets(self) -> None:
        """Create the summary indicators and module overview."""
        container = ttk.Frame(self._root, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        self._program_label = ttk.Label(
            container, font=("Segoe UI", 18, "bold")
        )
        self._program_label.pack(anchor=tk.W, pady=(0, 12))

        self._overall_label = ttk.Label(
            container, font=("Segoe UI", 12, "bold")
        )
        self._overall_label.pack(anchor=tk.W, pady=(0, 16))

        summary = ttk.LabelFrame(container, text="Studienziele", padding=12)
        summary.pack(fill=tk.X, pady=(0, 16))
        self._semester_label = ttk.Label(summary)
        self._semester_label.grid(row=0, column=0, sticky=tk.W, padx=8, pady=5)
        self._ects_label = ttk.Label(summary)
        self._ects_label.grid(row=1, column=0, sticky=tk.W, padx=8, pady=5)
        self._expected_ects_label = ttk.Label(summary)
        self._expected_ects_label.grid(
            row=2, column=0, sticky=tk.W, padx=8, pady=5
        )
        self._grade_label = ttk.Label(summary)
        self._grade_label.grid(row=0, column=1, sticky=tk.W, padx=24, pady=5)
        self._target_status_label = ttk.Label(summary)
        self._target_status_label.grid(
            row=1, column=1, sticky=tk.W, padx=24, pady=5
        )
        summary.columnconfigure(0, weight=1)
        summary.columnconfigure(1, weight=1)

        modules_frame = ttk.LabelFrame(
            container, text="Module und Prüfungsleistungen", padding=8
        )
        modules_frame.pack(fill=tk.BOTH, expand=True)
        columns = (
            "semester",
            "module",
            "ects",
            "assessment",
            "status",
            "grade",
        )
        self._module_table = ttk.Treeview(
            modules_frame, columns=columns, show="headings", height=12
        )
        headings = {
            "semester": "Semester",
            "module": "Modul",
            "ects": "ECTS",
            "assessment": "Prüfungsart",
            "status": "Status",
            "grade": "Note",
        }
        widths = {
            "semester": 80,
            "module": 260,
            "ects": 70,
            "assessment": 150,
            "status": 150,
            "grade": 70,
        }
        for column in columns:
            self._module_table.heading(column, text=headings[column])
            self._module_table.column(
                column,
                width=widths[column],
                anchor=tk.W if column == "module" else tk.CENTER,
            )
        scrollbar = ttk.Scrollbar(
            modules_frame, orient=tk.VERTICAL, command=self._module_table.yview
        )
        self._module_table.configure(yscrollcommand=scrollbar.set)
        self._module_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._refresh()

    def _refresh(self) -> None:
        """Load and display the latest dashboard data."""
        data = self._controller.load_dashboard_data()
        self._display_summary(data)
        self._display_modules(data)

    def _display_summary(self, data: DashboardData) -> None:
        """Update the program summary and target indicators."""
        colors = {
            OverallStatus.ON_TRACK: "#237a3b",
            OverallStatus.AT_RISK: "#a15c00",
            OverallStatus.OVERDUE: "#a32626",
        }
        self._program_label.configure(text=data.program_name)
        self._overall_label.configure(
            text=f"Gesamtstatus: {data.overall_status.value}",
            foreground=colors[data.overall_status],
        )
        self._semester_label.configure(
            text=(
                f"Semester: {data.current_semester} von "
                f"{data.planned_semesters} "
                f"({data.remaining_semesters} verbleibend) — "
                f"{data.time_status.value}"
            )
        )
        self._ects_label.configure(
            text=(
                f"ECTS: {data.completed_ects:g} / "
                f"{data.required_ects:g} "
                f"({data.progress_percentage:.1f} %) — "
                f"{data.ects_status.value}"
            )
        )
        self._expected_ects_label.configure(
            text=(
                f"ECTS-Ziel bis heute: {data.expected_ects:.1f} "
                f"(anhand des Studienzeitplans)"
            )
        )
        average_grade = (
            f"{data.average_grade:.2f}"
            if data.average_grade is not None
            else "Noch keine bestandene Prüfungsleistung"
        )
        self._grade_label.configure(
            text=f"Notendurchschnitt: {average_grade}"
        )
        self._target_status_label.configure(
            text=(
                f"Zielnote: {data.target_grade:.1f} — "
                f"{data.grade_status.value}"
            )
        )

    def _display_modules(self, data: DashboardData) -> None:
        """Replace the table contents with the current module list."""
        self._module_table.delete(*self._module_table.get_children())
        for module in data.modules:
            self._module_table.insert(
                "",
                tk.END,
                values=(
                    module.semester_number,
                    module.module_name,
                    f"{module.ects:g}",
                    module.assessment_type,
                    module.assessment_status,
                    f"{module.grade:.1f}" if module.grade is not None else "—",
                ),
            )
