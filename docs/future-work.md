# 色の選び方について、フィジカルロボットを想定するなら、前回の実装の方が自然とも考えられる

その通りです。**フィジカルロボットを想定するなら、前回の有限Palette方式の方が自然です。**

今回の実装は、

> Target上の任意の位置から、そのピクセル色を直接取り出す

ので、言ってしまえばロボットが無限色の絵具棚を持っている状態です。

現実には、

* 手元の絵具は有限
* 色は混ぜて作る
* 混色には時間と誤差がある
* 筆やパレットに前の色が残る
* 同じ色を完全には再現できない

ので、前回の方が物理的制約に近いです。

## ただし、前回もまだ「物理的」ではない

前回のPalette方式は自然ですが、まだ実際の画家・ロボットよりはかなり理想化されています。

```text
有限Paletteから色を選ぶ
```

だけだと、

```text
青
赤
黄
緑
```

のような既製色を瞬時に選べるだけです。

本当にPhysical寄りにするなら、色Actionは例えば次のようになります。

```text
SelectPigment
MixPigments
LoadBrush
ApplyStroke
CleanBrush
```

あるいは簡略化して、

```text
Action = (
  pigment_ratios,
  brush_position,
  brush_radius,
  pressure
)
```

とする。

この場合、Gradientの難しさは単なる描画精度ではなく、

> 限られた色材から、どの中間色をどの順番で作るか

になります。

## 研究上は二つに分けるときれいです

私は今回の経験から、色モデルを明示的に分けるのがよいと思います。

### Ideal Color Model

```text
color = target[y, x]
```

目的は、Brush形状やTerminationの性質を純粋に調べること。

### Physical Palette Model

```text
color ∈ finite_palette
```

あるいは

```text
color = mix(pigments)
```

目的は、現実的な制約下での制作戦略を調べること。

この二つを混ぜると、

* Gradientが難しいのはBrushのせいか
* Paletteのせいか
* Terminationのせいか

が分かりにくくなります。

逆に分離すれば、比較が研究になります。

## 今回のリポジトリの扱い

`painting-environment-lab-termination-aware`では、Terminationが主題なので、現在の「Target色を直接使う」実装にも合理性があります。

色選択の制約を一旦弱めることで、

> 改善が続くか、いつ止まるか

を見やすくしているからです。

ただしREADMEには、かなり明確に、

> The current painter uses an idealized color oracle.
> It is not intended to model a physical paint palette.

と書くべきです。

そしてFuture Workに、

```text
Physical Palette Model
- finite pigments
- color mixing
- brush contamination
- mixing cost
```

を置く。

Observation Designより前に、こちらを次候補にしてもよいくらいです。

今回の実装は「絵を描くロボット」より、**Terminationを調べるための理想化された診断環境**です。前回の実装は、粗いけれど、物理ロボットへ向かう思想としてはむしろ筋がよいです。


# フィジカルロボットが、市販品の油絵を混ぜることを実装する必要はない。準備された絵の具があればよい。ただし有限の数の中で。

そうですね。その方が、かなり現実的です。

フィジカルロボットだからといって、必ずしも

> チューブ絵具を混ぜ、筆を洗い、再調色する

ところまで再現する必要はありません。

むしろ最初の現実モデルとしては、

> **有限個の塗装剤が、あらかじめ使える状態で供給されている**

で十分です。

例えば、

```text
available_colors = 8
```

あるいは

```text
available_colors = 16
```

として、

```text
color ∈ {c1, c2, ..., cN}
```

から選ぶだけにする。

これは物理的にも自然です。

* 塗料タンクが複数ある
* ノズルや筆を色ごとに切り替える
* あらかじめ調色済みの塗料を使う
* 色交換には多少のコストがある

というロボットを想定できます。

## 本質は「混色」ではなく有限性

あなたの考えでは、重要なのは、

```text
無限RGB
```

ではなく、

```text
有限個の実在する塗装剤
```

で描くことですね。

この場合、前回のPalette方式は方向として正しいです。

ただし、前回の実装ではTarget画像からPaletteを抽出していたので、少し都合がよすぎる面もあります。

```python
palette = extract_palette(target)
```

だと、Targetごとに最適な塗料セットを事前準備していることになります。

これは実験としてはありですが、フィジカルロボットとしては、二種類に分けられます。

### Target-specific palette

Targetを見てから、使う有限色を準備する。

```text
Target
↓
Palette extraction
↓
8色を調色・準備
↓
Painting
```

看板制作や工業塗装なら、かなり自然です。

### Fixed palette

すべてのTargetに同じ色セットを使う。

```text
white
black
red
yellow
blue
green
...
```

こちらはより厳しい汎用ロボットです。

## 今回の研究にはTarget-specific paletteが合いそうです

今回の目的は、現実の絵具文化を再現することではなく、

> 有限色という制約の下で、どこまでTargetを近似できるか

を見ることです。

その意味では、

```text
TargetからN色を抽出
```

は妥当です。

ロボットが描画前に必要な色を準備してもらう、という前提にすればよい。

つまり、ロボットの仕事は、

```text
色を作ること
```

ではなく、

```text
準備された有限色を、どこに、どの大きさで、何回置くか
```

になります。

この切り分けはきれいです。

## Action Spaceも単純なまま保てる

```text
Action = (
  x,
  y,
  radius,
  color_index
)
```

です。

色はRGB値ではなく、

```text
color_index ∈ {0, 1, ..., N-1}
```

になります。

これはRLにも非常に扱いやすいです。

* `x, y, radius` は連続値
* `color_index` は離散値

なので、Hybrid Action Spaceになりますが、意味は明快です。

## 今回の実装についての結論

現在の

```python
color = target[y, x]
```

は、Terminationを単独で見やすくするための理想化としては有効です。

ただ、Painting Environmentの本命としては、

```text
finite prepared palette
```

の方が、あなたの構想に近いと思います。

そして、混色モデルまでは不要です。

むしろ、

> **塗料の準備はEnvironment外、描画はEnvironment内**

と境界を引けばよい。

これはロボット工学としても、研究設計としてもかなり筋が通っています。


# 調色を省いて、数十、数百くらいから選ぶる。有限性が必要。用意するパレットはターゲットは関係ない、ある種のテンプレートを作る必要がある。

つまり、

> **TargetごとにPaletteを抽出するのではなく、最初から汎用の有限Paletteを持つ**

ということですね。

そして色数は8色や16色ではなく、

```text
32
64
128
256
```

くらいまで広げてもよい。

これなら、

* 無限RGBではない
* Target専用でもない
* 調色工程も不要
* それでもかなり多くの色を表現できる

ので、現実のロボットとして十分納得感があります。

## 「テンプレートPalette」という考え方

たとえばPaletteを、RGB空間から規則的に作る。

### 単純なRGB Grid

```text
R = 0, 64, 128, 192, 255
G = 0, 64, 128, 192, 255
B = 0, 64, 128, 192, 255
```

なら、

```text
5 × 5 × 5 = 125色
```

です。

かなり分かりやすいです。

Actionは、

```text
color_index ∈ {0 ... 124}
```

になる。

これは実装も簡単で、再現性も高いです。

## ただしRGB等間隔は、人間の見た目では偏る

RGB空間の等間隔は、視覚的には均等ではありません。

たとえば暗い色が似て見えたり、緑周辺が細かく感じたりします。

そのため、より「見た目に均等」なPaletteを作るなら、

```text
Lab
OKLab
HSV
```

などの色空間でテンプレートを作る方法があります。

個人的には、最初は次の二つを比較するのが面白いです。

```text
rgb-grid-125
oklab-grid-125
```

同じ125色でも、Gradientの再現性や最終誤差が違うはずです。

## 色数そのものを実験軸にできる

これはかなり重要です。

```text
palette_size = 8
palette_size = 16
palette_size = 32
palette_size = 64
palette_size = 128
palette_size = 256
```

として、

* final_error
* accepted_steps
* stop_reason
* candidate_evaluations
* color_usage_count

を比較できる。

すると、

> 色数を増やすと、どこから改善が頭打ちになるか

が見えます。

たとえばGradientなら、

```text
8色   → バンディング
32色  → かなり改善
128色 → 十分滑らか
256色 → 改善は小さい
```

という関係になるかもしれません。

## フィジカル側の解釈も自然

Paletteを、

```text
paint cartridge rack
```

と考えればよいです。

```text
slot 0   = black
slot 1   = dark blue
slot 2   = blue
...
slot 127 = pale yellow
```

ロボットは色を混ぜない。

単に、

```text
select cartridge
load/apply
```

するだけ。

数百色あっても、工業用のインクや塗料供給系としては、概念上それほど不自然ではありません。

必ずしも数百本の筆を用意する必要はなく、

* ノズル切替
* カートリッジ切替
* 色材ディスペンサー
* 交換式ヘッド

のどれかで解釈できます。

## ここで重要なのは固定性

このPaletteは、

```text
Target A
Target B
Target C
```

で同じである必要があります。

それによって初めて、

> Environmentが汎用的な有限色制約を持つ

と言えます。

Targetから抽出してしまうと、描画前に答えをかなり教えていることになる。

固定Paletteなら、

```text
Target
↓
有限Paletteから近い色を選ぶ
↓
配置で近似する
```

という本来の問題になります。

## 私なら最初のテンプレートをこうします

まずはシンプルに、

```text
rgb-grid-64
```

です。

各チャンネル4段階。

```text
0.0
0.33
0.67
1.0
```

なので、

```text
4³ = 64色
```

になります。

次に、

```text
rgb-grid-125
```

で5段階。

そして、

```text
oklab-grid-64
```

を比較対象にする。

この三つだけでも、かなり研究になります。

## 今回のリポジトリとの関係

これはTermination-awareの範囲を超えているので、今回の実装へ無理に入れない方がよいと思います。

READMEのFuture Workなら、

```text
## Next Candidate: Fixed Finite Palette

The current painter samples the target color directly.

A more physical model uses a fixed, target-independent palette:

- rgb-grid-64
- rgb-grid-125
- perceptual-grid-64
- perceptual-grid-125
```

くらいでよい。

そして次のリポジトリ候補として、

```text
painting-environment-lab-fixed-palette
```

あるいは、

```text
painting-environment-lab-finite-color
```

が自然です。

私は`fixed-palette`の方が、Target-independentであることまで伝わって、かなりよい名前だと思います。
