# Termination Design

## Fixed budgetからprocess-awareな終了へ

従来の最小実装では、Episodeは固定ステップ数で終了する。

```text
paint for N steps
then stop
```

このリポジトリでは、`max_steps`を終了目標ではなく安全上限として扱う。
Greedy Painterは、次の一筆に十分な改善価値がある限り描き続ける。

## 判定

各探索回で現在誤差と最良候補の誤差を比較する。

```text
best_improvement = current_error - best_candidate_error
```

- `best_improvement > epsilon`: 一筆を採用する
- `best_improvement <= epsilon`: Canvasを変えず、候補を再抽選する
- この失敗が`patience`回連続する: `no_improvement`で終了する
- 採用Stroke数が`max_steps`に達する: `max_steps`で終了する

## なぜCanvasを変えずに再探索するのか

改善価値のないStrokeを実行すると、終了判定そのものがCanvasを傷つける。
`patience`は「悪いStrokeを許容する回数」ではなく、「同じ状態から候補集合を再抽選する回数」である。

## 観察対象

- final error
- accepted steps
- attempted searches
- candidate evaluations
- stop reason
- improvement curve
- brush-radius curve

Gradient Targetが`max_steps`を消費し、Flat Targetが早期終了するなら、それはTargetとAction Spaceの相性の差として読める。
