"""FREDのCSVで米国のCPIと政策金利を取得し、図にする手本。

ウェブの「Download」と同じCSV（fredgraph.csv）を取得する。アカウントもAPIキーも要らない。
取得したCSVは raw/、計算した表は data/、図は figures/ に保存する。
実行：python fred_example.py
"""
import io
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
import requests

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
DATA = HERE / "data"
FIGS = HERE / "figures"

# 日本語が表示できるフォントを、Mac、Windowsの順に探す。
names = {f.name for f in font_manager.fontManager.ttflist}
for name in ["Hiragino Sans", "Yu Gothic", "Meiryo", "Noto Sans CJK JP"]:
    if name in names:
        matplotlib.rcParams["font.family"] = name
        break


# 取得する関数。cosd は開始日。transformation を渡すと、FREDが変換した値を受け取る
# （"pc1" は前年同月比）。取得したCSVは、そのまま raw/ に保存する。
def fetch(series_id, start, transformation=None):
    params = {"id": series_id, "cosd": start}
    if transformation:
        params["transformation"] = transformation
    r = requests.get(URL, params=params, timeout=30)
    r.raise_for_status()
    suffix = f"_{transformation}" if transformation else ""
    (RAW / f"{series_id}{suffix}.csv").write_text(r.text)
    return r.text


# CSVを date と value の表にする。
# 1列目が observation_date、2列目が値で、欠けている時点は空欄になっている。
# to_numeric の errors="coerce" で、空欄を欠損値（NaN）にする。
def to_series(text):
    df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("date")["value"]


def describe(name, s):
    missing = [d.strftime("%Y-%m") for d in s[s.isna()].index]
    print(f"{name}: {len(s)}行 {s.index[0]:%Y-%m}〜{s.index[-1]:%Y-%m}"
          f" 最新値 {s.dropna().iloc[-1]} 欠損 {missing}")


# 前年同月比：12行前（12か月前）の値との比。
# 欠損の月を前の月の値で埋めないよう、shift で計算する。
# pct_change(12) は、pandas 2.2 では欠損を前の月の値で埋めてから計算する。
# 欠損の行を dropna で消してから shift すると、12行前が13か月前になる。
# FREDが計算した前年同月比（transformation=pc1）と比べて、計算を確かめる。
def make_table(cpi, ff, pc1):
    inflation = (cpi / cpi.shift(12) - 1) * 100
    diff = (inflation - pc1).abs().max()
    print(f"手元の計算とFREDの pc1 の差の最大値：{diff:.5f}")
    table = pd.DataFrame({"cpi": cpi, "inflation": inflation,
                          "fedfunds": ff})
    return table.loc["2000-01-01":]


def plot(table):
    t = table.loc["2000-01-01":]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(t.index, t["inflation"], color="#2a78d6", lw=1.8,
            label="インフレ率（CPIの前年同月比）")
    ax.plot(t.index, t["fedfunds"], color="#eb6834", lw=1.8,
            label="政策金利（FF金利の月平均）")
    ax.axhline(2, color="#898781", lw=0.9)
    ax.axhline(0, color="#c3c2b7", lw=0.9)
    ax.set_ylabel("%")
    ax.grid(color="#e1e0d9", lw=0.8)
    ax.legend(loc="upper left", frameon=False)
    fig.text(0.01, 0.01, "出所：FRED（CPIAUCSL、FEDFUNDS）",
             fontsize=8, color="#898781")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIGS / "inflation_policy_rate.png", dpi=200)
    plt.close(fig)


def main():
    for folder in (RAW, DATA, FIGS):
        folder.mkdir(exist_ok=True)
    # 2000年1月の前年同月比には1999年1月の値が要るので、CPIは1999年から取る。
    cpi = to_series(fetch("CPIAUCSL", "1999-01-01"))
    ff = to_series(fetch("FEDFUNDS", "2000-01-01"))
    pc1 = to_series(fetch("CPIAUCSL", "2000-01-01", transformation="pc1"))
    describe("CPIAUCSL", cpi)
    describe("FEDFUNDS", ff)

    table = make_table(cpi, ff, pc1)
    table.to_csv(DATA / "inflation_policy_rate.csv",
                 float_format="%.4f")
    plot(table)
    print("保存：data/inflation_policy_rate.csv、"
          "figures/inflation_policy_rate.png")


if __name__ == "__main__":
    main()
