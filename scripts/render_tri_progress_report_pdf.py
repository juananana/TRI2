#!/usr/bin/env python3
"""Render the formal Chinese TRI progress report as a CJK LaTeX PDF."""

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "planning" / "TRI_paper_progress_report_zh.md"
OUT_DIR = ROOT / "output" / "pdf"
TEX = OUT_DIR / "TRI_paper_progress_report_zh.tex"
PDF = OUT_DIR / "TRI_paper_progress_report_zh.pdf"


def inline(text: str) -> str:
    text = text.replace("—", "-").replace("–", "--").replace("…", "...")
    protected = []

    def hold(value: str) -> str:
        protected.append(value)
        return f"ZZPROTECTED{len(protected) - 1}ZZ"

    text = re.sub(r"\*\*(.+?)\*\*", lambda m: hold(r"\textbf{" + inline(m.group(1)) + "}"), text)
    text = re.sub(r"`(.+?)`", lambda m: hold(r"\texttt{" + escape(m.group(1)) + "}"), text)
    text = escape(text)
    for index, value in enumerate(protected):
        text = text.replace(f"ZZPROTECTED{index}ZZ", value)
    return text


def escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def table_block(lines: list[str], start: int) -> tuple[str, int]:
    rows = []
    index = start
    while index < len(lines) and "|" in lines[index]:
        cells = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            rows.append(cells)
        index += 1
    if not rows:
        return "", index
    count = max(len(row) for row in rows)
    width = max(0.10, min(0.94 / count, 0.22))
    columns = "@{}" + " ".join(f"p{{{width:.3f}\\linewidth}}" for _ in range(count)) + "@{}"
    output = [r"\begin{longtable}{" + columns + "}", r"\toprule"]
    for row_index, row in enumerate(rows):
        row += [""] * (count - len(row))
        rendered = " & ".join(inline(cell) for cell in row) + r" \\"
        output.append(rendered)
        if row_index == 0:
            output.append(r"\midrule\endhead")
    output.extend([r"\bottomrule", r"\end{longtable}", ""])
    return "\n".join(output), index


def render() -> str:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    body = []
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        if line.startswith("# "):
            index += 1
            continue
        if re.match(r"^(更新时间|拟投稿|拟题|论文题目|中文题目)：", line):
            index += 1
            continue
        if line.startswith("## "):
            body.append(r"\section{" + inline(line[3:]) + "}")
            index += 1
            continue
        if line.startswith("### "):
            body.append(r"\subsection{" + inline(line[4:]) + "}")
            index += 1
            continue
        if line.startswith("#### "):
            body.append(r"\subsubsection{" + inline(line[5:]) + "}")
            index += 1
            continue
        if "|" in line and index + 1 < len(lines) and "|" in lines[index + 1]:
            rendered, index = table_block(lines, index)
            body.append(rendered)
            continue
        if line.startswith("> "):
            quote = []
            while index < len(lines) and lines[index].startswith("> "):
                quote.append(inline(lines[index][2:]))
                index += 1
            body.append(r"\begin{quote}\small " + " ".join(quote) + r"\end{quote}")
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
            r"^(#|[-*] |\d+\. |> )", lines[index]
        ) and "|" not in lines[index]:
            paragraph.append(lines[index].strip())
            index += 1
        body.append(r"\par " + inline(" ".join(paragraph)))
    return "\n".join(body)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    document = r"""\documentclass[10pt,fontset=none]{ctexart}
\setCJKmainfont[Path=/System/Library/Fonts/Supplemental/,Extension=.ttc]{Songti}
\setCJKsansfont[Path=/System/Library/Fonts/,Extension=.ttc]{STHeiti Medium}
\setcounter{secnumdepth}{0}
\usepackage[a4paper,margin=2.1cm,headheight=14pt]{geometry}
\usepackage{booktabs,longtable,array,enumitem,xcolor,fancyhdr,hyperref}
\hypersetup{colorlinks=true,linkcolor=black,urlcolor=blue}
\setlength{\parindent}{2em}
\setlength{\parskip}{0.35em}
\linespread{0.91}
\setlist{nosep,leftmargin=2.2em}
\renewcommand{\arraystretch}{1.18}
\pagestyle{fancy}
\fancyhf{}
\lhead{TRI 论文研究进展与投稿可行性报告}
\rhead{2026 年 7 月 21 日}
\cfoot{\thepage}
\title{\vspace{-1.2cm}\textbf{TRI 论文研究进展与投稿可行性报告}}
\author{拟投稿：AAAI 2027 Main Technical Track\\
\parbox{0.92\textwidth}{\centering\small 英文题目：Updating the World Is Not Rebinding the Target: Temporal Referent Integrity in Tool-Using Agents}\\
中文题目：更新世界状态不等于重新绑定操作目标：工具型智能体中的时序指称完整性}
\date{2026 年 7 月 21 日}
\begin{document}
\maketitle
\thispagestyle{fancy}
""" + render() + r"""
\end{document}
"""
    TEX.write_text(document, encoding="utf-8")
    for _ in range(2):
        subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", TEX.name], cwd=OUT_DIR, check=True)
    print(PDF)


if __name__ == "__main__":
    main()
