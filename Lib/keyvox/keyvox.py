from datetime import datetime, timedelta
import hashlib
import hmac
import base64
import json
import requests
from typing import List, Dict, Any
from .keyvox_type import Unit, ApiResponse, LockPin, LockPinStatus,LockStatus





class KeyvoxError(Exception):
    pass


class Keyvox:
    def __init__(self, api_key: str, secret_key: str):
        """
        Keyvoxクラスのコンストラクタ。

        Args:
            api_key (str): APIキー
            secret_key (str): シークレットキー
        """
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
    def _extract_valid_fields(self, data: Dict[str, Any], cls) -> Dict[str, Any]:
        return {k: v for k, v in data.items() if k in cls.__annotations__}

    def getUnits(self) -> List[Unit]:
        """
        ユニット（部屋）のリストを取得します。

        Returns:
            List[Unit]: ユニットのリスト

        Raises:
            KeyvoxError: APIエラーが発生した場合
        """
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
        """
        指定されたロックIDに対する暗証番号のリストを取得します。

        Args:
            lockId (str): ロックID
            start_time (datetime, optional): 開始時間
            end_time (datetime, optional): 終了時間
            position (str, optional): 開始位置。デフォルトは"200"
            records (str, optional): 取得するレコード数。デフォルトは"10"

        Returns:
            List[LockPin]: 暗証番号のリスト

        Raises:
            KeyvoxError: APIエラーが発生した場合
        """
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

    

    def createLockPin(self, unitId: str, pinCode: str, sTime: datetime = None, eTime: datetime = None, targetName: str = None) -> LockPin:
        """
        新しい暗証番号を作成します。

        Args:
            unitId (str): ユニットID
            pinCode (str): 暗証番号
            sTime (datetime, optional): 開始時間。指定しない場合は現在時刻
            eTime (datetime, optional): 終了時間。指定しない場合は開始時間から1日後
            targetName (str, optional): ターゲット名。指定しない場合は"BCL太郎"

        Returns:
            LockPin: 作成された暗証番号の情報

        Raises:
            KeyvoxError: APIエラーが発生した場合
        """
        api_name = "createLockPin"
        if not sTime:
            sTime = datetime.now()
        if not eTime:
            eTime = sTime + timedelta(days=1)
        if not targetName:
            targetName = "BCL太郎"
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
        # print(data)
        if data:
            if "sTime" in data:
                data["sTime"] = datetime.fromtimestamp(int(data["sTime"]))
            if "eTime" in data:
                data["eTime"] = datetime.fromtimestamp(int(data["eTime"]))
            
            valid_fields = self._extract_valid_fields(data, LockPin)
            return LockPin(unitId=unitId, sTime=sTime, eTime=eTime,targetName=targetName, **valid_fields)
        else:
            raise KeyvoxError("予期しないレスポンス形式です")
        
    def getLockPinStatus(self, pinId:str)->LockPinStatus:
        """
        指定された暗証番号のステータスを取得します。

        Args:
            pinId (str): 暗証番号ID

        Returns:
            LockPinStatus: 暗証番号のステータス情報

        Raises:
            KeyvoxError: APIエラーが発生した場合
        """
        api_name = "getLockPinStatus"
        post_param = {
            "pinId": pinId
        }
        post_param = json.dumps(post_param)
        url = f"{self.base_url}{api_name}"
        headers, body = self._prepare_request(api_name, post_param=post_param)
        response = requests.post(url, headers=headers, data=body)
        json_response = response.json()
        if json_response.get("code") != "0" or json_response.get("msg") != "success":
            raise KeyvoxError(f"APIエラー: {json_response.get('msg')}")
        
        data = json_response.get("data")
        if data:
            valid_fields = self._extract_valid_fields(data, LockPinStatus)
            return LockPinStatus(**valid_fields)
        else:
            raise KeyvoxError("予期しないレスポンス形式です")


    def deleteLockPin(self, pinId:str)->bool:
        """
        指定された暗証番号を削除します。
        Args:
            pinId (str): 暗証番号ID
        Returns:
            bool: 削除が成功したかどうか
        """
        api_name = "disableLockPin"
        post_param = {
            "pinId": pinId
        }
        post_param = json.dumps(post_param)
        headers, body = self._prepare_request(api_name, post_param=post_param)
        url = f"{self.base_url}{api_name}"
        response = requests.post(url, headers=headers, data=body)
        json_response = response.json()
        if json_response.get("code") != "0" or json_response.get("msg") != "success":
            raise KeyvoxError(f"APIエラー: {json_response.get('msg')}")
        return True
    
    def changeLockPin(self, pinId:str, pinCode:str=None, targetName:str=None, sTime:datetime=None, eTime:datetime=None)->bool:
        """
        指定された暗証番号を変更します。
        Args:
            pinId (str): 暗証番号ID
            pinCode (str, optional): 暗証番号
            targetName (str, optional): ターゲット名
            sTime (datetime, optional): 開始時間
            eTime (datetime, optional): 終了時間
        Returns:
            bool: 変更が成功したかどうか
        """
        api_name = "changeLockPin"
        post_param = {
            "pinId": pinId
        }
        if pinCode:
            post_param["pinCode"] = pinCode
        if targetName:
            post_param["targetName"] = targetName
        if sTime:
            post_param["sTime"] = int(sTime.timestamp())
        if eTime:
            post_param["eTime"] = int(eTime.timestamp())
        
        headers, body = self._prepare_request(api_name, post_param=post_param)
        url = f"{self.base_url}{api_name}"
        response = requests.post(url, headers=headers, data=body)
        json_response = response.json()
        if json_response.get("code") != "0" or json_response.get("msg") != "success":
            raise KeyvoxError(f"APIエラー: {json_response.get('msg')}")
        return True

    def getLockStatus(self,lockId:str)->LockStatus:
        """
        指定されたロックのステータスを取得します。
        Args:
            lockId (str): ロックID
        Returns:
            LockStatus: ロックのステータス情報
        """
        api_name = "getLockStatus"
        post_param = {
            "lockId": lockId
        }
        post_param = json.dumps(post_param)
        headers, body = self._prepare_request(api_name, post_param=post_param)
        url = f"{self.base_url}{api_name}"
        response = requests.post(url, headers=headers, data=body)
        json_response = response.json()
        data = json_response.get("data")
        if data:
            valid_fields = self._extract_valid_fields(data, LockStatus)
            return LockStatus(**valid_fields)
        else:
            raise KeyvoxError("予期しないレスポンス形式です")

    def controlLock(self,lockId:str,controlType:int)->bool:
        """
        指定されたロックを制御します。
        Args:
            lockId (str): ロックID
            controlType (int): 制御タイプ 0:施錠、1:開錠
        Returns:
            bool: 制御が成功したかどうか
        """
        if controlType not in [0, 1]:
            raise ValueError("controlTypeは0または1である必要があります")
        
        api_name = "unlock"
        post_param ={
            "lockId":lockId,
            "flag":controlType
        }
        headers,body = self._prepare_request(api_name,post_param=post_param)  
        url = f"{self.base_url}{api_name}"  
        response = requests.post(url, headers=headers, data=body)  
        json_response = response.json()  
        if json_response.get("code") != "0" or json_response.get("msg") != "success":  
            raise KeyvoxError(f"APIエラー: {json_response.get('msg')}")  
        return True  


    







        


