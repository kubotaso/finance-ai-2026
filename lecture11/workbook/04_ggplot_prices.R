# 第11回：型の変換、収益率、ggplot2の作図を実行します。
# Lecture11/を作業場所にすると、data/を読み、output/に3枚の図を保存します。
library(tidyverse)

class(3)       # "numeric"
class("3")     # "character"
class(TRUE)    # "logical"
as.numeric("3") + 3   # 6


short <- read_csv(
  "data/prices_short.csv",
  col_types = cols(Date = col_date(), Code = col_character(),
                   C = col_character())
)
class(short$C)   # "character"
short <- short |> mutate(C = parse_number(C))
class(short$C)   # "numeric"
short |> select(Date, Code, C)


prices <- read_csv(
  "data/prices.csv",
  col_types = cols(Date = col_date(), Code = col_character())
)
prices2 <- prices |>
  select(Date, Code, C, AdjC) |>
  mutate(Name = case_when(
    Code == "01110" ~ "Auto A",
    Code == "02220" ~ "Auto B",
    Code == "03330" ~ "Retail C"
  ))
auto_a <- prices2 |> filter(Code == "01110")


returns <- prices2 |>
  arrange(Code, Date) |>
  group_by(Code) |>
  mutate(
    previous_close = lag(AdjC),
    Change = (AdjC / previous_close - 1) * 100
  ) |>
  ungroup()


returns |>
  filter(Code == "02220", Date == as.Date("2025-04-01")) |>
  select(Date, AdjC, previous_close, Change)


p_close <- ggplot(auto_a, aes(x = Date, y = C)) +
  geom_line(color = "steelblue", linewidth = 0.6) +
  labs(
    title = "Auto A: closing price, 2024-01-04 to 2025-12-30",
    x = "Date", y = "Yen per share",
    caption = "Source: Fictional data"
  ) +
  theme_minimal()
print(p_close)


peak <- prices |>
  mutate(csv_line = row_number() + 1L) |>
  filter(Code == "01110") |>
  slice_max(AdjC, n = 1)
peak |> select(Date, Code, AdjC, csv_line)


p_peak <- p_close +
  geom_point(data = peak, aes(y = AdjC), color = "red", size = 3)
print(p_peak)


indexed <- prices2 |>
  arrange(Code, Date) |>
  group_by(Code) |>
  mutate(Index = AdjC / first(AdjC) * 100) |>
  ungroup()


p_index <- ggplot(indexed, aes(x = Date, y = Index, color = Name)) +
  geom_line(linewidth = 0.6) +
  labs(
    title = "3 companies: adjusted closing price",
    subtitle = "2024-01-04 = 100",
    x = "Date", y = "Index", color = "Company",
    caption = "Source: Fictional data"
  ) +
  theme_minimal() +
  theme(legend.position = "bottom")
print(p_index)


dir.create("output", showWarnings = FALSE)
ggsave("output/ggplot_auto_a_close.png", plot = p_close,
       width = 8, height = 4, dpi = 150)
ggsave("output/ggplot_auto_a_peak.png", plot = p_peak,
       width = 8, height = 4, dpi = 150)
ggsave("output/ggplot_prices_index.png", plot = p_index,
       width = 8, height = 4.5, dpi = 150)


indexed |>
  group_by(Code, Name) |>
  slice_tail(n = 1) |>
  select(Date, Code, Name, Index) |>
  as.data.frame() |>
  print(row.names = FALSE, digits = 5)
