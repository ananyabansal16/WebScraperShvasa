import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def init_google_sheets(credentials_json_path=None):
    if credentials_json_path is None:
        credentials_json_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
    if not credentials_json_path:
        raise ValueError("Please set the GOOGLE_SHEETS_CREDENTIALS_JSON environment variable in .env file.")
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_json_path, scope)
    client = gspread.authorize(credentials)
    return client

def insert_questions_into_google_sheets(client, questions, keyword, website, spreadsheet_name='questions'):
    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(spreadsheet_name)
        spreadsheet.share(client.auth.service_account_email, perm_type='user', role='writer')

    worksheet = spreadsheet.sheet1
    rows = worksheet.get_all_values()
    next_row = len(rows) + 1 if rows else 2

    header = ["Website", "Keyword", "Title", "Link", "Description", "Date Published", "Answer", "Is answered?"]
    if next_row == 2:
        worksheet.update('A1:H1', [header])

    data = []
    for question in questions:
        # answer = get_answer_from_openai(question["title"])
        date_published = question["date_published"].strftime('%Y-%m-%d') if question["date_published"] else ''
        data.append([website, keyword, question["title"], question["link"], question["description"], date_published, '', 'False'])

    range_start = f'A{next_row}'
    range_end = f'H{next_row + len(data) - 1}'
    range_all = f'{range_start}:{range_end}'
    worksheet.update(range_all, data)
