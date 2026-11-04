# 第10回　マクロ時系列データ・FRED・新聞記事検索

全体をまとめて読む場合は、[講義PDF](lecture10.pdf) または [Markdown](lecture10.md) を開きます。

| 資料 | PDF | Markdown |
|---|---|---|
| マクロ時系列データの読み方 | [PDF](01_macro_timeseries.pdf) | [Markdown](01_macro_timeseries.md) |
| FREDをウェブで使う | [PDF](02_fred_web.pdf) | [Markdown](02_fred_web.md) |
| PythonでFREDのデータを取得し、図を描く | [PDF](03_fred_download.pdf) | [Markdown](03_fred_download.md) |
| 新聞記事の検索と、AIによるニュース検索の問題 | [PDF](04_news_search.pdf) | [Markdown](04_news_search.md) |

[example/fred_example.py](example/fred_example.py) は、FREDからCSVを取得してインフレ率と政策金利を描く作例です。[画面取得の参考スクリプト](example/fred_screenshots.py) と、[Codex](example/ai_news_test_codex.md)・[Claude](example/ai_news_test_claude.md)によるニュース検索の記録もあります。

プログラムの実行にはPython、pandas、matplotlib、requestsを使います。画面取得の参考スクリプトはPlaywrightを使います。FREDの公開CSVの取得にはAPIキーは不要です。

フォルダをまとめて取得すると、Markdown内の図や作例も同じ配置で利用できます。
