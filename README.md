# painting-environment-lab-termination-aware

> Painting until there is nothing worth painting.

固定ステップ数ではなく、**制作プロセス自身がEpisode長を決める**Greedy Painting Environmentの実験リポジトリです。

この版のテーマはTerminationです。Observation Designは実装せず、次の研究候補として最後に残します。

## このリポジトリで確かめること

従来のGreedy Painterは、Targetの性質にかかわらず指定された回数だけStrokeを実行します。その設計では、次の二つを区別できません。

1. まだ改善できるが、固定ステップ上限で打ち切られた
2. 現在のAction Spaceと探索方法では、もはや意味のある改善が見つからない

本リポジトリでは、`epsilon`、`patience`、`max_steps`を使って両者を観察可能にします。

```text
best improvement > epsilon
    └─ apply the stroke and continue

best improvement <= epsilon
    └─ keep the canvas unchanged and resample candidates

failed searches reach patience
    └─ stop: no_improvement

accepted strokes reach max_steps
    └─ stop: max_steps
```

`max_steps`は目標Episode長ではなく、計算を必ず止めるための安全装置です。

## 実装範囲

- Opaque Circle Stamp Brush
- Greedy candidate search
- Termination-aware episode loop
- `epsilon`
- `patience`
- `max_steps`
- `stop_reason`
- Flat / Geometry / Gradient / Noise Target
- Target画像と最終Canvasの保存
- Step log (`CSV`)
- Experiment summary (`JSON`)
- Error / improvement / brush-radius curve
- Target横断比較スクリプト
- Tests

## セットアップ

Ubuntuでは先に仮想環境機能を入れます。

```bash
sudo apt update
sudo apt install -y python3-venv
```

リポジトリ内で環境を作成します。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## 最小実行

```bash
painting-env-lab \
  --target gradient \
  --max-steps 2000 \
  --candidates 96 \
  --epsilon 1e-5 \
  --patience 12 \
  --output outputs/gradient
```

または、インストールせずモジュールとして実行できます。

```bash
PYTHONPATH=src python -m painting_env_lab.cli --target gradient
```

実行後、出力先に以下が生成されます。

```text
outputs/gradient/
├── target.png
├── final_canvas.png
├── steps.csv
├── summary.json
├── error_curve.png
├── improvement_curve.png
└── radius_curve.png
```

## Targetを比較する

```bash
python examples/compare_targets.py
```

同一設定で次を実行します。

```text
flat
geometry
gradient
noise
```

観察したい典型的な差は次です。

- Flatは少数の大Brushで早く停止するか
- Geometryは面を埋めた後、境界修正へ移るか
- Gradientは小さな改善を長く積み、`max_steps`まで消費するか
- Noiseは候補不足で早期停止するか、微小改善を延々続けるか

## Terminationの意味

この実装におけるStopは、Agentが明示的に選択するActionではありません。Greedy探索器が、現在のAction Spaceの中に十分価値のある次のStrokeを発見できなくなったときに終了します。

したがって、この段階で研究しているのは、

> Stop Actionの学習

ではなく、

> Action Space、candidate sampling、改善閾値から生まれるEpisodeの自然な長さ

です。

詳細は[`docs/termination-design.md`](docs/termination-design.md)を参照してください。

## 評価指標

最終誤差だけではなく、次を一緒に読みます。

| Metric | 意味 |
|---|---|
| `final_error` | 最終CanvasとTargetの差 |
| `accepted_steps` | 実際に採用されたStroke数 |
| `attempted_searches` | 候補再抽選を含む探索回数 |
| `candidate_evaluations` | 評価した候補Actionの総数 |
| `stop_reason` | `no_improvement`または`max_steps` |
| improvement curve | 改善量がどのように減衰したか |
| radius curve | 制作が大Brushから小Brushへ移ったか |

`accepted_steps`は、Targetを現在のBrushで表現するための一種の制作コストとして扱えます。

## ディレクトリ構成

```text
.
├── docs/
│   ├── experiment-notes.md
│   └── termination-design.md
├── examples/
│   └── compare_targets.py
├── outputs/
├── src/painting_env_lab/
│   ├── brush.py
│   ├── cli.py
│   ├── config.py
│   ├── experiment.py
│   ├── greedy.py
│   ├── metrics.py
│   ├── reporting.py
│   └── targets.py
└── tests/
```

## Tests

```bash
pytest
```

## Next Candidate: Observation Design

Observation Designはこのリポジトリには実装しません。Termination-aware版の結果を観察した後の、独立した次の候補です。

候補として、README上では次だけを記録します。

- Raw Target / Canvas
- Multi-resolution Image Pyramid
- TargetとCanvasの各解像度差分
- Agentが参照解像度を選択する設計
- Environment-provided observationとlearned representationの比較

この境界を保つことで、本リポジトリはTerminationの実験結果だけで完結します。

## Future Extensions

Terminationの延長としては、以下が考えられます。

- Stroke costを差し引いたutility
- Brush種類ごとのcost
- Wall-clockまたはcandidate-evaluation budget
- Learned Stop policy
- Behavior Cloning用のContinue / Stop label生成
- 複数seedでの停止分布

## License

MIT
