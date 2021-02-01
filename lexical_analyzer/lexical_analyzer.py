from __future__ import print_function
import sys
from io import StringIO


class LexicalAnalyzer:
    # following two must remain in the same order

    tk_EOI, tk_Mul, tk_Div, tk_Mod, tk_Add, tk_Sub, tk_Negate, tk_Not, tk_Lss, tk_Leq, tk_Gtr, \
    tk_Geq, tk_Eq, tk_Neq, tk_Assign, tk_And, tk_Or, tk_If, tk_Else, tk_While, tk_Print, \
    tk_Putc, tk_Lparen, tk_Rparen, tk_Lbrace, tk_Rbrace, tk_Semi, tk_Comma, tk_Ident, \
    tk_Integer, tk_String = range(31)

    all_syms = ["End_of_input", "Op_multiply", "Op_divide", "Op_mod", "Op_add", "Op_subtract",
                "Op_negate", "Op_not", "Op_less", "Op_lessequal", "Op_greater", "Op_greaterequal",
                "Op_equal", "Op_notequal", "Op_assign", "Op_and", "Op_or", "Keyword_if",
                "Keyword_else", "Keyword_while", "Keyword_print", "Keyword_putc", "LeftParen",
                "RightParen", "LeftBrace", "RightBrace", "Semicolon", "Comma", "Identifier",
                "Integer", "String"]

    # single character only symbols
    symbols = {'{': tk_Lbrace, '}': tk_Rbrace, '(': tk_Lparen, ')': tk_Rparen, '+': tk_Add, '-': tk_Sub,
               '*': tk_Mul, '%': tk_Mod, ';': tk_Semi, ',': tk_Comma}

    key_words = {'if': tk_If, 'else': tk_Else, 'print': tk_Print, 'putc': tk_Putc, 'while': tk_While}

    code = ""

    the_ch = " "  # dummy first char - but it must be a space
    the_col = 0
    the_line = 1
    input_file = None

    # *** show error and exit
    def error(self, line, col, msg):
        print(line, col, msg)
        exit(1)

    # *** get the next character from the input
    def next_ch(self):
        self.the_ch = self.input_file.read(1)
        self.the_col += 1
        if self.the_ch == '\n':
            self.the_line += 1
            self.the_col = 0
        return self.the_ch

    # *** 'x' - character constants
    def char_lit(self, err_line, err_col):
        n = ord(self.next_ch())  # skip opening quote
        if self.the_ch == '\'':
            self.error(err_line, err_col, "empty character constant")
        elif self.the_ch == '\\':
            self.next_ch()
            if self.the_ch == 'n':
                n = 10
            elif self.the_ch == '\\':
                n = ord('\\')
            else:
                self.error(err_line, err_col, "unknown escape sequence \\%c" % (self.the_ch))
        if self.next_ch() != '\'':
            self.error(err_line, err_col, "multi-character constant")
        self.next_ch()
        return self.tk_Integer, err_line, err_col, n

    # *** process divide or comments
    def div_or_cmt(self, err_line, err_col):
        if self.next_ch() != '*':
            return self.tk_Div, err_line, err_col

        # comment found
        self.next_ch()
        while True:
            if self.the_ch == '*':
                if self.next_ch() == '/':
                    self.next_ch()
                    return self.gettok()
            elif len(self.the_ch) == 0:
                self.error(err_line, err_col, "EOF in comment")
            else:
                self.next_ch()

    # *** "string"
    def string_lit(self, start, err_line, err_col):
        text = ""

        while self.next_ch() != start:
            if len(self.the_ch) == 0:
                self.error(err_line, err_col, "EOF while scanning string literal")
            if self.the_ch == '\n':
                self.error(err_line, err_col, "EOL while scanning string literal")
            text += self.the_ch

        self.next_ch()
        return self.tk_String, err_line, err_col, text

    # *** handle identifiers and integers
    def ident_or_int(self, err_line, err_col):
        is_number = True
        text = ""

        while self.the_ch.isalnum() or self.the_ch == '_':
            text += self.the_ch
            if not self.the_ch.isdigit():
                is_number = False
            self.next_ch()

        if len(text) == 0:
            self.error(err_line, err_col,
                       "ident_or_int: unrecognized character: (%d) '%c'" % (ord(self.the_ch), self.the_ch))

        if text[0].isdigit():
            if not is_number:
                self.error(err_line, err_col, "invalid number: %s" % (text))
            n = int(text)
            return self.tk_Integer, err_line, err_col, n

        if text in self.key_words:
            return self.key_words[text], err_line, err_col

        return self.tk_Ident, err_line, err_col, text

    # *** look ahead for '>=', etc.
    def follow(self, expect, ifyes, ifno, err_line, err_col):
        if self.next_ch() == expect:
            self.next_ch()
            return ifyes, err_line, err_col

        if ifno == self.tk_EOI:
            self.error(err_line, err_col, "follow: unrecognized character: (%d) '%c'" % (ord(self.the_ch), self.the_ch))

        return ifno, err_line, err_col

    # *** return the next token type
    def gettok(self):
        while self.the_ch.isspace():
            self.next_ch()

        err_line = self.the_line
        err_col = self.the_col

        if len(self.the_ch) == 0:
            return self.tk_EOI, err_line, err_col
        elif self.the_ch == '/':
            return self.div_or_cmt(err_line, err_col)
        elif self.the_ch == '\'':
            return self.char_lit(err_line, err_col)
        elif self.the_ch == '<':
            return self.follow('=', self.tk_Leq, self.tk_Lss, err_line, err_col)
        elif self.the_ch == '>':
            return self.follow('=', self.tk_Geq, self.tk_Gtr, err_line, err_col)
        elif self.the_ch == '=':
            return self.follow('=', self.tk_Eq, self.tk_Assign, err_line, err_col)
        elif self.the_ch == '!':
            return self.follow('=', self.tk_Neq, self.tk_Not, err_line, err_col)
        elif self.the_ch == '&':
            return self.follow('&', self.tk_And, self.tk_EOI, err_line, err_col)
        elif self.the_ch == '|':
            return self.follow('|', self.tk_Or, self.tk_EOI, err_line, err_col)
        elif self.the_ch == '"':
            return self.string_lit(self.the_ch, err_line, err_col)
        elif self.the_ch in self.symbols:
            sym = self.symbols[self.the_ch]
            self.next_ch()
            return sym, err_line, err_col
        else:
            return self.ident_or_int(err_line, err_col)

    # *** main driver
    def analyzer(self, code):
        self.code = StringIO(code)
        while True:
            t = self.gettok()
            tok = t[0]
            line = t[1]
            col = t[2]

            print("%5d  %5d   %-14s" % (line, col, self.all_syms[tok]), end='')

            if tok == self.tk_Integer:
                print("   %5d" % (t[3]))
            elif tok == self.tk_Ident:
                print("  %s" % (t[3]))
            elif tok == self.tk_String:
                print('  "%s"' % (t[3]))
            else:
                print("")

            if tok == self.tk_EOI:
                break


lexical_analyzer = LexicalAnalyzer()
del LexicalAnalyzer
