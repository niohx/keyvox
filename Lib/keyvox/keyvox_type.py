from typing import TypedDict, List, Optional, Union

class Unit(TypedDict):
    unitId: str
    placeName: str
    unitName: str
    unitType: Optional[str]
    unitState: str
    lockIds: List[str]
    placeType: str

class LockPin(TypedDict):
    id: str
    pinId: str
    pinCode: str
    qrCode: str
    sTime: str
    eTime: str

class PinListResponse(TypedDict):
    position: str
    records: str
    pinList: List[LockPin]

class ApiResponse(TypedDict):
    code: str
    msg: str
    data: Union[List[Unit], PinListResponse]