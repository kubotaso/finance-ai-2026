# 日銀APIの作例

- 系列：無担保コールＯ／Ｎ物レート／平均値 日次／金利（FM01 / STRDCLUCON）
- 期間：2024年1月〜2025年12月、日次、単位：年率%。市場で成立した平均金利。
- 暦日731行、観測値488行。休日などのnullはCSVで欠損として保持し、図は観測のある日を結ぶ。
- 最初：2024-01-04 -0.021%、最後：2025-12-30 0.727%
- 月平均：各月の観測値の単純平均。data/call_rate_monthly.csvに平均と観測数を保存。
- 図：figures/call_rate.png、figures/call_rate_monthly.png
- APIキーは不要。取得条件と日時：raw/request.json
- API仕様：https://www.stat-search.boj.or.jp/info/api_manual.pdf
