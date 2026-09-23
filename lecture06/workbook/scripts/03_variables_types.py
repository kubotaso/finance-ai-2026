# 3. 変数、型、計算

# 3-1 代入と表示
A = 1
B = 2
C = 3
print(A, B, C)

# 3-2 計算：100円を10%で20年間預けたときの単利と複利
print(10 * 20 + 100)
print(100 * 1.1 ** 20)
print(round(100 * 1.1 ** 20, 2))

# 3-3 型
print(type(3))
print(type(3.0))
print(type("Pen Pineapple Apple Pen"))
print(type(True))

# 3-4 = と ==
test = 59
print(test == 60)
print(test >= 60)
print(type(test >= 60))
