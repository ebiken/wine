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

- 日本語 PDF: `make ja`（asciidoctor-pdf が必要: `gem install asciidoctor-pdf`）
- HTML: `make html`

詳細は BUILD.adoc を参照。
