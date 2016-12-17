
## Warning: This this library is not currently in working condition and should not be used by anyone for any purpose.

## Status

Overall: Not working

- [x] convert lex into the new style
- [ ] get lex working and tested
- [x] begin converting yacc into the new style
- [ ] finish converting yacc into the new style
- [ ] get yacc working and tested

## Introduction

Gab Parser

 -  Gab is an implementation of lex and yacc-like tools
    in pure python. It seeks to be very simple to use.

 -  Parsing is based on LR-parsing which is fast, memory efficient,
    better suited to large grammars, and which has a number of nice
    properties when dealing with syntax errors and other parsing problems.
    Currently, Gab builds its parsing tables using the LALR(1)
    algorithm used in yacc.

 -  Unlike some similar libraries, Gab does not use
    Python introspection features to build lexers and parsers.
    This greatly simplifies the task of parser construction since it reduces
    the number of files and eliminates the need to run a separate lex/yacc
    tool before running your program.

 -  Gab can be used to build parsers for "real" programming languages.
    Although it is not ultra-fast due to its Python implementation,
    it can be used to parse grammars consisting of several hundred
    rules (as might be found for a language like C). The lexer and LR
    parser are also reasonably efficient when parsing typically
    sized programs.

## How to Use

Gab consists of two files : lex.py and yacc.py.
```
import gab_parser.lex as lex
import gab_parser.yacc as yacc
```

## Requirements

Gab requires the use of Python 3.4 or greater.
However, you should use the latest Python release if possible.
It should work on just about any platform.

## Resources

Gab is based loosely on and is a fork of PLY.
More information about PLY can be obtained on the PLY webpage at:

     http://www.dabeaz.com/ply

For a detailed overview of parsing theory, consult the excellent
book "Compilers : Principles, Techniques, and Tools" by Aho, Sethi, and
Ullman. The topics found in "Lex & Yacc" by Levine, Mason, and Brown
may also be useful.

The GitHub page for PLY can be found at:

     https://github.com/dabeaz/ply

## Acknowledgments

The CHANGES file acknowledges those who have contributed patches.

Elias Ioup did the first implementation of LALR(1) parsing in PLY-1.x.
Andrew Waters and Markus Schoepflin were instrumental in reporting bugs
and testing a revised LALR(1) implementation for PLY-2.0.
