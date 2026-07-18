# グラディエントについては、今回の結果と前回の実装を共有します。今回明らかに良くなっているのは、ターミネーション以外の実装に変更があったから？

**今回よくなった主因は、Termination-aware化だけではありません。**
前回から、Greedyの探索空間そのものがかなり変わっています。

画像を見る限り、今回の`final_canvas.png`は円形Stampの重なりで滑らかな勾配を近似しています。一方、前回の`canvas.png`は少数の量子化色と大きな帯状領域が目立ちます。この差は、主に次の変更から来ています。

## 最も大きい変更：色の選び方

前回は、Targetから最大8色程度のPaletteを抽出し、その限られた色だけを使っていました。

```python
palette = palette_from_target(target, count=8)
color = random_choice(palette)
```

しかもPalette抽出時にRGBを32刻みで量子化しています。

そのためGradientであっても、実際に使える色は少数です。結果として、

```text
滑らかな連続色
↓
数色の色帯
```

になりやすい実装でした。

今回は、候補Strokeの中心位置にある**Targetのピクセル色を直接使っています**。

```python
color = target[ty, tx]
```

つまり、Gradient内に存在する多数の色をそのまま利用できます。

これは今回の改善におそらく最も効いています。

---

## Brushサイズの探索も変わっています

前回はBrushサイズが固定候補でした。

```text
0.01
0.02
0.04
0.08
0.16
```

64px換算なら、おおよそ半径1、2、3、5、10px程度です。

今回は、

```text
min_radius = 1.5
max_radius = 24
```

の間を**log-uniformな連続値**で探索しています。

```python
radius = exp(uniform(log(min_radius), log(max_radius)))
```

したがって、

* 最初は大きなBrushで広く改善
* 後半は小さなBrushで局所修正

という使い分けが、前回より起きやすくなっています。

今回の画像で、右上付近などに大きな円、その隙間に小さな円が見えるのは、この探索の結果です。

---

## Target自体も同一ではありません

前回のGradient Targetは、サイズが`180 × 120`で、概ね次のRGB変化でした。

```python
R = 40 + x方向
G = 35 + y方向
B = 180 - x方向
```

今回はデフォルトで`64 × 64`です。また青成分に縦方向の弱いsin変化があります。

```python
red   = 0.10 + 0.80 * nx
green = 0.15 + 0.70 * ny
blue  = 0.85 - 0.55 * nx + 0.05 * sin(ny * pi)
```

見た目の大枠は似ていますが、同じ画像を描いているわけではありません。

特に解像度が、

```text
前回: 180 × 120 = 21,600 pixels
今回: 64 × 64 = 4,096 pixels
```

なので、今回の方が約5分の1の画素数です。円形Stampで近似するにはかなり有利です。

---

## 誤差計算の数値スケールも違います

前回は`uint8`、つまりRGBが`0–255`です。

今回は`float32`の`0.0–1.0`です。

そのため、

```text
前回のerror
今回のfinal_error
```

は数値をそのまま比較できません。

今回の

```text
0.0007435
```

が前回より小さいから改善した、と数値だけで判断することはできません。ただし、画像を見れば視覚的には明らかに今回の方が滑らかです。

---

## Termination-aware化が効いた部分

Termination-aware化そのものは、主として、

> 十分改善したところで、自律的に終了した

という部分に効いています。

今回のGradientは、

```text
accepted_steps = 88
attempted_searches = 138
stop_reason = no_improvement
```

でした。

つまり、2,000ステップ使ったから良くなったわけではありません。実際には88 Strokeで停止しています。

したがって今回の結果は、

```text
新しい色探索
＋
新しいBrush半径探索
＋
低い画像解像度
＋
Termination-awareな終了
```

の組み合わせです。

なかでも見た目の改善への寄与は、私は次の順だと考えます。

```text
1. Target地点の色を直接使う
2. Brush半径を連続的・広範囲に探索する
3. 64 × 64へ小型化した
4. Termination-aware化
```

## 厳密に比較するなら

Terminationだけの効果を確認するには、前回と今回で次を揃える必要があります。

```text
同じTarget画像
同じ解像度
同じPalette方式
同じBrushサイズ候補
同じCandidates数
同じSeed
同じ誤差関数
```

その上で終了方式だけを、

```text
Fixed 300 Steps
vs.
epsilon + patience
```

に変えるべきです。



現状の新リポジトリは、前回への「Termination機能だけの追加」ではなく、実際には**より強いGreedy Painterへ再実装したもの**です。ここはREADMEで明示した方がよい重要な点です。

# 色の選び方について、フィジカルロボットを想定するなら、前回の実装の方が自然とも考えられそう。

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
