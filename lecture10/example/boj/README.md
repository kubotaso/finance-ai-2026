# 日銀API：短期金利の日次推移と月平均

[第10回（5）の本文](../../05_boj_api.md)の作例です。`boj_example.py` は日銀APIの `getDataCode` から無担保コールO/N物レート（平均値）を取得し、日次と月平均の図を作ります。APIキーは使いません。

| 取得条件 | 値 |
|---|---|
| データベース | `FM01` |
| 系列コード | `STRDCLUCON` |
| 期間 | 2024年1月〜2025年12月 |
| 単位・頻度 | 年率%、日次 |

## 配置と実行

このフォルダの中身を `金融論/Lecture10/boj_rate/` にコピーして実行できます。スクリプトは自分のファイルがあるフォルダを基準に入出力するので、実行時の作業ディレクトリには依存しません。PythonのpandasとMatplotlibを使います。

```sh
python boj_example.py
```

保存済みの `raw/call_rate.json` があれば、APIにアクセスせずに再実行します。`--refresh` を付けると日銀から取得し直します。日次系列でも、取得期間は `202401` のように年月で指定します。

## 保存されるもの

- `raw/call_rate.json`：取得した応答です。
- `raw/request.json`：取得条件・URL・日時です。
- `data/call_rate.csv`：日付と日次金利です。
- `data/call_rate_monthly.csv`：各月の平均金利と観測数です。
- `figures/call_rate.png`：日次グラフです。
- `figures/call_rate_monthly.png`：月平均のグラフです。
- `settings.md`：系列情報と確認結果です。

2026年11月4日に取得した応答には731暦日、488個の観測値があります。休日などの `null` はCSVに欠損として残し、日次グラフでは観測値のある日を結びます。月平均は各月の観測値の単純平均です。2026年11月14日に第10回へ移し、第12回の共通コードへの依存を外しました。

仕様は[公式APIマニュアル](https://www.stat-search.boj.or.jp/info/api_manual.pdf)を参照できます。
