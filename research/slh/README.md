# Wine Research - Santa Lucia Highlands

## 概要

カリフォルニア州 Monterey County の **Santa Lucia Highlands（サンタ・ルシア・ハイランズ）** AVA を対象に、ワイン産地としての成り立ち・条件・生産者・銘柄を調査し、日本語の調査報告書としてまとめた。調査項目は、地形・畑・葡萄品種・ワイナリー・醸造家・ビンテージと品種による特性に加え、歴史・沿革、AVA の法的位置づけ、気候・土壌、代表的なラベル、参考文献を章立てして整理している。

報告書は `index-slh_ja.adoc` を起点に `chapters/` の各章を `include` した一冊で、`make ja` により日本語 PDF、`make html` により HTML を生成する。

## 構成

| ファイル・ディレクトリ | 説明 |
|------------------------|------|
| README.md | 本説明（このファイル） |
| PLAN.md | 調査報告書の作成計画・調査項目・推奨項目 |
| index-slh_ja.adoc | 本体。表紙・目次・chapters の include |
| chapters/*.adoc | 各章（歴史・AVA・地形・気候土壌・畑・品種・ワイナリー・醸造家・ヴィンテージ・銘柄・参考文献） |
| BUILD.adoc | ビルド手順（HTML / PDF） |
| Makefile | `make ja` で日本語 PDF、`make html` で HTML を生成 |
| out/ | ビルド出力（`index-slh_ja.pdf`, `index-slh_ja.html`） |

## ビルド

### 前提

- Asciidoctor がローカル環境にインストールされていること。
  - Ruby 版 asciidoctor の例: `gem install asciidoctor`

### Makefile を使ったビルド

`research/slh` で次を実行する。

| コマンド | 説明 |
|----------|------|
| `make ja` | 日本語 PDF を生成（`out/index-slh_ja.pdf`） |
| `make html` | HTML を生成（`out/index-slh_ja.html`） |
| `make <file.adoc>` | 指定した `.adoc` だけの PDF を生成（例: `make chapters/history_ja.adoc` → `out/chapters/history_ja.pdf`） |
| `make clean` | `out/` ディレクトリを削除 |

PDF には `../../pdf-theme-ja.yml` のテーマが適用される。

### HTML へのビルド

`research/slh` で次を実行する。

```shell
cd research/slh
asciidoctor -b html5 -D out index-slh_ja.adoc
```

- `out/index-slh_ja.html` が生成される。

### PDF へのビルド（任意）

asciidoctor-pdf を利用する場合の例。

```shell
gem install asciidoctor-pdf
cd research/slh
asciidoctor-pdf -D out index-slh_ja.adoc
```

- `out/index-slh_ja.pdf` が生成される。
