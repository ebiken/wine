Santa Lucia Highlands 調査報告書 作成計画

## 目的・前提

- **対象**: Santa Lucia Highlands（サンタ・ルシア・ハイランズ）のワインに関する調査報告書
- **言語**: 日本語
- **形式**: AsciiDoc（`_ja.adoc`）、章は [research/slh/chapters/](research/slh/chapters/) 配下に配置
- **成果物**: [research/slh/index-slh_ja.adoc](research/slh/index-slh_ja.adoc) が chapters/ を include して一冊にまとめる
- **参照**: [.cursor/rules/documentation.mdc](.cursor/rules/documentation.mdc) の命名・形式ルールに従う

---

## 調査項目（README 記載）

| # | 項目 | 想定章・ファイル |
|---|------|------------------|
| 1 | 地形 | chapters/terrain_ja.adoc |
| 2 | 畑（ヴィンヤード） | chapters/vineyards_ja.adoc |
| 3 | 葡萄品種 | chapters/grape-varieties_ja.adoc |
| 4 | ワイナリー | chapters/wineries_ja.adoc |
| 5 | 醸造家 | chapters/winemakers_ja.adoc |
| 6 | ビンテージと葡萄品種による特性 | chapters/vintage-variety_ja.adoc |

---

## 推奨追加項目

README に明示されていないが、産地レポートとして有用な項目。

| # | 項目 | 内容イメージ | 想定章・ファイル |
|---|------|--------------|------------------|
| 7 | 歴史・沿革 | 栽培・ワイン造りの始まり、AVA 認定経緯 | chapters/history_ja.adoc |
| 8 | 気候・土壌 | 地形と別に気候帯・降水量・土壌タイプを整理 | chapters/climate-soil_ja.adoc |
| 9 | AVA・法的位置づけ | 認定年、境界、サブ区域の有無、規制 | chapters/ava_ja.adoc |
| 10 | 代表的なラベル・銘柄 | 産地を代表するワイン・キュヴェの整理 | chapters/notable-labels_ja.adoc |
| 11 | 参考文献・情報源 | 一次・二次ソースの一覧と引用方針 | chapters/references_ja.adoc |

- **歴史**: 他章の背景として「なぜこの産地が成立したか」を書く。
- **気候・土壌**: 地形章と重ならないよう「数値・分類」に寄せるか、地形章に「気候・土壌」節を入れるかは執筆時に判断。
- **参考文献**: 調査の再現性と信頼性のため、早めに方針を決めておくことを推奨。

---

## ドキュメント構成

```
research/slh/
├── README.md
├── PLAN.md
├── index-slh_ja.adoc          # 表紙・目次・chapters の include
└── chapters/
    ├── terrain_ja.adoc
    ├── vineyards_ja.adoc
    ├── grape-varieties_ja.adoc
    ├── wineries_ja.adoc
    ├── winemakers_ja.adoc
    ├── vintage-variety_ja.adoc
    ├── history_ja.adoc        # 推奨
    ├── climate-soil_ja.adoc   # 推奨
    ├── ava_ja.adoc            # 推奨
    ├── notable-labels_ja.adoc # 推奨
    └── references_ja.adoc     # 推奨
```

- 章の並びは「概説（歴史・AVA・地形・気候・土壌）→ 畑・品種 → 生産者（ワイナリー・醸造家）→ 特性・銘柄 → 参考文献」を想定。index の include 順で制御する。

---

## 実施ステップ

1. **PLAN.md の作成**  
   本計画を [research/slh/PLAN.md](research/slh/PLAN.md) に保存する。

2. **index-slh_ja.adoc のひな形作成**  
   表紙・タイトル・目次プレースホルダと、上記章の `include::chapters/xxx_ja.adoc[]` を並べる。

3. **chapters/ と各章ファイルの作成**  
   - 必須 6 章 + 推奨 5 章の adoc ファイルを用意。  
   - 各ファイルは「# 章タイトル」と簡単なリード文のみでよい（後から本文を充実させる）。

4. **調査・執筆**  
   各章ごとに情報収集し、README の調査項目と推奨項目に沿って本文を書く。references_ja.adoc で情報源を明示する。

5. **ビルド・確認**  
   AsciiDoc で index-slh_ja.adoc をビルドし、PDF または HTML で体裁・リンクを確認する。

---

## 注意事項

- ファイルはすべて `research/slh/` 以下に置き、他フォルダは参照しない（README 方針）。
- 日本語執筆・`_ja.adoc` サフィックスは documentation ルールに従う。
- 推奨項目のうち「気候・土壌」は、地形章と統合する場合は chapters を 1 本にまとめ、index の include を 1 つにしてもよい。

