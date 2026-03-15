# Santa Lucia Highlands 調査報告書
# make ja                    → 日本語 PDF を生成（index 全体）
# make <file.adoc>           → 指定した .adoc だけの PDF を生成（out/<stem>.pdf ができる）

SOURCES = index-slh_ja.adoc
OUTDIR = out
PDF = $(OUTDIR)/index-slh_ja.pdf
HTML = $(OUTDIR)/index-slh_ja.html
PDF_THEME = ../../pdf-theme-ja.yml

.PHONY: ja html clean

# 日本語 PDF を生成（asciidoctor-pdf が必要: gem install asciidoctor-pdf）
ja: $(PDF)

$(PDF): $(SOURCES)
	@mkdir -p $(OUTDIR)
	asciidoctor-pdf -a pdf-theme=$(PDF_THEME) -D $(OUTDIR) index-slh_ja.adoc
	@echo "Generated: $(PDF)"

# 単一ファイルの PDF: make chapters/history_ja.adoc → out/chapters/history_ja.pdf
ADOC_FILES = $(wildcard *.adoc chapters/*.adoc)
.PHONY: $(ADOC_FILES)

# make <file.adoc> 用のルール（phony なので常にレシピ実行）
$(ADOC_FILES):
	@mkdir -p $(OUTDIR)/$(dir $@)
	asciidoctor-pdf -a pdf-theme=$(PDF_THEME) -o $(OUTDIR)/$(patsubst %.adoc,%.pdf,$@) $@
	@echo "Generated: $(OUTDIR)/$(patsubst %.adoc,%.pdf,$@)"

# 参考: HTML を生成
html: $(HTML)

$(HTML): $(SOURCES)
	@mkdir -p $(OUTDIR)
	asciidoctor -b html5 -D $(OUTDIR) index-slh_ja.adoc
	@echo "Generated: $(HTML)"

clean:
	rm -rf $(OUTDIR)
