from hashlib import sha256
import hmac
import time
from logger import Logger
import requests
from config import Config

CONFIG = Config()

ACTUAL_API = "https://open-api.bingx.com"
DEMO_API = "https://open-api-vst.bingx.com"
SERVER_TIME = "/openApi/swap/v2/server/time"
WALLET_API = "/openApi/swap/v2/user/balance"
POS_API = "/openApi/swap/v2/trade/closeAllPositions"
ORDER_API = "/openApi/swap/v2/trade/allOpenOrders"

APIDOMAIN = ACTUAL_API
if eval(CONFIG.IS_TEST):
    APIDOMAIN = DEMO_API

OK_STATUS = {"code": 200, "status": "ok"}
HTTP_OK_LIST = [0, 200]
SERVER_REQUEST_BUFFER = 4700 # 5 second max for api service, 300 ms buffer
logger_mod = Logger("BingX API")
logger = logger_mod.get_logger()

class BINGX:

    def __init__(self, api_key, api_secret) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.timestamp = 0
        self.session = requests.Session()
        pass

    def __is_error(self, json):
        return json.get("code") != None and json.get("code") not in HTTP_OK_LIST

    def __get_server_time(self):
        now  = int(time.time()*1000)
        if now - self.timestamp < SERVER_REQUEST_BUFFER:
            return str(self.timestamp)
        r = self.session.get("%s%s" % (APIDOMAIN, SERVER_TIME))
        if r.status_code == 200 and r.json().get("data") and r.json().get("data").get("serverTime"):
            current_time = r.json().get("data").get("serverTime")
            self.timestamp = current_time
            return str(current_time)
        else:
            return None

    def __get_sign(self, payload):
        signature = hmac.new(self.api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature
    
    def __prase_param(self, params_map, time_stamp):
        sortedKeys = sorted(params_map)
        param_str = "&".join(["%s=%s" % (x, params_map[x]) for x in sortedKeys])
        param_str += "&timestamp="+time_stamp
        return param_str
    
    def __send_request(self, method, api, param_map):
        server_time = self.__get_server_time()
        if not server_time:
            return {"Timestamp error"}
        param_str = self.__prase_param(param_map, server_time)
        url = "%s%s?%s&signature=%s" % (APIDOMAIN, api, param_str, self.__get_sign(param_str))
        headers = {
            'X-BX-APIKEY': self.api_key,
        }
        try:
            r = self.session.request(method, url, headers=headers, data={})
            if r.status_code != 200:
                logger.warning({"code": r.status_code, "msg": r.json()})
            return r.json()
        except Exception as e:
            logger.warning(f"Error [API]:  {str(e)}")
            return {"code": 99999, "msg": "BingX server unreachable"}
    
    def get_wallet(self):
        method = "GET"
        param_map = {
            "recvWindow": 0
        }
        return self.__send_request(method, WALLET_API, param_map)
    
    def close_all_pos(self):
        method = "POST"
        param_map = {
            "recvWindow": 0
        }
        return self.__send_request(method, POS_API, param_map)
    
    def close_all_order(self):
        method = "DELETE"
        param_map = {
            "recvWindow": 0
        }
        return self.__send_request(method, ORDER_API, param_map)
    
