import datetime
from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any

@dataclass
class Unit:
    unitId: str
    placeName: str
    unitName: str
    unitType: Optional[str]
    unitState: str
    lockIds: List[str]
    placeType: str

@dataclass
class LockPin:
    id: str
    pinId: str
    pinCode: Optional[str] = None
    qrCode: Optional[str] = None
    sTime: Optional[datetime.datetime] = None
    eTime: Optional[datetime.datetime] = None
    category: Optional[str] = None

@dataclass
class PinListResponse:
    position: str
    records: str
    pinList: List[LockPin]

@dataclass
class LockPinStatus:
    pinCode: str
    status: str

@dataclass
class ApiResponse:
    code: str
    msg: str
    data: Union[List[Unit], PinListResponse]