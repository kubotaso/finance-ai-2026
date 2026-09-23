"""第10回ワークブック：架空の数字で指標の式を確かめ、トヨタ自動車の決算と株価で計算する。

workbook/ folderで実行します:
    python workbook.py

1節は架空の数字だけで、API keyは要りません。2節でJ-Quants APIからトヨタ自動車の決算サマリーと株価を
取得します。取得のcodeは第8回・第9回と同じ形で、このfileの2-0に書いてあります。実行するたびに
APIから取り直します。取得したデータは、そのままの形で他の人に配布しません。
"""

import pandas as pd

# ------------------------------------------------------------
# 1-1 時価総額、BPS、PBR

price = 1000            # 株価（円）
shares = 1_000_000      # 株数（株）
equity = 500_000_000    # 自己資本（円）

market_cap = price * shares
bps = equity / shares

print("時価総額:", market_cap)
print("BPS:", bps)
print("PBR（時価総額 / 自己資本）:", market_cap / equity)
print("PBR（株価 / BPS）:", price / bps)

# ------------------------------------------------------------
# 1-2 株式分割

split = 2
price_after = price / split
shares_after = shares * split
bps_after = equity / shares_after

print("分割後の株価:", price_after)
print("分割後のBPS:", bps_after)
print("分割後の株価 / 分割後のBPS:", price_after / bps_after)
print("分割後の株価 / 分割前のBPS:", price_after / bps)

# ------------------------------------------------------------
# 1-3 ROEと自己資本の大きさ

net_income = 50_000_000
print("ROE:", net_income / equity)

equity_small = 250_000_000
print("自己資本が半分のときのROE:", net_income / equity_small)

# ------------------------------------------------------------
# 1-4 デュポン分解

sales = 1_000_000_000
total_assets = 1_000_000_000

margin = net_income / sales             # 売上高純利益率
turnover = sales / total_assets         # 総資産回転率
leverage = total_assets / equity        # 財務レバレッジ

print("売上高純利益率:", margin)
print("総資産回転率:", turnover)
print("財務レバレッジ:", leverage)
print("自己資本比率:", equity / total_assets)
print("3つの積:", margin * turnover * leverage)
print("直接計算したROE:", net_income / equity)

# ------------------------------------------------------------
# 1-5 期末・期首・平均の自己資本

equity_begin = 470_000_000
equity_avg = (equity_begin + equity) / 2

print("期末の自己資本で割ったROE:", net_income / equity)
print("期首の自己資本で割ったROE:", net_income / equity_begin)
print("平均の自己資本で割ったROE:", net_income / equity_avg)

# ------------------------------------------------------------
# 1-6 EPS・DPSと、PER・PBR・配当利回り

dividends = 20_000_000

eps = net_income / shares      # 1株当たり純利益
dps = dividends / shares       # 1株当たり配当
per = price / eps
pbr = price / bps
dividend_yield = dps / price

print("EPS:", eps, " DPS:", dps)
print("PER:", per, " PBR:", pbr, " 配当利回り:", dividend_yield)

# ------------------------------------------------------------
# 1-7 PBR＝PER×ROE

roe_end = net_income / equity

print("PER × ROE（期末の自己資本）:", per * roe_end)
print("PBR:", pbr)
print("PER × ROE（平均の自己資本）:", per * net_income / equity_avg)

# ------------------------------------------------------------
# 1-8 割引率が違えばPBRも違う

def pbr_no_growth(roe, k, payout=1.0):
    """利益が毎年同じで、割合payoutを配当する場合のPBR（PER = payout / k）"""
    return payout / k * roe

print("A社 ROE 10%、k 5%:", round(pbr_no_growth(0.10, 0.05), 2))
print("B社 ROE 15%、k 10%:", round(pbr_no_growth(0.15, 0.10), 2))

# ------------------------------------------------------------
# 2-0 J-Quants APIから取得する準備
# ------------------------------------------------------------
# 第8回の toyota_oct2025.py 、第9回の6節と同じ仕組みです。URLに条件を付けて送ると、JSONが返ってきます。
# その "data" の中身（1行が1つの辞書）をDataFrameにします。
# API keyは、環境変数 JQUANTS_API_KEY にあればそれを使い、なければ最初の取得のときに
# 非表示の入力欄で受け取ります。このfileにも出力にも書き込みません。
# 実行するたびにAPIから取り直します。開示が追加・訂正されていれば、行や数値が前回と変わります。
# 取得したデータは、J-Quantsの利用条件により、そのままの形で他の人に配布しません。
#
# 応答が200以外のとき fetch は「HTTP 4xx」で止まります。よくある原因は次のとおりです。
#   400  銘柄コード・日付・取得できる期間（Freeプランは12週間前まで）が違う
#   401  API keyが違う
#   403  このプランでは取れないデータか期間
#   429  回数制限。Freeプランは1分に5回まで。少し待ってからやり直す
#
# 行を選んで Shift+Enter で使うときは、先に下の import と BASE・api_key の行を送り、
# 次に def の行から関数の終わりまでをまとめて送ります。関数の中の数行だけを送ると SyntaxError になります。
# 1行が長かったり、複数の関数を一度に選んだりすると、terminalの行編集が途中で崩れることがあります。
# 一度送った定義はそのterminalを閉じるまで残るので、以後は fetch(...) の行だけを送れば済みます。
import os
from getpass import getpass

import requests

BASE = "https://api.jquants.com/v2"
api_key = os.environ.get("JQUANTS_API_KEY", "")


def fetch(endpoint, params):
    """J-Quants API V2に条件を送り、返ってきた全行をDataFrameにする。"""
    global api_key
    if not api_key:
        api_key = getpass("J-Quants API key: ").strip()
    params = dict(params)
    rows = []
    while True:
        r = requests.get(BASE + endpoint, params=params,
                         headers={"x-api-key": api_key}, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}")
        payload = r.json()
        rows.extend(payload["data"])
        cursor = payload.get("pagination_key")
        if not cursor:
            break
        params["pagination_key"] = cursor
    if not rows:
        raise RuntimeError("0件です。銘柄・期間を確認します。")
    return pd.DataFrame(rows)

# ------------------------------------------------------------
# 2-1 決算サマリーと株価を読み込む
# ------------------------------------------------------------
# /fins/summary は決算短信のサマリー（開示1回 = 1行）、/equities/bars/daily は日次の株価です。
# 銘柄コードは証券コード7203の末尾に0を付けた5桁です。株価は評価日を含む2026年6月の分だけ取ります。
code = "72030"
fins = fetch("/fins/summary", {"code": code})
daily = fetch("/equities/bars/daily",
              {"code": code, "from": "2026-06-01", "to": "2026-06-19"})

# 読んだ直後はすべて文字列なので、使う列を日付型と数値型に直す（第7回・第9回と同じ手順）
for col in ["DiscDate", "CurPerEn", "CurFYEn"]:
    fins[col] = pd.to_datetime(fins[col], errors="coerce")
for col in ["Sales", "NP", "TA", "Eq", "ShEq", "EqAR", "EPS", "BPS", "DivAnn", "ShOutFY", "TrShFY", "ROE"]:
    fins[col] = pd.to_numeric(fins[col], errors="coerce")
fins = fins.sort_values(["DiscDate", "CurPerEn"]).reset_index(drop=True)
daily["Date"] = pd.to_datetime(daily["Date"])
for col in ["C", "AdjFactor", "AdjC"]:
    daily[col] = pd.to_numeric(daily[col], errors="coerce")

print(fins[["DiscDate", "DocType", "CurPerType", "CurPerEn", "CurFYEn"]])
# 1行が1回の開示。四半期（1Q〜3Q）と通期（FY）が混ざっている。金額の列は円単位。

# ------------------------------------------------------------
# 2-2 通期の行を選ぶ
# ------------------------------------------------------------
# 通期（FY）・連結（Consolidated）の決算短信で、評価日2026-06-19までに開示された行を残す。
# 同じ決算期の開示が2回以上あれば（訂正など）、最後の開示を使う。第11回で同じ手順を多くの会社に広げる。
eval_date = "2026-06-19"
fy = fins[(fins["CurPerType"] == "FY")
          & fins["DocType"].str.startswith("FYFinancialStatements_Consolidated_")
          & (fins["DiscDate"] <= eval_date)]
fy = fy.sort_values(["CurPerEn", "DiscDate"]).drop_duplicates("CurPerEn", keep="last")
print(fy[["DiscDate", "CurFYEn", "DocType", "Sales", "NP", "TA", "Eq", "ShEq", "EPS", "BPS", "DivAnn"]])
# 2025年3月期と2026年3月期の2行。NP は親会社の所有者に帰属する当期利益、Eq は純資産、ShEq は自己資本。

# ------------------------------------------------------------
# 2-3 評価日の株価

day = daily[daily["Date"] == "2026-06-19"]
price = float(day["C"].iloc[0])
print(day[["Date", "Code", "C", "AdjFactor", "AdjC"]])

# ------------------------------------------------------------
# 2-4 自己資本とBPSの定義を確かめる

if len(fy) < 2: raise ValueError("評価日までの連結通期が2期必要です")
cur, prev = fy.iloc[-1], fy.iloc[-2]
print(cur[["Code","CurPerEn","DiscDate","DocType"]])

shares = cur["ShOutFY"] - cur["TrShFY"]     # 期末発行済株式数 - 期末自己株式数
print("株数:", shares)
print("BPS（決算短信）:", cur["BPS"])
print("ShEq / 株数:", round(cur["ShEq"] / shares, 2))
print("Eq / 株数:", round(cur["Eq"] / shares, 2))

# ------------------------------------------------------------
# 2-5 ROEとデュポン分解

net_income = cur["NP"]
sales = cur["Sales"]
total_assets = cur["TA"]
equity = cur["ShEq"]
equity_prev = prev["ShEq"]

margin = net_income / sales
turnover = sales / total_assets
leverage = total_assets / equity

print("売上高純利益率:", round(margin, 4))
print("総資産回転率:", round(turnover, 4))
print("財務レバレッジ:", round(leverage, 4))
print("3つの積:", round(margin * turnover * leverage, 4))
print("ROE（期末の自己資本）:", round(net_income / equity, 4))
print("ROE（平均の自己資本）:", round(net_income / ((equity_prev + equity) / 2), 4))
print("ROE（決算サマリーの列）:", cur["ROE"])

# ------------------------------------------------------------
# 2-6 PER・PBR・配当利回り

per = price / cur["EPS"] if pd.notna(cur["EPS"]) and cur["EPS"] > 0 else float("nan")
pbr = price * shares / cur["ShEq"] if cur["ShEq"] > 0 and shares > 0 else float("nan")
dividend_yield = cur["DivAnn"] / price
roe_end = net_income / equity

print("PER:", round(per, 2))
print("PBR:", round(pbr, 4))
print("配当利回り:", round(dividend_yield, 4))
print("PER × ROE（期末）:", round(per * roe_end, 4))
