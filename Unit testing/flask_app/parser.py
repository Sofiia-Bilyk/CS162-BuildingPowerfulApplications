"""
Recursive descent parser for simple arithmetic expressions.
Supports: + - * / ^ (exponentiation) and parentheses.
No use of eval().

Grammar (from lowest to highest precedence):
    expr    → term   (( '+' | '-' ) term)*
    term    → factor (( '*' | '/' ) factor)*
    factor  → unary  ( '^' factor )*        ← right-associative via recursion
    unary   → '-' unary | primary
    primary → NUMBER | '(' expr ')'
"""


class ParseError(ValueError):
    """Raised when the expression is syntactically or semantically invalid."""


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list:
    """
    Split the expression string into a flat list of tokens.
    Tokens are either floats or single-character operators/parens.
    """
    tokens = []
    i = 0
    while i < len(text):
        ch = text[i]

        if ch.isspace():
            i += 1
            continue

        # Multi-character number (integer or decimal)
        if ch.isdigit() or ch == '.':
            j = i
            while j < len(text) and (text[j].isdigit() or text[j] == '.'):
                j += 1
            tokens.append(float(text[i:j]))
            i = j
            continue

        if ch in '+-*/^()':
            tokens.append(ch)
            i += 1
            continue

        raise ParseError(f"Unexpected character: {ch!r}")

    return tokens


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class _Parser:
    """
    Recursive descent parser that consumes a token list and returns a float.
    """

    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0  # current position in token list

    # --- helpers ---

    def _peek(self):
        """Return the current token without consuming it, or None at end."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume(self):
        """Return the current token and advance the position."""
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _expect(self, value):
        """Consume a token that must equal `value`, or raise ParseError."""
        if self._peek() is None:
            raise ParseError(f"Expected {value!r} but reached end of expression")
        tok = self._consume()
        if tok != value:
            raise ParseError(f"Expected {value!r}, got {tok!r}")

    # --- grammar rules ---

    def parse(self) -> float:
        result = self._expr()
        if self._peek() is not None:
            raise ParseError(f"Unexpected token: {self._peek()!r}")
        return result

    def _expr(self) -> float:
        """expr → term (( '+' | '-' ) term)*"""
        value = self._term()
        while self._peek() in ('+', '-'):
            op = self._consume()
            right = self._term()
            if op == '+':
                value += right
            else:
                value -= right
        return value

    def _term(self) -> float:
        """term → factor (( '*' | '/' ) factor)*"""
        value = self._factor()
        while self._peek() in ('*', '/'):
            op = self._consume()
            right = self._factor()
            if op == '/':
                if right == 0:
                    raise ParseError("Division by zero")
                value /= right
            else:
                value *= right
        return value

    def _factor(self) -> float:
        """factor → unary ( '^' factor )*   (right-associative)"""
        base = self._unary()
        if self._peek() == '^':
            self._consume()
            exponent = self._factor()  # recurse for right-associativity
            return base ** exponent
        return base

    def _unary(self) -> float:
        """unary → '-' unary | primary"""
        if self._peek() == '-':
            self._consume()
            return -self._unary()
        return self._primary()

    def _primary(self) -> float:
        """primary → NUMBER | '(' expr ')'"""
        tok = self._peek()

        if tok is None:
            raise ParseError("Unexpected end of expression")

        # Parenthesised sub-expression
        if tok == '(':
            self._consume()
            value = self._expr()
            self._expect(')')
            return value

        # Numeric literal
        if isinstance(tok, float):
            self._consume()
            return tok

        raise ParseError(f"Unexpected token: {tok!r}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def evaluate(expression: str) -> float:
    """
    Parse and evaluate an arithmetic expression string.
    Returns a float result.
    Raises ParseError on bad input.
    """
    tokens = _tokenize(expression)
    if not tokens:
        raise ParseError("Empty expression")
    result = _Parser(tokens).parse()
    return result
