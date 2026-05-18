from openpyxl import Workbook
from openpyxl.styles import Font
from django.http import HttpResponse


def export_to_excel(*, filename: str, title: str, headers: list[str], rows: list[list]) -> HttpResponse:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = title[:31]
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for row in rows:
        sheet.append(row)
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    workbook.save(response)
    return response
