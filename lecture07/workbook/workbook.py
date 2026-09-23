"""第7回ワークブックの「実行する」codeを上から並べたscript。

workbook/ folderで実行します:
    python workbook.py
図はwindowで表示され、閉じると次へ進みます。output/ folderにCSVを1つ書き出します。

VS Codeで一部の処理だけを試す場合は、実行したい行をマウスで選んで
Shift + Enter を押すと、選んだ部分だけをターミナルで実行できます。
"""

# ------------------------------------------------------------
# 準備
import sys
print(sys.executable)

import pandas as pd
import matplotlib
print(pd.__version__, matplotlib.__version__)

# ------------------------------------------------------------
# 1-1 listとfor
codes = ["01110", "02220", "03330"]
for code in codes:
    print(code, len(code))

# ------------------------------------------------------------
# 1-2 関数とreturn
def pct_change(old, new):
    return (new - old) / old * 100

change = pct_change(2600, 2670)
print(round(change, 2))

# ------------------------------------------------------------
# 2-1 CSVをtextとして見る
print(open("data/prices_short.csv", encoding="utf-8").read())

# ------------------------------------------------------------
# 3-1 read_csv
import pandas as pd

short = pd.read_csv("data/prices_short.csv")
print(short)

# ------------------------------------------------------------
# 3-2 shapeとdtypes
print(short.shape)
print(short.dtypes)

# ------------------------------------------------------------
# 3-3 列を選ぶ
print(short["C"])

print(short[["Date", "Code", "C"]])

# ------------------------------------------------------------
# 3-4 行を選ぶ
print(short[short["Code"] == "01110"])

# ------------------------------------------------------------
# 3-5 listとDataFrame、関数とmethod
vo_list = [27465800, 10278200, 0]
print(vo_list * 2)
print(short["Vo"] * 2)

print(len(short))
print(short.head(2))

# ------------------------------------------------------------
# 4-1 銘柄コードを文字列で読む
short = pd.read_csv("data/prices_short.csv", dtype={"Code": str})
print(short.dtypes)
print(short[short["Code"] == "01110"])

# ------------------------------------------------------------
# 4-2 数に見える文字列を数にする
print(short["C"] * 2)

c_text = short["C"].str.replace(",", "")
short["C"] = pd.to_numeric(c_text)
print(short.dtypes)
print(short)

# ------------------------------------------------------------
# 4-3 日付を日付型にする
short["Date"] = pd.to_datetime(short["Date"])
print(short.dtypes)
print(short)

# ------------------------------------------------------------
# 4-4 並べ替える
short = short.sort_values(["Code", "Date"]).reset_index(drop=True)
print(short)

# ------------------------------------------------------------
# 4-5 欠損と0
print(short.isna().sum())
print(short[short["Code"] == "03330"])

retail = short[short["Code"] == "03330"]
print(retail["C"].mean())
print(retail["C"].fillna(0).mean())

# ------------------------------------------------------------
# 4-6 保存して読み直す
import os

os.makedirs("output", exist_ok=True)
short.to_csv("output/prices_short_clean.csv", index=False)

back = pd.read_csv("output/prices_short_clean.csv")
print(back.dtypes)
print(back.head(3))

# ------------------------------------------------------------
# 5-1 dtypeとparse_datesを付けて読む
prices = pd.read_csv("data/prices.csv", dtype={"Code": str}, parse_dates=["Date"])
print(prices.shape)
print(prices.dtypes)
print(prices.head())

# ------------------------------------------------------------
# 5-2 銘柄ごとの行数
print(prices["Code"].value_counts())

# ------------------------------------------------------------
# 5-3 期間で絞る
aug = prices[(prices["Date"] >= "2024-08-01") & (prices["Date"] <= "2024-08-31")]
print(aug.shape)
print(aug.head())

# ------------------------------------------------------------
# 5-4 列を足す
prices["HLmean"] = (prices["H"] + prices["L"]) / 2
print(prices[["Date", "Code", "H", "L", "HLmean"]].head(3))

# ------------------------------------------------------------
# 5-5 銘柄コードに名前を付ける
names = {"01110": "Auto A", "02220": "Auto B", "03330": "Retail C"}
prices["Name"] = prices["Code"].map(names)
print(prices[["Date", "Code", "Name", "C"]].tail(3))

# ------------------------------------------------------------
# 5-6 確認表を作る
raw = pd.read_csv("data/prices.csv")

check = pd.DataFrame({
    "step": ["read only", "dtype and parse_dates", "2024-08 only"],
    "rows": [len(raw), len(prices), len(aug)],
    "Code dtype": [raw["Code"].dtype, prices["Code"].dtype, aug["Code"].dtype],
    "Date dtype": [raw["Date"].dtype, prices["Date"].dtype, aug["Date"].dtype],
    "missing C": [raw["C"].isna().sum(), prices["C"].isna().sum(), aug["C"].isna().sum()],
    "Vo == 0": [(raw["Vo"] == 0).sum(), (prices["Vo"] == 0).sum(), (aug["Vo"] == 0).sum()],
})
print(check)

# ------------------------------------------------------------
# 6-1 1社の終値
import matplotlib.pyplot as plt

auto_a = prices[prices["Code"] == "01110"]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(auto_a["Date"], auto_a["C"])
ax.set_title("Auto A: closing price, 2024-01-04 to 2025-12-30")
ax.set_xlabel("Date")
ax.set_ylabel("Yen per share")
fig.text(0.99, 0.01, "Source: Fictional data", ha="right", fontsize=8)
plt.show()

# ------------------------------------------------------------
# 6-2 株式分割と調整後終値
split = prices[(prices["Code"] == "02220") & (prices["Date"] >= "2025-03-27") & (prices["Date"] <= "2025-04-03")]
print(split[["Date", "C", "AdjFactor", "AdjC", "Vo", "AdjVo"]])

auto_b = prices[(prices["Code"] == "02220") & (prices["Date"] >= "2025-01-01") & (prices["Date"] <= "2025-06-30")]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(auto_b["Date"], auto_b["C"], label="C (unadjusted)")
ax.plot(auto_b["Date"], auto_b["AdjC"], label="AdjC (adjusted for the split)")
ax.axvline(pd.Timestamp("2025-04-01"), color="gray", linestyle="--")
ax.set_title("Auto B: 2-for-1 split on 2025-04-01, 2025-01 to 2025-06")
ax.set_xlabel("Date")
ax.set_ylabel("Yen per share")
ax.legend()
fig.text(0.99, 0.01, "Source: Fictional data", ha="right", fontsize=8)
plt.show()

# ------------------------------------------------------------
# 6-3 3社をforで重ねる
fig, ax = plt.subplots(figsize=(8, 4))
for code in ["01110", "02220", "03330"]:
    one = prices[prices["Code"] == code]
    ax.plot(one["Date"], one["AdjC"], label=names[code])
ax.set_title("Adjusted close of three firms, 2024-01-04 to 2025-12-30")
ax.set_xlabel("Date")
ax.set_ylabel("Yen per share")
ax.legend()
fig.text(0.99, 0.01, "Source: Fictional data", ha="right", fontsize=8)
plt.show()

# ------------------------------------------------------------
# 6-4 最初の日を100にそろえる
fig, ax = plt.subplots(figsize=(8, 4))
for code in ["01110", "02220", "03330"]:
    one = prices[prices["Code"] == code]
    base = one["AdjC"].iloc[0]
    ax.plot(one["Date"], one["AdjC"] / base * 100, label=names[code])
ax.axhline(100, color="gray", linewidth=0.8)
ax.set_title("Adjusted close, 2024-01-04 = 100")
ax.set_xlabel("Date")
ax.set_ylabel("Index (2024-01-04 = 100)")
ax.legend()
fig.text(0.99, 0.01, "Source: Fictional data", ha="right", fontsize=8)
plt.show()

# ------------------------------------------------------------
# 6-5 日次の変化率のヒストグラム
auto_a = prices[prices["Code"] == "01110"].copy()
auto_a["change"] = (auto_a["AdjC"] - auto_a["AdjC"].shift(1)) / auto_a["AdjC"].shift(1) * 100
print(auto_a["change"].describe())

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(auto_a["change"].dropna(), bins=40)
ax.set_title("Auto A: daily change of adjusted close, 2024-01-05 to 2025-12-30")
ax.set_xlabel("Daily change (%)")
ax.set_ylabel("Number of days")
fig.text(0.99, 0.01, "Source: Fictional data", ha="right", fontsize=8)
plt.show()

# ------------------------------------------------------------
# 6-6 図の1点をCSVの行まで戻る
auto_a = prices[prices["Code"] == "01110"]
i = auto_a["AdjC"].idxmax()
print(i)
print(prices.loc[i, ["Date", "Code", "AdjC"]])

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(auto_a["Date"], auto_a["AdjC"])
ax.plot(prices.loc[i, "Date"], prices.loc[i, "AdjC"], "o", color="red")
ax.set_title("Auto A: adjusted close and its maximum, 2024-01-04 to 2025-12-30")
ax.set_xlabel("Date")
ax.set_ylabel("Yen per share")
fig.text(0.99, 0.01, "Source: Fictional data", ha="right", fontsize=8)
plt.show()

lines = open("data/prices.csv", encoding="utf-8").read().splitlines()
print(lines[0])
print(lines[i + 1])

# ------------------------------------------------------------
# 7-1 読み込みの関数
def load_prices(path):
    frame = pd.read_csv(path, dtype={"Code": str}, parse_dates=["Date"])
    frame = frame.sort_values(["Code", "Date"]).reset_index(drop=True)
    return frame

prices2 = load_prices("data/prices.csv")
print(prices2.shape)
print(prices2.dtypes)

# ------------------------------------------------------------
# 7-2 銘柄と期間を引数にした図の関数
def plot_normalized(df, codes, start, end, source="Fictional data"):
    period = df[df["Date"].between(start, end)].sort_values("Date")
    fig, ax = plt.subplots(figsize=(8, 4))
    plotted = 0
    for code in codes:
        one = period[period["Code"] == code].dropna(subset=["AdjC"])
        if one.empty or one["AdjC"].iloc[0] <= 0:
            print(f"{code}: 正の基準値がありません。銘柄・期間・欠損を確認します。")
            continue
        base = one["AdjC"].iloc[0]
        base_date = one["Date"].iloc[0].date()
        ax.plot(one["Date"], one["AdjC"] / base * 100, label=f"{code} (base {base_date})")
        plotted += 1
    if not plotted:
        ax.text(0.5, 0.5, "No valid observations", transform=ax.transAxes, ha="center")
    ax.axhline(100, color="gray", linewidth=0.8)
    ax.set_title("Adjusted close, first trading day = 100, " + start + " to " + end)
    ax.set_xlabel("Date")
    ax.set_ylabel("Index (first trading day = 100)")
    ax.legend()
    fig.text(0.99, 0.01, "Source: " + source, ha="right", fontsize=8)
    return ax

plot_normalized(prices2, ["01110", "02220", "03330"], "2024-01-04", "2025-12-30")
plt.show()
