import gspread
import os
import pandas as pd
from google.oauth2.service_account import Credentials

CREDENTIALS_FILE = os.getenv('GBOT_GOOGLE_SERVICE_ACCOUNT', 'config/services_account.json')
GBOT_GSHEET_ID = "1ss4RoFEIpXSg5PfT0YxkK-od8l3rNTLIRBcU0iCYGgk"
EXPECTED_HEADERS = ['propw_uid','Amount']

class GSheet():
    def __init__(self, dbcon, config):
        self.dbcon = dbcon
        self.config = config

    def get_worksheet(self, sheet_id):
        client = self.init_gspread_client()
        sheet = client.open_by_key(sheet_id)
        return sheet.get_worksheet(1)

    def init_gspread_client(self):
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
        return gspread.authorize(credentials)

    def get_all_user(self, worksheet):
        records = worksheet.get_all_records(expected_headers=EXPECTED_HEADERS)
        df = pd.DataFrame(records)
        return df

    def df_to_tupples(self, df):
        jiant_tupple = []
        for _, row in df.iterrows():
            small_tupple = (int(row[EXPECTED_HEADERS[0]]), int(row[EXPECTED_HEADERS[1]]))
            jiant_tupple.append(small_tupple)
        return jiant_tupple

    def store_to_db(self):
        worksheet = self.get_worksheet(GBOT_GSHEET_ID)
        df = self.get_all_user(worksheet)
        tupple_data = self.df_to_tupples(df)
        self.dbcon.update_propw_table(tupple_data)