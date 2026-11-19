"""日銀APIから無担保コールO/N物レートを取得して描く。"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import pandas as pd

HERE = Path(__file__).resolve().parent


def download(url):
    with urlopen(url, timeout=60) as response:
        return response.read()


def configure_plot():
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager
    names = {font.name for font in font_manager.fontManager.ttflist}
    for name in ("Hiragino Sans", "Yu Gothic", "Meiryo", "Noto Sans CJK JP"):
        if name in names:
            matplotlib.rcParams["font.family"] = name
            break
    matplotlib.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                               "axes.unicode_minus": False, "font.size": 11})


def main(refresh=False):
    for name in ("raw", "data", "figures"):
        (HERE / name).mkdir(exist_ok=True)
    params = {"db": "FM01", "code": "STRDCLUCON", "startDate": "202401", "endDate": "202512"}
    url = "https://www.stat-search.boj.or.jp/api/v1/getDataCode?" + urlencode(params)
    path = HERE / "raw/call_rate.json"
    if refresh or not path.exists():
        response = json.loads(download(url))
        if response.get("STATUS") != 200:
            raise RuntimeError("日銀API: " + response.get("MESSAGE", "取得エラー"))
        if response.get("NEXTPOSITION"):
            raise ValueError("日銀APIの応答に続きがあります。取得範囲を狭めてください。")
        path.write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8")
        (HERE / "raw/request.json").write_text(json.dumps({"url": url, "parameters": params,
            "retrieved_at": datetime.now().astimezone().isoformat()}, ensure_ascii=False, indent=2))
    series = json.loads(path.read_text())["RESULTSET"][0]
    assert series["SERIES_CODE"] == "STRDCLUCON" and series["FREQUENCY"] == "DAILY"
    assert series["UNIT_J"] == "年％"
    d = series["VALUES"]
    assert len(d["SURVEY_DATES"]) == len(d["VALUES"])
    df = pd.DataFrame({"date": pd.to_datetime([str(date) for date in d["SURVEY_DATES"]], format="%Y%m%d"), "rate_pct": d["VALUES"]})
    assert not df["date"].duplicated().any()
    df.to_csv(HERE / "data/call_rate.csv", index=False)
    configure_plot()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 4.7))
    observed = df.dropna(subset=["rate_pct"])
    ax.plot(observed["date"], observed["rate_pct"], color="#276fa4", lw=1.8)
    ax.axhline(0, color="#888888", lw=.8)
    ax.set(title="日本の短期金利：無担保コールO/N物レート", ylabel="年率（%）")
    ax.grid(axis="y", color="#dddddd")
    fig.text(.08, .025, "2024〜2025年・日次平均。出所：日本銀行 時系列統計データ検索API（FM01 / STRDCLUCON）", fontsize=9)
    fig.tight_layout(rect=(0, .055, 1, 1))
    fig.savefig(HERE / "figures/call_rate.png", dpi=180)
    plt.close(fig)

    monthly = df.set_index("date")["rate_pct"].resample("MS").agg(["mean", "count"])
    monthly = monthly.rename(columns={"mean": "mean_rate_pct", "count": "observations"})
    monthly.index.name = "month"
    monthly.to_csv(HERE / "data/call_rate_monthly.csv")
    fig, ax = plt.subplots(figsize=(10, 4.7))
    ax.plot(monthly.index, monthly["mean_rate_pct"], marker="o", ms=3,
            color="#276fa4", lw=1.8)
    ax.axhline(0, color="#888888", lw=.8)
    ax.set(title="日本の短期金利：日次平均値から作った月平均", ylabel="年率（%）")
    ax.grid(axis="y", color="#dddddd")
    fig.text(.08, .025, "2024〜2025年。各月の観測値の単純平均。出所：日本銀行（FM01 / STRDCLUCON）", fontsize=9)
    fig.tight_layout(rect=(0, .055, 1, 1))
    fig.savefig(HERE / "figures/call_rate_monthly.png", dpi=180)
    plt.close(fig)
    first, last = observed.iloc[0], observed.iloc[-1]
    (HERE / "settings.md").write_text(f"""# 日銀APIの作例

- 系列：{series['NAME_OF_TIME_SERIES_J']}（FM01 / STRDCLUCON）
- 期間：2024年1月〜2025年12月、日次、単位：年率%。市場で成立した平均金利。
- 暦日{len(df)}行、観測値{len(observed)}行。休日などのnullはCSVで欠損として保持し、図は観測のある日を結ぶ。
- 最初：{first['date'].date()} {first['rate_pct']:g}%、最後：{last['date'].date()} {last['rate_pct']:g}%
- 月平均：各月の観測値の単純平均。data/call_rate_monthly.csvに平均と観測数を保存。
- 図：figures/call_rate.png、figures/call_rate_monthly.png
- APIキーは不要。取得条件と日時：raw/request.json
- API仕様：https://www.stat-search.boj.or.jp/info/api_manual.pdf
""", encoding="utf-8")
    print(f"日銀: {len(df)}暦日、{len(observed)}観測。{first['rate_pct']:g}% → {last['rate_pct']:g}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    main(parser.parse_args().refresh)
