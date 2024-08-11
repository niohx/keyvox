## 概要

Keyvox APIをPythonで扱うためのライブラリです。
こちらは自分自身で使うためのライブラリですので、
自分が必要な関数のみを実装しています。
現在は`getUtils()`と`getLockPinList()`のみ実装しています。

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


```
