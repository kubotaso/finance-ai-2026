# ベクトルを作り、表とグラフで確かめます。
x <- 1:5
y <- x^2
xy <- data.frame(x = x, y = y)
mean_y <- mean(y)

print(xy)
print(mean_y)

plot(x, y, type = "b")
