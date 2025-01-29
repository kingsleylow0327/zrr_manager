import gspread
import os
import pandas as pd
from google.oauth2.service_account import Credentials

CREDENTIALS_FILE = os.getenv('GBOT_GOOGLE_SERVICE_ACCOUNT', 'config/services_account.json')
GBOT_GSHEET_ID = "1ss4RoFEIpXSg5PfT0YxkK-od8l3rNTLIRBcU0iCYGgk"
PROPW_EXPECTED_HEADERS = ['propw_uid','Amount']
BINGX_EXPECTED_HEADERS = ['UID','Trading Volume (USDT)']
SHEET_MAPPING = {"BINGX":2,
                 "PROPW":1}

class GSheet():
    def __init__(self, dbcon, config):
        self.dbcon = dbcon
        self.config = config

    def get_worksheet(self, sheet_id, table_number):
        client = self.init_gspread_client()
        sheet = client.open_by_key(sheet_id)
        return sheet.get_worksheet(table_number)

    def init_gspread_client(self):
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
        return gspread.authorize(credentials)

    def get_all_user(self, worksheet, target_header, header_offset=0):
        all_data = worksheet.get_all_values()
        header = all_data[header_offset]
        data = all_data[header_offset + 1:]
        df = pd.DataFrame(data, columns=header)
        df[target_header[1]] = df[target_header[1]].str.replace(',', '', regex=True)
        return df

    def df_to_tupples_propw(self, df, header):
        jiant_tupple = []
        for _, row in df.iterrows():
            small_tupple = (int(float(row[header[0]])), int(float(row[header[1]])))
            jiant_tupple.append(small_tupple)
        return jiant_tupple
    
    def df_to_tupples_bingx(self, df, header):
        df = df[header]
        jiant_tupple = []
        for _, row in df.iterrows():
            small_tupple = (int(float(row[header[0]])), int(float(row[header[1]])))
            jiant_tupple.append(small_tupple)
        return jiant_tupple

    def store_to_propw_db(self):
        worksheet = self.get_worksheet(GBOT_GSHEET_ID, SHEET_MAPPING.get("PROPW"))
        df = self.get_all_user(worksheet, PROPW_EXPECTED_HEADERS)
        tupple_data = self.df_to_tupples_propw(df, PROPW_EXPECTED_HEADERS)
        self.dbcon.update_propw_table(tupple_data)
    
    def store_to_bingx_db(self):
        worksheet = self.get_worksheet(GBOT_GSHEET_ID, SHEET_MAPPING.get("BINGX"))
        df = self.get_all_user(worksheet, BINGX_EXPECTED_HEADERS, 3)
        tupple_data = self.df_to_tupples_bingx(df, BINGX_EXPECTED_HEADERS)
        self.dbcon.update_bingx_table(tupple_data)

