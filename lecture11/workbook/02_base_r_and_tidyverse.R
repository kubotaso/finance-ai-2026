# 同じ株価の表をbase Rとtidyverseで扱います。
# 第6回のprices.csvから、Auto Aの3日分を取り出した値です。
library(tidyverse)

# Cは終値（円）、Voは出来高（株）です。
d <- data.frame(
  Date = as.Date(c("2024-08-01", "2024-08-02", "2024-08-05")),
  Code = c("01110", "01110", "01110"),
  C = c(2454, 2492, 2467),
  Vo = c(20507300, 28425400, 27465800)
)
print(d)

# 1. 日付と終値の列を選びます。
# base R：[行, 列]の列に、列名を文字列で書きます。
print(d[, c("Date", "C")])

# tidyverse：select()に列名を書きます。
print(d |> select(Date, C))

# 2. 終値が2,470円以上の日を選びます。
# base R：$で列を取り出し、条件を[行, 列]の行に書きます。
print(d[d$C >= 2470, ])

# tidyverse：filter()に条件を書きます。
print(d |> filter(C >= 2470))

# 3. 終値の単位を千円にした列を作ります。
# base R：表をコピーし、$で列を追加します。
base_result <- d
base_result$C_thousand_yen <- base_result$C / 1000
print(base_result)

# tidyverse：mutate()で列を追加した表を作ります。
tidy_result <- d |> mutate(C_thousand_yen = C / 1000)
print(tidy_result)

# 4. 3日間の終値の平均を求めます。どちらも2,471円です。
# base R：取り出した列にmean()を使うと、数値が返ります。
print(mean(d$C))

# tidyverse：summarise()で集計すると、1行の表が返ります。
print(d |> summarise(mean_close = mean(C)))

# base Rは[ ]や$で表を操作します。
# tidyverseは操作ごとの関数を使います。
# |>は左の表を右の関数に渡します。
