from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from settings import LIST_NAME_FOR_REPORT, RANGE_NAME, SPREADSHEET_ID

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def get_service_sacc(scopes):
    credentials = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES)
    
    return build('sheets', 'v4', credentials=credentials)


def balance_report():
    try:
        # Call the Sheets API
        sheet = get_service_sacc(SCOPES).spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return
        list_for_report = [LIST_NAME_FOR_REPORT, []]
        for name in list_for_report[0]:
            list_for_report[1].append(values[1][values[0].index(name)])
        return list_for_report
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    balance_report()
