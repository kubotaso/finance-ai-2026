# LaTeXのサンプル

第1回で見た論文例の原稿です。日米の自動車メーカー5社の株価と円ドル相場の関係を、LP-IVとイベントスタディで調べています。AIの支援を受けて作成した教材用の試作です。表紙は通常の論文の体裁にしています。

`main.pdf`（英語版、20ページ）と `main_ja.pdf`（日本語版、19ページ）が出来上がりです。`.tex` を開いて、PDFのどこがどの記述から出ているかを見てください。表紙の日付は今回の改訂日（2026年9月23日）で、各 `.tex` の `\date{...}` から変更できます。

## file

| file | 役割 |
|---|---|
| `main.tex` | 英語版の本文。これがMarkdownの `.md` にあたります |
| `main_ja.tex` | 日本語版の本文 |
| `references.bib` | 参考文献のdatabase。BibTeX形式。2つの本文で共通 |
| `cumulative_returns.png`、`correlation_matrix.png`、`lp_iv_irf.png`、`event_study_car.png` | 図 |
| `main.pdf`、`main_ja.pdf` | compile結果 |

## compileする

英語版は4回走らせます。1回では参照番号と文献リストが揃いません。

```
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

1回目が本文を組んで、`\citep` の記録を `main.aux` に書き出します。`bibtex` がそれと `references.bib` を突き合わせて文献リスト（`main.bbl`）を作ります。3回目で文献リストが本文に入り、4回目で番号と相互参照が確定します。

日本語版は `pdflatex` の代わりに `lualatex` を使います。

```
lualatex main_ja.tex
bibtex main_ja
lualatex main_ja.tex
lualatex main_ja.tex
```

`latexmk -pdf main.tex`、`latexmk -lualatex main_ja.tex` を使うと、必要な回数だけ自動で回ります。

compileすると `.aux`、`.log`、`.bbl`、`.blg`、`.out` などの中間fileができます。消してもかまいません。

## 中身の見どころ

`main.tex` の先頭（1〜12行目）がpreambleで、使うpackageと文書の設定を書きます。

```latex
\documentclass[12pt,a4paper]{article}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{natbib}
\usepackage[margin=1in]{geometry}
```

`main_ja.tex` は、ここに日本語用の2行が入ります。

```latex
\usepackage{luatexja}
\usepackage[haranoaji]{luatexja-preset}
```

本文での引用は `\citep{jorda2005}` と書きます。`references.bib` の中に、同じkeyのentryがあります。

```bibtex
@article{jorda2005,
  author  = {Jord{\`a}, {\`O}scar},
  title   = {Estimation and Inference of Impulse Responses by Local Projections},
  journal = {American Economic Review},
  ...
}
```

文献リストの形は、本文の最後にある `\bibliographystyle{apalike}` が決めます。

番号付けは書きません。表に `\label{tab:events}` を付け、本文から `Table~\ref{tab:events}` で呼びます。表を入れ替えても番号は自動で付き直します。図も節も同じ仕組みです。

## 手元にTeXがない場合

Overleafを使うとinstallなしでcompileできます。このfolderをまとめてZIPにして、Overleafの「New Project」→「Upload Project」に投げると開けます。日本語版は、メニューの「Compiler」をLuaLaTeXに替えます。
