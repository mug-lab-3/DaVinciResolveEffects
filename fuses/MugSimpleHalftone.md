# MugSimpleHalftone.fuse 技術仕様書

## 概要

MugSimpleHalftone.fuse は、DaVinci Resolve/Fusion 用の高性能なハーフトーンエフェクトプラグインです。六角形グリッドベースのドット配置により、印刷物風のハーフトーン効果を生成します。GPU アクセラレーション（OpenCL）を使用し、リアルタイムでの高品質なレンダリングを実現します。v2.41 では「Invert Brightness」オプションが追加され、明るい領域を強調するハイライト寄りの表現も可能になりました。

## アーキテクチャ概要

```mermaid
graph TD
    A[入力画像] --> B[セル情報計算カーネル]
    B --> C[セル情報バッファ1<br/>位置情報]
    B --> D[セル情報バッファ2<br/>ドット情報]
    B --> E[セル情報バッファ3<br/>色情報]

    C --> F[ドット描画カーネル]
    D --> F
    E --> F
    A --> F

    F --> G[最終出力画像]

    H[パラメータ] --> B
    H --> F

    style B fill:#e1f5fe
    style F fill:#f3e5f5
    style G fill:#e8f5e8
```

## メイン処理フロー

### 1. 全体処理フロー

Fusion から渡される入力画像と UI パラメータは `Process()` に集約され、セル解析（`CellInfoKernel`）と描画（`RenderDotsKernel`）を 2 段階で実行します。パラメータは処理ステージごとに評価され、値の一部は GPU カーネルへ定数としてバンドルされます。

```mermaid
sequenceDiagram
     participant Img as Source Image
     participant Cfg as UI Parameters
     participant Proc as Process()
     participant CK as CellInfoKernel
     participant RK as RenderDotsKernel
     participant Out as Output

     Img->>Proc: Input image
     Cfg->>Proc: Screen Density〜Paper Color
     Proc->>Proc: セルグリッド計算 & パラメータ整形
     Proc->>CK: CellInfoParams を渡して実行
     CK->>Proc: cell_info1/2/3
     Proc->>RK: Dot 描画用パラメータを渡して実行
     RK->>Proc: Dot Coverage & 色ブレンド済み画像
     Proc->>Out: 最終画像を出力
```

### 1-1. パラメータ駆動の処理ステージ

ドット生成は次の 6 ステージで進み、各ステージが該当パラメータを順に適用します。式中の $L$ はセル輝度、$R_{\max}$ はセルが取り得る最大半径です。

1. **セルグリッド生成 — Screen Density**  
   `Screen Density` は水平方向のセル数を指定し、六角グリッドのピッチ $p_x$ と $p_y$ を決定します。ピッチは `CellInfoKernel` と `RenderDotsKernel` の両方で共有され、後段のサンプリング半径やアンチエイリアス幅の基準になります。
2. **輝度統計と正規化 — Contrast**  
   サンプリングした平均輝度 $L$ は $L' = 0.5 + (L-0.5)\times\text{Contrast}$ でリマップし、`Contrast` が高いほどシャドウとハイライトを強調します。ここで得た $L'$ が以後のトーン計算の基礎になります。
3. **トーン生成 — Invert Brightness / Dot Gain / Dot Size Curve**  
   `Invert Brightness` がオフなら $T_0 = 1 - L'$, オンなら $T_0 = L'$ で極性を切り替えます。続いて `Dot Gain` で $T_1 = \mathrm{saturate}(T_0 + \text{DotGain})$ の線形オフセット、`Dot Size Curve` で $T_2 = \mathrm{saturate}(T_1)^{\max(\text{DotSizeCurve},10^{-4})}$ の非線形リマップを行い、ハイライト・シャドウどちらにドットを残すかを制御します。
4. **描画許可と半径制御 — Brightness Cutoff / Cutoff Dot Radius / Clip Dot Radius**  
   `Brightness Cutoff` は $L'$ と閾値を比較し、条件を満たさないセルをゼロ半径にします。条件を満たしたセルは $\text{radius}_\text{raw} = T_2\times R_{\max}$ を計算し、`Cutoff Dot Radius` 未満ならノイズ抑制のため描画しません。最後に `Clip Dot Radius` を掛け上限 $R_{\max}\times\text{ClipDotRadius}$ に収め、極端な肥大化を止めます。
5. **境界サンプリング設計 — Enable Dot Antialias / AA Edge Softness**  
   `Enable Dot Antialias` がオンの場合のみ後述のアンチエイリアス計算を有効化します。`AA Edge Softness` はセルピッチから求める幅 $w = \text{AAEdgeSoftness} \times p_\text{avg}$ を与え、半径から内側バリアを引いた上でソフトなカバレッジ関数を構築します。オフの場合はハードなステップ関数が使用されます。
6. **色と紙の決定 — Use Original Color / Dot Color* / Blend With Input / Paper Color Preset / Paper Color***  
   `Use Original Color` がオンなら cell_info3 の平均色を採用し、オフなら `Dot Color` の RGBA（`Dot Color Red/Green/Blue/Alpha`）を使用します。`Blend With Input` がオンの場合は入力画像が背景、オフの場合は紙色が背景になります。紙色は `Paper Color Preset` でプリセットを選ぶか、`Paper Color Red/Green/Blue/Alpha` で直接指定します。これらの値は次節のブレンド処理で使用されます。

ステージ 1〜4 が `CellInfoKernel`、ステージ 5〜6 が `RenderDotsKernel` の主担当です。アンチエイリアスと色処理の詳細は以下の節で掘り下げます。

### 1-2. アンチエイリアス処理

`Enable Dot Antialias` がオンのセルには、ピクセルとセル中心の距離 $d$ に基づいてカバレッジを計算します。セルピッチから算出した幅 $w = \text{AAEdgeSoftness} \times p_\text{avg}$ を使い、

1. 内側半径を $r_{\text{inner}} = \max(r - w,\, 0)$ と定義。
2. $d \le r_{\text{inner}}$ ならカバレッジ 1、$d \ge r$ なら 0。
3. それ以外は $\mathrm{saturate}\Big(\dfrac{r - d}{w}\Big)$ で滑らかに減衰。

`Enable Dot Antialias` がオフ、または半径が `DOT_RADIUS_THRESHOLD` 未満のセルはハードエッジ（0/1）のみを使用します。選ばれたカバレッジは近傍セルの中で最も強いドットに限定して適用され、次節の色ブレンドに渡されます。

### 1-3. 色とブレンド

最終色は紙色／入力画像／ドット色の 3 者合成で決まります。

1. **ドット色の選択** — `Use Original Color` がオンのときはセル平均色に $(1-L')$ を掛け、暗部ほど濃くなるよう調整します。オフのときは `Dot Color Red/Green/Blue` と `Dot Color Alpha` がそのまま使用されます。
2. **背景ベースの決定** — `Blend With Input` がオンなら入力ピクセルがベース。オフなら `Paper Color Preset` の選択値で `Paper Color Red/Green/Blue/Alpha` を上書きし、その RGBA を背景として採用します。`Paper Color Alpha` を 1 未満に設定すれば、背景と入力の合成を意図的に透過させることもできます。
3. **合成** — `RenderDotsKernel` 内の `blendDotOver()` で $\text{Final} = (1-\alpha_\text{dot})\times\text{Base} + \alpha_\text{dot}\times\text{DotColor}$ を計算します。$\alpha_\text{dot}$ はアンチエイリアスで得たカバレッジと `Dot Color Alpha` の積です。

これらの結果が GPU テクスチャとして戻り、`Process()` が Fusion へ最終画像を返します。

### 2. セルグリッド計算

六角形配置のセルグリッドは以下の計算で決定されます：

```lua
-- セルピッチ計算
local SIN60 = 0.866025  -- √3/2
local cellBasePitch = floor(max(3.0, width / screenDensity))
local cellPitchX = cellBasePitch
local cellPitchY = floor(max(3.0, cellBasePitch * SIN60))

-- グリッドサイズ
local cellGridNumX = ceil(width / cellPitchX) + 3
local cellGridNumY = ceil(height / cellPitchY) + 2
```

## GPU カーネル詳細

### CellInfoKernel（セル情報計算）

このカーネルは各セルの基本情報を計算し、3 つの情報バッファに格納します。

```mermaid
graph LR
    A[入力画像] --> B[セル位置計算]
    B --> C[円形サンプリング]
    C --> D[輝度・色平均計算]
    D --> E[ドットサイズ決定]

    E --> F[バッファ1<br/>位置情報]
    E --> G[バッファ2<br/>ドット情報]
    E --> H[バッファ3<br/>色情報]

    style F fill:#ffecb3
    style G fill:#c8e6c9
    style H fill:#f8bbd9
```

#### セル情報バッファの構造

**cellInfo1 (位置情報)**

- `x`: セル IDX (グリッド座標 X)
- `y`: セル IDY (グリッド座標 Y)
- `z`: セル中心位置 X (ピクセル座標)
- `w`: セル中心位置 Y (ピクセル座標)

**cellInfo2 (ドット情報)**

- `x`: セル輝度値 (0.0-1.0)
- `y`: ドット半径 (ピクセル単位)
- `z`: 行オフセットフラグ (0=通常行, 1=オフセット行)
- `w`: 予約済み (将来拡張用)

**cellInfo3 (色情報)**

- `x`: 元の色 R 成分 (0.0-1.0)
- `y`: 元の色 G 成分 (0.0-1.0)
- `z`: 元の色 B 成分 (0.0-1.0)
- `w`: 元の色 A 成分 (透明度)

#### 六角形グリッド配置

```mermaid
graph TB
    subgraph "六角形グリッド配置パターン"
        A1[●] --- B1[●]
        A1 --- C1[●]
        B1 --- C1
        B1 --- D1[●]
        C1 --- D1
        C1 --- E1[●]
        D1 --- E1

        A2[●] --- B2[●]
        A2 --- C2[●]
        B2 --- C2
        B2 --- D2[●]
        C2 --- D2

        A1 --- A2
        B1 --- B2
        C1 --- C2
        D1 --- D2
    end

    subgraph "オフセットパターン"
        F[偶数行: 通常配置]
        G[奇数行: 半セル右にオフセット]
    end
```

#### 円形サンプリング最適化

```mermaid
flowchart TD
    A[サンプリング開始] --> B{半径 > 閾値?}
    B -->|Yes| C[ステップサイズ=2<br/>高速サンプリング]
    B -->|No| D[ステップサイズ=1<br/>精密サンプリング]

    C --> E[円形範囲チェック]
    D --> E

    E --> F[Y方向早期カットオフ]
    F --> G[X方向範囲事前計算]
    G --> H[ピクセルサンプリング]
    H --> I[輝度・色累積]
    I --> J[平均値計算]
```

### RenderDotsKernel（ドット描画）

各ピクセルが属するセルとその周辺セルを検索し、ドットの描画を行います。

```mermaid
graph TD
    A[各ピクセル処理] --> B[所属セル特定]
    B --> C{高密度モード?}

    C -->|Yes| D[近接セルのみチェック<br/>2セル程度]
    C -->|No| E[全周辺セルチェック<br/>6セル]

    D --> F[ドット描画判定]
    E --> F

    F --> G{ドット内?}
    G -->|Yes| H[アンチエイリアス計算]
    G -->|No| I[背景色]

    H --> J[色ブレンド]
    J --> K[最終色出力]
    I --> K

    style D fill:#ffcdd2
    style E fill:#c8e6c9
```

#### 隣接セル検索パターン

```mermaid
graph TB
    subgraph "偶数行の隣接パターン"
        A1[上左] --- B1[現在セル]
        C1[上右] --- B1
        D1[右] --- B1
        E1[下右] --- B1
        F1[下左] --- B1
        G1[左] --- B1
    end

    subgraph "奇数行の隣接パターン"
        A2[上左] --- B2[現在セル]
        C2[上右] --- B2
        D2[右] --- B2
        E2[下右] --- B2
        F2[下左] --- B2
        G2[左] --- B2
    end
```

## パラメータ詳細

### 基本パラメータ

| パラメータ        | デフォルト | 範囲     | 説明                                                                       |
| ----------------- | ---------- | -------- | -------------------------------------------------------------------------- |
| Screen Density    | 150.0      | 1-1000   | ハーフトーンパターンの密度                                                 |
| Contrast          | 1.0        | 0.1-15.0 | コントラスト調整                                                           |
| Dot Gain          | 0.0        | -1.0-1.0 | インクの滲み効果シミュレート                                               |
| Invert Brightness | Off        | 0 or 1   | 明るい領域ほどドットを大きくする（閾値判定も反転）                         |
| Brightness Cutoff | 0.75       | 0.0-1.0  | ドットの描画条件を決める明度閾値（Invert Brightness 有効時は明部側で判定） |
| Cutoff Dot Radius | 0.05       | 0.0-1.0  | 描画しない最小ドット半径                                                   |
| Clip Dot Radius   | 1.0        | 0.0-1.0  | ドットの最大サイズ制限                                                     |

### 視覚効果パラメータ

```mermaid
graph LR
    A[明度] --> B{Brightness Cutoff}
    B -->|条件外| C[ドット非描画]
    B -->|条件内| D[ドットサイズ計算]

    D --> E[トーン値計算<br/>Invert 有効時は明度を使用]
    E --> F[Dot Gain適用]
    F --> G[最大サイズ制限]
    G --> H{半径 < Cutoff?}
    H -->|Yes| I[ドット非描画]
    H -->|No| J[ドット描画]
```

### 色設定

```mermaid
graph TD
    A[色設定] --> B{Use Original Color?}
    B -->|Yes| C[元画像の色を保持]
    B -->|No| D[ユーザー指定色]

    D --> E[ドット色設定]
    D --> F{Blend With Input?}
    F -->|Yes| G[入力画像上に描画]
    F -->|No| H[紙色背景に描画]

    C --> I[最終合成]
    E --> I
    G --> I
    H --> I
```

## アンチエイリアシング

小さなドットの境界を滑らかに保つため、RenderDotsKernel では距離ベースのカバレッジ計算と段階的な減衰を組み合わせたアンチエイリアシングを行います。

### カバレッジ計算の流れ

- ドット半径 `dotRadius` に対して、`AA Edge Softness` パラメータから算出した実効エッジ幅 `aaEdgeWidth` を適用し、内側境界 `innerRadius = max(dotRadius - aaEdgeWidth, 0)` を定義します。
- ピクセルの距離二乗 `distSq` が `dotRadius^2` を超えればカバレッジは 0。`innerRadius^2` より小さければ 1。境界帯に入った場合は $\text{coverage} = \text{saturate}\Big(\dfrac{dotRadius - dist}{aaEdgeWidth}\Big)$ を用いた線形フェードで 0-1 の値を作ります。
- `aaEdgeWidth` が 0、またはドット半径が `DOT_RADIUS_THRESHOLD` 以下の場合はアンチエイリアスをスキップし、カバレッジはステップ関数として扱います。

```mermaid
graph LR
    A[ピクセル-ドット中心距離 dist] --> B{dist ≥ dotRadius?}
    B -->|Yes| C[coverage = 0.0]
    B -->|No| D{dist ≤ innerRadius?}
    D -->|Yes| E[coverage = 1.0]
    D -->|No| F["(dotRadius - dist) / aaEdgeWidth"]
    F --> G[saturate]

    C --> H[blendDotOver]
    E --> H
    G --> H
```

### 重なり合うドットの優先判定

- 各ピクセルは所属セルに加えて最大 6（高密度時は 2）つの隣接セルからの候補ドットを評価します。
- `checkCellDot()` が返すカバレッジ（エッジ減衰後の 0-1 値）に、オリジナルカラー使用時は「暗い色ほど強い」となるよう $1-\text{luma}$ を掛け合わせ、`bestStrength` として保持します。
- `bestStrength` が大きい候補、同値の場合はカバレッジが大きい候補が選択され、`blendDotOver()` で紙色／入力画像の上に 1 枚のドットとしてブレンドされます（複数ドットの加算合成を避け、にじみや過剰な濃度を防止）。
- AA 処理はこの最終的に選ばれたドットに対してのみ適用されるため、隣接セルが重なっても境界のフェザリング幅は維持されます。

### 実装上の考慮

- バウンディングボックス（`dotRadius + margin + aaEdgeWidth`）で不必要な距離計算を除外し、AA のコストを局所化しています。
- ピクセルごとに平方根計算を遅延させ、`distSq` 比較で早期リターンすることで、アンチエイリアスを有効にしても GPU の負荷が過剰に増えないようにしています。
- `AA Edge Softness` はセルピッチの平均に基づいて物理的なピクセル幅へ変換されるため、スクリーン密度を変えてもアンチエイリアス幅の感覚が大きくズレない設計です。

### 視覚比較サマリー（GitHub プレビュー対応）

| 距離カテゴリ     | ピクセル距離の状態               | カバレッジ値 | ドットの見え方 | 説明                                                                                    |
| ---------------- | -------------------------------- | ------------ | -------------- | --------------------------------------------------------------------------------------- |
| 中心コア         | $dist \le innerRadius$           | 1.00         | `⬤`            | 完全に塗りつぶされた領域。ブレンド時もドット色がそのまま適用されます。                  |
| 滑らかなエッジ帯 | $innerRadius < dist < dotRadius$ | 0.01〜0.99   | `◐`            | 距離に応じた減衰でフェザー状に見える領域。AA Edge Softness が広いほど滑らかになります。 |
| 外側             | $dist \ge dotRadius$             | 0.00         | `○`            | カバレッジ 0 のため背景色のみが残ります。                                               |

### 候補セルの視覚フロー

```mermaid
flowchart TB
    subgraph PixelEvaluation["ピクセルごとの評価"]
        A[所属セルを特定] --> B{高密度モード?}
        B -->|Yes| C[隣接2セルを候補化]
        B -->|No| D[隣接6セルを候補化]
        C --> E["各候補に対して\ncheckCellDot()"]
        D --> E
        E --> F["カバレッジ × (1 - luma) で\nbestStrength を更新"]
        F --> G{最終候補決定}
    end

    G --> H["選ばれたドットにのみ\nAA カバレッジを適用"]
    H --> I["blendDotOver() で背景と合成"]
```

上図の通り、重なり合う領域でも最終的に 1 つの候補ドットが選ばれ、アンチエイリアスはそのドットのみに適用されます。

## 最適化技術

### 1. GPU 並列処理最適化

- **バウンディングボックス**: ドット周辺のみを計算対象とする
- **早期リターン**: 計算不要なケースの高速スキップ
- **ベクトル演算**: SIMD 命令活用による高速化

### 2. メモリアクセス最適化

```mermaid
graph TD
    A[テクスチャキャッシュ] --> B[局所性重視アクセス]
    B --> C[事前計算値の活用]
    C --> D[分岐削減]
    D --> E[レジスタ使用量最適化]
```

### 3. 動的品質調整

- **高密度モード**: 密度に応じて隣接セルチェック数を調整
- **サンプリング最適化**: 半径に応じてサンプリングステップを調整

## 使用例と Tips

### 基本的な使用方法

1. **新聞風効果**: Screen Density = 80-120, Use Original Color = Off
2. **雑誌風効果**: Screen Density = 150-200, Use Original Color = On
3. **アート効果**: Screen Density = 50-80, Dot Gain = 0.2-0.5
4. **ハイライト強調**: Invert Brightness = On, Brightness Cutoff = 0.7-0.9, Dot Gain = -0.1~-0.3

### パフォーマンス最適化

- 高解像度画像では Screen Density を下げる
- リアルタイム再生時は Enable Dot Antialias を無効にする
- Original Color 使用時は、コントラストを適切に調整する

## 技術的制約

- OpenCL 対応 GPU 必須
- 最大解像度: GPU VRAM に依存
- セルグリッド最大サイズ: 理論上無制限（実際はメモリ制約）

## 拡張可能性

現在の実装は将来的な機能拡張を考慮して設計されています：

- cellInfo2.w フィールド（予約済み）
- 追加のブレンドモード
- カスタムドット形状
- マルチレイヤー対応

---

_このドキュメントは MugSimpleHalftone.fuse v2.60 に基づいて作成されています。_
