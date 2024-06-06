# Anim Curves による In/Out Anim の計算

## 基本計算式

### Clip情報

#### レンダリング開始位置

```
comp.RenderStart
```

#### レンダリング終了位置

```
comp.RenderEnd
```

#### Clipレンダリング長

[レンダリング終了位置](#レンダリング終了位置) - [レンダリング開始位置](#レンダリング開始位置) = Clipレンダリング長

```
comp.RenderEnd - comp.RenderStart
```

#### 前半 or 後半 判定

前半を0、後半を1とする例

```
iif((time/comp.RenderEnd) < 0.5, 0, 1)
```


### Timeline情報

#### Frame Rate

```
comp:GetPrefs("Comp.FrameFormat.Rate")
```

### 単位変換

#### AnimTime(sec) -> FrameCount

AnimTime × [FrameRate](#frame-rate) = FrameCount

※ AnimTimeはアニメーション時間を表す任意の値(変数)

```
AnimTime * comp:GetPrefs("Comp.FrameFormat.Rate") = FrameCount
```

#### FrameCount -> Ratio(%)

FrameCount ÷ [Clipレンダリング長](#clipレンダリング長) = Ratio

```
(AnimTime * comp:GetPrefs("Comp.FrameFormat.Rate")) / (comp.RenderEnd - comp.RenderStart)
```

## Anim curves 設定

### In Anim

#### Time Scalce

[Ratio](#framecount---ratio)の逆数

```
1.0 / ((AnimTime * comp:GetPrefs("Comp.FrameFormat.Rate")) / (comp.RenderEnd - comp.RenderStart))
```

#### Time Offset

```
0
```

### Out Anim

#### Time Scalce

[Ratio](#framecount---ratio)の逆数
> In Animと同じ

```
1.0 / ((AnimTime * comp:GetPrefs("Comp.FrameFormat.Rate")) / (comp.RenderEnd - comp.RenderStart))
```

#### Time Offset

1 - [Ratio](#framecount---ratio)
> 誤差を考慮して1フレーム分早く始めるように計算する必要がある
```
1.0 - (((AnimTime * comp:GetPrefs("Comp.FrameFormat.Rate")) + 1) / (comp.RenderEnd - comp.RenderStart))
```
