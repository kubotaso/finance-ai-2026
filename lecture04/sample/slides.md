---
marp: true
theme: default
paginate: true
size: 16:9
footer: "Markdownの記法サンプル"
style: |
  section {
    font-family: "Hiragino Sans", "Yu Gothic", sans-serif;
    font-size: 30px;
    color: #17233c;
  }
  h1 { color: #173a68; }
  strong { color: #b23a48; }
  section.lead {
    background: #f3f6fa;
    text-align: center;
  }
  footer { color: #6b7280; font-size: 15px; }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# 日米の短期市場金利

## 2015年から2026年まで

久保田荘　2026年10月15日

---

# 同じdataから、reportとslide

- `report.md` と `slides.md` は別のfile
- 図は共通の `figures/` を見る
- 記法は同じ。`---` で頁を区切るところだけが違う

**slideは箇条書きと図。reportの文章をそのまま貼ると入らない。**

---

# 図を貼る

![width:900px](figures/fig01_policy_rates.png)

---

# 背景を敷く

![bg right:40%](figures/fig01_policy_rates.png)

`![bg right:40%](...)` と書くと、画像が右40%の背景になります。

本文は残った左側に流れます。

---

# 米国

- 2022年3月まで 0.2%
- 2023年8月に **5.33%** でピーク
- 直近（2026年8月）は 3.63%

17か月で5.1%ポイント上げた計算になります。

---

# 日本

- 2016年3月にマイナス入り
- 最も低いのは2018年6月の −0.071%
- 2024年3月に解除、2026年7月は **0.978%**

マイナス金利は8年続きました。

---

# 数式も書ける

金利差を次のように定義します。

$$
s_t = i^{US}_t - i^{JP}_t
$$

2023年に5%ポイントを超え、いまは2.7%ポイント前後です。

---

<!-- _class: lead -->

# 書き出し方

```
marp slides.md --pdf --allow-local-files --no-stdin
```
