# 第11回　R入門：株価データを読む、選ぶ、集計する

講義本文は [PDF](lecture11.pdf)、[Markdown](lecture11.md)、[HTML](lecture11.html) で読めます。

Rの実行環境、基本文法、base Rとtidyverse、仮想の株価CSVの集計、ggplot2による作図、J-Quantsへの接続を扱います。

## 演習ファイル

| ファイル | 内容 |
|---|---|
| [workbook.Rmd](workbook/workbook.Rmd)・[実行結果](workbook/workbook.html) | 説明とコードを順に読む演習 |
| [workbook.R](workbook/workbook.R) | 演習をまとめて実行するスクリプト |
| [01_compare_editors.R](workbook/01_compare_editors.R) | 実行環境を比べる短い計算と作図 |
| [02_base_r_and_tidyverse.R](workbook/02_base_r_and_tidyverse.R) | 同じ表を2通りの書き方で操作 |
| [03_jquants_auto.R](workbook/03_jquants_auto.R) | 自動車3社の株価取得と比較 |
| [04_ggplot_prices.R](workbook/04_ggplot_prices.R) | 型の変換・収益率・ggplot2の作図 |
| [data/prices.csv](workbook/data/prices.csv)・[prices_short.csv](workbook/data/prices_short.csv) | 第6回と同じ仮想の株価CSV |

`金融論/Lecture11` を作り、`workbook/` の中のファイルと `data/` をコピーすると、本文の相対パスで実習できます。実行結果は `output/` に保存されます。

基本演習にはtidyverse、R MarkdownのHTML作成にはrmarkdownとPandocを使います。J-Quantsの追加例にはjsonliteと自分のAPIキーを使います。環境の準備はCodexに頼めます。

`assets/` は講義本文の図と画面です。Markdown・HTMLを読むときは、同じフォルダ構成で保存すると画像も表示されます。
