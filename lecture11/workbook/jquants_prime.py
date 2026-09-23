"""第11回 実データのサンプル: J-Quants APIから東証プライム非金融企業のPBRとROEを作り、図にする。

workbook/ folderで実行します:
    python jquants_prime.py

本文の「実データに広げるとどうなるか」の表と図を、取得から作図まで1つのfileで作ります。
API keyは環境変数 JQUANTS_API_KEY から読み、なければ入力欄で聞きます。
Freeプランは1分に5回までなので、問い合わせごとに13秒空けます。
約50回の問い合わせがあるので、初回は10分余りかかります。
取得した表は jquants_data/ に保存し、2回目からはAPIを呼ばずにそれを読みます。
途中で止まっても、保存済みの日の分は取り直しません。
J-Quantsの利用条件により、取得したデータは他の人に配れません。
"""

import os
import time
import unicodedata
from getpass import getpass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests

# ------------------------------------------------------------
# 1 条件を決める
#
# Freeプランで取れるのは、12週間前までの2年分です。
# 2026年9月13日に取得したとき、最新は6月21日だったので、評価日を6月19日にしました。
# 取れる範囲より後の日付を指定すると、HTTP 400になります。

EVAL_DATE = "2026-06-19"      # 株価を比べる日
DISC_START = "2026-04-15"     # 決算短信を集め始める日
FY_END = "2026-03-31"         # 対象の決算期末
BASE = "https://api.jquants.com/v2"
SAVE = Path("jquants_data")
OUT = Path("output")

# ------------------------------------------------------------
# 2 取得の関数
#
# fetch は1つの問い合わせを送り、pagination_key が続く限り次のページも取ります。
# load_or_fetch は、保存したCSVがあればそれを読み、なければ fetch して保存します。
# CSVは文字列のまま読みます。銘柄コードの先頭の0や、空欄を残すためです。

KEY = os.environ.get("JQUANTS_API_KEY", "").strip()
last_request = 0.0


def fetch(endpoint, params):
    global KEY, last_request
    if not KEY:
        KEY = getpass("J-Quants API key: ").strip()
    params, rows = dict(params), []
    while True:
        time.sleep(max(0, 13 - (time.monotonic() - last_request)))
        last_request = time.monotonic()
        r = requests.get(BASE + endpoint, params=params,
                         headers={"x-api-key": KEY}, timeout=60)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {endpoint} {params}")
        payload = r.json()
        rows += payload["data"]
        if not payload.get("pagination_key"):
            return pd.DataFrame(rows)
        params["pagination_key"] = payload["pagination_key"]


def load_or_fetch(name, endpoint, params):
    path = SAVE / name
    if not path.exists():
        print("取得:", endpoint, params)
        frame = fetch(endpoint, params)
        if frame.empty:
            frame = pd.DataFrame(columns=["Code"])
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)
    return pd.read_csv(path, dtype=str, keep_default_na=False)


# ------------------------------------------------------------
# 3 3つの表を取る
#
# 銘柄一覧と株価は、評価日の1日分を全銘柄まとめて取ります（それぞれ1回）。
# 決算短信サマリーは、会社ごとではなく開示日ごとに取ります。
# 会社ごとだとプライムだけで1,500回を超えますが、日ごとなら営業日の数（44回）で済みます。
# 営業日は取引カレンダーから選びます（HolDiv が "1" の日）。

master = load_or_fetch("master.csv", "/equities/master", {"date": EVAL_DATE})
daily = load_or_fetch(f"daily_{EVAL_DATE}.csv", "/equities/bars/daily",
                      {"date": EVAL_DATE})
calendar = load_or_fetch("calendar_2026.csv", "/markets/calendar",
                         {"from": DISC_START, "to": EVAL_DATE})
days = calendar.loc[calendar["HolDiv"] == "1", "Date"]
days = days[days.between(DISC_START, EVAL_DATE)]
fins = pd.concat([load_or_fetch(f"fins/fins_{d}.csv", "/fins/summary", {"date": d})
                  for d in days], ignore_index=True)
print("銘柄:", len(master), "行 株価:", len(daily), "行 決算:", len(fins), "行")

# ------------------------------------------------------------
# 4 使う決算を選び、1社1行にする
#
# 評価日の取引終了（15時30分）より前に開示された行だけを使います。
# 2026年3月期の連結の通期決算に絞り、訂正開示があれば最後の開示を残します。

counts = []


def count(step, frame):
    counts.append({"step": step, "companies": frame["Code"].nunique()})


count("銘柄一覧", master)
before = (fins["DiscDate"] < EVAL_DATE) | (
    (fins["DiscDate"] == EVAL_DATE) & (fins["DiscTime"] < "15:30:00"))
fy = fins[before & (fins["CurFYEn"] == FY_END) & (fins["CurPerType"] == "FY")
          & fins["DocType"].str.startswith("FYFinancialStatements_Consolidated_")]
fy = fy.sort_values(["Code", "DiscDate", "DiscTime", "DiscNo"])
fy = fy.drop_duplicates("Code", keep="last")
count("3月期・連結通期の決算（全市場）", fy)

# ------------------------------------------------------------
# 5 3つの表を結ぶ
#
# 実データの業種名は「証券･商品先物取引業」のように半角の中黒を含みます。
# NFKCで半角の「･」を全角の「・」にそろえてから、金融業の一覧と比べます。

prime = master[master["MktNm"] == "プライム"]
count("プライム", prime)
cols = ["Code", "DiscDate", "DocType", "NP", "Sales", "TA", "ShEq",
        "ShOutFY", "TrShFY"]
panel = prime[["Code", "CoName", "S17Nm", "S33Nm"]].merge(
    fy[cols], on="Code", validate="one_to_one")
panel = panel.merge(daily[["Code", "C"]], on="Code", validate="one_to_one")
count("プライム・決算・株価がそろう", panel)

num = ["NP", "Sales", "TA", "ShEq", "ShOutFY", "TrShFY", "C"]
panel[num] = panel[num].apply(pd.to_numeric, errors="coerce")
financial = ["銀行業", "証券・商品先物取引業", "保険業", "その他金融業"]
industry = panel["S33Nm"].map(lambda s: unicodedata.normalize("NFKC", s))
panel = panel[~industry.isin(financial)].copy()
count("金融業を除く", panel)

# ------------------------------------------------------------
# 6 PBRとROEを作り、条件を満たす会社に絞る

panel["Shares"] = panel["ShOutFY"] - panel["TrShFY"]
panel["MV"] = panel["C"] * panel["Shares"]
need = ["NP", "Sales", "TA", "ShEq", "Shares", "C", "MV", "S17Nm", "S33Nm"]
panel = panel[panel[need].notna().all(axis=1)]
count("必要な値がそろう", panel)
positive = ["Sales", "TA", "ShEq", "Shares", "C", "MV"]
sample = panel[(panel[positive] > 0).all(axis=1)].copy()
count("分母などが正", sample)

sample["PBR"] = sample["MV"] / sample["ShEq"]
sample["ROE"] = sample["NP"] / sample["ShEq"]
print(pd.DataFrame(counts))
print("社数:", len(sample))
print("PBRの中央値:", round(sample["PBR"].median(), 4))
print("ROEの中央値（%）:", round(sample["ROE"].median() * 100, 2))
print("PBR1倍未満:", (sample["PBR"] < 1).sum(), "社")
print("赤字:", (sample["NP"] < 0).sum(), "社")

# ------------------------------------------------------------
# 7 図にする
#
# PBRは右に長い分布なので、上位1%は描かずに、描かなかった社数を題名に書きます。
# 散布図は縦軸を対数にし、ROEの上下1%は描きません。

OUT.mkdir(exist_ok=True)
pbr_cap = sample["PBR"].quantile(0.99)
roe_lo, roe_hi = sample["ROE"].quantile([0.01, 0.99])
pbr_in = sample["PBR"] <= pbr_cap
roe_in = sample["ROE"].between(roe_lo, roe_hi)
note = (f"TSE Prime, non-financial, FY ending {FY_END[:7]}, "
        f"price on {EVAL_DATE}. Source: J-Quants API V2")

fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
axes[0].hist(sample.loc[pbr_in, "PBR"], bins=40, color="#2a78d6",
             edgecolor="white")
axes[0].axvline(1, color="#52514e", linewidth=1)
axes[0].set(xlabel="PBR (times)", ylabel="Number of firms")
axes[0].set_title(f"PBR: {(~pbr_in).sum()} firms above {pbr_cap:.1f} "
                  "not shown", loc="left", fontsize=10)
axes[1].hist(sample.loc[roe_in, "ROE"] * 100, bins=40, color="#2a78d6",
             edgecolor="white")
axes[1].axvline(0, color="#52514e", linewidth=1)
axes[1].set(xlabel="ROE (%)", ylabel="Number of firms")
axes[1].set_title(f"ROE: {(~roe_in).sum()} firms outside "
                  f"{roe_lo*100:.1f} to {roe_hi*100:.1f}% not shown",
                  loc="left", fontsize=10)
fig.suptitle(f"Distribution of PBR and ROE (n = {len(sample)})",
             x=0.01, ha="left", fontsize=11)
fig.text(0.01, -0.04, note, fontsize=8, color="#52514e")
fig.tight_layout()
fig.savefig(OUT / "pbr_roe_hist.png", dpi=160, bbox_inches="tight")
plt.show()

toyota = sample[sample["Code"] == "72030"]
fig, ax = plt.subplots(figsize=(7, 4.6))
ax.scatter(sample.loc[roe_in, "ROE"] * 100, sample.loc[roe_in, "PBR"],
           s=12, color="#2a78d6", alpha=0.5)
ax.scatter(toyota["ROE"] * 100, toyota["PBR"], s=60,
           facecolors="none", edgecolors="black", linewidths=1.5)
ax.annotate("Toyota (7203)", (toyota["ROE"].iloc[0] * 100,
            toyota["PBR"].iloc[0]), xytext=(10, -18),
            textcoords="offset points", fontsize=9)
ax.set_yscale("log")
ax.axhline(1, color="#52514e", linewidth=0.8)
ax.axvline(0, color="#52514e", linewidth=0.8)
ax.set(xlabel="ROE (%)", ylabel="PBR (times, log scale)")
ax.set_title(f"ROE and PBR (n = {roe_in.sum()} shown; {(~roe_in).sum()} "
             "outside ROE 1st-99th percentile)", loc="left", fontsize=10)
ax.grid(color="#e1e0d9", linewidth=0.6)
fig.text(0.01, -0.04, note, fontsize=8, color="#52514e")
fig.tight_layout()
fig.savefig(OUT / "roe_pbr_scatter.png", dpi=160, bbox_inches="tight")
plt.show()

pd.DataFrame(counts).to_csv(OUT / "sample_counts.csv", index=False)
print("保存しました:", OUT)
