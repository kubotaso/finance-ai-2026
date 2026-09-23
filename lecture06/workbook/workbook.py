# 第6回 ワークブック（script版）
#
# このfileは、この回の3〜7節のcodeを上から順に並べたscriptです。
# terminalで python workbook.py と打つか、VS Codeの右上の ▷ を押すと、
# 上から下まで一度に実行され、print したものだけがterminalに表示されます。
# 一部だけ試したいときは、行を選んで Shift+Enter を押します。
#
# `#` から行末まではコメントで、Pythonは読み飛ばします。
# 説明はコメントで書いてあるので、codeと見比べながら読みます。
# 行を選んで Cmd+/（WindowsはCtrl+/）を押すと、その行がコメントになります。
# もう一度押すと戻ります。実行したくない行を一時的に止めるときに使います。

# 最初に、このscriptを動かしているPythonの場所を表示します。
# pathに finance-env が入っていれば、HW01で作った環境で動いています。
import sys
print(sys.executable)


# 2. 現在価値の最初の例
# 1年後に受け取る110円は、割引率10%なら今日のいくらにあたるか。
# 変数に値を入れてから、式で計算し、round で小数2桁に丸めて表示します。
amount = 110
rate = 0.10
years = 1
pv = amount / (1 + rate) ** years
print(round(pv, 2))       # 100.0


# 3. 変数、型、計算

# 3-1 代入と表示
# = は「右の値を左の名前に入れる」。print は複数の値を空白で区切って表示します。
A = 1
B = 2
C = 3
print(A, B, C)            # 1 2 3

# 3-2 計算：100円を年10%で20年間預ける
# 単利は毎年10円ずつ増えるので 10 × 20 + 100。
# 複利は毎年1.1倍になるので 100 × 1.1 の20乗。** はべき乗です。
print(10 * 20 + 100)      # 300
print(100 * 1.1 ** 20)    # 672.7499949325611
print(round(100 * 1.1 ** 20, 2))   # 672.75

# 3-3 型
# 値には種類（型）があります。type で確かめられます。
# 3 は int（整数）、3.0 は float（小数）、引用符で囲んだものは str（文字列）、
# True と False は bool（真偽値）です。
print(type(3))
print(type(3.0))
print(type("Pen Pineapple Apple Pen"))
print(type(True))

# 3-4 = と ==
# = は代入、== は「等しいか」を調べる比較です。比較の結果は True か False になります。
test = 59
print(test == 60)         # False
print(test >= 60)         # False
print(type(test >= 60))   # <class 'bool'>


# 4. 条件分岐

# 4-1 if と else
# if の後ろの条件が True なら字下げした部分を実行し、False なら else の部分を実行します。
# 行末の : と、その下の字下げ（空白4つ）で範囲を示します。
test = 61
if test >= 60:
    print("Pass")
else:
    print("Fail")

# 4-2 elif
# 条件を上から順に調べ、最初に True になったところだけを実行します。
# 60 は「> 60」ではないので、次の「== 60」に進みます。
test = 60
if test > 60:
    print("Pass")
elif test == 60:
    print("Just barely Pass")
else:
    print("Fail")


# 5. listと繰り返し

# 5-1 list
# [ ] で値を並べたものがlistです。番号は0から始まるので、values[0] が最初、values[2] が3つ目です。
# len は要素の数を返します。
values = [A, B, C]
print(values)             # [1, 2, 3]
print(values[0])          # 1
print(values[2])          # 3
print(len(values))        # 3

# 5-2 for
# range(1, 6) は 1, 2, 3, 4, 5 を順に返します（終わりの6は含みません）。
# i にその値が順に入り、字下げした部分が5回実行されます。
total = 0
for i in range(1, 6):
    total = total + i
    print(total)          # 1, 3, 6, 10, 15 と順に表示

# 5-3 複利をforで計算する：100円を10%で20年
# fuku を20回、1.1倍します。3-2の 100 * 1.1 ** 20 と同じ値になります。
fuku = 100
for year in range(1, 21):
    fuku = fuku * 1.1
print(round(fuku, 2))     # 672.75

# 最初の10年は10%、11年目からは20%
# for の中に if を入れると、年によって計算を変えられます。
fuku = 100
for year in range(1, 21):
    if year <= 10:
        fuku = fuku * 1.1
    else:
        fuku = fuku * 1.2
print(round(fuku, 2))     # 1605.98


# 6. 関数

# 6-1 関数を作る
# def で関数を定義します。( ) の中が引数で、return の値が呼び出したところに返ります。
# 定義しただけでは何も起きず、future_value(100, 0.10, 2) のように呼ぶと計算されます。
def future_value(principal, rate, years):
    return principal * (1 + rate) ** years


print(round(future_value(100, 0.10, 2), 2))   # 121.0


# 6-2 print と return
# print は画面に表示するだけで、値を返しません。
# x には計算結果が入りますが、y には None（値がない）が入ります。
def future_value_print(principal, rate, years):
    print(principal * (1 + rate) ** years)


x = future_value(100, 0.10, 2)
y = future_value_print(100, 0.10, 2)   # ここで 121.00000000000001 が表示される
print("x:", x)            # x: 121.00000000000001
print("y:", y)            # y: None


# 7. 現在価値

# 将来の金額 amount を、割引率 rate で years 年分割り引きます。
# 6-1の future_value の逆の計算です。
def present_value(amount, rate, years):
    return amount / (1 + rate) ** years


# 7-1 1回だけ受け取る：1年後の110円を10%で割り引く
# 小数の計算は最後の桁がずれることがあるので、表示するときは round で丸めます。
print(present_value(110, 0.10, 1))             # 99.99999999999999
print(round(present_value(110, 0.10, 1), 2))   # 100.0

# 7-2 現在価値と将来の金額を往復する
# 今日の値を1年分増やすと、元の110円に戻ります。
today = present_value(110, 0.10, 1)
print(round(future_value(today, 0.10, 1), 2))  # 110.0

# 7-3 何年も受け取る：毎年1万円を1年後から5年後まで、割引率5%
# 受け取る年ごとに現在価値を計算し、total に足していきます。
# 各行は「年、その年の分の現在価値、ここまでの合計」です。
total = 0
for t in range(1, 6):
    pv_t = present_value(10000, 0.05, t)
    total = total + pv_t
    print(t, round(pv_t, 2), round(total, 2))
# 5年分の合計は 43294.77 円です。
