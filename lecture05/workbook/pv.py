# 1年後に受け取る110円の現在価値（割引率10%）

amount = 110
rate = 0.10
years = 1

pv = amount / (1 + rate) ** years
print("現在価値:", round(pv, 2))

pv * 2
