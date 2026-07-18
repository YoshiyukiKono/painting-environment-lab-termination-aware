# Experiment Notes

## 最初に比較するTarget

| Target | 主に要求される性質 | 予想される終了挙動 |
|---|---|---|
| Flat | 大面積を少数Strokeで覆う | 早い終了 |
| Geometry | 面と境界の両方を扱う | 中程度 |
| Gradient | 小さな改善を長く積む | 長いTail、上限到達の可能性 |
| Noise | 高周波構造と候補探索 | 早期停滞または非効率な長期化 |

## パラメータSweep候補

- `epsilon`: 何を「描く価値がある」とみなすか
- `patience`: 候補集合の偶然による誤終了をどこまで避けるか
- `candidates_per_search`: 1探索の質と計算量
- `max_steps`: 安全上限
- Brush radius range: Target表現効率

## 解釈上の注意

`max_steps`到達は、単純に「もっと描けばよい」とは限らない。

- Action Spaceが非効率
- `epsilon`が小さすぎる
- 小さな改善候補が常に偶然見つかる
- Candidate samplingが偏っている

という可能性を切り分ける必要がある。
