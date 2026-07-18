```bash
$  painting-env-lab   --target gradient   --max-steps 2000   --candidates 96   --epsilon 1e-5   --patience 12   --output outputs/gradient
$  painting-env-lab   --target flat   --max-steps 2000   --candidates 96   --epsilon 1e-5   --patience 12   --output outputs/flat
$  painting-env-lab   --target geometry   --max-steps 2000   --candidates 96   --epsilon 1e-5   --patience 12   --output outputs/geometry
$  painting-env-lab   --target noise   --max-steps 2000   --candidates 96   --epsilon 1e-5   --patience 12   --output outputs/noise
$  python examples/compare_targets.py
```

結果はこうなった。

```text
{'target': 'flat', 'stop_reason': 'no_improvement', 'accepted_steps': 5, 'attempted_searches': 17, 'candidate_evaluations': 1632, 'final_error': 0.0}
{'target': 'geometry', 'stop_reason': 'no_improvement', 'accepted_steps': 93, 'attempted_searches': 138, 'candidate_evaluations': 13248, 'final_error': 0.0008505044970661402}
{'target': 'gradient', 'stop_reason': 'no_improvement', 'accepted_steps': 88, 'attempted_searches': 138, 'candidate_evaluations': 13248, 'final_error': 0.0007435291190631688}
{'target': 'noise', 'stop_reason': 'no_improvement', 'accepted_steps': 210, 'attempted_searches': 347, 'candidate_evaluations': 33312, 'final_error': 0.006565795745700598}

```

かなりきれいに差が出ています。今回の結果だけでも、Termination-awareにした意味が十分あります。

まず表にするとこうです。

| target   | accepted steps | attempted searches | candidate evaluations | final error |
| -------- | -------------: | -----------------: | --------------------: | ----------: |
| flat     |              5 |                 17 |                 1,632 |    0.000000 |
| geometry |             93 |                138 |                13,248 |    0.000851 |
| gradient |             88 |                138 |                13,248 |    0.000744 |
| noise    |            210 |                347 |                33,312 |    0.006566 |

## 最も明確なのはFlat

```text
accepted_steps = 5
final_error = 0.0
```

Flatは、現在のBrushとPaletteで完全に表現できています。

しかも5 Strokeで終了しているので、

> 大きな単純色面は、現在のAction Spaceと非常に相性がよい

と言えます。

`attempted_searches = 17`なのは、5回描いた後も候補探索を行い、`patience`分だけ改善候補が見つからなかったためです。

つまり、概念的には、

```text
5回描画
+
12回連続で改善なし
=
17 searches
```

でしょう。実行時の`patience = 12`と正確に一致しています。

## GeometryとGradientがほぼ同じ探索量

ここは少し意外で、面白い結果です。

```text
geometry: 93 accepted
gradient: 88 accepted
```

最終誤差も、

```text
geometry: 0.0008505
gradient: 0.0007435
```

でGradientの方がわずかに低い。

つまり今回の条件では、

> Gradientが特別に最後までステップを消費したわけではない

ということです。

以前の固定ステップ実験でGradientが難しく見えたとしても、今回のTermination-aware設定では、GeometryとGradientはほぼ同程度の探索予算で局所的な限界に到達しています。

これは、少なくとも次のどちらかを示唆します。

* Gradient Generatorが、現在のBrushでも比較的近似しやすい構造だった
* `epsilon`と候補生成方式により、細かな改善を拾えなくなった地点がGeometryとほぼ同じだった

「Gradientは無限に細かく改善し続けるだろう」という仮説は、今回の実験では支持されなかったわけです。これは失敗ではなく、まさに実験結果です。

## Noiseは明確に別格

```text
accepted_steps = 210
candidate_evaluations = 33,312
final_error = 0.006566
```

Noiseは他のTargetより約2.5倍のStrokeを受け入れ、候補評価も約2.5倍行っています。それでも最終誤差は最も高い。

これはかなり分かりやすく、

> 高周波で局所的に変化するTargetは、現在の円形Stamp Action Spaceでは表現効率が悪い

と読めます。

Noiseは改善余地が多数あるので長く描き続けます。しかし、一筆ごとの改善が局所的で、完全には近づけない。

したがってNoiseは、

* 長く改善可能
* しかし最終精度は低い
* 多数の候補評価を消費する

という、現在のGreedy Painterにとって最も難しいTargetです。

## `accepted_steps`と`attempted_searches`の差も重要

例えばNoiseでは、

```text
accepted_steps = 210
attempted_searches = 347
```

です。

137回は、候補を探索したもののStrokeを採用しなかった検索です。

ただし、最後の12回だけが連続失敗だったはずなので、それ以前にも、

```text
改善なし
↓
次の探索で改善あり
↓
patienceをリセット
```

という局面が何度もあったことになります。

これはNoiseの探索地形が、

> 改善候補が疎らだが、完全には途切れない

状態だった可能性を示しています。

単にStroke数だけでなく、

```text
acceptance_rate
=
accepted_steps / attempted_searches
```

も有用です。

概算すると、

```text
flat      29%
geometry  67%
gradient  64%
noise     61%
```

です。

Flatの率が低いのは、5 Strokeで完全一致した後に12回失敗して終了するためなので、難しさを意味しません。一方、Geometry・Gradient・Noiseでは、探索成功率自体は意外に近いです。

## 今回の最も重要な観察

今回の順位は、単純に最終誤差だけを見ると、

```text
flat
gradient
geometry
noise
```

です。

制作コスト、つまりAccepted Stepsで見ると、

```text
flat
gradient
geometry
noise
```

で、同じ順序です。

ただしGeometryとGradientはほぼ同等です。

したがって現段階では、Target分類は次の三群に見えます。

```text
Easy
└── Flat

Middle
├── Geometry
└── Gradient

Hard
└── Noise
```

この結果はREADMEに、最初のBenchmark Resultとして載せてもよいくらいです。

そして次の実験として最も価値があるのは、Gradientだけ`epsilon`を一桁ずつ下げてみることです。

```bash
--epsilon 1e-4
--epsilon 1e-5
--epsilon 1e-6
--epsilon 1e-7
```

これで、

> Gradientは改善余地がないのか、それともepsilon以下の微小改善しか残っていないのか

を切り分けられます。

Noiseについては`max_steps`よりも、Brushの最小半径や候補数を変えた方が差が出そうです。今回の結果を見る限り、Termination-aware設計は、Targetごとの「最終誤差」だけでなく、**どれだけ長く改善を続けられるか**をかなり明瞭に可視化できています。
