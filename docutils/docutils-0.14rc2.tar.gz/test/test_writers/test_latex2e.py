# -*- coding: utf-8 -*-
#! /usr/bin/env python

# $Id: test_latex2e.py 8058 2017-04-19 16:45:32Z milde $
# Author: engelbert gruber <grubert@users.sourceforge.net>
# Copyright: This module has been placed in the public domain.

"""
Tests for latex2e writer.
"""

import string
from __init__ import DocutilsTestSupport

def suite():
    settings = {'use_latex_toc': False}
    s = DocutilsTestSupport.PublishTestSuite('latex', suite_settings=settings)
    s.generateTests(totest)
    settings['use_latex_toc'] = True
    s.generateTests(totest_latex_toc)
    settings['use_latex_toc'] = False
    settings['sectnum_xform'] = False
    s.generateTests(totest_latex_sectnum)
    settings['sectnum_xform'] = True
    settings['use_latex_citations'] = True
    s.generateTests(totest_latex_citations)
    settings['table_style'] = ['colwidths-auto']
    s.generateTests(totest_table_style_auto)
    settings['table_style'] = ['booktabs']
    s.generateTests(totest_table_style_booktabs)
    settings['stylesheet_path'] = 'data/spam,data/ham.tex'
    s.generateTests(totest_stylesheet)
    settings['embed_stylesheet'] = True
    settings['warning_stream'] = ''
    s.generateTests(totest_stylesheet_embed)
    return s

head_template = string.Template(
r"""$head_prefix% generated by Docutils <http://docutils.sourceforge.net/>
\usepackage{cmap} % fix search and cut-and-paste in Acrobat
$requirements
%%% Custom LaTeX preamble
$latex_preamble
%%% User specified packages and stylesheets
$stylesheet
%%% Fallback definitions for Docutils-specific commands
$fallbacks$pdfsetup
$titledata
%%% Body
\begin{document}
""")

parts = dict(
head_prefix = r"""\documentclass[a4paper]{article}
""",
requirements = r"""\usepackage{ifthen}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
""",
latex_preamble = r"""% PDF Standard Fonts
\usepackage{mathptmx} % Times
\usepackage[scaled=.90]{helvet}
\usepackage{courier}
""",
longtable = r"""\usepackage{longtable,ltcaption,array}
\setlength{\extrarowheight}{2pt}
\newlength{\DUtablewidth} % internal use in tables
""",
stylesheet = '',
fallbacks =  '',
fallbacks_highlight = r"""% basic code highlight:
\providecommand*\DUrolecomment[1]{\textcolor[rgb]{0.40,0.40,0.40}{#1}}
\providecommand*\DUroledeleted[1]{\textcolor[rgb]{0.40,0.40,0.40}{#1}}
\providecommand*\DUrolekeyword[1]{\textbf{#1}}
\providecommand*\DUrolestring[1]{\textit{#1}}

% inline markup (custom roles)
% \DUrole{#1}{#2} tries \DUrole#1{#2}
\providecommand*{\DUrole}[2]{%
  % backwards compatibility: try \docutilsrole#1{#2}
  \ifcsname docutilsrole#1\endcsname%
    \csname docutilsrole#1\endcsname{#2}%
  \else
    \csname DUrole#1\endcsname{#2}%
  \fi%
}
""",
pdfsetup = r"""
% hyperlinks:
\ifthenelse{\isundefined{\hypersetup}}{
  \usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
  \usepackage{bookmark}
  \urlstyle{same} % normal text font (alternatives: tt, rm, sf)
}{}
""",
titledata = '')

head = head_template.substitute(parts)

head_table = head_template.substitute(
    dict(parts, requirements = parts['requirements'] + parts['longtable']))

head_booktabs = head_template.substitute(
    dict(parts, requirements=parts['requirements']
         + '\\usepackage{booktabs}\n' + parts['longtable']))

head_textcomp = head_template.substitute(
    dict(parts, requirements = parts['requirements'] +
r"""\usepackage{textcomp} % text symbol macros
"""))

head_alltt = head_template.substitute(
    dict(parts, requirements = parts['requirements'] +
r"""\usepackage{alltt}
"""))


totest = {}
totest_latex_toc = {}
totest_latex_sectnum = {}
totest_latex_citations = {}
totest_stylesheet = {}
totest_stylesheet_embed = {}
totest_table_style_auto = {}
totest_table_style_booktabs = {}

totest['url_chars'] = [
["http://nowhere/url_with%28parens%29",
head + r"""
\url{http://nowhere/url_with\%28parens\%29}

\end{document}
"""],
]

totest['textcomp'] = [
["2 µm is just 2/1000000 m",
head_textcomp + r"""
2 µm is just 2/1000000 m

\end{document}
"""],
]

totest['spanish quote'] = [
[".. role:: language-es\n\nUnd damit :language-es:`basta`!",
head_template.substitute(dict(parts, requirements =
r"""\usepackage{ifthen}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[spanish,english]{babel}
\AtBeginDocument{\shorthandoff{.<>}}
""")) + r"""
Und damit \foreignlanguage{spanish}{basta}!

\end{document}
"""],
]

totest['code role'] = [
[":code:`x=1`",
head_template.substitute(dict(parts, requirements = parts['requirements']+
r"""\usepackage{color}
""", fallbacks = parts['fallbacks_highlight'])) + r"""
\texttt{\DUrole{code}{x=1}}

\end{document}
"""],
]

totest['table_of_contents'] = [
# input
["""\
.. contents:: Table of Contents

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.
""",
## # expected output
head_template.substitute(dict(parts,
    requirements=parts['requirements'] + '\\setcounter{secnumdepth}{0}\n',
    fallbacks=r"""
% title for topics, admonitions, unsupported section levels, and sidebar
\providecommand*{\DUtitle}[2][class-arg]{%
  % call \DUtitle#1{#2} if it exists:
  \ifcsname DUtitle#1\endcsname%
    \csname DUtitle#1\endcsname{#2}%
  \else
    \smallskip\noindent\textbf{#2}\smallskip%
  \fi
}
""")) + r"""
\phantomsection\label{table-of-contents}
\pdfbookmark[1]{Table of Contents}{table-of-contents}
\DUtitle[contents]{Table of Contents}

\begin{list}{}{}
\item \hyperref[title-1]{Title 1}

\begin{list}{}{}
\item \hyperref[title-2]{Title 2}
\end{list}
\end{list}


\section{Title 1%
  \label{title-1}%
}

Paragraph 1.


\subsection{Title 2%
  \label{title-2}%
}

Paragraph 2.

\end{document}
"""],
]

totest['footnote text'] = [
# input
["""\
.. [1] paragraph

.. [2]

.. [3] 1. enumeration
""",
## # expected output
head_template.substitute(dict(parts,
    fallbacks=r"""% numeric or symbol footnotes with hyperlinks
\providecommand*{\DUfootnotemark}[3]{%
  \raisebox{1em}{\hypertarget{#1}{}}%
  \hyperlink{#2}{\textsuperscript{#3}}%
}
\providecommand{\DUfootnotetext}[4]{%
  \begingroup%
  \renewcommand{\thefootnote}{%
    \protect\raisebox{1em}{\protect\hypertarget{#1}{}}%
    \protect\hyperlink{#2}{#3}}%
  \footnotetext{#4}%
  \endgroup%
}
""")) + r"""%
\DUfootnotetext{id1}{id1}{1}{%
paragraph
}
%
\DUfootnotetext{id2}{id2}{2}{}
%
\DUfootnotetext{id3}{id3}{3}{
\begin{enumerate}
\item enumeration
\end{enumerate}
}

\end{document}
"""],
]

totest_latex_toc['no_sectnum'] = [
# input
["""\
.. contents::

first section
-------------
""",
## # expected output
head_template.substitute(dict(parts,
    requirements=parts['requirements'] + '\\setcounter{secnumdepth}{0}\n'
)) + r"""
\phantomsection\label{contents}
\pdfbookmark[1]{Contents}{contents}
\tableofcontents


\section{first section%
  \label{first-section}%
}

\end{document}
"""],
]

totest_latex_toc['sectnum'] = [
# input
["""\
.. contents::
.. sectnum::

first section
-------------
""",
## # expected output
head_template.substitute(dict(parts,
    requirements=parts['requirements'] + '\\setcounter{secnumdepth}{0}\n'
)) + r"""
\phantomsection\label{contents}
\pdfbookmark[1]{Contents}{contents}
\tableofcontents


\section{1   first section%
  \label{first-section}%
}

\end{document}
"""],
]


totest_latex_sectnum['no_sectnum'] = [
# input
["""\
some text

first section
-------------
""",
## # expected output
head_template.substitute(dict(parts, requirements = parts['requirements'] +
r"""\setcounter{secnumdepth}{0}
""")) + r"""
some text


\section{first section%
  \label{first-section}%
}

\end{document}
"""],
]

totest_latex_sectnum['sectnum'] = [
# input
["""\
.. sectnum::

some text

first section
-------------
""",
## # expected output
head_template.substitute(dict(parts,
    requirements=parts['requirements'] + '\\setcounter{secnumdepth}{0}\n'
)) + r"""
some text


\section{first section%
  \label{first-section}%
}

\end{document}
"""],
]

totest_latex_citations['citations_with_underscore'] = [
# input
["""\
Just a test citation [my_cite2006]_.

.. [my_cite2006]
   The underscore is mishandled.
""",
## # expected output
head + r"""
Just a test citation \cite{my_cite2006}.

\begin{thebibliography}{my\_cite2006}
\bibitem[my\_cite2006]{my_cite2006}{
The underscore is mishandled.
}
\end{thebibliography}

\end{document}
"""],
]


totest_latex_citations['adjacent_citations'] = [
# input
["""\
Two non-citations: [MeYou2007]_[YouMe2007]_.

Need to be separated for grouping: [MeYou2007]_ [YouMe2007]_.

Two spaces (or anything else) for no grouping: [MeYou2007]_  [YouMe2007]_.

But a line break should work: [MeYou2007]_
[YouMe2007]_.

.. [MeYou2007] not.
.. [YouMe2007] important.
""",
# expected output
head + r"""
Two non-citations: {[}MeYou2007{]}\_{[}YouMe2007{]}\_.

Need to be separated for grouping: \cite{MeYou2007,YouMe2007}.

Two spaces (or anything else) for no grouping: \cite{MeYou2007}  \cite{YouMe2007}.

But a line break should work: \cite{MeYou2007,YouMe2007}.

\begin{thebibliography}{MeYou2007}
\bibitem[MeYou2007]{MeYou2007}{
not.
}
\bibitem[YouMe2007]{YouMe2007}{
important.
}
\end{thebibliography}

\end{document}
"""],
]


totest['enumerated_lists'] = [
# input
["""\
1. Item 1.
2. Second to the previous item this one will explain

  a) nothing.
  b) or some other.

3. Third is

  (I) having pre and postfixes
  (II) in roman numerals.
""",
# expected output
head + r"""
\begin{enumerate}
\item Item 1.

\item Second to the previous item this one will explain
\end{enumerate}

\begin{quote}
\begin{enumerate}
\renewcommand{\labelenumi}{\alph{enumi})}
\item nothing.

\item or some other.
\end{enumerate}
\end{quote}

\begin{enumerate}
\setcounter{enumi}{2}
\item Third is
\end{enumerate}

\begin{quote}
\begin{enumerate}
\renewcommand{\labelenumi}{(\Roman{enumi})}
\item having pre and postfixes

\item in roman numerals.
\end{enumerate}
\end{quote}

\end{document}
"""],
]

# TODO: need to test for quote replacing if the language uses "ASCII-quotes"
# as active character (e.g. de (ngerman)).


totest['table_caption'] = [
# input
["""\
.. table:: Foo

   +-----+-----+
   |     |     |
   +-----+-----+
   |     |     |
   +-----+-----+
""",
head_table + r"""
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable}[c]{|p{0.075\DUtablewidth}|p{0.075\DUtablewidth}|}
\caption{Foo}\\
\hline
 &  \\
\hline
 &  \\
\hline
\end{longtable}

\end{document}
"""],
]

totest['table_styles'] = [
["""\
.. table::
   :class: borderless

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
   |  3  |  4  |
   +-----+-----+
""",
head_table + r"""
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable*}[c]{p{0.075\DUtablewidth}p{0.075\DUtablewidth}}

1
 & 
2
 \\

3
 & 
4
 \\
\end{longtable*}

\end{document}
"""],
["""\
.. table::
   :class: booktabs

   +-----+-+
   |  1  |2|
   +-----+-+
""",
head_booktabs + r"""
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable*}[c]{p{0.075\DUtablewidth}p{0.028\DUtablewidth}}
\toprule

1
 & 
2
 \\
\bottomrule
\end{longtable*}

\end{document}
"""],
["""\
.. table::
   :class: colwidths-auto

   +-----+-+
   |  1  |2|
   +-----+-+
""",
head_table + r"""
\begin{longtable*}[c]{|l|l|}
\hline
1 & 2 \\
\hline
\end{longtable*}

\end{document}
"""],
["""\
.. table::
   :widths: auto

   +-----+-+
   |  1  |2|
   +-----+-+
""",
head_table + r"""
\begin{longtable*}[c]{|l|l|}
\hline
1 & 2 \\
\hline
\end{longtable*}

\end{document}
"""],
["""\
.. table::
   :widths: 15, 30

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
""",
head_table + r"""
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable*}[c]{|p{0.191\DUtablewidth}|p{0.365\DUtablewidth}|}
\hline

1
 & 
2
 \\
\hline
\end{longtable*}

\end{document}
"""],
]

totest_table_style_booktabs['table_styles'] = [
# borderless overrides "booktabs" table_style
["""\
.. table::
   :class: borderless

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
   |  3  |  4  |
   +-----+-----+
""",
head_table + r"""
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable*}[c]{p{0.075\DUtablewidth}p{0.075\DUtablewidth}}

1
 & 
2
 \\

3
 & 
4
 \\
\end{longtable*}

\end{document}
"""],
["""\
.. table::
   :widths: auto

   +-----+-+
   |  1  |2|
   +-----+-+
""",
head_booktabs + r"""
\begin{longtable*}[c]{ll}
\toprule
1 & 2 \\
\bottomrule
\end{longtable*}

\end{document}
"""],
["""\
.. table::
   :widths: 15, 30

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
""",
head_booktabs + r"""
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable*}[c]{p{0.191\DUtablewidth}p{0.365\DUtablewidth}}
\toprule

1
 & 
2
 \\
\bottomrule
\end{longtable*}

\end{document}
"""],
]
totest_table_style_auto['table_styles'] = [
["""\
.. table::
   :class: borderless

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
   |  3  |  4  |
   +-----+-----+
""",
head_table + r"""
\begin{longtable*}[c]{ll}
1 & 2 \\
3 & 4 \\
\end{longtable*}

\end{document}
"""],
["""\
.. table::
   :class: booktabs

   +-----+-+
   |  1  |2|
   +-----+-+
""",
head_booktabs + r"""
\begin{longtable*}[c]{ll}
\toprule
1 & 2 \\
\bottomrule
\end{longtable*}

\end{document}
"""],
# given width overrides "colwidth-auto"
["""\
.. table::
   :widths: 15, 30

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
""",
head_table + r"""
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable*}[c]{|p{0.191\DUtablewidth}|p{0.365\DUtablewidth}|}
\hline

1
 & 
2
 \\
\hline
\end{longtable*}

\end{document}
"""],
]

totest['table_align'] = [
# input
["""\
.. table::
   :align: right

   +-----+-----+
   |  1  |  2  |
   +-----+-----+
""",
head_table + r"""
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable*}[r]{|p{0.075\DUtablewidth}|p{0.075\DUtablewidth}|}
\hline

1
 & 
2
 \\
\hline
\end{longtable*}

\end{document}
"""],
]

totest['table_empty_thead_entry'] = [
# input
["""\
===== ======
Title
===== ======
entry value1
===== ======
""",
head_table + r"""
\setlength{\DUtablewidth}{\linewidth}
\begin{longtable*}[c]{|p{0.075\DUtablewidth}|p{0.086\DUtablewidth}|}
\hline
\textbf{%
Title
} &  \\
\hline
\endfirsthead
\hline
\textbf{%
Title
} &  \\
\hline
\endhead
\multicolumn{2}{c}{\hfill ... continued on next page} \\
\endfoot
\endlastfoot

entry
 & 
value1
 \\
\hline
\end{longtable*}

\end{document}
"""],
]

# The "[" needs to be protected (otherwise it will be seen as an
# option to "\\", "\item", etc. ).

totest['bracket_protection'] = [
# input
["""
* [no option] to this item
""",
head + r"""
\begin{itemize}
\item {[}no option{]} to this item
\end{itemize}

\end{document}
"""],
]

totest['literal_block'] = [
# input
["""\
Test special characters { [ \\\\ ] } in literal block::

  { [ ( \macro

  } ] )
""",
head_alltt + r"""
Test special characters \{ {[} \textbackslash{} {]} \} in literal block:

\begin{quote}
\begin{alltt}
\{ [ ( \textbackslash{}macro

\} ] )
\end{alltt}
\end{quote}

\end{document}
"""],
]

totest['raw'] = [
[r""".. raw:: latex

   $E=mc^2$

A paragraph.

.. |sub| raw:: latex

   (some raw text)

Foo |sub|
same paragraph.
""",
head + r"""
$E=mc^2$

A paragraph.

Foo (some raw text)
same paragraph.

\end{document}
"""],
]

totest['title_with_inline_markup'] = [
["""\
This is the *Title*
===================

This is the *Subtitle*
----------------------

This is a *section title*
~~~~~~~~~~~~~~~~~~~~~~~~~

This is the *document*.
""",
head_template.substitute(dict(parts,
    requirements=parts['requirements'] + '\\setcounter{secnumdepth}{0}\n',
    fallbacks=r"""
% subtitle (in document title)
\providecommand*{\DUdocumentsubtitle}[1]{{\large #1}}
""",
    pdfsetup=parts['pdfsetup'] + r"""\hypersetup{
  pdftitle={This is the Title},
}
""", titledata=r"""%%% Title Data
\title{\phantomsection%
  This is the \emph{Title}%
  \label{this-is-the-title}%
  \\ % subtitle%
  \DUdocumentsubtitle{This is the \emph{Subtitle}}%
  \label{this-is-the-subtitle}}
\author{}
\date{}
""")) + r"""\maketitle


\section{This is a \emph{section title}%
  \label{this-is-a-section-title}%
}

This is the \emph{document}.

\end{document}
"""],
]

totest_stylesheet['two-styles'] = [
# input
["""two stylesheet links in the header""",
head_template.substitute(dict(parts, stylesheet =
r"""\usepackage{data/spam}
\input{data/ham.tex}
""")) + r"""
two stylesheet links in the header

\end{document}
"""],
]

totest_stylesheet_embed['two-styles'] = [
# input
["""two stylesheets embedded in the header""",
head_template.substitute(dict(parts, stylesheet =
r"""% Cannot embed stylesheet 'data/spam.sty':
%   No such file or directory.
% embedded stylesheet: data/ham.tex
\newcommand{\ham}{wonderful ham}

""")) + r"""
two stylesheets embedded in the header

\end{document}
"""],
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
