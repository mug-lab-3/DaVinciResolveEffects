# RectangleEx

角を持って動かせる四角形


## Flow

RectangleExの構成は以下の通り  

* メインとなるRectangleノード
* 色変更用のBackgroundノード
* 移動用のTransformノード

![Flow](flow.png)

* 既存のノードと重複しないようにRectangleExのプリフィックスをつける
* `RectangleEx_Rectangle`, `RectangleEx_Transform`は[スクリプト内](#execute-script)で参照しているため名前変更不可


## Area Control

左上、右下をそれぞれ`Left Top`, `Right Bottom`として[RectangleEx_Rectangle](#flow)へコントロールを追加し  
それを使用して四角形の位置・サイズ調整を行う

### Left Top

| 設定先 | 値 |
| ---- | ---- |
| Name | `Left Top` |
| ID | `LeftTop` |
| Type | `Point` |
| Page | `Controls` |
| Default | `0.25` : `0.75` |
| Input Ctrol | `OffsetControl` |
| View Ctrl | `CrosshairControl` |
| DispScale | 空欄 |
| Style | `NormalCross` |

### Right Bottom

| 設定先 | 値 |
| ---- | ---- |
| Name | `Right Bottom` |
| ID | `RightBottom` |
| Type | `Point` |
| Page | `Controls` |
| Default | `0.75` : `0.25` |
| Input Ctrol | `OffsetControl` |
| View Ctrl | `CrosshairControl` |
| DispScale | 空欄 |
| Style | `NormalCross` |


## Calculated Parameters

[RectangleEx_Rectangle](#flow)の下記パラメータはExpressionに設定し、  
`Left Top`, `Right Bottom`から計算で求める

### Width

右端 - 左端 = 幅  
左右入れ替わっても問題ないように絶対値(abs)を取るようにする  
更に枠線の幅を考慮して塗りつぶしのときはSolidのときは外側、枠線のときは内側を指定できるようにする

```lua
abs(RightBottom.X - LeftTop.X) + iif(Solid==0, BorderWidth, -BorderWidth)
```

### Height

上端 - 下端 = 高さ  
上下入れ替わっても問題ないように絶対値(abs)を取るようにする  
更に枠線の幅を考慮して塗りつぶしのときはSolidのときは外側、枠線のときは内側を指定できるようにする  
その際、アスペクト比の補正をかける

```lua
abs(LeftTop.Y - RightBottom.Y) + (iif(Solid==0,BorderWidth, -BorderWidth) * (MaskWidth / MaskHeight))
```

### Center

* 左端 + (幅 / 2) = 中央X
* 下端 + (高さ / 2) = 中央Y

```lua
Point(LeftTop.X + ((RightBottom.X - LeftTop.X) / 2), RightBottom.Y + ((LeftTop.Y - RightBottom.Y) / 2))
```


## Centering Button

[RectangleEx_Transform](#flow)を使用して位置を移動した場合  
`Left Top`, `Right Bottom`での制御位置とずれが生じてしまう   
それを解消するためのボタンを用意する

### Control

以下の設定でCenteringボタンを追加する

| 設定先 | 値 |
| ---- | ---- |
| Name | `Centering` |
| ID | `Centering` |
| Type | `Number` |
| Page | `Controls` |
| Default | 空欄 |
| Range | 空欄 |
| Allowed | 空欄 |
| Input Ctrol | `ButtonControl` |
| View Ctrl | `None` |
| Width | 空欄 |
| Execute | [Execute Script](#execute-script) |

- [ ] Animatable
- [x] Passive

### Execute Script

[RectangleEx_Transform](#flow)での移動量を[Rectangle](#flow)に加算した上で、  
[RectangleEx_Transform](#flow)での移動量を0に戻すことにより、移動位置を維持したまま  
`Left Top`, `Right Bottom`の制御位置ずれを解消する

```lua
comp:Lock()

local centerOffsetX = (RectangleEx_Transform.Center[1][1] - 0.5)
local centerOffsetY = (RectangleEx_Transform.Center[1][2] - 0.5)

RectangleEx_Rectangle.LeftTop = {
    RectangleEx_Rectangle.LeftTop[1][1] + centerOffsetX,
    RectangleEx_Rectangle.LeftTop[1][2] + centerOffsetY,
}

RectangleEx_Rectangle.RightBottom = {
    RectangleEx_Rectangle.RightBottom[1][1] + centerOffsetX,
    RectangleEx_Rectangle.RightBottom[1][2] + centerOffsetY,
}

RectangleEx_Transform.Center = {0.5, 0.5}

comp:Unlock()
```
