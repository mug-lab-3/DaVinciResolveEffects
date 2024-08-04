# Anim CurvesとFollowerの組み合わせによるアニメーションTimingの計算

## Follower

Delay Timeを追加して秒単位でDelayを設定できるようにする

### Timing

* Timingタブに`DelayTime`として新しいコントロールを以下の設定で追加する
  | 設定先 | 値 |
  | ---- | ---- |
  | Name | `Delay Time(sec)` |
  | ID | `DelayTime` |
  | Type | `Number` |
  | Page | `Timing` |
  | Default | `0` |
  | Range | 空欄 |
  | Allowed | `0` to: 空欄 |
  | Input Ctrol | `ScrewControl` |
  | View Ctrl | `None` |
  | Center | 空欄 |
  | Steps | 空欄 |

### Frame Render Script

Settings -> Frame Render Scriptに以下を設定する

```lua
local framerate = comp:GetPrefs("Comp.FrameFormat.Rate")
local clipLength = (comp.RenderEnd - comp.RenderStart)

local delayCount = ceil(self.DelayTime * framerate)
if delayCount > (clipLength - 1) then
  delayCount = clipLength - 1
  self.DelayTime = delayCount / framerate
end

self.DelayType = 2
self.Delay = delayCount
```

## Anim Curves

### In Anim

Floowerに設定したAnimCurvesに以下を設定し
`AnimTime`でIn Anim時間を調整できるようにする

* Controlsタブに`AnimTime`として新しいコントロールを追加する

  | 設定先 | 値 |
  | ---- | ---- |
  | Name | `Anim Time(sec)` |
  | ID | `AnimTime` |
  | Type | `Number` |
  | Page | `Controls` |
  | Default | `0` |
  | Range | 空欄 |
  | Allowed | `0` to: 空欄 |
  | Input Ctrol | `SliderControl` |
  | View Ctrl | `None` |
  | Center | 空欄 |
  | Steps | 空欄 |

#### Frame Render Script

Settings -> Frame Render Scriptに以下を設定する

* `Follower1`となっているところは設定元のfollowerに置き換える

```lua
local follower = Follower1
local tag = "InAnim :" .. self.Name
local debugEnable = comp:GetData("DebugEnable")
local framerate = comp:GetPrefs("Comp.FrameFormat.Rate")
local clipLength = (comp.RenderEnd - comp.RenderStart)
local ratioCorrection = (clipLength + 1) / clipLength
local textLength = GetTextLength(follower.Text.Value)

local delayCount = ceil(follower.DelayTime * framerate)
if delayCount > (clipLength - 1) then
  delayCount = clipLength - 1
end

local animCount = ceil((self.AnimTime * framerate) - delayCount)
if animCount <= 0 then
  animCount = 1
end
if (animCount + delayCount) > clipLength then
  animCount = clipLength - delayCount
end

if debugEnable then
  local digit = floor(math.log10(clipLength) + 1)
  print(string.format("[%s] start=%0"..digit.."d, end=%0"..digit.."d, delay=%0" .. digit.."d, anim=%0"..digit .. "d", tag, 0, (animCount + delayCount), delayCount, animCount))
end

self.Source = "Duration"
self.ClipHigh = 1
self.ClipLow = 1
self.AnimTime = (animCount + delayCount) / framerate
self.TimeScale = ratioCorrection / (animCount / clipLength)
self.TimeOffset = 0
```

### Out Anim

Floowerに設定したAnimCurvesに以下を設定し
`AnimTime`でOut Anim時間を調整できるようにする

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
local follower = Follower1
local tag = "OutAnim:" .. self.Name
local debugEnable = comp:GetData("DebugEnable")
local framerate = comp:GetPrefs("Comp.FrameFormat.Rate")
local clipLength = (comp.RenderEnd - comp.RenderStart)
local ratioCorrection = (clipLength + 1) / clipLength 

local delayCount = ceil(follower.DelayTime * framerate)
if delayCount > (clipLength - 1) then
  delayCount = clipLength - 1
end

local animCount = ceil((self.AnimTime * framerate) - delayCount)
if animCount <= 0 then
  animCount = 1
end
if (animCount + delayCount) > clipLength then
  animCount = clipLength - delayCount
end

if debugEnable then
  local digit = floor(math.log10(clipLength) + 1)
  print(string.format("[%s] start=%0"..digit.."d, end=%0"..digit.."d, delay=%0" .. digit.."d, anim=%0"..digit .. "d", tag, clipLength - (animCount + delayCount), clipLength, delayCount, animCount))
end

self.Source = "Duration"
self.ClipHigh = 1
self.ClipLow = 1
self.AnimTime = (animCount + delayCount) / framerate
self.TimeScale  = ratioCorrection / (animCount / clipLength)
self.TimeOffset = (1 - ((animCount + delayCount) / clipLength)) / ratioCorrection
```


### Mid Anim

Floowerに設定したAnimCurvesに以下を設定し
`AnimStartTime`, `AnimEndTime`でMid Anim時間を調整できるようにする

* Controlsタブに`AnimStartTime`として新しいコントロールを追加する
  | 設定先 | 値 |
  | ---- | ---- |
  | Name | `Anim Start Time(sec)` |
  | ID | `AnimStartTime` |
  | Type | `Number` |
  | Page | `Controls` |
  | Default | `0` |
  | Range | 空欄 |
  | Allowed | `0` to: 空欄 |
  | Input Ctrol | `ScrewControl` |
  | View Ctrl | `None` |
  | Center | 空欄 |
  | Steps | 空欄 |
* Controlsタブに`AnimEndTime`として新しいコントロールを追加する
  | 設定先 | 値 |
  | ---- | ---- |
  | Name | `Anim End Time(sec)` |
  | ID | `AnimEndTime` |
  | Type | `Number` |
  | Page | `Controls` |
  | Default | `0` |
  | Range | 空欄 |
  | Allowed | `0` to: 空欄 |
  | Input Ctrol | `ScrewControl` |
  | View Ctrl | `None` |
  | Center | 空欄 |
  | Steps | 空欄 |

#### Frame Render Script

Settings -> Frame Render Scriptに以下を設定する

* `Follower1`となっているところは設定元のfollowerに置き換える

```lua
local tag = "MidAnim:" .. self.Name
local debugEnable = comp:GetData("DebugEnable")
local framerate = comp:GetPrefs("Comp.FrameFormat.Rate")
local clipLength = (comp.RenderEnd - comp.RenderStart)
local isError = false

local delayCount = ceil(Follower1.DelayTime * framerate)
if delayCount > (clipLength - 1) then
  delayCount = clipLength - 1
end

local animStartCount = floor(self.AnimStartTime * framerate)
local animEndCount = ceil(self.AnimEndTime * framerate)
if (clipLength -1) < animStartCount  then
  isError = true
end
if clipLength < animEndCount  then
  isError = true
end
if animEndCount <= animStartCount then
  isError = true
end

local animCount = animEndCount - animStartCount
local ratioCorrection = (clipLength + 1) / clipLength 

if animCount > clipLength then
  isError = true
end

local magicOffset = 0
if animCount <= delayCount then
  isError = true
end

if debugEnable then
  local digit = floor(math.log10(clipLength) + 1)
  print(string.format("[%s] Confirmed value: start=%0"..digit.."d, end=%0"..digit.."d, delay=%0" .. digit.."d, anim=%0"..digit .. "d, error=%s", tag, animStartCount, animEndCount, delayCount, (animCount - delayCount), tostring(isError)))
end

self.Source = "Duration"
self.ClipHigh = 1
self.ClipLow = 1
if not isError then
  self.TimeScale  = ratioCorrection / ((animCount - delayCount) / clipLength)
  self.TimeOffset = (animStartCount / clipLength) / ratioCorrection
else
  self.TimeScale  = 0
  self.TimeOffset = 0
end
```