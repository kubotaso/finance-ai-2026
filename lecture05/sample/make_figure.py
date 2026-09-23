"""data/policy_rates.csv から figures/fig01_policy_rates.png を作る。

    python make_figure.py

原稿から図を作り直せる形にしておくと、画像pathはそのまま使える。caption・対象期間・本文の数値・結論は、更新したdataと照合する。
"""
import pathlib
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

# 日本語のfontはOSで名前が違う。入っているものを1つ選ぶ。
available = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
for name in ["Hiragino Sans", "Yu Gothic", "Meiryo", "Noto Sans CJK JP"]:
    if name in available:
        matplotlib.rcParams["font.family"] = name
        break
matplotlib.rcParams["axes.unicode_minus"] = False

ROOT = pathlib.Path(__file__).resolve().parent
d = pd.read_csv(ROOT / "data/policy_rates.csv", index_col="date", parse_dates=True)

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(d.index, d["us_policy_rate"], label="米国（FF金利）", color="#b23a48", lw=1.8)
ax.plot(d.index, d["jp_policy_rate"], label="日本（無担保コールO/N）", color="#173a68", lw=1.8)
ax.axhline(0, color="#9aa4b5", lw=0.8)
ax.set_ylabel("%")
ax.set_xlabel("")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color="#e3e8ef", lw=0.8)
fig.tight_layout()

out = ROOT / "figures/fig01_policy_rates.png"
out.parent.mkdir(exist_ok=True)
fig.savefig(out, dpi=160)
print("wrote", out)
