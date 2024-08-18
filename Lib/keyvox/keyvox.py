from datetime import datetime, timedelta
import hashlib
import hmac
import base64
import json
import requests
from typing import List, Dict, Any
from .keyvox_type import Unit, ApiResponse, LockPin


class KeyvoxError(Exception):
    pass


class Keyvox:
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://eco.blockchainlock.io/api/eagle-pms/v1/"

    def _get_date(self):
        stime = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

        return stime

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

    def getLockPinList(self, lockId: str, start_time: datetime = None, end_time: datetime = None, position: str = "200", records: str = "10") -> List[LockPin]:
        api_name = "getLockPinList"

        post_param = {
            "lockId": lockId,
            # "position": position,
            # "records": records
        }

        if start_time:
            post_param["sTime"] = int(start_time.timestamp())

        if end_time:
            post_param["eTime"] = int(end_time.timestamp())
        post_param = json.dumps(post_param)
        headers, body = self._prepare_request(api_name, post_param=post_param)
        url = f"{self.base_url}{api_name}"

        response = requests.post(url, headers=headers, data=body)
        json_response = response.json()

        if json_response.get("code") != "0" or json_response.get("msg") != "success":
            raise KeyvoxError(f"APIエラー: {json_response.get('msg')}")

        data = json_response.get("data")
        if isinstance(data, dict) and "pinList" in data:
            pin_list = []
            for pin_data in data["pinList"]:
                if "sTime" in pin_data:
                    pin_data["sTime"] = datetime.fromtimestamp(
                        int(pin_data["sTime"]))
                if "eTime" in pin_data:
                    pin_data["eTime"] = datetime.fromtimestamp(
                        int(pin_data["eTime"]))

                # LockPinクラスに定義されているフィールドのみを抽出
                valid_fields = self._extract_valid_fields(pin_data, LockPin)
                pin = LockPin(**valid_fields)
                pin_list.append(pin)
            return pin_list
        else:
            raise KeyvoxError("予期しないレスポンス形式です")

    def _extract_valid_fields(self, data: Dict[str, Any], cls) -> Dict[str, Any]:
        return {k: v for k, v in data.items() if k in cls.__annotations__}

    def createLockPin(self, unitId: str, pinCode: str, sTime: datetime, eTime: datetime, targetName:str)->LockPin:
        api_name = "createLockPin"
        if not sTime:
            sTime = datetime.now()
        if not eTime:
            eTime = sTime + timedelta(days=1)
        if not targetName:
            targetName = "テスト太郎"
        post_param = {
            "unitId": unitId,
            "pinCode": pinCode,
            "sTime": int(sTime.timestamp()),
            "eTime": int(eTime.timestamp()),
            "targetName": targetName
        }
        post_param = json.dumps(post_param)
        headers, body = self._prepare_request(api_name, post_param=post_param)
        url = f"{self.base_url}{api_name}"
        response = requests.post(url, headers=headers, data=body)
        json_response = response.json()
        if json_response.get("code") != "0" or json_response.get("msg") != "success":
            raise KeyvoxError(f"APIエラー: {json_response.get('msg')}")
        
        data = json_response.get("data")
        if data:
            if "sTime" in data:
                data["sTime"] = datetime.fromtimestamp(int(data["sTime"]))
            if "eTime" in data:
                data["eTime"] = datetime.fromtimestamp(int(data["eTime"]))
            
            valid_fields = self._extract_valid_fields(data, LockPin)
            return LockPin(**valid_fields)
        else:
            raise KeyvoxError("予期しないレスポンス形式です")
        
    def getLockPinStatus(self, lockId:str, pinCode:str)->LockPinStatus:

        
        