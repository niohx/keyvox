## 概要

Keyvox APIをPythonで扱うためのライブラリです。
こちらは自分自身で使うためのライブラリですので、
自身が必要な関数のみを実装しています。
現在は

- `getUtils()`
- `getLockPinList()`
- `getLockPinStatus()`
- `createLockPin()`
- `changeLockPin()`
- `deleteLockPin()`
- `getLockStatus()`
- `controlLock()`

を実装しています。

ご自身のコーディングの際にご活用ください。

## インストール

`git clone` し、`pip install .` でインストールしてください。

```
cd keyvox
pip install .
```

## 使い方

```
from keyvox import Keyvox

kv = Keyvox("API_KEY", "API_SECRET")

doors = kv.getUtils() # 部屋リストの取得

keys = kv.getLockPinList("rockId") #向こう3日間で払いだされる鍵の一覧を取得

key = kv.createLockPin("lockId", "targetName", "sTime", "eTime") #鍵の発行

status = kv.getLockPinStatus("pinId") #鍵のステータスを取得

key  = kv.changeLockPin("pinId", "pinCode", "targetName", "sTime", "eTime") #鍵の変更

result = kv.deleteLockPin("pinId") #鍵の削除

status = kv.getLockStatus("lockId") #鍵のステータスを取得

result = kv.controlLock("lockId", "controlType") #鍵の制御 controlTypeは0:施錠、1:開錠





```
