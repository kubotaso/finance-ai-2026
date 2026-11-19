# J-Quantsで自動車3社の株価を取得し、R標準の作図機能で比較します。
# Lecture11/を作業場所にして実行します。JSONの読み込みにjsonliteを使います。
# APIキーはapi_key.txtまたは環境変数JQUANTS_API_KEYから読みます。

companies <- data.frame(
  Code = c("72030", "72670", "72010"),
  Name = c("Toyota", "Honda", "Nissan"),
  stringsAsFactors = FALSE
)
start_date <- "2025-01-01"
end_date <- "2025-06-30"
out_dir <- "output"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

# APIキーを表示せずに読みます。
read_api_key <- function() {
  key <- trimws(Sys.getenv("JQUANTS_API_KEY"))
  if (nzchar(key)) return(key)
  directory <- normalizePath(getwd())
  paths <- Sys.getenv("JQUANTS_API_KEY_FILE")
  for (i in 1:6) {
    paths <- c(paths, file.path(directory, "api_key.txt"))
    directory <- dirname(directory)
  }
  paths <- unique(paths[nzchar(paths) & file.exists(paths)])
  if (!length(paths)) stop("api_key.txtが見つかりません。", call. = FALSE)
  entries <- trimws(readLines(paths[1], warn = FALSE, encoding = "UTF-8"))
  entries <- sub("^\ufeff", "", entries)
  named <- grep("^(export +)?JQUANTS_API_KEY *=", entries, value = TRUE)
  if (length(named)) {
    key <- trimws(sub("^[^=]*=", "", named[1]))
  } else {
    entries <- entries[nzchar(entries) & !startsWith(entries, "#")]
    if (length(entries) != 1) stop("JQUANTS_API_KEYの行を確認できます。", call. = FALSE)
    key <- entries[1]
  }
  key <- gsub("^['\"]|['\"]$", "", key)
  if (!length(key) || !nzchar(key)) stop("APIキーが空です。", call. = FALSE)
  key
}
api_key <- read_api_key()

# V2のGETリクエストです。続きのページがあれば取得します。
# 依頼の間隔を13秒あけ、無料プランの回数制限内で進めます。
last_request <- Sys.time() - 13
request_page <- function(endpoint, params) {
  wait <- 13 - as.numeric(difftime(Sys.time(), last_request, units = "secs"))
  if (wait > 0) Sys.sleep(wait)
  last_request <<- Sys.time()
  query <- paste(paste0(names(params), "=", vapply(params, utils::URLencode,
                 character(1), reserved = TRUE)), collapse = "&")
  con <- url(paste0("https://api.jquants.com/v2", endpoint, "?", query),
             headers = c("x-api-key" = api_key), method = "libcurl")
  on.exit(try(close(con), silent = TRUE))
  jsonlite::fromJSON(con)
}
fetch <- function(endpoint, params) {
  pages <- list()
  repeat {
    body <- request_page(endpoint, params)
    if (!is.data.frame(body$data) || !nrow(body$data)) {
      stop("取得データが空です。銘柄・期間・契約プランを確認できます。", call. = FALSE)
    }
    pages[[length(pages) + 1]] <- body$data
    cursor <- body$pagination_key
    if (is.null(cursor) || !nzchar(cursor)) break
    params$pagination_key <- cursor
  }
  do.call(rbind, pages)
}

# 銘柄名・業種と、日次株価を順に取得します。
master_list <- price_list <- vector("list", nrow(companies))
for (i in seq_len(nrow(companies))) {
  code <- companies$Code[i]
  master_list[[i]] <- fetch("/equities/master", list(code = code, date = end_date))
  price_list[[i]] <- fetch("/equities/bars/daily",
                          list(code = code, from = start_date, to = end_date))
  message(companies$Name[i], ": ", nrow(price_list[[i]]), " rows")
}
company_check <- do.call(rbind, master_list)
company_check <- company_check[, c("Code", "CoName", "S33Nm")]
if (!all(company_check$S33Nm == "輸送用機器")) {
  stop("銘柄一覧の業種を確認できます。", call. = FALSE)
}
print(company_check, row.names = FALSE)
auto_prices <- do.call(rbind, price_list)
auto_prices <- auto_prices[, c("Date", "Code", "C", "AdjC", "Vo")]
auto_prices$Date <- as.Date(auto_prices$Date)
auto_prices$Code <- as.character(auto_prices$Code)
auto_prices <- auto_prices[order(auto_prices$Code, auto_prices$Date), ]
stopifnot(!anyDuplicated(auto_prices[, c("Date", "Code")]))

# 3社すべてに価格がある共通の日付を、横に並べた表にします。
wide <- reshape(auto_prices[, c("Date", "Code", "AdjC")],
                idvar = "Date", timevar = "Code", direction = "wide")
wide <- wide[order(wide$Date), ]
price_columns <- paste0("AdjC.", companies$Code)
wide <- wide[complete.cases(wide[, price_columns]), ]
if (!nrow(wide)) stop("3社共通の価格がありません。", call. = FALSE)
auto_dates <- wide$Date
auto_close <- as.matrix(wide[, price_columns])
colnames(auto_close) <- companies$Name
if (any(auto_close <= 0)) stop("価格が0以下の行があります。", call. = FALSE)

# 各社の最初の価格で割り、初日を100にそろえます。
auto_index <- sweep(auto_close, 2, auto_close[1, ], "/") * 100
colors <- c("#2266AA", "#CC5533", "#228866")

# 円建てと初日=100の2枚を、同じ色で描きます。
draw_comparison <- function(values, title, ylab, baseline = NULL) {
  par(mar = c(4.8, 4.8, 3.8, 1.4), las = 1)
  plot(auto_dates, values[, 1], type = "n", ylim = range(values),
       xlab = "Date", ylab = ylab, main = title)
  grid(col = "#E3E7EC")
  if (!is.null(baseline)) abline(h = baseline, col = "#888888", lty = 2)
  for (i in seq_len(ncol(values))) {
    lines(auto_dates, values[, i], col = colors[i], lwd = 2)
  }
  legend("bottomleft", legend = companies$Name, col = colors, lty = 1,
         lwd = 2, bty = "n", horiz = TRUE)
  mtext("Source: J-Quants API V2 | Adjusted close | Jan-Jun 2025",
        side = 1, line = 3.5, cex = 0.75)
}

png(file.path(out_dir, "jquants_auto_close.png"), width = 1400, height = 800, res = 150)
draw_comparison(auto_close, "Japanese automakers: adjusted closing prices",
                "Adjusted close (JPY/share)")
invisible(dev.off())
png(file.path(out_dir, "jquants_auto_index.png"), width = 1400, height = 800, res = 150)
draw_comparison(auto_index, "Japanese automakers: price performance",
                "Index (first common trading day = 100)", baseline = 100)
invisible(dev.off())
if (interactive()) {
  draw_comparison(auto_index, "Japanese automakers: price performance",
                  "Index (first common trading day = 100)", baseline = 100)
}

# 元の株価は手元のoutput/に保存します。
write.csv(auto_prices, file.path(out_dir, "jquants_auto_prices.csv"), row.names = FALSE)
write.csv(company_check, file.path(out_dir, "jquants_auto_companies.csv"), row.names = FALSE)
comparison <- data.frame(
  Name = companies$Name,
  Code = companies$Code,
  start_date = min(auto_dates),
  end_date = max(auto_dates),
  common_days = length(auto_dates),
  start_close = as.numeric(auto_close[1, ]),
  end_close = as.numeric(auto_close[nrow(auto_close), ]),
  end_index = as.numeric(auto_index[nrow(auto_index), ]),
  change_pct = as.numeric(auto_index[nrow(auto_index), ] - 100)
)
write.csv(comparison, file.path(out_dir, "jquants_auto_comparison.csv"), row.names = FALSE)
print(comparison, row.names = FALSE)
message("2枚の図と確認用の表をoutput/に保存しました。")
