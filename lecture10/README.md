# 第10回　マクロ時系列データ・FRED・新聞記事検索・日銀API

最初の4本は、[講義PDF](lecture10.pdf) または [Markdown](lecture10.md) でまとめて読めます。

| 資料 | PDF・HTML | Markdown |
|---|---|---|
| マクロ時系列データの読み方 | [PDF](01_macro_timeseries.pdf) | [Markdown](01_macro_timeseries.md) |
| FREDをウェブで使う | [PDF](02_fred_web.pdf) | [Markdown](02_fred_web.md) |
| PythonでFREDのデータを取得し、図を描く | [PDF](03_fred_download.pdf) | [Markdown](03_fred_download.md) |
| 新聞記事の検索と、AIによるニュース検索の問題 | [PDF](04_news_search.pdf) | [Markdown](04_news_search.md) |
| 日銀APIで日本の金利を取得する | [HTML](05_boj_api.html) | [Markdown](05_boj_api.md) |

[example/fred_example.py](example/fred_example.py) は、FREDからCSVを取得してインフレ率と政策金利を描く作例です。[画面取得の参考スクリプト](example/fred_screenshots.py) と、[Codex](example/ai_news_test_codex.md)・[Claude](example/ai_news_test_claude.md)によるニュース検索の記録もあります。

[日銀APIの作例](example/boj/README.md)では、保存済みのデータから無担保コールO/N物レートの日次と月平均の図を作れます。

プログラムの実行にはPython、pandas、matplotlib、requestsを使います。画面取得の参考スクリプトはPlaywrightを使います。FREDの公開CSVの取得にはAPIキーは不要です。

フォルダをまとめて取得すると、Markdown内の図や作例も同じ配置で利用できます。
