#!/usr/bin/env python3
"""Render the formal Chinese TRI research summary as a CJK PDF."""

from pathlib import Path
import re
import subprocess

from render_tri_progress_report_pdf import inline, table_block


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "planning" / "TRI_formal_research_summary_zh.md"
OUT_DIR = ROOT / "output" / "pdf"
TEX = OUT_DIR / "TRI_formal_research_summary_zh.tex"
PDF = OUT_DIR / "TRI_formal_research_summary_zh.pdf"


def render_body() -> str:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    index = lines.index("## 摘要")
    body = []
    while index < len(lines):
        line = lines[index].rstrip()
        if line.startswith("## "):
            body.append(r"\section{" + inline(line[3:]) + "}")
            index += 1
            continue
        if line.startswith("### "):
            body.append(r"\subsection{" + inline(line[4:]) + "}")
            index += 1
            continue
        if "|" in line and index + 1 < len(lines) and "|" in lines[index + 1]:
            rendered, index = table_block(lines, index)
            body.append(rendered)
            continue
        if re.match(r"^[-*] ", line):
            items = []
            while index < len(lines) and re.match(r"^[-*] ", lines[index]):
                items.append(r"\item " + inline(lines[index][2:]))
                index += 1
            body.extend([r"\begin{itemize}", *items, r"\end{itemize}"])
            continue
        if re.match(r"^\d+\. ", line):
            items = []
            while index < len(lines) and re.match(r"^\d+\. ", lines[index]):
                items.append(r"\item " + inline(re.sub(r"^\d+\. ", "", lines[index])))
                index += 1
            body.extend([r"\begin{enumerate}", *items, r"\end{enumerate}"])
            continue
        if not line.strip():
            index += 1
            continue
        paragraph = [line]
        index += 1
        while index < len(lines) and lines[index].strip() and not re.match(
            r"^(#|[-*] |\d+\. )", lines[index]
        ) and "|" not in lines[index]:
            paragraph.append(lines[index].strip())
            index += 1
        body.append(r"\par " + inline(" ".join(paragraph)))
    return "\n".join(body)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    document = r"""\documentclass[10.5pt,fontset=none]{ctexart}
\setCJKmainfont[Path=/System/Library/Fonts/Supplemental/,Extension=.ttc]{Songti}
\setCJKsansfont[Path=/System/Library/Fonts/,Extension=.ttc]{STHeiti Medium}
\setcounter{secnumdepth}{0}
\usepackage[a4paper,margin=2.2cm,headheight=14pt]{geometry}
\usepackage{booktabs,longtable,array,enumitem,xcolor,fancyhdr,hyperref,ragged2e}
\hypersetup{colorlinks=true,linkcolor=black,urlcolor=blue}
\definecolor{TRIBlue}{HTML}{2E74B5}
\definecolor{TRIDark}{HTML}{1F4D78}
\definecolor{TRIMuted}{HTML}{5F6973}
\setlength{\parindent}{2em}
\setlength{\parskip}{0.36em}
\linespread{1.04}
\setlist{leftmargin=2.2em,itemsep=0.25em,topsep=0.35em}
\renewcommand{\arraystretch}{1.24}
\setlength{\tabcolsep}{4pt}
\pagestyle{fancy}
\fancyhf{}
\lhead{\small\color{TRIMuted}TRI 论文研究总结}
\rhead{\small\color{TRIMuted}2026 年 7 月 21 日}
\cfoot{\thepage}
\ctexset{
  section={format=\Large\bfseries\sffamily\color{TRIBlue},beforeskip=1.2em,afterskip=0.6em},
  subsection={format=\large\bfseries\sffamily\color{TRIDark},beforeskip=0.9em,afterskip=0.4em}
}
\begin{document}
\begin{flushleft}
{\small\bfseries\sffamily\color{TRIBlue}研究总结}\par\vspace{0.45cm}
{\Huge\bfseries\sffamily 更新世界状态不等于重新绑定操作目标}\par\vspace{0.25cm}
{\Large\sffamily\color{TRIDark}工具型智能体中的时序指称完整性}\par\vspace{0.8cm}
{\small\textbf{英文题目：}Updating the World Is Not Rebinding the Target: Temporal Referent Integrity in Tool-Using Agents}\par
{\small\textbf{投稿方向：}AAAI 2027 Main Technical Track}\par
{\small\textbf{更新时间：}2026 年 7 月 21 日}\par\vspace{0.35cm}
{\color{TRIBlue}\rule{\textwidth}{1.1pt}}
\end{flushleft}
""" + render_body() + r"""
\end{document}
"""
    TEX.write_text(document, encoding="utf-8")
    for _ in range(2):
        subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", TEX.name],
            cwd=OUT_DIR,
            check=True,
        )
    print(PDF)


if __name__ == "__main__":
    main()
