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

#### Controls

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
  | Input Ctrol | `ScrewControl` |
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

#### Controls

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
  | Input Ctrol | `ScrewControl` |
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
`AnimStartTime`, `AnimTime`でMid Anim時間を調整できるようにする

#### Controls

* Controlsタブに`AnimStartOffset`として新しいコントロールを追加する
  | 設定先 | 値 |
  | ---- | ---- |
  | Name | `Anim Start Offset(sec)` |
  | ID | `AnimStartOffset` |
  | Type | `Number` |
  | Page | `Controls` |
  | Default | `0` |
  | Range | 空欄 |
  | Allowed | 空欄 |
  | Input Ctrol | `ScrewControl` |
  | View Ctrl | `None` |
  | Center | 空欄 |
  | Steps | 空欄 |
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
  | Input Ctrol | `ScrewControl` |
  | View Ctrl | `None` |
  | Center | 空欄 |
  | Steps | 空欄 |

#### Frame Render Script

Settings -> Frame Render Scriptに以下を設定する

* `Follower1`となっているところは設定元のfollowerに置き換える

```lua
local follower = Follower1
local framerate = comp:GetPrefs("Comp.FrameFormat.Rate")
local clipLength = (comp.RenderEnd - comp.RenderStart)
local ratioCorrection = (clipLength + 1) / clipLength
local debug = ""

local delayCount = 0
if follower and follower.DelayTime then
  delayCount = ceil(follower.DelayTime * framerate)
  if delayCount > (clipLength - 1) then
    delayCount = clipLength - 1
  end
end

local animCount = ceil((self.AnimTime * framerate) - delayCount)
if animCount <= 0 then
  animCount = 1
end
if (animCount + delayCount) > clipLength then
  animCount = clipLength - delayCount
end

local animStartCount = 0
if 0 < self.AnimStartOffset then
  animStartCount = floor(self.AnimStartOffset * framerate)
else
  animStartCount = clipLength - floor(self.AnimStartOffset * -1 * framerate)
end
if animStartCount < 0 then
  animStartCount = 0
end
if (animStartCount + delayCount + animCount) > clipLength then
  animStartCount = clipLength - animCount - delayCount - 1
end

if self.debug then
  local animEndFrame = (animStartCount + delayCount + animCount)
  debug = debug .. "AnimStartOffset : " .. self.AnimStartOffset .. "\n"
  debug = debug .. "AnimTime : " .. self.AnimTime .. "\n"
  debug = debug .. "ClipLength : " .. clipLength .. "(" .. comp.RenderEnd .. " - ".. comp.RenderStart .. ")\n"
  debug = debug .. "AnimStartFrame : " .. animStartCount .."(" .. (comp.RenderStart + animStartCount) .. ")\n"
  debug = debug .. "AnimEndFrame : " .. animEndFrame .."(" .. (comp.RenderStart + animEndFrame) .. ")\n"
  debug = debug .. "animCount : " .. animCount .. "\n"
  debug = debug .. "delayCount : " .. delayCount .. "\n"
  self.debug = debug
end

self.Source = "Duration"
self.ClipHigh = 1
self.ClipLow = 1
self.AnimTime = (animCount + delayCount) / framerate
if 0 < self.AnimStartOffset then
  self.AnimStartOffset = animStartCount / framerate
else
  self.AnimStartOffset = ((clipLength - animStartCount) / framerate) * -1
end
self.TimeScale  = ratioCorrection / (animCount / clipLength)
self.TimeOffset = (animStartCount / clipLength) / ratioCorrection
```