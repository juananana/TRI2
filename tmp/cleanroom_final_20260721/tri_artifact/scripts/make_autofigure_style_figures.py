from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTDIR = ROOT / "outputs" / "aaai_submission" / "figures" / "autofigure_style"
DEFAULT_SOURCE_COPY = (
    ROOT
    / "outputs"
    / "aaai_submission"
    / "tri_aaai2027_submission_source"
    / "figures"
    / "autofigure_style"
)


COMMON_PREAMBLE = r"""\documentclass[tikz,border=0pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{xcolor}
\usetikzlibrary{arrows.meta,calc,fit,positioning,backgrounds}
\definecolor{ink}{HTML}{14212B}
\definecolor{muted}{HTML}{5B6570}
\definecolor{line}{HTML}{CBD2D9}
\definecolor{paper}{HTML}{F7F9FA}
\definecolor{softblue}{HTML}{EAF2FF}
\definecolor{blue}{HTML}{356AA0}
\definecolor{softteal}{HTML}{E7F4F1}
\definecolor{teal}{HTML}{167D73}
\definecolor{softorange}{HTML}{F9ECE5}
\definecolor{orange}{HTML}{C4572D}
\definecolor{softred}{HTML}{F8E7E6}
\definecolor{red}{HTML}{B54642}
\definecolor{softgray}{HTML}{F1F3F5}
\definecolor{graybar}{HTML}{7A8793}
\definecolor{graybarlight}{HTML}{B3BBC3}
\tikzset{
  font=\sffamily,
  title/.style={font=\sffamily\bfseries\fontsize{8.5}{10}\selectfont, text=ink},
  tinylabel/.style={font=\sffamily\fontsize{5.8}{7}\selectfont, text=muted},
  small/.style={font=\sffamily\fontsize{6.5}{8}\selectfont, text=ink},
  smallbold/.style={font=\sffamily\bfseries\fontsize{6.7}{8}\selectfont, text=ink},
  card/.style={rounded corners=2.4pt, draw=line, line width=.42pt, fill=white, inner sep=3.5pt},
  softcard/.style={rounded corners=2.4pt, draw=line, line width=.42pt, inner sep=3.5pt},
  arrow/.style={-{Stealth[length=4pt,width=4.5pt]}, line width=.55pt, draw=muted},
  heavyarrow/.style={-{Stealth[length=4.8pt,width=5.2pt]}, line width=.85pt},
}
\begin{document}
"""


def write(path: Path, body: str) -> None:
    path.write_text(COMMON_PREAMBLE + body + "\n\\end{document}\n", encoding="utf-8")


def fig1() -> str:
    return r"""
\begin{tikzpicture}[x=1cm,y=1cm]
\path[fill=white] (0,0) rectangle (18.0,7.05);
\node[title,anchor=west] at (.25,6.72) {A. Same refresh, different authorization};
\node[title,anchor=west] at (11.35,6.72) {B. What generic state misses};

% Shared world transition.
\node[softcard,fill=softgray,minimum width=17.5cm,minimum height=.76cm,anchor=west] (world) at (.25,5.75) {};
\node[smallbold,anchor=west] at (.55,5.91) {$S_0$: A wins selector $q$};
\node[tinylabel,anchor=west] at (.55,5.62) {A: highest priority unread email};
\draw[arrow] (4.2,5.75) -- (5.35,5.75);
\node[smallbold] at (6.35,5.91) {refresh};
\node[tinylabel] at (6.35,5.62) {same external update};
\draw[arrow] (7.35,5.75) -- (8.55,5.75);
\node[smallbold,anchor=west] at (8.85,5.91) {$S_1$: B wins $q$; A still valid};
\node[tinylabel,anchor=west] at (8.85,5.62) {updating the world is not rebinding the target};

% Preserve lane.
\node[softcard,fill=softteal,minimum width=3.35cm,minimum height=1.18cm,anchor=west] (pinst) at (.35,4.05) {};
\node[smallbold,teal,anchor=west] at (.62,4.72) {PRESERVE};
\node[small,anchor=west] at (.62,4.38) {Choose $q$ now; refresh;};
\node[small,anchor=west] at (.62,4.08) {then act on it.};
\node[card,draw=teal,minimum width=2.55cm,minimum height=.95cm,anchor=west] (pbind) at (4.45,4.16) {};
\node[tinylabel,teal] at (5.73,4.64) {bind before refresh};
\node[smallbold] at (5.73,4.29) {$d(r)=A$};
\node[card,draw=teal,fill=softteal,minimum width=2.48cm,minimum height=.95cm,anchor=west] (ptgt) at (7.75,4.16) {};
\node[tinylabel] at (8.99,4.64) {authorized target};
\node[font=\sffamily\bfseries\fontsize{11}{12}\selectfont,text=teal] at (8.99,4.26) {A};
\draw[heavyarrow,draw=teal] (pinst.east) -- (pbind.west);
\draw[heavyarrow,draw=teal] (pbind.east) -- (ptgt.west);

% Reevaluate lane.
\node[softcard,fill=softorange,minimum width=3.35cm,minimum height=1.18cm,anchor=west] (rinst) at (.35,2.35) {};
\node[smallbold,orange,anchor=west] at (.62,3.02) {REEVALUATE};
\node[small,anchor=west] at (.62,2.68) {Refresh first; then};
\node[small,anchor=west] at (.62,2.38) {choose $q$ and act.};
\node[card,draw=orange,minimum width=2.55cm,minimum height=.95cm,anchor=west] (rbind) at (4.45,2.46) {};
\node[tinylabel,orange] at (5.73,2.94) {defer binding};
\node[smallbold] at (5.73,2.59) {$q$ executable at $S_1$};
\node[card,draw=orange,fill=softorange,minimum width=2.48cm,minimum height=.95cm,anchor=west] (rtgt) at (7.75,2.46) {};
\node[tinylabel] at (8.99,2.94) {authorized target};
\node[font=\sffamily\bfseries\fontsize{9}{11}\selectfont,text=orange] at (8.99,2.57) {B = $q(S_1)$};
\draw[heavyarrow,draw=orange] (rinst.east) -- (rbind.west);
\draw[heavyarrow,draw=orange] (rbind.east) -- (rtgt.west);

% Generic ambiguity panel.
\node[softcard,fill=paper,minimum width=5.95cm,minimum height=3.65cm,anchor=north west] (gen) at (11.35,4.93) {};
\node[smallbold,anchor=west] at (11.72,4.58) {Generic ledger};
\node[tinylabel,anchor=west] at (11.72,4.25) {stores ID, facts, selector, action};
\node[card,minimum width=1.46cm,minimum height=.55cm] at (12.25,3.55) {A};
\node[card,minimum width=1.46cm,minimum height=.55cm] at (14.05,3.55) {$q$};
\node[card,minimum width=1.46cm,minimum height=.55cm] at (15.85,3.55) {$S_1$};
\draw[arrow] (12.98,3.55) -- (13.32,3.55);
\draw[arrow] (14.78,3.55) -- (15.12,3.55);
\node[tinylabel,align=center,text width=5.1cm] at (14.35,2.84) {No field says whether $q$ is provenance for A or a live query after refresh.};
\node[softcard,fill=softred,draw=red,minimum width=4.7cm,minimum height=.72cm] at (14.35,1.93) {};
\node[smallbold,red] at (14.35,1.93) {re-running $q(S_1)$ can write B};

% Law strip.
\node[softcard,fill=softblue,draw=blue,minimum width=17.45cm,minimum height=.65cm,anchor=west] at (.28,.55) {};
\node[smallbold,blue,anchor=west] at (.58,.57) {TRI contract:};
\node[small,anchor=west] at (2.25,.57) {$d_{t+1}(r)\neq d_t(r)$ only when intervening language authorizes the denotation change.};
\end{tikzpicture}
"""


def fig2() -> str:
    return r"""
\begin{tikzpicture}[x=1cm,y=1cm]
\path[fill=white] (0,0) rectangle (18.0,7.35);
\node[title,anchor=west] at (.28,7.02) {Lifecycle-compiled control: make post-binding authorization executable};

% Main pipeline.
\node[softcard,fill=softgray,minimum width=3.25cm,minimum height=1.05cm,anchor=west] (input) at (.35,5.55) {};
\node[smallbold] at (1.98,6.07) {Instruction + $S_0$};
\node[tinylabel] at (1.98,5.75) {action schema included};

\node[card,draw=teal,minimum width=3.0cm,minimum height=1.05cm,anchor=west] (comp) at (4.35,5.55) {};
\node[smallbold,teal] at (5.85,6.07) {Lifecycle compiler};
\node[tinylabel] at (5.85,5.75) {before refresh};

\node[softcard,fill=softteal,draw=teal,minimum width=4.05cm,minimum height=1.05cm,anchor=west] (record) at (8.1,5.55) {};
\node[smallbold,teal] at (10.12,6.09) {Reference contract $L(r)$};
\node[tinylabel] at (10.12,5.75) {mode | ID | selector | validity | fallback};

\node[softcard,fill=softorange,draw=orange,minimum width=2.15cm,minimum height=1.05cm,anchor=west] (refresh) at (12.95,5.55) {};
\node[smallbold,orange] at (14.03,6.06) {Refresh};
\node[tinylabel] at (14.03,5.74) {observe $S_1$};

\node[card,draw=ink,minimum width=2.25cm,minimum height=1.05cm,anchor=west] (bound) at (15.7,5.55) {};
\node[smallbold] at (16.83,6.06) {Boundary};
\node[tinylabel] at (16.83,5.74) {act or reject};

\draw[heavyarrow,draw=muted] (input.east) -- (comp.west);
\draw[heavyarrow,draw=teal] (comp.east) -- (record.west);
\draw[heavyarrow,draw=orange] (record.east) -- (refresh.west);
\draw[heavyarrow,draw=muted] (refresh.east) -- (bound.west);

% Branches.
\node[softcard,fill=softteal,draw=teal,minimum width=4.3cm,minimum height=1.02cm,anchor=north west] (b1) at (1.0,4.15) {};
\node[smallbold,teal,anchor=west] at (1.28,3.82) {Preserve + valid};
\node[tinylabel,anchor=west] at (1.28,3.49) {emit bound ID; selector is provenance};
\node[font=\sffamily\bfseries\fontsize{11}{12}\selectfont,text=teal] at (4.7,3.68) {A};

\node[softcard,fill=softred,draw=red,minimum width=4.3cm,minimum height=1.02cm,anchor=north west] (b2) at (6.85,4.15) {};
\node[smallbold,red,anchor=west] at (7.13,3.82) {Preserve + invalid};
\node[tinylabel,anchor=west] at (7.13,3.49) {reject or apply explicit fallback};
\node[font=\sffamily\bfseries\fontsize{10}{12}\selectfont,text=red] at (10.5,3.68) {$\bot$};

\node[softcard,fill=softorange,draw=orange,minimum width=4.3cm,minimum height=1.02cm,anchor=north west] (b3) at (12.7,4.15) {};
\node[smallbold,orange,anchor=west] at (12.98,3.82) {Reevaluate};
\node[tinylabel,anchor=west] at (12.98,3.49) {actor resolves live selector in $S_1$};
\node[font=\sffamily\bfseries\fontsize{9}{11}\selectfont,text=orange] at (16.1,3.68) {$q(S_1)$};

\draw[arrow] (16.83,5.55) |- (3.15,4.15);
\draw[arrow] (16.83,5.55) |- (9.0,4.15);
\draw[arrow] (16.83,5.55) |- (14.85,4.15);

% Factorial comparison strip.
\node[title,anchor=west] at (.35,2.58) {Factorial evaluation isolates representation from execution};
\node[softcard,fill=paper,minimum width=17.3cm,minimum height=1.75cm,anchor=west] at (.35,.72) {};
\node[smallbold,anchor=west] at (.75,1.95) {State representation};
\node[softcard,fill=softgray,minimum width=3.45cm,minimum height=.67cm,anchor=west] at (.75,1.2) {};
\node[small] at (2.47,1.2) {Generic structured ledger};
\node[tinylabel,anchor=west] at (4.35,1.2) {ID + facts + selector, but no reference mode};
\node[softcard,fill=softteal,draw=teal,minimum width=3.45cm,minimum height=.67cm,anchor=west] at (.75,.38) {};
\node[smallbold,teal] at (2.47,.38) {Lifecycle state};
\node[tinylabel,anchor=west] at (4.35,.38) {committed identity and authorized transition are explicit};

\node[smallbold,anchor=west] at (11.0,1.95) {Execution};
\node[softcard,fill=white,minimum width=2.55cm,minimum height=.67cm,anchor=west] at (11.0,1.2) {};
\node[small] at (12.28,1.2) {Free actor};
\node[softcard,fill=white,draw=teal,minimum width=2.55cm,minimum height=.67cm,anchor=west] at (14.0,1.2) {};
\node[smallbold,teal] at (15.28,1.2) {Gated};
\node[tinylabel,anchor=west] at (11.0,.42) {The paper crosses both axes to measure what actually drives the gain.};
\end{tikzpicture}
"""


def fig3() -> str:
    return r"""
\begin{tikzpicture}[x=1cm,y=1cm]
\path[fill=white] (0,0) rectangle (18.0,7.1);
\node[title,anchor=west] at (.28,6.78) {Factorial results: lifecycle representation is the main effect};
\node[tinylabel,anchor=west] at (.28,6.42) {Accuracy is exact target or final SQLite state. Bars follow Table 4 in the AAAI draft.};

% Helper macro-like chart drawn inline.
\foreach \x/\name/\vals/\gain in {
  .55/{Qwen primary}/{64.4,65.0,96.9,98.1}/{+31.9},
  5.65/{GLM primary}/{71.9,73.1,98.1,100.0}/{+25.0},
  10.1/{Qwen transfer}/{46.2,46.2,87.5,82.5}/{+41.2}
} {
  \node[smallbold,anchor=west] at (\x,5.95) {\name};
  \draw[line,line width=.4pt] (\x,2.05) -- ++(4.25,0);
  \foreach \t in {0,50,100} {
    \draw[line,line width=.3pt] (\x,2.05+3.2*\t/100) -- ++(4.25,0);
    \node[tinylabel,anchor=east] at (\x-.08,2.05+3.2*\t/100) {\t};
  }
}

% Qwen primary bars.
\foreach \i/\v/\c/\lab in {0/64.4/graybarlight/GF,1/65.0/graybar/GG,2/96.9/teal!55/LF,3/98.1/teal/LG} {
  \pgfmathsetmacro{\bx}{.95+\i*.83}
  \pgfmathsetmacro{\bh}{3.2*\v/100}
  \fill[\c] (\bx,2.05) rectangle ++(.42,\bh);
  \node[tinylabel,rotate=90] at (\bx+.21,1.62) {\lab};
  \node[font=\sffamily\bfseries\fontsize{5.3}{6}\selectfont,text=ink] at (\bx+.21,2.16+\bh) {\v};
}
\node[softcard,fill=softteal,draw=teal,minimum width=1.4cm,minimum height=.46cm] at (4.15,5.16) {};
\node[smallbold,teal] at (4.15,5.16) {+31.9};

% GLM primary bars.
\foreach \i/\v/\c/\lab in {0/71.9/graybarlight/GF,1/73.1/graybar/GG,2/98.1/teal!55/LF,3/100.0/teal/LG} {
  \pgfmathsetmacro{\bx}{6.05+\i*.83}
  \pgfmathsetmacro{\bh}{3.2*\v/100}
  \fill[\c] (\bx,2.05) rectangle ++(.42,\bh);
  \node[tinylabel,rotate=90] at (\bx+.21,1.62) {\lab};
  \node[font=\sffamily\bfseries\fontsize{5.3}{6}\selectfont,text=ink] at (\bx+.21,2.16+\bh) {\v};
}
\node[softcard,fill=softteal,draw=teal,minimum width=1.4cm,minimum height=.46cm] at (9.25,5.16) {};
\node[smallbold,teal] at (9.25,5.16) {+25.0};

% Transfer bars.
\foreach \i/\v/\c/\lab in {0/46.2/graybarlight/GF,1/46.2/graybar/GG,2/87.5/teal!55/LF,3/82.5/teal/LG} {
  \pgfmathsetmacro{\bx}{10.5+\i*.83}
  \pgfmathsetmacro{\bh}{3.2*\v/100}
  \fill[\c] (\bx,2.05) rectangle ++(.42,\bh);
  \node[tinylabel,rotate=90] at (\bx+.21,1.62) {\lab};
  \node[font=\sffamily\bfseries\fontsize{5.3}{6}\selectfont,text=ink] at (\bx+.21,2.16+\bh) {\v};
}
\node[softcard,fill=softteal,draw=teal,minimum width=1.4cm,minimum height=.46cm] at (13.7,5.16) {};
\node[smallbold,teal] at (13.7,5.16) {+41.2};

% SQLite consequence panel.
\node[softcard,fill=paper,minimum width=3.35cm,minimum height=4.1cm,anchor=north west] at (14.5,6.08) {};
\node[smallbold,anchor=west] at (14.78,5.72) {SQLite consequences};
\node[tinylabel,anchor=west] at (14.78,5.39) {80 paired trajectories};
\node[softcard,fill=softred,draw=red,minimum width=2.75cm,minimum height=.82cm] at (16.15,4.65) {};
\node[font=\sffamily\bfseries\fontsize{14}{15}\selectfont,text=red] at (15.32,4.55) {21};
\node[tinylabel,anchor=west,align=left] at (15.72,4.66) {Generic\\wrong writes};
\node[softcard,fill=softteal,draw=teal,minimum width=2.75cm,minimum height=.82cm] at (16.15,3.55) {};
\node[font=\sffamily\bfseries\fontsize{14}{15}\selectfont,text=teal] at (15.32,3.45) {0};
\node[tinylabel,anchor=west,align=left] at (15.72,3.56) {Lifecycle\\wrong writes};
\node[smallbold,anchor=west] at (14.78,2.55) {Final DB state};
\node[softcard,fill=white,minimum width=1.2cm,minimum height=.62cm] at (15.42,2.03) {};
\node[smallbold,text=graybar] at (15.42,2.09) {53/80};
\node[tinylabel] at (15.42,1.78) {Generic};
\node[softcard,fill=white,draw=teal,minimum width=1.2cm,minimum height=.62cm] at (16.78,2.03) {};
\node[smallbold,text=teal] at (16.78,2.09) {80/80};
\node[tinylabel] at (16.78,1.78) {Lifecycle};

% Legend.
\foreach \x/\c/\txt in {.7/graybarlight/Generic + actor,3.55/graybar/Generic + gate,6.25/teal!55/Lifecycle + actor,9.25/teal/Lifecycle + gate} {
  \fill[\c] (\x,.56) rectangle ++(.22,.22);
  \node[tinylabel,anchor=west] at (\x+.32,.67) {\txt};
}
\node[tinylabel,anchor=west] at (12.7,.67) {GF/GG/LF/LG are bar labels.};
\end{tikzpicture}
"""


FIGURES = {
    "tri_fig1_reference_contrast": fig1,
    "tri_fig2_lifecycle_controller": fig2,
    "tri_fig3_factorial_dashboard": fig3,
}


def compile_tex(tex_path: Path) -> None:
    subprocess.run(
        [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            tex_path.name,
        ],
        cwd=tex_path.parent,
        check=True,
    )


def copy_outputs(outdir: Path, source_copy: Path) -> None:
    source_copy.mkdir(parents=True, exist_ok=True)
    for suffix in (".tex", ".pdf"):
        for path in outdir.glob(f"tri_fig*{suffix}"):
            shutil.copy2(path, source_copy / path.name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    parser.add_argument("--no-compile", action="store_true")
    parser.add_argument("--no-source-copy", action="store_true")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for name, make_body in FIGURES.items():
        tex_path = outdir / f"{name}.tex"
        write(tex_path, make_body())
        if not args.no_compile:
            compile_tex(tex_path)

    if not args.no_source_copy:
        copy_outputs(outdir, DEFAULT_SOURCE_COPY)

    for name in FIGURES:
        pdf = outdir / f"{name}.pdf"
        print(pdf if pdf.exists() else outdir / f"{name}.tex")


if __name__ == "__main__":
    main()
