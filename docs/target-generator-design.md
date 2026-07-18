今回の設計思想では、`--target`は**画像ファイルではなく、Target Generatorを指定する**という意味です。

例えば、

```bash
painting-env-lab --target gradient
```

は内部では概念的に

```python
target = GradientTargetGenerator(seed=...)
canvas = WhiteCanvas()
```

を実行して、

```
Target Image
      ↑
Gradient Generator
```

が毎回画像を生成しています。

つまり、

```
--target flat
```

なら

```
■■■■■■■■
■■■■■■■■
■■■■■■■■
```

のような画像を生成し、

```
--target geometry
```

なら

```
○
□
△
```

をランダム配置した画像を生成する。

```
--target gradient
```

なら

```
████
▓▓▓▓
▒▒▒▒
░░░░
```

という連続的なGradientを生成する。

---

## この設計にした理由

これは、

```
Target Generator
```

です。

最初から

```
images/
 dog.png
 cat.png
```

ではなく、

Environmentが

```
Target
```

まで生成する。

理由は

**再現性**

です。

例えば

```bash
painting-env-lab \
    --target gradient \
    --seed 42
```

なら

誰が実行しても

同じTargetになります。

---

## 将来はここにImageLoaderが加わる

だからTargetは

```
TargetProvider
```

という抽象になる。

```
TargetProvider

├── FlatGenerator
├── GeometryGenerator
├── GradientGenerator
├── NoiseGenerator
└── ImageLoader
```

ImageLoaderだけが

```
dog.png
```

などを読む。

他は全部コード生成。

---


---

## 抽象

実は、このリポジトリは**「画像を描く」リポジトリではない**ということです。

より正確には、

```
Target Generator
      ↓
Greedy Painter
      ↓
Termination
      ↓
Evaluation
```

という一つの実験系です。

つまり、画像は「入力データ」ではなく、**Environmentの一部**です。

---

### 改善

`--help`を充実させる。

例えば、

```bash
painting-env-lab --list-targets
```

で

```
Available Target Generators

flat
geometry
gradient
noise
```

を表示できるようにする。
