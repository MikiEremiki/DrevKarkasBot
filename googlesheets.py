from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from settings import RANGE_NAME, SPREADSHEET_ID, PATH_LIST_NAME_FOR_REPORT
from utilites import get_list_items_in_file

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def get_service_sacc(scopes):
    credentials = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=scopes)
    
    return build('sheets', 'v4', credentials=credentials)


def get_values(spreadsheet_id, range_name):
    sheet = get_service_sacc(SCOPES).spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=range_name).execute()
    return result.get('values', [])


def balance_of_accountable_funds_report():
    try:
        values = get_values(SPREADSHEET_ID['ДДС'], RANGE_NAME['ДДС'])

        if not values:
            print('No data found.')
            return

        list_name_for_report = get_list_items_in_file(PATH_LIST_NAME_FOR_REPORT)

        list_for_report = [list_name_for_report, []]
        for name in list_for_report[0]:
            list_for_report[1].append(values[1][values[0].index(name)])
        return list_for_report
    except HttpError as err:
        print(err)


def balance_of_warehouse_report():
    report = {
        'Сейчас': {
            'Доска': {}
        },
        'Прогноз': {
            'Доска': {}
        },
    }
    try:
        values = get_values(SPREADSHEET_ID['Производство'], RANGE_NAME['Производство'])

        if not values:
            print('No data found.')
            return

        column_cursor = values[1].index('Объем')
        report['Сейчас']['Дата'] = values[6][column_cursor + 1] + 'г'
        report['Прогноз']['Дата'] = values[7][column_cursor + 1] + 'г'

        report['Сейчас']['Доска']['Всего'] = values[6][column_cursor] + ' m3'
        report['Прогноз']['Доска']['Всего'] = values[7][column_cursor] + ' m3'

        list_cross_sections = ['45x90', '45x140', '45x190']
        column_cursor = values[1].index('45x90')
        for i in range(3):
            report['Сейчас']['Доска'][list_cross_sections[i]] = values[6][column_cursor + 2 + i * 3] + ' m3'
            report['Прогноз']['Доска'][list_cross_sections[i]] = values[7][column_cursor + 2 + i * 3] + ' m3'

        column_cursor = values[3].index('Цена пластин')
        report['Сейчас']['Пластины'] = f'{values[6][column_cursor]}'.replace(u'\xa0', u' ')
        report['Прогноз']['Пластины'] = f'{values[7][column_cursor]}'.replace(u'\xa0', u' ')

        return report

    except HttpError as err:
        print(err)


def get_list_of_all_names_from_sheet():
    try:
        values = get_values(SPREADSHEET_ID['ДДС'], RANGE_NAME['ДДС'])

        if not values:
            print('No data found.')
            return []

        first_index = values[0].index('ФП')
        last_index = values[0].index('Илья (Сбер)')

        return values[0][first_index:last_index + 1]
    except HttpError as err:
        print(err)
