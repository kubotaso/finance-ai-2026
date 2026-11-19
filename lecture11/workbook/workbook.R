# 第11回　ワークブック（script版）
# 第6回の仮想の株価CSVをRで読み、選び、集計します。
# Lecture11/を作業場所にすると、data/のCSVを読んでoutput/に結果を保存します。

R.version.string
packageVersion("tidyverse")
packageVersion("rmarkdown")
basename(getwd())

A <- 1
B <- 2
3 -> C
A
print(B)
C

D <- c(A, B, C)
D
D[1]
D[3]

v1 <- c(2, 3, 4)
v2 <- c(6, 4, 2)
v1 * v2
v1 * 2

class(3)
class("Pen Pineapple Apple Pen")
class(3 >= 60)

try({
  "3" + "3"
})

D <- 0
for (i in 1:5) {
  D <- D + i
  print(D)
}

test <- 60
if (test > 60) {
  print("Pass")
} else if (test == 60) {
  print("Just barely Pass")
} else {
  print("Fail")
}

10 * 20 + 100
100 * 1.1^20
Fuku <- 100
for (i in 1:20) {
  if (i <= 10) {
    Fuku <- Fuku * 1.1
  } else {
    Fuku <- Fuku * 1.2
  }
}
Fuku

future_value <- function(principal, rate, years) {
  principal * (1 + rate)^years
}
future_value(100, 0.10, 2)

library(tidyverse)
prices <- read_csv(
  "data/prices.csv",
  col_types = cols(Date = col_date(), Code = col_character())
)
nrow(prices)
ncol(prices)
glimpse(prices)

n_distinct(prices$Code)
n_distinct(prices$Date)
prices |> count(Code)

prices1 <- prices |> select(Date, Code, C, AdjC, Vo)
ncol(prices1)
head(prices1)

auto_a <- prices1 |> filter(Code == "01110")
nrow(auto_a)

colSums(is.na(prices1))
prices1 |> filter(is.na(C))

prices2 <- prices1 |> mutate(C_thousand_yen = C / 1000)
head(prices2)

prices2 <- prices2 |>
  mutate(Name = case_when(
    Code == "01110" ~ "Auto A",
    Code == "02220" ~ "Auto B",
    Code == "03330" ~ "Retail C",
    TRUE ~ "その他"
  ))
prices2 |> count(Code, Name)

prices2 <- prices2 |>
  mutate(volume_group = if_else(Vo >= 10000000,
                                "1000万株以上", "1000万株未満"))
prices2 |> count(volume_group)

price_summary <- prices2 |>
  group_by(Code, Name) |>
  summarise(
    days = n(),
    priced_days = sum(!is.na(AdjC)),
    mean_adjusted_close = mean(AdjC, na.rm = TRUE),
    .groups = "drop"
  )
price_summary

priced <- prices2 |> drop_na(AdjC)
nrow(priced)
priced |> count(Code)

tab1 <- priced |> count(Code)
tab2 <- priced %>% count(Code)
tab3 <- count(priced, Code)
identical(tab1, tab2)
identical(tab1, tab3)

three_days <- auto_a |>
  filter(Date >= as.Date("2024-08-01"), Date <= as.Date("2024-08-05"))
three_days |> select(Date, C)
mean(three_days$C)

retail_three <- prices1 |>
  filter(Code == "03330",
         Date >= as.Date("2024-08-01"), Date <= as.Date("2024-08-05"))
retail_three |> select(Date, C, Vo)
mean(retail_three$C)
mean(retail_three$C, na.rm = TRUE)
sum(!is.na(retail_three$C))

dir.create("output", showWarnings = FALSE)
check_rows <- tibble(
  step = c("all rows", "AdjC not NA", "Auto A"),
  rows = c(nrow(prices), nrow(priced), nrow(auto_a))
)
check_missing <- tibble(
  variable = names(prices1),
  n_missing = colSums(is.na(prices1))
)
write_csv(check_rows, "output/price_check_rows.csv")
write_csv(check_missing, "output/price_check_missing.csv")
write_csv(price_summary, "output/price_summary.csv")
check_rows
check_missing
