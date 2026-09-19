"""
Exportación de cuadrantes a formatos de archivo (Excel y HTML).
"""
from __future__ import annotations

from pathlib import Path
from src.domain.constants import DAY_NAMES, DAYS, PERIOD_HOURS, PERIODS
from src.domain.entities import AssignmentReport, Teacher


def export_to_excel(report: AssignmentReport, teachers: list[Teacher], output_path: str | Path) -> None:
    try:
        import openpyxl
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    except ImportError:
        raise ImportError("Instala openpyxl para exportar a Excel: pip install openpyxl")

    wb = openpyxl.Workbook()
    ws_grid = wb.active
    ws_grid.title = "Cuadrante Semanal"
    ws_grid.views.sheetView[0].showGridLines = True

    t_name_by_id = {t.id: t.name for t in teachers}
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    hour_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    hour_font = Font(name="Calibri", size=10, bold=True)
    alert_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    thin_border = Border(
        left=Side(style="thin", color="BFBFBF"),
        right=Side(style="thin", color="BFBFBF"),
        top=Side(style="thin", color="BFBFBF"),
        bottom=Side(style="thin", color="BFBFBF"),
    )

    ws_grid.cell(row=1, column=1, value="HORA / PERIODO").fill = header_fill
    ws_grid.cell(row=1, column=1).font = header_font
    ws_grid.cell(row=1, column=1).alignment = Alignment(horizontal="center", vertical="center")

    for col_idx, d_name in enumerate(DAY_NAMES, start=2):
        cell = ws_grid.cell(row=1, column=col_idx, value=d_name.upper())
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    assign_map = {(a.slot.day, a.slot.period): a for a in report.assignments if a.slot.week == 0}

    for p in range(PERIODS):
        row_idx = p + 2
        ws_grid.row_dimensions[row_idx].height = 45

        hour_cell = ws_grid.cell(row=row_idx, column=1, value=f"P{p}\n{PERIOD_HOURS[p]}")
        hour_cell.fill = hour_fill
        hour_cell.font = hour_font
        hour_cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        hour_cell.border = thin_border

        for d in range(DAYS):
            col_idx = d + 2
            cell = ws_grid.cell(row=row_idx, column=col_idx)
            assignment = assign_map.get((d, p))

            if assignment and assignment.assigned_teachers:
                names = [t_name_by_id.get(t_id, t_id) for t_id in assignment.assigned_teachers]
                cell.value = "\n".join(f"• {n}" for n in names)
            else:
                cell.value = "⚠️ SIN CUBRIR"

            if assignment and assignment.deficit > 0:
                cell.fill = alert_fill
                cell.font = Font(name="Calibri", color="C00000", bold=True)
            else:
                cell.font = Font(name="Calibri", size=10)

            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            cell.border = thin_border

    ws_grid.column_dimensions["A"].width = 18
    for col_letter in ["B", "C", "D", "E", "F"]:
        ws_grid.column_dimensions[col_letter].width = 30

    wb.save(output_path)


