# 6. 関数

# 6-1 関数を作る
def future_value(principal, rate, years):
    return principal * (1 + rate) ** years


print(round(future_value(100, 0.10, 2), 2))


# 6-2 print と return
def future_value_print(principal, rate, years):
    print(principal * (1 + rate) ** years)


x = future_value(100, 0.10, 2)
y = future_value_print(100, 0.10, 2)
print("x:", x)
print("y:", y)
