import datetime
import hashlib
import hmac
import base64
import json
import requests
from typing import List
from .keyvox_type import Unit, ApiResponse,LockPin

class KeyvoxError(Exception):
    pass

class Keyvox:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://eco.blockchainlock.io/api/eagle-pms/v1/"

    def _get_date(self):
        return datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    def _calculate_digest(self, post_param):
        param_hash = hashlib.sha256(post_param.encode()).digest()
        return f"SHA-256={base64.b64encode(param_hash).decode()}"

    def _calculate_signature(self, date, request_line, digest):
        string_to_sign = f"date: {date}{request_line}\ndigest: {digest}"
        signature = hmac.new(
            self.secret_key.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()

    def _prepare_request(self, api_name, method="POST", post_param="{}"):
        date = self._get_date()
        request_line = f"\n{method} /api/eagle-pms/v1/{api_name} HTTP/1.1"
        digest = self._calculate_digest(post_param)
        signature = self._calculate_signature(date, request_line, digest)

        headers = {
            "date": date,
            "authorization": f'hmac username="{self.api_key}", algorithm="hmac-sha256", headers="date request-line digest", signature="{signature}"',
            "x-target-host": "default.pms",
            "digest": digest,
            "Content-Type": "application/json"
        }

        return headers, post_param

    def getUnits(self) -> List[Unit]:
        api_name = "getUnits"
        headers, body = self._prepare_request(api_name)
        url = f"{self.base_url}{api_name}"
        
        response = requests.post(url, headers=headers, data=body)
        json_response: ApiResponse = response.json()
        
        if json_response.get("code") != "0" or json_response.get("msg") != "success":
            raise KeyvoxError(f"APIエラー: {json_response.get('msg')}")
        
        data = json_response.get("data")
        if not isinstance(data, list):
            raise KeyvoxError("予期しないレスポンス形式です")
        
        # lockIdsをパースして文字列のリストに変換
        for unit in data:
            if "lockIds" in unit and unit["lockIds"]:
                unit["lockIds"] = unit["lockIds"].split(",")
            else:
                unit["lockIds"] = []
        
        return data
    
    def getLockPinList(self, lockId: str, sTime: datetime, eTime: datetime, position: str = "200", records: str = "10") -> List[LockPin]:
        api_name = "getLockPinList"
        
        # datetimeをUNIXタイムスタンプに変換
        sTime_unix = int(sTime.timestamp())
        print(f"sTime_unix:{sTime_unix}")
        eTime_unix = int(eTime.timestamp())
        
        post_param = json.dumps({
            "lockId": lockId,
            "sTime": str(sTime_unix),
            "eTime": str(eTime_unix),
            # "position": position,
            "records": records
        })
        headers, body = self._prepare_request(api_name, post_param=post_param)
        url = f"{self.base_url}{api_name}"
        
        response = requests.post(url, headers=headers, data=body)
        json_response: ApiResponse = response.json()
        print(json_response)
        
        if json_response.get("code") != "0" or json_response.get("msg") != "success":
            raise KeyvoxError(f"APIエラー: {json_response.get('msg')}")
        
        data = json_response.get("data")
        if not isinstance(data, dict) or "pinList" not in data:
            raise KeyvoxError("予期しないレスポンス形式です")
        
        return data["pinList"]





# 使用例
# api_key = "Bw0yFwIVWFNRiZapLIgDyFdyIUsI10NvAZNqI3jP"
# secret_key = "3Nr5EU4JhOTzOTMc1r2PI83lg6E0ZTfS1yX7ynQbeGdcMC6a"
# instance = Keyvox(api_key, secret_key)
# units = instance.getUnits()
# print(json.dumps(units, indent=2))