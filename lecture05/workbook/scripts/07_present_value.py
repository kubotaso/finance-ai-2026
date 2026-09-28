# 7. 現在価値

def future_value(principal, rate, years):
    return principal * (1 + rate) ** years


def present_value(amount, rate, years):
    return amount / (1 + rate) ** years


# 7-1 1回だけ受け取る：1年後の110円を10%で割り引く
print(present_value(110, 0.10, 1))
print(round(present_value(110, 0.10, 1), 2))

# 7-2 現在価値と将来の金額を往復する
today = present_value(110, 0.10, 1)
print(round(future_value(today, 0.10, 1), 2))

# 7-3 何年も受け取る：毎年1万円を1年後から5年後まで、割引率5%
total = 0
for t in range(1, 6):
    pv_t = present_value(10000, 0.05, t)
    total = total + pv_t
    print(t, round(pv_t, 2), round(total, 2))
