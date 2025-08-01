import gspread
import os
import pandas as pd
from google.oauth2.service_account import Credentials

CREDENTIALS_FILE = os.getenv('GBOT_GOOGLE_SERVICE_ACCOUNT', 'config/services_account.json')
GBOT_GSHEET_ID = "1ss4RoFEIpXSg5PfT0YxkK-od8l3rNTLIRBcU0iCYGgk"
PROPW_EXPECTED_HEADERS = ['propw_uid','Amount']
BITGET_EXPECTED_HEADERS = ['UID','Trading Volume (USDT)']
PIONEX_EXPECTED_HEADERS = ['purchase_date', 'uid','Amount']
VIP_EXPECTED_HEADERS = ['VIP Level', 'Discord Id']
WHITELIST_EXPECTED_HEADERS = ['Discord Id']
SHEET_MAPPING = {"VIP":0,
                 "WHITE_LIST":1}
MIN_TRADE_VOLUME = 300000
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
    
    def df_to_tupples_bingx(self, df, header):
        df = df[header]
        jiant_tupple = []
        for _, row in df.iterrows():
            if (row[header[0]] == ''):
                break
            small_tupple = (int(float(row[header[0]])), int(float(row[header[1]])), row[header[2]])
            jiant_tupple.append(small_tupple)
        return jiant_tupple
    
    def df_to_json_vip(self, df, header):
        df = df[header]
        json_ret = []
        for _, row in df.iterrows():
            if (row[header[0]] == ''):
                break
            small_json = { 
                header[0]: row[header[0]],
                header[1]: row[header[1]]
            }
            json_ret.append(small_json)
        return json_ret
    
    def df_to_json_whitelist(self, df, header):
        df = df[header]
        json_ret = []
        for _, row in df.iterrows():
            if (row[header[0]] == ''):
                break
            small_json = { 
                header[0]: row[header[0]]
            }
            json_ret.append(small_json)
        return json_ret
    
    def df_to_tupples_bitget(self, df, header):
        jiant_tupple = []
        for _, row in df.iterrows():
            if (row[header[0]] == ''):
                break
            small_tupple = (row[header[0]], int(float(row[header[1]] if row[header[1]].strip() != '' else 0)))
            jiant_tupple.append(small_tupple)
        return jiant_tupple
    
    def df_to_tupples_pionex(self, df, header):
        jiant_tupple = []
        for _, row in df.iterrows():
            if (row[header[1]] == ''):
                break
            small_tupple = (int(float(row[header[1]])), int(float(row[header[2]])))
            jiant_tupple.append(small_tupple)
        return jiant_tupple

    def store_to_propw_db(self):
        worksheet = self.get_worksheet(GBOT_GSHEET_ID, SHEET_MAPPING.get("PROPW"))
        df = self.get_all_user(worksheet, PROPW_EXPECTED_HEADERS)
        tupple_data = self.df_to_tupples_propw(df, PROPW_EXPECTED_HEADERS)
        self.dbcon.update_propw_table(tupple_data)
    
    async def store_to_bingx_db(self):
        worksheet = self.get_worksheet(GBOT_GSHEET_ID, SHEET_MAPPING.get("BINGX"))
        df = self.get_all_user(worksheet, VIP_EXPECTED_HEADERS, 2)
        tupple_data = self.df_to_tupples_bingx(df, VIP_EXPECTED_HEADERS)
        await self.dbcon.update_bingx_table(tupple_data)

    def get_vip_data(self):
        worksheet = self.get_worksheet(GBOT_GSHEET_ID, SHEET_MAPPING.get("VIP"))
        df = self.get_all_user(worksheet, VIP_EXPECTED_HEADERS, 2)
        json_data = self.df_to_json_vip(df, VIP_EXPECTED_HEADERS)
        return json_data
    
    def get_whitelist_data(self):
        worksheet = self.get_worksheet(GBOT_GSHEET_ID, SHEET_MAPPING.get("WHITE_LIST"))
        df = self.get_all_user(worksheet, WHITELIST_EXPECTED_HEADERS, 2)
        json_data = self.df_to_json_whitelist(df, WHITELIST_EXPECTED_HEADERS)
        return json_data
    
    async def store_to_bitget_db(self):
        worksheet = self.get_worksheet(GBOT_GSHEET_ID, SHEET_MAPPING.get("BITGET"))
        df = self.get_all_user(worksheet, BITGET_EXPECTED_HEADERS, 2)
        tupple_data = self.df_to_tupples_bitget(df, BITGET_EXPECTED_HEADERS)
        await self.dbcon.update_bitget_table(tupple_data)

if __name__ == "__main__":
    gsheet = GSheet(None,None)

    # BingX
    worksheet = gsheet.get_worksheet(GBOT_GSHEET_ID, SHEET_MAPPING.get("VIP"))
    df = gsheet.get_all_user(worksheet, VIP_EXPECTED_HEADERS, 2)
    json_data = gsheet.df_to_json_vip(df, VIP_EXPECTED_HEADERS)
    print(json_data)
    # sql_format = """INSERT INTO trade_volume_table (uuid, volume) VALUES ('{}', '{}') ON DUPLICATE KEY UPDATE volume = VALUES(volume);\n"""
    # jiant_string = ""
    # for t in tupple_data:
    #     jiant_string += sql_format.format(t[0], t[1])
    # with open('bingx_sql.txt', 'w') as file:
    #     file.write(jiant_string)

    # # Bitget
    # print("Start Bitget")
    # worksheet = gsheet.get_worksheet(GBOT_GSHEET_ID, SHEET_MAPPING.get("BITGET"))
    # df = gsheet.get_all_user(worksheet, BITGET_EXPECTED_HEADERS, 2)
    # tupple_data = gsheet.df_to_tupples_bitget(df, BITGET_EXPECTED_HEADERS)
    # sql_format = """INSERT INTO bitget_table (uuid, volume) VALUES ('{}', '{}') ON DUPLICATE KEY UPDATE volume = VALUES(volume);\n"""
    # # sql_format = """INSERT INTO bitget_table (uuid) VALUES ('{}') ON DUPLICATE KEY UPDATE uuid = uuid;\n"""
    # jiant_string = ""
    # print("Start Bitget Write")
    # for t in tupple_data:
    #     jiant_string += sql_format.format(t[0], t[1])
    # with open('bitget_sql.txt', 'w') as file:
    #     file.write(jiant_string)
    
    # # Pionex
    # print("Start Pionex")
    # worksheet = gsheet.get_worksheet(GBOT_GSHEET_ID, SHEET_MAPPING.get("PIONEX"))
    # df = gsheet.get_all_user(worksheet, PIONEX_EXPECTED_HEADERS, 0)
    # tupple_data = gsheet.df_to_tupples_pionex(df, PIONEX_EXPECTED_HEADERS)
    # sql_format = """INSERT INTO pionex_table (pionex_uid, amount) VALUES ('{}', '{}') ON DUPLICATE KEY UPDATE pionex_uid = VALUES(pionex_uid), amount = VALUES(amount);\n"""
    # jiant_string = ""
    # print("Start Pionex Write")
    # for t in tupple_data:
    #     jiant_string += sql_format.format(t[0], t[1])
    # with open('pionex_sql.txt', 'w') as file:
    #     file.write(jiant_string)
