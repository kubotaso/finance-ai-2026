"""第11回ワークブック：架空の企業表を結合し、指標を作り、業種別に集計して図にする。

workbook/ folderで実行します:
    python workbook.py

data/ の表はすべて架空のデータで、列名はJ-Quants APIと同じです。API keyは要りません。
5節では、2〜4節で1つずつ確かめた処理を、このfileの中で2つの関数にまとめます。
"""

# ------------------------------------------------------------
# 1-1 型と欠損を確かめる

import pandas as pd
import matplotlib.pyplot as plt

prices = pd.read_csv("data/prices.csv", dtype={"Code": str}, parse_dates=["Date"])
print(prices.shape)
print(prices.dtypes)
print(prices.isna().sum())

# ------------------------------------------------------------
# 1-2 ifと、列に対する条件

close = 3958
if close > 3000:
    print("3,000円より高い")

high = prices["C"] > 3000
print(high.head(3))
print("3,000円より高い行の数:", high.sum())
print(prices[high].head(3))

# ------------------------------------------------------------
# 2-1 株価と企業情報を結ぶ

master = pd.read_csv("data/master.csv", dtype={"Code": str})
short = prices[prices["Date"].between("2024-08-01", "2024-08-05")][["Date", "Code", "C"]]

merged = short.merge(master, on="Code", how="left")
print("結合前:", len(short), "行 結合後:", len(merged), "行")
print(merged)

print("master の行数:", len(master), " 銘柄コードの種類:", master["Code"].nunique())
print(master[master["Code"].duplicated(keep=False)])

# ------------------------------------------------------------
# 2-2 validateで重複を止める

master_u = master.drop_duplicates()
print("重複を除いた master:", len(master_u), "行")

merged = short.merge(master_u, on="Code", how="left", validate="many_to_one")
print("結合後:", len(merged), "行")

# ------------------------------------------------------------
# 2-3 通期決算を選び、訂正開示をそろえる

fins = pd.read_csv("data/fins.csv", dtype={"Code": str}, parse_dates=["DiscDate", "CurPerEn"])
print("fins:", len(fins), "行")

fy = fins[(fins["CurPerType"] == "FY")
          & fins["DocType"].str.startswith("FYFinancialStatements")
          & (fins["CurPerEn"] == "2025-03-31")
          & (fins["DiscDate"] <= "2025-06-30")]
print("条件に合う行:", len(fy), " 銘柄:", fy["Code"].nunique())
print(fy["Code"].value_counts().head(3))

print(fy.loc[fy["Code"] == "05550", ["DiscDate", "Code", "NP", "ShEq", "BPS"]])

fy = fy.sort_values(["Code", "DiscDate"]).drop_duplicates("Code", keep="last")
print("銘柄ごとに最後の開示だけ残した行:", len(fy))

# ------------------------------------------------------------
# 2-4 3つの表を結合し、行数を記録する

daily = pd.read_csv("data/daily_2025-06-30.csv", dtype={"Code": str}, parse_dates=["Date"])

counts = []
counts.append({"step": "master（重複を除く）", "rows": len(master_u)})
counts.append({"step": "通期決算（銘柄ごとに1行）", "rows": len(fy)})

panel = master_u.merge(fy, on="Code", how="left", validate="one_to_one")
counts.append({"step": "master と決算（left）", "rows": len(panel)})

panel = panel.merge(daily[["Code", "C"]], on="Code", how="left", validate="one_to_one")
counts.append({"step": "株価を結合（left）", "rows": len(panel)})

print(pd.DataFrame(counts))

# ------------------------------------------------------------
# 3-1 列をまとめて計算する

panel["Shares"] = panel["ShOutFY"] - panel["TrShFY"]
panel["MV"] = panel["C"] * panel["Shares"]
panel["PBR"] = panel["MV"] / panel["ShEq"]
panel["ROE"] = panel["NP"] / panel["ShEq"]
panel["PBR_BPS"] = panel["C"] / panel["BPS"]

print(panel[["Code", "CoName", "C", "NP", "ShEq", "PBR", "PBR_BPS", "ROE"]])

# ------------------------------------------------------------
# 3-2 標本の条件を1つずつ足す

financial = ["銀行業", "証券、商品先物取引業", "保険業", "その他金融業"]
steps = [
    ("プライム", panel["MktNm"] == "プライム"),
    ("金融業を除く", ~panel["S33Nm"].isin(financial)),
    ("通期決算がある", panel["NP"].notna() & panel["ShEq"].notna()),
    ("自己資本が正", panel["ShEq"] > 0),
]
keep = pd.Series(True, index=panel.index)
for step, condition in steps:
    keep = keep & condition
    counts.append({"step": step, "rows": int(keep.sum())})

print(pd.DataFrame(counts))

print(panel.loc[panel["ShEq"] <= 0, ["Code", "CoName", "NP", "ShEq", "ROE", "PBR"]])

# ------------------------------------------------------------
# 3-3 欠損を0で埋めない

kept = panel[keep]
print("社数:", len(kept), " PBRがある社数:", kept["PBR"].notna().sum())
print("PBRの中央値（欠損を除く）:", round(kept["PBR"].median(), 3))
print("PBRの中央値（欠損を0で埋める）:", round(kept["PBR"].fillna(0).median(), 3))
print(kept.loc[kept["PBR"].isna(), ["Code", "CoName", "C", "PBR"]])

sample = kept[kept["PBR"].notna()].copy()
counts.append({"step": "評価日の株価がある", "rows": len(sample)})
print(pd.DataFrame(counts))

# ------------------------------------------------------------
# 3-4 業種別に集計する

by_industry = (sample.groupby("S33Nm")
               .agg(n=("Code", "count"),
                    PBR_mean=("PBR", "mean"), PBR_median=("PBR", "median"),
                    ROE_mean=("ROE", "mean"), ROE_median=("ROE", "median"))
               .reset_index())
print(by_industry.round(3))

# ------------------------------------------------------------
# 4-1 分布を見る

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.hist(sample["PBR"], bins=20, color="#2a78d6", edgecolor="white")
ax.set_xlabel("PBR (times)")
ax.set_ylabel("Number of firms")
ax.set_title(f"PBR on 2025-06-30, FY ending 2025-03 (n = {len(sample)})", loc="left")
fig.text(0.01, -0.02, "Fictional data", fontsize=8, color="#52514e")
plt.show()

# ------------------------------------------------------------
# 4-2 散布図

fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(sample["ROE"] * 100, sample["PBR"], color="#2a78d6", s=40)
for _, row in sample[sample["PBR"] > 10].iterrows():
    ax.annotate(row["Code"], (row["ROE"] * 100, row["PBR"]), xytext=(-40, -4), textcoords="offset points")
ax.set_xlabel("ROE (%, year-end equity)")
ax.set_ylabel("PBR (times)")
ax.set_title(f"ROE and PBR (n = {len(sample)})", loc="left")
ax.grid(color="#e1e0d9", linewidth=0.6)
fig.text(0.01, -0.02, "Price: 2025-06-30. Fiscal year ending 2025-03. Fictional data", fontsize=8, color="#52514e")
plt.show()

# ------------------------------------------------------------
# 4-3 外れ値を隠すことと、除くことは違う

fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(sample["ROE"] * 100, sample["PBR"], color="#2a78d6", s=40)
ax.set_ylim(0, 4)
hidden = (sample["PBR"] > 4).sum()
ax.set_xlabel("ROE (%, year-end equity)")
ax.set_ylabel("PBR (times)")
ax.set_title(f"ROE and PBR, y-axis cut at 4 (n = {len(sample)}, {hidden} not shown)", loc="left")
ax.grid(color="#e1e0d9", linewidth=0.6)
fig.text(0.01, -0.02, "Price: 2025-06-30. Fiscal year ending 2025-03. Fictional data", fontsize=8, color="#52514e")
plt.show()

print(f"PBRの中央値（{len(sample)}社）:", round(sample["PBR"].median(), 3))

# ------------------------------------------------------------
# 4-4 図の1点を元の表まで辿る

code = sample.loc[sample["PBR"].idxmax(), "Code"]
print("PBRが最大の銘柄:", code)
print(master_u[master_u["Code"] == code])
print(fins.loc[fins["Code"] == code, ["DiscDate", "DocType", "CurPerEn", "NP", "ShEq", "BPS", "ShOutFY", "TrShFY"]])
print(daily.loc[daily["Code"] == code, ["Date", "C"]])

# ------------------------------------------------------------
# 5-1 処理を関数にまとめる
# ------------------------------------------------------------
# 2〜3節で1つずつ確かめた読み込み・結合・変数作成・条件を、そのままの順で1つの関数にします。
# 引数を変えれば、評価日・決算期・結合方法を変えて同じ手順をもう一度実行できます。
# この関数は長いので、Shift+Enter でまとめて送るとterminalの行編集が崩れます。
# notebookなら、このcellをそのまま実行すれば定義されます。
def build_sample(data_dir, eval_date, fy_end, how="left"):
    """3つの表を読んで結合し、条件を1つずつ足して、最後に残った標本と段階ごとの社数の表を返す。"""
    counts = []

    def count(step, frame):
        counts.append({"step": step, "rows": len(frame), "companies": frame["Code"].nunique()})

    master = pd.read_csv(f"{data_dir}/master.csv", dtype={"Code": str}).drop_duplicates()
    fins = pd.read_csv(f"{data_dir}/fins.csv", dtype={"Code": str}, parse_dates=["DiscDate", "CurPerEn"])
    daily = pd.read_csv(f"{data_dir}/daily_{eval_date}.csv", dtype={"Code": str}, parse_dates=["Date"])
    count("銘柄の表（重複を除く）", master)

    fy = fins[(fins["CurPerType"] == "FY")
              & fins["DocType"].str.startswith("FYFinancialStatements")
              & (fins["CurPerEn"] == fy_end)
              & (fins["DiscDate"] <= eval_date)]
    fy = fy.sort_values(["Code", "DiscDate"]).drop_duplicates("Code", keep="last")
    count("通期決算（銘柄ごとに1行）", fy)

    panel = master.merge(fy, on="Code", how=how, validate="one_to_one")
    count(f"銘柄と決算の結合（{how}）", panel)
    panel = panel.merge(daily[["Code", "C"]], on="Code", how="left", validate="one_to_one")
    count("評価日の株価を結合", panel)

    panel["Shares"] = panel["ShOutFY"] - panel["TrShFY"]
    panel["MV"] = panel["C"] * panel["Shares"]
    panel["PBR"] = panel["MV"] / panel["ShEq"]
    panel["ROE"] = panel["NP"] / panel["ShEq"]

    financial = ["銀行業", "証券、商品先物取引業", "保険業", "その他金融業"]
    steps = [
        ("プライム", panel["MktNm"] == "プライム"),
        ("金融業を除く", ~panel["S33Nm"].isin(financial)),
        ("通期決算がある", panel["NP"].notna() & panel["ShEq"].notna()),
        ("自己資本が正", panel["ShEq"] > 0),
        ("評価日の株価がある", panel["C"].notna()),
    ]
    keep = pd.Series(True, index=panel.index)
    for step, condition in steps:
        keep = keep & condition
        count(step, panel[keep])
    return panel[keep].copy(), pd.DataFrame(counts)


def industry_table(sample):
    """業種ごとの社数と、PBR・ROEの平均・中央値。"""
    return (sample.groupby("S33Nm")
            .agg(n=("Code", "count"),
                 PBR_mean=("PBR", "mean"), PBR_median=("PBR", "median"),
                 ROE_mean=("ROE", "mean"), ROE_median=("ROE", "median"))
            .reset_index())


sample_fn, counts_fn = build_sample("data", eval_date="2025-06-30", fy_end="2025-03-31")
print(counts_fn)
print(industry_table(sample_fn).round(3))
# 読み方: 社数の表と業種別の表は、2〜4節で1つずつ作ったものと同じです。
# how="inner" にすると、結合の段階は63社になり、最後の標本は46社で変わりません。
# eval_date を "2025-07-31" にすると、その日の株価 daily_2025-07-31.csv がないので FileNotFoundError になります。
# 評価日を変えるには、その日の株価の表も用意します。
