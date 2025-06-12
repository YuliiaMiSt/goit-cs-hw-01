class LexicalError(Exception):
    pass


class SyntaxError(Exception):
    pass


class TokenType:
    INTEGER = "INTEGER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"


class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __str__(self):
        return f"Token({self.type}, {repr(self.value)})"

    __repr__ = __str__


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = text[0] if text else None

    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        res = ""
        while self.current_char is not None and self.current_char.isdigit():
            res += self.current_char
            self.advance()
        return int(res)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.integer())

            if self.current_char == "+":
                self.advance()
                return Token(TokenType.PLUS, "+")

            if self.current_char == "-":
                self.advance()
                return Token(TokenType.MINUS, "-")

            if self.current_char == "*":
                self.advance()
                return Token(TokenType.MUL, "*")

            if self.current_char == "/":
                self.advance()
                return Token(TokenType.DIV, "/")

            if self.current_char == "(":
                self.advance()
                return Token(TokenType.LPAREN, "(")

            if self.current_char == ")":
                self.advance()
                return Token(TokenType.RPAREN, ")")

            raise LexicalError(f"Невідомий символ: {self.current_char}")

        return Token(TokenType.EOF, None)


# AST-нод
class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num:
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def error(self, msg="Синтаксична помилка"):
        raise SyntaxError(msg)

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Очікував {token_type}, але отримано {self.current_token.type}")

    def factor(self):
        tok = self.current_token
        if tok.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Num(tok)
        elif tok.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        else:
            self.error()

    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            op = self.current_token
            if op.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            else:
                self.eat(TokenType.DIV)
            node = BinOp(left=node, op=op, right=self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token
            if op.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            else:
                self.eat(TokenType.MINUS)
            node = BinOp(left=node, op=op, right=self.term())
        return node

    def parse(self):
        node = self.expr()
        if self.current_token.type != TokenType.EOF:
            self.error("Зайві символи в кінці виразу")
        return node


class Interpreter:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f"No visit_{type(node).__name__} method")

    def visit_BinOp(self, node):
        if node.op.type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        if node.op.type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        if node.op.type == TokenType.MUL:
            return self.visit(node.left) * self.visit(node.right)
        if node.op.type == TokenType.DIV:
            right = self.visit(node.right)
            if right == 0:
                raise ZeroDivisionError("Ділення на нуль")
            return self.visit(node.left) / right

    def visit_Num(self, node):
        return node.value

    def interpret(self, tree):
        return self.visit(tree)


def main():
    print(
        "Простий інтерпретатор арифметичних виразів. Підтримується +, -, *, /, дужки."
    )
    while True:
        try:
            text = input(">>> ")
            if text.lower() in ("exit", "quit"):
                print("До зустрічі!")
                break
            lexer = Lexer(text)
            parser = Parser(lexer)
            tree = parser.parse()
            result = Interpreter().interpret(tree)

            if isinstance(result, float) and result.is_integer():
                result = int(result)
            print("= ", result)
        except (LexicalError, SyntaxError, ZeroDivisionError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Невідома помилка: {e}")


if __name__ == "__main__":
    main()
