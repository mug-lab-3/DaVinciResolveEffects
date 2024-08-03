# Anim CurvesとFollowerの組み合わせによるアニメーションTimingの計算

## Follower

Delay Timeを追加して秒単位でDelayを設定できるようにする

### Timing

* Delay typeは`Between First and Last Character`に設定する
* Timingタブに`DelayTime`として新しいコントロールを追加する

  | 設定先 | 値 |
  | ---- | ---- |
  | Name | `Delay Time(sec)` |
  | ID | `DelayTime` |
  | Type | `Number` |
  | Page | `Timing` |
  | Default | `0` |
  | Range | `0` to: `10` |
  | Allowed | `0` to: 空欄 |
  | Input Ctrol | `SliderControl` |
  | View Ctrl | `None` |
  | Center | 空欄 |
  | Steps | 空欄 |

### Frame Render Script

Settings -> Frame Render Scriptに以下を設定する

```lua
local framerate = comp:GetPrefs("Comp.FrameFormat.Rate")
self.Delay = ceil(self.DelayTime * framerate)
```

## Anim Curves

### In Anim

Floowerに設定したAnimCurvesに以下を設定し
`AnimTime`でIn Anim時間を調整できるようにする

* Curve Shape -> Source は`Duration`に設定する
* Scaling -> Clip Low に`✓`を入れる
* Scaling -> Clip High に`✓`を入れる
* Controlsタブに`AnimTime`として新しいコントロールを追加する

  | 設定先 | 値 |
  | ---- | ---- |
  | Name | `Anim Time(sec)` |
  | ID | `AnimTime` |
  | Type | `Number` |
  | Page | `Controls` |
  | Default | `0` |
  | Range | `0` to: `10` |
  | Allowed | `0` to: 空欄 |
  | Input Ctrol | `SliderControl` |
  | View Ctrl | `None` |
  | Center | 空欄 |
  | Steps | 空欄 |

#### Frame Render Script

Settings -> Frame Render Scriptに以下を設定する

* `Follower1`となっているところは設定元のfollowerに置き換える

```lua
local framerate = comp:GetPrefs("Comp.FrameFormat.Rate")
local delayCount = ceil(Follower1.DelayTime * framerate)
local animCount = ceil(self.AnimTime * framerate)
local clipLength = (comp.RenderEnd - comp.RenderStart) + 1
local ratioCorrection = (clipLength + 1) / clipLength 

if delayCount > clipLength then
  delayCount = clipLength
end

if animCount > clipLength then
  animCount = clipLength
  self.AnimTime = animCount / framerate 
end

if animCount <= delayCount then
   animCount = delayCount
   delayCount = floor(delayCount - ratioCorrection)
   self.AnimTime = animCount / framerate
end

self.TimeScale = ratioCorrection / ((animCount - delayCount) / clipLength)
self.TimeOffset = 0
```

### Out Anim

Floowerに設定したAnimCurvesに以下を設定し
`AnimTime`でOut Anim時間を調整できるようにする

* Curve Shape -> Source は`Duration`に設定する
* Scaling -> Clip Low に`✓`を入れる
* Scaling -> Clip High に`✓`を入れる
* Controlsタブに`AnimTime`として新しいコントロールを追加する

  | 設定先 | 値 |
  | ---- | ---- |
  | Name | `Anim Time(sec)` |
  | ID | `AnimTime` |
  | Type | `Number` |
  | Page | `Controls` |
  | Default | `0` |
  | Range | `0` to: `10` |
  | Allowed | `0` to: 空欄 |
  | Input Ctrol | `SliderControl` |
  | View Ctrl | `None` |
  | Center | 空欄 |
  | Steps | 空欄 |


#### Frame Render Script

Settings -> Frame Render Scriptに以下を設定する

* `Follower1`となっているところは設定元のfollowerに置き換える

```lua
local framerate = comp:GetPrefs("Comp.FrameFormat.Rate")
local delayCount = ceil(Follower1.DelayTime * framerate)
local animCount = ceil(self.AnimTime * framerate)
local clipLength = (comp.RenderEnd - comp.RenderStart) + 1
local ratioCorrection = (clipLength + 1) / clipLength 

if delayCount > clipLength then
  delayCount = clipLength 
end

if animCount > clipLength then
  animCount = clipLength 
  self.AnimTime = animCount / framerate 
end

local magicOffset = 0
if animCount <= delayCount then
   magicOffset = 2
   animCount = delayCount
   delayCount = floor(delayCount - ratioCorrection)
   self.AnimTime = animCount / framerate
end

self.TimeScale  = ratioCorrection / ((animCount - delayCount)   / clipLength)
self.TimeOffset = (1 / ratioCorrection) - ((animCount + magicOffset) / clipLength)
```