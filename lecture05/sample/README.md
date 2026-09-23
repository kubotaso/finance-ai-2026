# 記法サンプル

第5回で出てくるMarkdownの記法を一通り使った原稿です。VS Codeで `report.md` を開き、プレビュー（⇧⌘V）を横に並べると、記号と見た目の対応が読めます。

## file

| file | 中身 |
|---|---|
| `report.md` | 原稿。使った記法の一覧が末尾にあります |
| `slides.md` | 同じ内容のMarp slide |
| `data/policy_rates.csv` | 日米の政策金利（月次、2015年1月〜2026年8月、140行） |
| `make_figure.py` | CSVから `figures/fig01_policy_rates.png` を作る |

変換した結果も置いてあります。元のMarkdownと見比べてください。

| 変換後のfile | 何から | 中身 |
|---|---|---|
| `report.docx` | `report.md` | Word。見出しstyleが入っています |
| `report.html` | `report.md` | browserで開く |
| `report.pdf` | `report.html` | Chromeで印刷したもの |
| `report.pptx` | `report_slides.md` | 長い説明をスライド用に整理した、編集可能なPandoc版 |
| `slides.pdf` | `slides.md` | Marpのslide |
| `slides.pptx` | `slides.md` | Marpの見た目のまま。各頁が画像で、文字は直せません |
| `slides_editable.pptx` | `slides_editable.md` | 日本語の折り返しを避けて整理したPandoc編集版。Marpとレイアウトは異なります |

## 動かす

```
python make_figure.py

pandoc report.md -o report.docx
pandoc report.md -o report.html --standalone --math-method=mathjax --toc --toc-depth=2 --metadata lang=ja
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --no-pdf-header-footer --print-to-pdf=report.pdf report.html

marp slides.md --pdf --allow-local-files --no-stdin

marp slides.md --pptx --allow-local-files --no-stdin
marp slides.md --pptx --pptx-editable --allow-local-files --no-stdin -o slides_editable.pptx
pandoc report_slides.md --slide-level=1 -o report.pptx
```

`report.pdf` はHTMLから作るので、その前の行のHTML変換を先に走らせます。PDFの2つはどちらもChromeを使います。入っていない場合でも、`.docx` とHTMLだけで記法の確認はできます。

## dataの出所

| 系列 | 出所 |
|---|---|
| 無担保コール翌日物（月平均） | 日本銀行 主要時系列統計データ表 FM02 |
| Federal Funds Rate（実効、月平均） | FRED `FEDFUNDS` |

元教材に保存されていた2015年以降の140か月分をコピーしています。今回の再取得はありません。原取得日の記録は配布CSVに含まれていないため未確認です。日本は市場金利、米国は実効FF金利の月平均で、政策の誘導目標そのものではありません。

日本銀行：https://www.boj.or.jp/statistics/market/short/mutan/index.htm
FRED：https://fred.stlouisfed.org/series/FEDFUNDS


## 改訂版の表示確認

文書原稿をそのままPPTXへ変換すると長いcodeや記法一覧がはみ出すため、report_slides.mdにスライド用の要約を保存しました。Marp editable変換は日本語テキストの折り返しによる重なりが解消しなかったため、配布用のslides_editable.pptxはslides_editable.mdをPandocで変換した編集版にしています。Marpの見た目を維持するslides.pdf・画像方式slides.pptxとはレイアウトが異なります。MacのLibreOfficeで描画を確認し、PowerPoint・Windowsでの同一表示は未確認です。

編集版の再生成は、Codexへ「slides_editable.mdを見出しレベル1でPPTXへ変換し、日本語表示を確認」と依頼できます。上のMarp editable commandは元の方式を試すための参考です。
