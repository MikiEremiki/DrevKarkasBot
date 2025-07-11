import logging

from gspread_asyncio import AsyncioGspreadClientManager, AsyncioGspreadClient
from google.oauth2.service_account import Credentials

from settings import RANGE_NAME, SPREADSHEET_ID, PATH_LIST_NAME_FOR_REPORT
from utilites import get_list_items_in_file

googlesheets_logger = logging.getLogger('bot.googlesheets')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
dk_ferm_sheet = 'https://docs.google.com/spreadsheets/d/1u9qAK8YZctW0_TFbQFfh4EPFH7FqMRwsxZkwnRwAvqY'


def get_creds():
    creds = Credentials.from_service_account_file('credentials.json')
    scoped = creds.with_scopes(SCOPES)
    return scoped


agcm = AsyncioGspreadClientManager(get_creds)


async def balance_of_accountable_funds_report():
    agc: AsyncioGspreadClient = await agcm.authorize()
    ss = await agc.open_by_url(SPREADSHEET_ID['ДДС'])
    values = await ss.values_get(RANGE_NAME['ДДС'])
    values = values['values']

    if not values:
        print('No data found.')
        return
    first_index = values[0].index('ФП')

    list_id_for_report = get_list_items_in_file(PATH_LIST_NAME_FOR_REPORT)

    list_for_report = [[], []]
    for index in list_id_for_report:
        list_for_report[0].append(values[0][int(index)+first_index])
        list_for_report[1].append(values[1][int(index)+first_index])
    return list_for_report


async def balance_of_warehouse_report():
    report = {
        'Сейчас': {
            'Доска': {},
            'Пластины': ''
        },
        'Прогноз': {
            'Доска': {},
            'Пластины': ''
        },
    }

    agc: AsyncioGspreadClient = await agcm.authorize()
    ss = await agc.open_by_url(SPREADSHEET_ID['Производство'])
    values = await ss.values_get(RANGE_NAME['Производство'])
    values = values['values']

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
        report['Сейчас']['Доска'][list_cross_sections[i]] = values[6][
                                                                column_cursor + 2 + i * 3] + ' m3'
        report['Прогноз']['Доска'][list_cross_sections[i]] = values[7][
                                                                 column_cursor + 2 + i * 3] + ' m3'

    column_cursor = values[3].index('Цена пластин')
    report['Сейчас']['Пластины'] = (
        f'{values[6][column_cursor]}'.replace(u'\xa0', u' ')
    )
    report['Прогноз']['Пластины'] = (
        f'{values[7][column_cursor]}'.replace(u'\xa0', u' ')
    )

    return report


async def get_list_of_all_names_from_sheet():
    agc: AsyncioGspreadClient = await agcm.authorize()
    ss = await agc.open_by_url(SPREADSHEET_ID['ДДС'])
    values = await ss.values_get(RANGE_NAME['ДДС'])
    values = values['values']

    if not values:
        print('No data found.')
        return

    first_index = values[0].index('ФП')
    last_index = values[0].index('Илья (Сбер)')

    return values[0][first_index:last_index + 1]


async def write_time_stamp(
        datetime,
        type_timestamp,
        full_name,
        chat_id,
        delta_time='00:00',
):
    agc: AsyncioGspreadClient = await agcm.authorize()
    ss = await agc.open_by_url(SPREADSHEET_ID['Отчет'])
    values_column = await ss.values_get(RANGE_NAME['Ответы на форму_A'])
    values_column = values_column['values']

    if not values_column:
        print('No data found.')
        return

    row = len(values_column) + 1
    value_input_option = 'USER_ENTERED'
    response_value_render_option = 'FORMATTED_VALUE'
    values = [
        [datetime, type_timestamp, full_name, delta_time, chat_id],
    ]
    value_range_body = {
        'values': values,
    }
    range_sheet = f'{RANGE_NAME["Ответы на форму"]}A{row}:E{row}'

    response = await ss.values_update(
        range=range_sheet,
        params={
            'valueInputOption': value_input_option,
            'responseValueRenderOption': response_value_render_option
        },
        body=value_range_body
    )

    googlesheets_logger.info(": ".join(
        [
            'spreadsheetId: ',
            response['spreadsheetId'],
            '\n'
            'updatedRange: ',
            response['updatedRange']
        ]
    ))


if __name__ == '__main__':
    write_time_stamp('21.08.2023 21:31:00',
                     'Приход',
                     'Еремин Михаил',
                     454342281)
