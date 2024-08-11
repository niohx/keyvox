## インストール

`git clone` する。

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


```
