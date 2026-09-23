"""J-Quantsで、トヨタ自動車の2025年10月の日次株価を取得し、表と図にする。

このscriptは、第8回の「Codexに取得を頼む」の依頼文をそのまま1つのPython fileにしたものです。
上から順に読むと、APIで株価を取るときに何が起きているかが分かります。

実行のしかた:
    python toyota_oct2025.py

  1. API keyを環境変数 JQUANTS_API_KEY に入れておくと、そのまま動きます。
     入れていなければ、実行時に非表示の入力欄が出るので、そこに貼り付けます。
     keyはこのfileにも、出力fileにも書き込みません。
  2. output/ folderに、表のCSVと図のPNGができます。

必要なlibrary: requests, pandas, matplotlib（pip install requests pandas matplotlib）
"""

# ----------------------------------------------------------------------
# 0. 準備：libraryの読み込み
# ----------------------------------------------------------------------
# requests   : インターネット越しにAPIへリクエストを送る
# pandas     : 返ってきたデータを表（DataFrame）として扱う
# matplotlib : 図を描く
# os/getpass : API keyを環境変数か非表示入力から受け取る
# pathlib    : 出力folderを作る
import os
from getpass import getpass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests

# ----------------------------------------------------------------------
# 1. 取得の条件を決める
# ----------------------------------------------------------------------
# J-Quantsの銘柄コードは、証券コード4桁の末尾に0を付けた5桁です。
# トヨタ自動車の証券コードは7203なので、"72030" になります。
CODE = "72030"
START = "2025-10-01"
END = "2025-10-31"

# API V2の入口（base URL）。この後ろに /equities/master などを付けて使います。
BASE = "https://api.jquants.com/v2"

# 出力先。なければ作ります。
OUT = Path("output")
OUT.mkdir(exist_ok=True)

# ----------------------------------------------------------------------
# 2. API keyを受け取る
# ----------------------------------------------------------------------
# API keyは、J-Quantsに「誰の依頼か」を伝えるパスワードのような文字列です。
# codeの中に直接書くと、fileを渡した相手にkeyも渡ってしまいます。
# そこで、環境変数に入っていればそれを使い、なければ画面に出ない入力欄で受け取ります。
api_key = os.environ.get("JQUANTS_API_KEY", "").strip()
if not api_key:
    api_key = getpass("J-Quants API key（入力は表示されません）: ").strip()
if not api_key:
    raise SystemExit("API keyが空です。J-Quantsのマイページで発行したkeyを入力します。")


# ----------------------------------------------------------------------
# 3. APIに依頼を送る関数
# ----------------------------------------------------------------------
def fetch(endpoint, params):
    """J-Quants API V2から、条件に合う行をすべて取り出してDataFrameで返す。

    endpoint : "/equities/master" のような、取りたいデータの種類
    params   : {"code": "72030", "from": "2025-10-01", ...} のような条件

    仕組み:
      - requests.get が、BASE + endpoint のURLに params を付けてリクエストを送ります。
        実際に送られるURLは、例えば次のような形です。
        https://api.jquants.com/v2/equities/bars/daily?code=72030&from=2025-10-01&to=2025-10-31
      - headers の x-api-key に、API keyを載せます。
      - 返ってくるのはJSONという形式の文字列で、response.json() で辞書に変わります。
        {"data": [{"Date": "2025-10-01", "Code": "72030", "C": ...}, ...]} という形で、
        "data" の中に1日1行の辞書が並んでいます。
      - 件数が多いと1回で全部は返らず、"pagination_key" が付いてきます。
        その値を条件に足してもう一度送ると、続きが返ります。なくなるまで繰り返します。
    """
    params = dict(params)
    rows = []
    while True:
        response = requests.get(
            BASE + endpoint,
            params=params,
            headers={"x-api-key": api_key},
            timeout=30,
        )
        # 200以外は失敗です。よくあるものを日本語にしておきます。
        if response.status_code != 200:
            reasons = {
                400: "銘柄コード・日付・取得できる期間（Freeプランは12週間前まで）を確認します。",
                401: "API keyが違います。",
                403: "このプランでは取れないデータか期間です。",
                429: "回数制限です。1分ほど待ってからやり直します。",
            }
            raise SystemExit(
                f"HTTP {response.status_code}: "
                + reasons.get(response.status_code, "サービスの状態を確認します。")
            )
        payload = response.json()
        rows.extend(payload["data"])
        cursor = payload.get("pagination_key")
        if not cursor:
            break
        params["pagination_key"] = cursor
    if not rows:
        raise SystemExit("該当データが0件です。銘柄・期間を確認します。")
    # 辞書のlistをDataFrameにすると、辞書のkeyが列名になります。
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
# 4. 会社名と銘柄コードを確かめる
# ----------------------------------------------------------------------
# /equities/master は上場銘柄の一覧です。code と date を渡すと、その日時点の
# 会社名（CoName）、33業種（S33Nm）、市場区分（MktNm）が1行返ります。
# 「72030 は本当にトヨタ自動車か」を、株価を取る前にここで確かめます。
master = fetch("/equities/master", {"code": CODE, "date": START})
company_name = master.loc[0, "CoName"]

print("=== 会社の確認 ===")
print(master[["Date", "Code", "CoName", "S33Nm", "MktNm"]].to_string(index=False))
print()

# ----------------------------------------------------------------------
# 5. 日次株価を取得して、表にする
# ----------------------------------------------------------------------
# /equities/bars/daily は日々の四本値です。code と from, to を渡します。
# 返ってくる列のうち、この回で使うのは次の4つです。
#   Date : 取引日
#   C    : 終値（その日の最後の取引価格。円）
#   Vo   : 出来高（その日に売買された株数）
#   AdjC : 調整済み終値（株式分割などをそろえた終値。円）
bars = fetch("/equities/bars/daily", {"code": CODE, "from": START, "to": END})

# Date は文字列で届くので、日付型に直してから日付順に並べます（第7回と同じ手順）。
bars["Date"] = pd.to_datetime(bars["Date"])
bars = bars.sort_values("Date").reset_index(drop=True)

# 必要な列だけを残し、読みやすい列名を付けた表を作ります。
table = bars[["Date", "C", "Vo", "AdjC"]].rename(
    columns={"Date": "日付", "C": "終値（円）", "Vo": "出来高（株）", "AdjC": "調整済み終値（円）"}
)
table["日付"] = table["日付"].dt.strftime("%Y-%m-%d")

print(f"=== {company_name}（{CODE}）の日次株価 {START} 〜 {END} ===")
print(table.to_string(index=False))
print()
print(f"行数: {len(table)}（2025年10月の東証の営業日は22日）")
print()

# 表をCSVに保存します。encoding を utf-8-sig にすると、Excelで開いても文字化けしません。
csv_path = OUT / f"toyota_{START}_{END}.csv"
table.to_csv(csv_path, index=False, encoding="utf-8-sig")

# ----------------------------------------------------------------------
# 6. 調整済み終値の折れ線グラフ
# ----------------------------------------------------------------------
# fig が図全体、ax が線を描く座標軸です。
# タイトルに会社名と期間、縦軸に単位、右下に出所を入れておくと、図だけを見ても
# 何の数値か分かります。日本語のfontがないPCでも崩れないよう、図の文字は英語にしています。
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(bars["Date"], bars["AdjC"], marker="o")
ax.set_title(f"Toyota Motor ({CODE}): adjusted close, {START} to {END}")
ax.set_xlabel("Date")
ax.set_ylabel("Yen per share")
ax.grid(True, linewidth=0.3)
fig.autofmt_xdate()  # 日付のラベルを斜めにして重ならないようにする
fig.text(0.99, 0.01, "Source: J-Quants API V2", ha="right", fontsize=8)
fig.tight_layout()

png_path = OUT / f"toyota_{START}_{END}_adjc.png"
fig.savefig(png_path, dpi=150)
plt.show()

# ----------------------------------------------------------------------
# 7. 結果の確認
# ----------------------------------------------------------------------
# 図の1点と表の同じ日の値が一致することを、最大の日で確かめます。
i = bars["AdjC"].idxmax()
print("=== 確認 ===")
print(f"調整済み終値の最大: {bars.loc[i, 'Date'].date()} の {bars.loc[i, 'AdjC']:.1f} 円")
print(f"表を保存しました: {csv_path}")
print(f"図を保存しました: {png_path}")
print()
print("注意: J-Quantsから取得したデータそのものを、他の人に配布・公開することはできません。")
