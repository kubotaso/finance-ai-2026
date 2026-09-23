# %% [markdown]
# # 第6回 ワークブック
#
# Python I：script・対話モード・notebook、基本文法と現在価値
#
# 2026年10月20日（火）3限 金融論

# %% [markdown]
# ## 使い方
#
# このfileは、`# %%` で区切られたcellの並びです。上から順に、1つずつ実行していきます。
#
# - 実行する cellの中にカーソルを置き、Shift+Enterを押します。右側にInteractive windowが開いて結果が出て、次のcellに進みます。押す前に、何が出るか予想します。
# - やってみる すぐ下の `# ここに書きます` のcellに自分で書いて実行します。既にあるcellを書き換える指示もあります。
#
# errorを確かめるcellは、確かめたら行頭に `#` を付けておきます。行を選んで ⌘/（WindowsはCtrl+/）を押すと付きます。8節で全部を実行し直すとき、errorで止まらなくなります。
#
# 詰まったら、cellの内容とエラーの表示をCodexに見せて聞けます。「やってみる」の答え合わせも頼めます。同じ内容のnotebook版が `workbook.ipynb`、ただのscriptにしたものが `workbook.py` です。
#
# `scripts/` には、3〜7節の「実行する」codeを、節ごとに1つの `.py` にしたものがあります（`03_variables_types.py` など）。どれも単独で実行でき、このfileと同じ結果がterminalに出ます。

# %% [markdown]
# ## 準備
#
# 1. `workbook/` folderを、自分の作業場所にコピーします。
# 2. VS Codeでfolderごと開きます（File → Open Folder）。
# 3. 拡張機能の Python と Jupyter（どちらもMicrosoft）が入っているか確認します。
# 4. このfileを開き、画面右下のinterpreter表示から、HW01で作った `finance-env` を選びます。
# 5. 下のcellの中にカーソルを置き、Shift+Enterを押します。Interactive windowが開きます。`ipykernel` を入れるか聞かれたら Install を押します。表示されたpathに `finance-env` が含まれていれば準備完了です。

# %%
import sys
print(sys.executable)

# %% [markdown]
# # 1. terminalで動かす
#
# 先に、このfileの外で、scriptと対話モードを動かします。
#
# ## 1-1 pv.pyを実行する
#
# 1. VS CodeのExplorerで `pv.py` を開きます。1年後に受け取る110円の現在価値を計算するcodeです。
# 2. 右上の ▷ を押します。下にterminalが開き、結果が出ます。右下のinterpreter表示が `finance-env` でなければ、⇧⌘P（WindowsはCtrl+Shift+P）→ `Python: Select Interpreter` で選びます。
# 3. 同じterminalで `python pv.py` と打っても、同じ結果になります。
#
# こう表示されます。
#
# ```
# 現在価値: 100.0
# ```
#
# 最後の行の `pv * 2` は計算されていますが、何も表示されません。scriptでは `print` したものだけが表示されます。
#
# やってみる
#
# 1. `years = 1` を `years = 2` に変えて保存し（⌘S、WindowsはCtrl+S）、もう一度実行します。`現在価値: 90.91` になります。
# 2. `amount = 110` の行を消して保存し、実行します。`NameError: name 'amount' is not defined` が出ます。scriptは毎回、何もない状態から上へ順に実行するので、前回の `amount` は残っていません。
# 3. 確かめたら、`pv.py` を元に戻して保存します。

# %% [markdown]
# ## 1-2 対話モードで動かす
#
# 1. 1-1で使ったterminalで `python` と打ちます。`>>>` が出ます。
# 2. 次の2行を1行ずつ打ち、そのたびにEnterを押します。
#
# ```
# >>> amount = 110
# >>> amount * 2
# 220
# ```
#
# `print` しなくても、式の値が表示されます。
#
# 3. `exit()` と打って抜けます。
# 4. もう一度 `python` と打ち、`amount` と打ちます。`NameError: name 'amount' is not defined` になります。抜けたときに変数が消えたからです。`exit()` で抜けます。
#
# やってみる
#
# `python` を起動して、`>>>` の後ろに `python pv.py` と打ちます。`SyntaxError: invalid syntax` になります。`>>>` の後ろに打つのはPythonのcodeで、`python pv.py` はterminalに打つcommandです。`exit()` で抜けてから打つと動きます。

# %% [markdown]
# # 2. cellごとに動かす
#
# ## 2-1 同じcodeをcellで実行する
#
# 実行する

# %%
amount = 110
rate = 0.10
years = 1

# %%
pv = amount / (1 + rate) ** years
round(pv, 2)

# %% [markdown]
# 最後の行の値は、`print` しなくてもInteractive windowに表示されます。結果はこのfileには残らず、残るのはcodeだけです。
#
# やってみる
#
# 上のcellの `years = 1` を `years = 2` に変え、そのcellと次のcellを順に実行します。90.91になります。確かめたら `years = 1` に戻し、2つのcellをもう一度実行します。

# %% [markdown]
# ## 2-2 変数はkernelに残る
#
# 実行する

# %%
price = 100

# %%
price * 2

# %% [markdown]
# やってみる
#
# 1. 上の `price = 100` を `price = 300` に書き換えます。そのcellは実行しません。
# 2. `price * 2` のcellだけを実行します。200のままです。kernelの中の `price` がまだ100なので、画面のcodeと結果が合っていません。
# 3. `price = 300` のcellを実行してから、`price * 2` を実行し直すと600になります。

# %% [markdown]
# ## 2-3 scriptとの違い
#
# やってみる
#
# 下のcellに `amount` とだけ書いて実行します。110が出ます。1-1のscriptでは、`amount = 110` の行を消すとerrorになりました。Interactive windowでは、一度実行した変数は、kernelを再起動するまで残ります。

# %%
# ここに書きます

# %% [markdown]
# # 3. 変数、型、計算
#
# ## 3-1 代入と表示
#
# 実行する

# %%
A = 1
B = 2
C = 3
print(A, B, C)

# %% [markdown]
# やってみる
#
# `print(A + B * C)` と `print((A + B) * C)` を、結果を予想してから実行します。

# %%
# ここに書きます

# %% [markdown]
# ## 3-2 計算
#
# 100円を10%で20年間預けたときの、単利と複利です。
#
# 実行する

# %%
# 単利
10 * 20 + 100

# %%
# 複利
100 * 1.1 ** 20

# %% [markdown]
# 末尾が長くなるのは、小数を2進数で近似して計算しているためです。`round(100 * 1.1 ** 20, 2)` と書くと、小数第2位で丸めた672.75になります。
#
# やってみる
#
# 1. `round(100 * 1.1 ** 20, 2)` を実行します。
# 2. `100 * 1.1 ^ 20` を実行します。`TypeError` が出ます。Pythonのべき乗は `**` で、`^` は別の記号です。確かめたら行頭に `#` を付けます。

# %%
# ここに書きます

# %% [markdown]
# ## 3-3 型
#
# 実行する

# %%
print(type(3))
print(type(3.0))
print(type("Pen Pineapple Apple Pen"))
print(type(True))

# %% [markdown]
# `int` は整数、`float` は小数、`str` は文字列、`bool` は `True` か `False` です。
#
# やってみる
#
# 1. `print("3" + "3")` と `print(int("3") + int("3"))` を実行します。前者は文字がつながって `33`、後者は数として足して `6` です。
# 2. `"3" + 3` を実行します。文字列と数は足せないので `TypeError` です。確かめたら行頭に `#` を付けます。

# %%
# ここに書きます

# %% [markdown]
# ## 3-4 `=` と `==`
#
# `=` は代入、`==` は等しいかどうかを調べる記号です。
#
# 実行する

# %%
test = 59
print(test == 60)
print(test >= 60)
print(type(test >= 60))

# %% [markdown]
# やってみる
#
# 上のcellの `test = 59` を60、61に変えて、それぞれ実行します。

# %% [markdown]
# # 4. 条件分岐
#
# ## 4-1 if と else
#
# テストの点数が60点以上なら Pass、それ以外なら Fail と表示します。
#
# 実行する

# %%
test = 61
if test >= 60:
    print("Pass")
else:
    print("Fail")

# %% [markdown]
# やってみる
#
# 上のcellの `test` を59、60、61に変えて、それぞれ実行します。

# %% [markdown]
# ## 4-2 elif
#
# 実行する

# %%
test = 60
if test > 60:
    print("Pass")
elif test == 60:
    print("Just barely Pass")
else:
    print("Fail")

# %% [markdown]
# やってみる
#
# 1. 4-1のcodeを下のcellにコピーし、`print("Pass")` の行の字下げを消して実行します。`IndentationError` が出ます。
# 2. 字下げを戻し、`if` の行の最後の `:` を消して実行します。`SyntaxError` が出ます。
# 3. 確かめたら、cellの全行を選んで ⌘/（WindowsはCtrl+/）を押し、行頭に `#` を付けます。

# %%
# ここに書きます

# %% [markdown]
# # 5. listと繰り返し
#
# ## 5-1 list
#
# 実行する

# %%
values = [A, B, C]
print(values)
print(values[0])
print(values[2])
print(len(values))

# %% [markdown]
# 番号は0から始まります。`values[0]` が1番目、`values[2]` が3番目です。
#
# やってみる
#
# 1. `print([2, 3, 4] * 2)` を実行します。要素ごとの掛け算ではなく、listの繰り返しになります。
# 2. `values[3]` を実行します。要素は3つなので `IndexError` です。確かめたら行頭に `#` を付けます。

# %%
# ここに書きます

# %% [markdown]
# ## 5-2 for
#
# 1から5までを順に足し、途中の結果を表示します。
#
# 実行する 表示される5つの数を予想してから押します。

# %%
total = 0
for i in range(1, 6):
    total = total + i
    print(total)

# %% [markdown]
# やってみる
#
# 1. `print(list(range(1, 6)))` を実行し、`range(1, 6)` の中身を見ます。6は含まれません。
# 2. `range(1, 14, 3)` の中身を見ます。3ずつ増えます。
# 3. `range(1, 14, 3)` を使って、上と同じように足し算を繰り返します。1、5、12、22、35と表示されます。

# %%
# ここに書きます

# %% [markdown]
# ## 5-3 複利をforで計算する
#
# 前の年の金額に1.1を掛ける、を20回繰り返します。
#
# 実行する

# %%
fuku = 100
for year in range(1, 21):
    fuku = fuku * 1.1
print(round(fuku, 2))

# %% [markdown]
# 3-2の `100 * 1.1 ** 20` と同じ672.75です。
#
# 最初の10年は10%、11年目からは20%になる場合は、`if` を組み合わせます。
#
# 実行する

# %%
fuku = 100
for year in range(1, 21):
    if year <= 10:
        fuku = fuku * 1.1
    else:
        fuku = fuku * 1.2
print(round(fuku, 2))

# %% [markdown]
# やってみる
#
# 金利が20%に上がる年を、11年目から6年目に早めます。20年後の金額が大きくなるか小さくなるか、予想してから実行します。

# %%
# ここに書きます

# %% [markdown]
# # 6. 関数
#
# ## 6-1 関数を作る
#
# `principal` 円を金利 `rate` で `years` 年、複利で運用した金額を返す関数です。
#
# 実行する

# %%
def future_value(principal, rate, years):
    return principal * (1 + rate) ** years

# %% [markdown]
# 何も表示されません。関数を作っただけです。使うときは、名前の後ろの `( )` に値を入れます。
#
# 実行する

# %%
round(future_value(100, 0.10, 2), 2)

# %% [markdown]
# やってみる
#
# 引数を変えて、100円を10%で20年（672.75）と、5%で20年を計算します。

# %%
# ここに書きます

# %% [markdown]
# ## 6-2 print と return
#
# 実行する

# %%
def future_value_print(principal, rate, years):
    print(principal * (1 + rate) ** years)

x = future_value(100, 0.10, 2)
y = future_value_print(100, 0.10, 2)
print("x:", x)
print("y:", y)

# %% [markdown]
# `future_value_print` は画面に表示しますが、値を返しません。`y` の中身は `None`（何もない）です。`return` で返した `x` は、次の計算に使えます。
#
# やってみる
#
# 単利の金額を返す関数 `simple_interest(principal, rate, years)` を作ります。100円を10%で20年預けたとき、単利は300、複利は672.75です。

# %%
# ここに書きます

# %% [markdown]
# # 7. 現在価値
#
# ## 7-1 1回だけ受け取る
#
# `years` 年後に受け取る `amount` 円を、割引率 `rate` で今の価値に直す関数です。
#
# 実行する

# %%
def present_value(amount, rate, years):
    return amount / (1 + rate) ** years

present_value(110, 0.10, 1)

# %% [markdown]
# 手で計算すると 110 ÷ 1.1 = 100 です。表示が `99.99999999999999` になるのは、3-2と同じく小数の近似のためです。`round(present_value(110, 0.10, 1), 2)` とすると100.0になります。
#
# やってみる
#
# 次の3つを、先に手で計算してから確かめます。
#
# - 割引率0%で、1年後の110円（110）
# - 割引率10%で、2年後の121円（100）
# - 割引率10%で、10年後の110円（約42.41）

# %%
# ここに書きます

# %% [markdown]
# ## 7-2 現在価値と将来の金額を往復する
#
# 実行する

# %%
today = present_value(110, 0.10, 1)
round(future_value(today, 0.10, 1), 2)

# %% [markdown]
# 1年後の110円を今の価値に直し、それを1年運用すると110円に戻ります。

# %% [markdown]
# ## 7-3 何年も受け取る
#
# 毎年1万円を5年間受け取ります。割引率は5%です。受け取る時点は、1年後から5年後とします。
#
# 実行する

# %%
total = 0
for t in range(1, 6):
    pv_t = present_value(10000, 0.05, t)
    total = total + pv_t
    print(t, round(pv_t, 2), round(total, 2))

# %% [markdown]
# 左から、受け取る年、その年の1万円の現在価値、その年までの合計です。5年分で約43,294.77円です。
#
# やってみる
#
# 受け取る時点を「今すぐ（0年後）から4年後」に変えます。変えるのは `range` の中だけです。合計は約45,459.51円で、1年後からの場合より大きくなります。

# %%
# ここに書きます

# %% [markdown]
# # 8. 最初から実行し直す
#
# 1. Interactive window上部の Restart を押します。kernelの変数がすべて消えます。
# 2. このfileに戻り、editor右上の Run All Cells（またはコマンドパレットの `Jupyter: Run All Cells`）を押します。上のcellから順に、全部が実行されます。
# 3. errorで止まったら、そのcellでerrorを確かめた行に `#` が付いているかを見ます。
#
# 2-2で `price = 300` に書き換えたままなら、`price * 2` の結果は600になります。今度は画面のcodeと結果が一致しています。
#
# Restart と Run All は、scriptを ▷ で実行するのと同じく、空の状態から上へ順に実行します。

# %% [markdown]
# # 9. 発展：練習問題
#
# 金額の単位は万円です。
#
# ## 問1
#
# 毎年末に50万円を積み立て、年5%の複利で運用します。10年後に、積み立てた500万円に対して利子は合計いくらになっていますか。

# %%
# ここに書きます

# %% [markdown]
# ## 問2
#
# 夫婦がそれぞれ年1,000万円を稼いでいます。30年の固定金利ローン（年3%の複利）で住宅を買い、毎年末に世帯収入の1/5を返済に充てます。いくらの住宅まで買えますか。

# %%
# ここに書きます

# %% [markdown]
# ## 問3
#
# 問2と同じく世帯収入の1/5を返済に充てます。ただし1人が15年後に退職し、世帯収入は1〜15年目が2,000万円、16〜30年目が1,000万円になります。いくらの住宅まで買えますか。

# %%
# ここに書きます

# %% [markdown]
# ## 問4
#
# 72の法則では、利子率36%なら 72 ÷ 36 = 2 年で2倍になるはずです。実際に計算すると約1.85倍にしかなりません。なぜでしょうか。

# %%
# ここに書きます
