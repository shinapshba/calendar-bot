import uuid
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, PatternFill

from integration.dto import Week, Month, Quarter, Year


def _build_days_sheet(wb, days):
    ws_days = wb.create_sheet('Дни')
    ws_days.append(['Дата', 'День недели', 'Тип дня', 'Рабочие часы', 'Описание'])
    for cell in ws_days[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
        cell.fill = PatternFill(start_color='DDDDDD', end_color='DDDDDD', fill_type='solid')
    for day in days:
        ws_days.append([day.date, day.weekday, day.work_type, day.work_hours, day.title])
    return ws_days


def _adjust_width(ws):
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:  # noqa
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width


def _create_file(statistics, days, result_name):
    wb = openpyxl.Workbook()
    default_sheet = wb.active
    wb.remove(default_sheet)
    ws_statistics = wb.create_sheet('Статистика')
    ws_days = _build_days_sheet(wb, days)
    ws_statistics.append([statistics])
    for row in ws_statistics['A']:
        row.alignment = Alignment(wrap_text=True)
    _adjust_width(ws_statistics)
    _adjust_width(ws_days)
    result_name = result_name + '-' + str(uuid.uuid4()) + '.xlsx'
    wb.save(result_name)
    return result_name


def create_file_week(week: Week):
    statistics = f'{week.title}\n\nС {week.start_date} по {week.end_date}\n\nРабочие часы: {week.work_hours}\n'
    return _create_file(statistics, week.days, './tmp/production-calendar-week')


def create_file_month(month: Month):
    statistics = (f'Месяц\n\n'
                  f'С {month.start_date} по {month.end_date}\n\n'
                  f'Рабочие часы: {month.work_hours}\n\n'
                  f'Рабочие дни: {month.work_days}\n\n'
                  f'Выходные: {month.weekends}\n\n'
                  f'Праздники: {month.holidays}\n')
    return _create_file(statistics, month.days, './tmp/production-calendar-month')


def create_file_quarter(quarter: Quarter):
    statistics = (f'Квартал\n\n'
                  f'С {quarter.start_date} по {quarter.end_date}\n\n'
                  f'Рабочие часы: {quarter.work_hours}\n\n'
                  f'Рабочие дни: {quarter.work_days}\n\n'
                  f'Выходные: {quarter.weekends}\n\n'
                  f'Праздники: {quarter.holidays}\n')
    return _create_file(statistics, quarter.days, './tmp/production-calendar-quarter')


def create_file_year(year: Year):
    statistics = (f'Квартал\n\n'
                  f'С {year.start_date} по {year.end_date}\n\n'
                  f'Рабочие часы: {year.work_hours}\n\n'
                  f'Рабочие дни: {year.work_days}\n\n'
                  f'Выходные: {year.weekends}\n\n'
                  f'Праздники: {year.holidays}\n')
    return _create_file(statistics, year.days, './tmp/production-calendar-year')
