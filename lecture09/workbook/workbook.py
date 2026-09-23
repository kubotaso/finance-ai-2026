"""第9回ワークブック：運転資金・財務三表・減価償却を小さな数値で追い、J-Quantsの決算サマリーを照合する。

workbook/ folderで実行します:
    python workbook.py

1〜5節は架空の数値の計算で、API keyは要りません。
6節でJ-Quantsから決算サマリーを1回取得します。API keyは環境変数 JQUANTS_API_KEY にあればそれを使い、
なければ非表示の入力欄で受け取ります。keyはこのfileにも出力にも書き込みません。
実行するたびにAPIから取り直します。取得したデータは、そのままの形で他の人に配布しません。

各節の頭に、codeが何をしているかと、会計としてどういう意味かをコメントで書いてあります。
表の数値は講義本文の表と同じです。数値を変えて試すときは、値を書き換えて実行し直します。
"""

# ------------------------------------------------------------
# 準備
# ------------------------------------------------------------
# 使うlibraryはpandasだけです。表（DataFrame）を作り、列どうしの計算で
# 会計の数値を組み立てていきます。
import sys
print(sys.executable)

import pandas as pd
print(pd.__version__)

# ============================================================
# 1. 運転資金と設備資金
# ============================================================
# 会計の基本は「売ったとき・使ったときに記録する」（発生主義）で、
# 「現金が動いたときに記録する」（現金主義）ではありません。
# そのため、利益と現金は同じ月には動きません。1節はそのずれを数値で見ます。

# ------------------------------------------------------------
# 1-1 仕入れ・販売・入金の時差
# ------------------------------------------------------------
# 架空の小売店。単位は万円。
#   - 1〜4か月目に毎月80万円で仕入れ、同じ月に100万円で売る。在庫は残さない。
#   - 仕入れ代金は1か月後に払う（払うまでの間は「買掛金」という負債）。
#   - 売上代金は2か月後に受け取る（受け取るまでの間は「売掛金」という資産）。
#   - 5か月目以降は仕入れも販売もせず、残った代金のやり取りだけ。
#
# profit（利益）は「売上 − 仕入れ」で、売った月に発生主義で記録します。
# cash_in / cash_out は、実際に現金が動く月です。
#   shift(2, fill_value=0) は列を2行下へずらし、空いた行を0にする操作で、
#   「売上の代金は2か月後に入る」という時差をそのまま表しています。
# cumsum() は上からの累計です。profit_total が利益の累計、cash_total が現金の累計です。
cash_flow = pd.DataFrame({"month": [1, 2, 3, 4, 5, 6]})
cash_flow["sales"] = [100, 100, 100, 100, 0, 0]
cash_flow["purchases"] = [80, 80, 80, 80, 0, 0]
cash_flow["profit"] = cash_flow["sales"] - cash_flow["purchases"]
cash_flow["cash_in"] = cash_flow["sales"].shift(2, fill_value=0)
cash_flow["cash_out"] = cash_flow["purchases"].shift(1, fill_value=0)
cash_flow["cash_change"] = cash_flow["cash_in"] - cash_flow["cash_out"]
cash_flow["profit_total"] = cash_flow["profit"].cumsum()
cash_flow["cash_total"] = cash_flow["cash_change"].cumsum()
print(cash_flow)
# 読み方: 利益は毎月20万円ずつ積み上がるのに、現金の累計は2か月目に -80万円です。
# 仕入れの支払いが先に来て、売上の入金が後になるからです。この不足を借入などで
# 埋められなければ、利益が出ていても支払いができません（黒字倒産）。
# 6か月目に代金のやり取りが終わると、現金の累計は利益の累計と同じ80万円に追いつきます。

# ------------------------------------------------------------
# 1-2 運転資金＝売掛金＋在庫－買掛金
# ------------------------------------------------------------
# 売掛金（receivables）：売ったがまだ受け取っていない代金。相手に貸しているのと同じで、資産。
#   「売上の累計 − 入金の累計」で、その月末に未回収で残っている額になります。
# 買掛金（payables）：仕入れたがまだ払っていない代金。相手から借りているのと同じで、負債。
#   「仕入れの累計 − 支払いの累計」です。
# 在庫（inventory）：売るために持っている商品。この例では0。
#
# 運転資金 = 売掛金 + 在庫 − 買掛金
#   営業を回すために、商品と売掛金の形で寝ている資金から、取引先に待ってもらっている
#   買掛金を引いたものです。この金額の分だけ、利益が現金になっていません。
cash_flow["receivables"] = cash_flow["sales"].cumsum() - cash_flow["cash_in"].cumsum()
cash_flow["inventory"] = 0
cash_flow["payables"] = cash_flow["purchases"].cumsum() - cash_flow["cash_out"].cumsum()
cash_flow["working_capital"] = cash_flow["receivables"] + cash_flow["inventory"] - cash_flow["payables"]
cash_flow["profit_minus_wc"] = cash_flow["profit_total"] - cash_flow["working_capital"]
print(cash_flow[["month", "profit_total", "receivables", "payables", "working_capital", "profit_minus_wc", "cash_total"]])
# 読み方: 2か月目末は売掛金200、買掛金80で、運転資金は120万円。
# profit_minus_wc（利益の累計 − 運転資金）は、どの月も cash_total と一致します。
# 「現金 = 利益の累計 − 運転資金」。利益が売掛金として相手の手元にある間は、現金ではありません。
# 入金を1か月後に早める（shift(2) を shift(1) にする）と、現金が足りない月はなくなります。
# 在庫を持つと、その分が商品の形でとどまるので、必要な運転資金が増えます。試すには、売上原価 cogs と
# 仕入れ purchases を分け、仕入れ = 売上原価 + 在庫の増加分 として同じ表を作ります。在庫が毎月10万円ずつ
# 増えて40万円で止まる例では、4か月目の買掛金は90万円、運転資金は150万円、現金の累計は -70万円になります。

# ============================================================
# 2. 内部資金と外部資金
# ============================================================
# ある会社が200百万円の機械を買う資金を集めます。単位は百万円。
#   内部資金：会社が稼いだ利益のうち、配当で外に出さずに残した分（利益の留保）。
#   外部資金：株式の発行、社債、銀行借入など、会社の外から集めた資金。
# B/Sでは、利益の留保と株式の発行は「純資産」に、借入は「負債」に入ります。
# 純資産は返済の義務がなく、負債は期限に返す義務があります。これが資金の性格の違いです。
funding = pd.DataFrame({
    "source": ["retained earnings", "new shares", "bank loan"],
    "kind": ["internal", "external", "external"],
    "bs_side": ["net assets", "net assets", "liabilities"],
    "amount": [60, 40, 100],
})
print(funding)

total = funding["amount"].sum()
internal = funding[funding["kind"] == "internal"]["amount"].sum()
liabilities_increase = funding[funding["bs_side"] == "liabilities"]["amount"].sum()
net_assets_increase = funding[funding["bs_side"] == "net assets"]["amount"].sum()

print("total:", total, " internal share:", round(internal / total * 100, 1), "%")
print("machine acquired by exchanging 200 cash; acquisition itself does not increase net assets")
print("liabilities + net assets increase:", liabilities_increase + net_assets_increase)
# 読み方: 内部資金の割合は30%。B/Sの右側は負債+100、純資産+100で合計200増え、
# 左側は機械が200増えます（集めた現金200を機械200と交換しただけなので、
# 買う行為そのものは純資産を増やしません）。
# 利益の留保60で純資産は増えましたが、その60は機械の代金に使われ、現金としては残っていません。
# B/Sの「利益剰余金」は、現金の残高ではなく、過去の利益のうち会社に残した額の記録です。

# ============================================================
# 3. B/S：ある時点の資産・負債・純資産
# ============================================================

# ------------------------------------------------------------
# 3-1 資産＝負債＋純資産
# ------------------------------------------------------------
# B/S（貸借対照表）は、期末など「ある時点」の残高です。単位は百万円。
#   左側（資産）    ：資金の使い道。現金、売掛金、在庫、機械。
#   右側（負債）    ：返す義務のある資金。買掛金、銀行借入。
#   右側（純資産）  ：返す義務のない資金。資本金（株主の払込み）、利益剰余金（残した利益）、
#                     非支配株主持分（子会社の株を持つ親会社以外の株主の分）。
# 左右の合計は必ず一致します。資産はすべて、負債か純資産のどちらかで賄われているからです。
balance = pd.DataFrame({
    "item": ["cash", "receivables", "inventory", "machines",
             "payables", "bank loans",
             "capital", "retained earnings", "non-controlling interests"],
    "side": ["assets", "assets", "assets", "assets",
             "liabilities", "liabilities",
             "net assets", "net assets", "net assets"],
    "amount": [50, 120, 30, 200, 80, 150, 100, 60, 10],
})

assets = balance[balance["side"] == "assets"]["amount"].sum()
liabilities = balance[balance["side"] == "liabilities"]["amount"].sum()
net_assets = balance[balance["side"] == "net assets"]["amount"].sum()
print("assets:", assets)
print("liabilities + net assets:", liabilities + net_assets)
print(balance)
# 読み方: 資産400 = 負債230 + 純資産170。
# 1年以内に現金になる資産（現金・売掛金・在庫）が流動資産、それより長い機械が固定資産。
# 1年以内に払う買掛金が流動負債です。

# 純資産と自己資本
#   連結決算では、子会社の株式を親会社以外の株主も持っていることがあります。
#   その分が非支配株主持分で、純資産には入りますが、親会社の株主のものではありません。
#   純資産から非支配株主持分を除いたものが「自己資本」（親会社の株主の分）です。
#   自己資本比率 = 自己資本 ÷ 総資産。借入に頼らずにどれだけ資産を賄っているかの目安で、
#   高いほど返済負担が小さい会社です。
equity = net_assets - 10
print("net assets / assets:", round(net_assets / assets * 100, 1), "%")
print("equity / assets:", round(equity / assets * 100, 1), "%")
# 読み方: 純資産÷総資産は42.5%、自己資本÷総資産は40.0%。
# 6節のJ-Quantsでは Eq が純資産、EqAR が自己資本比率なので、Eq / TA と EqAR は一致しません。

# ------------------------------------------------------------
# 3-2 簿価の純資産と時価総額
# ------------------------------------------------------------
# 簿価：B/Sに載っている帳簿上の金額。過去に払い込まれた資本と、積み上げた利益の記録。
# 時価：市場で付いた価格。株式なら「株価 × 発行済株式数」= 時価総額。
# 2つは別々に決まります。B/Sは過去の取引の記録、時価総額は投資家の将来の予想を映すからです。
shares = 100_000
price = 2500
market_cap = price * shares / 1_000_000
book_equity = 160
print("market capitalization (million yen):", market_cap)
print("book equity (million yen):", book_equity)
print("book equity per share (yen):", book_equity * 1_000_000 / shares)
# 読み方: 時価総額250百万円に対し、簿価の自己資本は160百万円。1株当たりの簿価は1,600円。
# 株価が1,200円なら時価総額は120百万円で簿価を下回りますが、B/Sの数値は変わりません。
# この2つの比が第10回のPBR（株価純資産倍率）です。

# ============================================================
# 4. P/L：期間の収益と費用
# ============================================================
# P/L（損益計算書）は、1年間などの「期間」に、収益をいくら得て、費用をいくら使ったかの流れです。
# B/Sが時点の残高であるのに対し、P/Lは期間の増減です。単位は百万円。
#
# 日本基準のP/Lは、利益を段階ごとに表示します。上から順に「本業に近い順」です。
#   売上高                       ：商品やサービスを売って得た収益
#   − 売上原価                   ：売った商品の仕入れ・製造にかかった費用
#   = 売上総利益（粗利）         ：商品そのものの儲け
#   − 販売費及び一般管理費（販管費）：人件費、広告費、家賃など、売るため・会社を動かすための費用
#   = 営業利益                   ：本業の儲け
#   + 営業外収益 − 営業外費用    ：受取利息・支払利息など、本業以外で毎年ある損益
#   = 経常利益                   ：会社全体の通常の儲け（日本基準にだけある段階）
#   ± 特別損益                   ：災害損失、固定資産の売却損益など、毎年は起きない損益
#   = 税金等調整前当期純利益
#   − 法人税等                   ：税金
#   = 当期純利益                 ：最終的な儲け
#   − 非支配株主に帰属する利益   ：子会社の利益のうち、親会社以外の株主の分
#   = 親会社株主に帰属する当期純利益：親会社の株主の取り分。J-Quantsの NP はこれ。
sales = 1000
cost_of_sales = 700
sga = 220
non_operating_income = 15
non_operating_expenses = 25
extraordinary_losses = 10
income_taxes = 18
profit_to_nci = 2

gross_profit = sales - cost_of_sales
operating_profit = gross_profit - sga
ordinary_profit = operating_profit + non_operating_income - non_operating_expenses
profit_before_tax = ordinary_profit - extraordinary_losses
net_income = profit_before_tax - income_taxes
net_income_parent = net_income - profit_to_nci

steps = pd.DataFrame({
    "line": ["売上高", "売上総利益", "営業利益", "経常利益",
             "税金等調整前当期純利益", "当期純利益", "親会社株主に帰属する当期純利益"],
    "million_yen": [sales, gross_profit, operating_profit, ordinary_profit,
                    profit_before_tax, net_income, net_income_parent],
})
print(steps)
# 読み方: 売上1,000 → 粗利300 → 営業利益80 → 経常利益70 → 税引前60 → 純利益42 → 親会社分40。
# 段階を分けるのは、「本業で稼げているか」（営業利益）と「借金の利息や一時的な損で
# 最終利益がどう変わったか」を分けて読むためです。営業利益は黒字なのに純利益が赤字なら、
# 本業以外のどこかに原因があります。
# IFRS（国際会計基準）には経常利益の段階がありません。6節のトヨタはIFRSなので、
# J-Quantsの OdP（経常利益）は空欄になります。

# ============================================================
# 5. C/Fと減価償却
# ============================================================
# C/F（キャッシュ・フロー計算書）は、期間中の現金の出入りを3つに分けます。
#   営業活動：本業で入った現金と出た現金
#   投資活動：設備の購入・売却、他社への投資
#   財務活動：借入と返済、株式の発行、配当の支払い
# P/Lは発生主義、C/Fは現金主義なので、両者のずれを見ると「利益と現金の違い」が分かります。

# ------------------------------------------------------------
# 5-1 200,000円の機械を4年間使う
# ------------------------------------------------------------
# 条件（単位は円）
#   - 株主が払い込んだ200,000円の現金（資本金）で会社を始める。
#   - 1年目の初めに200,000円の機械を現金で買う。耐用年数4年、4年後の価値（残存価額）は0。
#   - 機械を使って毎年80,000円を現金で売り上げる。ほかの費用と税金はない。
#
# 減価償却：何年も使う設備の代金を、買った年に全部費用にするのではなく、
#   使う年数に分けて費用にする記録の仕方。売上を生む期間と費用を対応させるためです。
#   定額法では毎年同じ額。ここでは 200,000 ÷ 4 = 50,000円。
price = 200000
life = 4
years = list(range(1, life + 1))    # [1, 2, 3, 4]

# P/L：毎年の費用は減価償却費50,000円だけ。純利益は 80,000 − 50,000 = 30,000円。
pl = pd.DataFrame({"year": years})
pl["sales"] = 80000
pl["depreciation"] = price / life
pl["net_income"] = pl["sales"] - pl["depreciation"]
print(pl)

# C/F：
#   営業活動 = 純利益 + 減価償却費 = 80,000円。
#     減価償却費はP/Lでは費用ですが、その年に現金は1円も出ていきません（出たのは1年目の購入時）。
#     だから純利益に「足し戻す」と、本業で実際に入った現金になります。
#     実際の決算書の営業C/Fも、純利益から出発して減価償却費などを足し戻す形（間接法）で作られています。
#   投資活動 = 1年目に −200,000円（機械の購入）。2年目以降は0。
#   財務活動 = 借入も配当もないので0。
cf = pd.DataFrame({"year": years})
cf["operating"] = pl["net_income"] + pl["depreciation"]
cf["investing"] = [-price] + [0] * (life - 1)    # 1年目だけ -200,000
cf["financing"] = 0
cf["change_in_cash"] = cf["operating"] + cf["investing"] + cf["financing"]
print(cf)

# B/S（各年末）：
#   現金 = 最初の200,000円 + 現金増減の累計。
#   減価償却累計額 = これまでの減価償却費の合計。機械の簿価をこの分だけ減らす。
#   機械の簿価 = 取得価額200,000円 − 減価償却累計額。4年目末に0。
#   純資産 = 資本金200,000円 + 利益剰余金（純利益の累計）。
#   負債は0なので、資産合計 = 純資産 になるはずです。balanced 列でそれを確かめます。
bs = pd.DataFrame({"year": years})
bs["cash"] = price + cf["change_in_cash"].cumsum()
bs["accumulated_depreciation"] = pl["depreciation"].cumsum()
bs["machine_book_value"] = price - bs["accumulated_depreciation"]
bs["total_assets"] = bs["cash"] + bs["machine_book_value"]
bs["liabilities"] = 0
bs["capital"] = price
bs["retained_earnings"] = pl["net_income"].cumsum()
bs["liabilities_and_net_assets"] = bs["liabilities"] + bs["capital"] + bs["retained_earnings"]
bs["balanced"] = bs["total_assets"] == bs["liabilities_and_net_assets"]
print(bs)
# 読み方: 同じ機械の代金200,000円が、3つの表に別々の形で出ています。
#   C/F：買った年の投資活動に、現金の支出として一度に。
#   P/L：4年間に分けて、減価償却費として。
#   B/S：機械の簿価が毎年50,000円ずつ減る形で。
# 純資産が毎年30,000円ずつ増えるのは、純利益が利益剰余金に加わるからです。
# 減価償却費は費用であって、純資産に足すものではありません。
# 耐用年数を変えて試すには、life を5にして5-1を実行し直します。減価償却費と純利益は毎年40,000円になります。

# ------------------------------------------------------------
# 5-2 機械の代金を買った年に全部費用にすると
# ------------------------------------------------------------
# 減価償却をせずに、1年目に200,000円を全部費用にした場合と比べます。
compare = pd.DataFrame({"year": years})
compare["net_income_with_depreciation"] = pl["net_income"]
compare["change_in_cash"] = cf["change_in_cash"]
compare["all_expensed_in_year1"] = [80000 - price] + [80000] * (life - 1)
print(compare)
print(compare.sum())
# 読み方: 減価償却ありなら純利益は毎年30,000円。1年目に全部費用にすると
# 1年目 −120,000円、2〜4年目 80,000円で、現金の増減と同じ形になります。
# 4年間の合計はどれも120,000円で同じです。違うのは「どの年に記録するか」だけです。
# 減価償却は、4年間使う機械の費用を、その機械が売上を生む4年間に割り当てる
# 記録の仕方であって、現金の動きを変えるものではありません。

# ============================================================
# 6. 決算サマリーの取得と照合
# ============================================================
# ここからは実在の会社（トヨタ自動車、証券コード7203）の決算短信の数値を、J-QuantsのAPIから取得します。
# 1〜5節で見た項目が、実際の決算ではどの列に入るかを確かめます。

# ------------------------------------------------------------
# 6-0 J-Quants APIから取得する準備
# ------------------------------------------------------------
# 第8回の toyota_oct2025.py と同じ仕組みです。URLに条件を付けて送ると、JSONが返ってきます。
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
# 6-1 1社の決算サマリーを取得する
# ------------------------------------------------------------
# /fins/summary に銘柄コードを送ると、決算短信の1ページ目（サマリー）の数値が「開示1回 = 1行」で返ります。
# 銘柄コードは、証券コード7203の末尾に0を付けた5桁の 72030 です。
code = "72030"
fins = fetch("/fins/summary", {"code": code})

# 読んだ直後は、日付も金額も文字列です。使う列を日付型と数値型に直します（第7回と同じ手順）。
for col in ["DiscDate", "CurPerSt", "CurPerEn", "CurFYSt", "CurFYEn"]:
    fins[col] = pd.to_datetime(fins[col], errors="coerce")
for col in ["Sales", "OP", "OdP", "NP", "TA", "Eq", "EqAR", "EPS", "BPS", "DivAnn"]:
    fins[col] = pd.to_numeric(fins[col], errors="coerce")
fins = fins.sort_values(["DiscDate", "CurPerEn"]).reset_index(drop=True)

print(fins.shape)
print(fins[["DiscDate", "DocType", "CurPerType", "CurPerSt", "CurPerEn"]])
# 読み方（列の意味）:
#   DiscDate   ：開示日。決算短信を公表した日。
#   DocType    ：書類の種類。FYFinancialStatements_Consolidated_IFRS なら
#                通期（FY）・連結（Consolidated）・IFRS の決算短信。
#                単体なら NonConsolidated、日本基準なら末尾が JP。
#   CurPerType ：期間の種類。1Q、2Q、3Q、FY。
#   CurPerSt / CurPerEn：その行が対象とする期間の初日と末日。
# Freeプランで取れるのは12週間より前の約2年分なので、取得日によって行数が変わります。

# ------------------------------------------------------------
# 6-2 四半期は期首からの累計
# ------------------------------------------------------------
# 決算短信の四半期の数値は、その四半期だけでなく「事業年度の初めからの累計」です。
# 3Qの Sales は4月から12月までの9か月分。通期(FY)から3Qを引くと、1〜3月の3か月分になります。
# CurFYEn は事業年度の末日で、2026年3月期なら 2026-03-31 です。
fy2026 = fins[fins["CurFYEn"] == "2026-03-31"]
print(fy2026[["DiscDate", "CurPerType", "CurPerSt", "CurPerEn", "Sales", "OP", "NP"]])
# 読み方: 4行とも CurPerSt は2025-04-01。金額の単位は円。
#   Sales：売上高（トヨタの決算短信では「営業収益」）
#   OP   ：営業利益
#   NP   ：親会社株主に帰属する当期純利益（4節の最後の段階。当期純利益そのものではない）

# ------------------------------------------------------------
# 6-3 実績と予想
# ------------------------------------------------------------
# 決算短信には「実績」と「会社の業績予想」の両方が載っています。
#   Sales, NP        ：実績
#   FSales, FNP      ：その事業年度の通期についての会社予想（四半期の行に入る）
#   NxFSales, NxFNp  ：翌事業年度の通期についての会社予想（通期の行に入る）
# 予想は会社が出す見通しで、株価はこの予想の変化にも反応します（第10回）。
# 6-1で数に直したのは実績の列だけなので、予想の列はまだ文字列（object）です。同じ手順で数に直します。
# errors="coerce" は、数に直せない値（空欄）を NaN にする指定です。
for col in ["FSales", "FNP", "NxFSales", "NxFNp"]:
    print(col, fins[col].dtype)
    fins[col] = pd.to_numeric(fins[col], errors="coerce")

view = fins[["DiscDate", "CurPerType"]].copy()
for col in ["Sales", "FSales", "NxFSales", "NP", "FNP", "NxFNp"]:
    view[col + " (100M yen)"] = (fins[col] / 100_000_000).round(0)
print(view)
# 読み方: 表示は億円。通期の行では FSales が空欄で、翌年度の予想が NxFSales に入ります。
# 四半期の行を上から追うと、通期予想 FNP が期中にどう修正されたかが分かります。

# ------------------------------------------------------------
# 6-5 最新の通期の行
# ------------------------------------------------------------
# 通期（FY）・連結（Consolidated）の決算短信の行だけを残し、決算期末 CurPerEn の順に並べた最後の行が、
# いちばん新しい通期決算です。
fy = fins[(fins["CurPerType"] == "FY")
          & fins["DocType"].str.startswith("FYFinancialStatements_Consolidated_")]
if fy.empty:
    raise ValueError("連結の通期決算の行がありません")
latest_fy = fy.sort_values(["CurPerEn", "DiscDate"]).iloc[-1]
print(latest_fy[["DiscDate", "DocType", "CurPerEn", "Sales", "OP", "OdP", "NP", "TA", "Eq", "EqAR", "EPS", "BPS", "DivAnn"]])
# 読み方（3節・4節との対応）:
#   OdP  ：経常利益。IFRSのトヨタにはこの段階がないので NaN。
#   TA   ：総資産（B/Sの左側の合計）
#   Eq   ：純資産（非支配株主持分を含む）
#   EqAR ：自己資本比率（自己資本 ÷ 総資産）。3-1と同じく、Eq / TA とは一致しない。
#   EPS  ：1株当たり純利益 = NP ÷ 株数
#   BPS  ：1株当たり純資産 = 自己資本 ÷ 株数（3-2の「1株当たりの簿価」。第10回のPBRで使う）
#   DivAnn：1株当たりの年間配当（円）

# ------------------------------------------------------------
# 6-6 決算短信と照合する
# ------------------------------------------------------------
# APIの値が正しいかは、原資料である決算短信の1ページ目と突き合わせて確かめます。
# トヨタの決算短信は https://global.toyota/jp/ir/financial-results/ から開けます。
# 「(1)連結経営成績」「(2)連結財政状態」の百万円単位の数値を、下の None に入れます。
# 照合で確かめることは2つです。
#   1. 数値が一致するか。
#   2. APIの列名が決算短信のどの項目にあたるか。
#      NP は「当期利益」ではなく「親会社の所有者に帰属する当期利益」、
#      Eq は「親会社の所有者に帰属する持分」ではなく「資本合計」に一致します。
tanshin = {
    "Sales": None,   # 営業収益
    "OP": None,      # 営業利益
    "NP": None,      # 親会社の所有者に帰属する当期利益
    "TA": None,      # 資産合計
    "Eq": None,      # 資本合計
}

rows = []
for item in ["Sales", "OP", "NP", "TA", "Eq"]:
    rows.append({
        "item": item,
        "api (million yen)": latest_fy[item] / 1_000_000,
        "tanshin (million yen)": tanshin[item],
    })
check = pd.DataFrame(rows)
check["difference"] = check["api (million yen)"] - pd.to_numeric(check["tanshin (million yen)"])
print(check)
# 読み方: None のままなら difference は NaN。決算短信の値を入れると、一致していれば 0.0 になります。

# ------------------------------------------------------------
# 6-7 確認メモ
# ------------------------------------------------------------
# 照合の結果を、次の項目でメモに残します。HW02の段階提出Aの「決算短信の数値確認メモ」に使えます。
#   - 企業名・銘柄コード
#   - 対象の決算期（CurPerEn）と開示日（DiscDate）
#   - 書類の種類（DocType）：通期／四半期、連結／単体、会計基準
#   - 照合した原資料（URL、ページ、表の名前）
#   - 照合した項目と結果（APIの値、決算短信の値、単位、一致したか）
#   - APIの列と決算短信の項目名の対応で気づいたこと
#   - サマリーにない数値で、原資料で読んだこと
# 自分の会社で同じことをするときは、6-1の code を変えて6節を上から実行し直します。
