# 🎨 Mug Advanced Halftone

<p align="center">
  <img src="images/sample.png" alt="MugAdvancedHalftone sample" width="600">
</p>

## 📝 概要
`MugAdvancedHalftone` は、DaVinci Resolve / Fusion 向けのハーフトーン生成プラグインです
網点、コミック風、ドット絵、レトロPC、サーマルカメラなどの質感をシミュレートします

### ✨ 主な機能
- **グリッド**: 六角形（ハニカム）配置による自然な網点
- **ドット形状**: 円形、四角形、ひし形、線、クロスハッチ
- **揺らぎ（Jitter）**: 位置・サイズ・縦横比の個別のランダム化
- **カラー**: 16色パレット等の制限、版ズレ（RGB Shift）の再現
- **描画制御**: アンチエイリアス、輝度反転、ドットゲイン調整

---

## 📦 インストール

本エフェクトを使用するには、以下のファイルをOSごとの所定フォルダに配置してください

| ファイル | 必須 | 用途 | 配置先フォルダ |
| :--- | :---: | :--- | :--- |
| [**MugAdvancedHalftone.fuse**](./MugAdvancedHalftone.fuse) | **必須** | プラグイン本体 (Fusion用) | `Fuses` |
| [**MugAdvancedHalftone.setting**](./MugAdvancedHalftone.setting) | **必須** | Editページ表示用プリセット | `Templates/Edit/Effects` |
| [**MugAdvancedHalftone.png**](./MugAdvancedHalftone.png) | 任意 | アイコン画像 | `Templates/Edit/Effects` |

### 配置フォルダのパス

#### 📂 Fuses フォルダ (`.fuse` を配置)

**Windows**
```text
%AppData%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Fuses\
```

**macOS**
```text
/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Fuses/
```

**Linux**
```text
~/.local/share/BlackmagicDesign/DaVinciResolve/Fusion/Fuses/
```

#### 📂 Templates/Edit/Effects フォルダ (`.setting` と `.png` を配置)

**Windows**
```text
%AppData%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Templates\Edit\Effects\
```

**macOS**
```text
/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Templates/Edit/Effects/
```

**Linux**
```text
~/.local/share/BlackmagicDesign/DaVinciResolve/Fusion/Templates/Edit/Effects/
```

---

## ⚙️ パラメータ

| セクション | パラメータ | 説明 |
| :--- | :--- | :--- |
| **Global** | Screen Density | ドットの細かさ |
| | Contrast | 元画像のコントラスト調整 |
| **Dot Shape** | Dot Shape | ドットの形状 |
| | Line Angle | 線・網線の角度 |
| | Dot Aspect Ratio | 縦横比（正:縦長 / 負:横長） |
| | Dot Gain | ドットの太り |
| | Dot Size Curve | サイズの成長曲線 |
| | Cutoff Dot Radius | 描画する最小の半径 |
| | Clip Dot Radius | 最大サイズの制限 |
| | Invert Brightness | 明暗の反転 |
| | Enable Antialias | 境界のぼかし処理 |
| **Dot Jitter** | Jitter Noise Phase| アニメーションの位相 |
| | Position Jitter | 位置のランダムなズレ |
| | Size Jitter | サイズのランダムなムラ |
| | Aspect Jitter | 縦横比のランダムな歪み |
| **Dot Color** | Use Original Color| 元画像の色をドットに使用 |
| | Color Reduction | カラーパレットの制限 |
| | RGB Shift | 版ズレ・色収差の強さ |
| | Dot Color | 指定色の設定 |
| **Background** | Blend With Input | 元の画像に直接合成 |
| | Paper Color | 背景色（紙の色） |

---

## ⚖️ ライセンス
本プロジェクトは **MITライセンス** のもとで公開されています
詳細は [LICENSE](./LICENSE) ファイルをご確認ください

### ✅ やっていいこと（OK）
- **商用利用**: Youtube動画や広告、映画などの制作に自由に使用できます
- **改変**: Fuseファイルの中身を書き換えて自分好みに調整できます
- **再配布**: 規約を守れば、自分のサイトなどで紹介・配布できます（ただし、著作権表示が必要です）

### ❌ やってはいけないこと（NG）
- **無保証**: このプラグインの使用によって生じたいかなる損害についても、作者は責任を負いません
- **著作権表示の削除**: ソースコード内にある作者名やライセンス条項を消してはいけません

---

## 🔗 リンク
- [<img src="https://cdn.simpleicons.org/youtube" width="16" height="16"> **YouTube: Mug Lab**](https://www.youtube.com/@MugLab3)
- [<picture><source media="(prefers-color-scheme: dark)" srcset="https://cdn.simpleicons.org/github/white"><img src="https://cdn.simpleicons.org/github/black" width="16" height="16"></picture> **GitHub: Mug Lab Repository**](https://github.com/mug-lab-3/DaVinciResolveEffects)
- [<picture><source media="(prefers-color-scheme: dark)" srcset="https://cdn.simpleicons.org/x/white"><img src="https://cdn.simpleicons.org/x/black" width="16" height="16"></picture> **X: @MugLab3**](https://x.com/MugLab3)
