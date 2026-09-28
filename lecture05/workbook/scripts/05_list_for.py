# 5. listと繰り返し

# 5-1 list
A = 1
B = 2
C = 3
values = [A, B, C]
print(values)
print(values[0])
print(values[2])
print(len(values))

# 5-2 for：1から5までを順に足し、途中の結果を表示する
total = 0
for i in range(1, 6):
    total = total + i
    print(total)

# 5-3 複利をforで計算する：100円を10%で20年
fuku = 100
for year in range(1, 21):
    fuku = fuku * 1.1
print(round(fuku, 2))

# 最初の10年は10%、11年目からは20%
fuku = 100
for year in range(1, 21):
    if year <= 10:
        fuku = fuku * 1.1
    else:
        fuku = fuku * 1.2
print(round(fuku, 2))
