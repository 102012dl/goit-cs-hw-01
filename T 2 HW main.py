\Завдання 2 

class TokenType:
    INTEGER = 'INTEGER'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MUL = 'MUL'
    DIV = 'DIV'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    EOF = 'EOF'  # Означає кінець вхідного рядка
class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    def __str__(self):
        return f'Token({self.type}, {repr(self.value)})'
    def __repr__(self):
        return self.__str__()
class LexicalError(Exception):
    pass
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
    def advance(self):
        """ Переміщуємо 'вказівник' на наступний символ вхідного рядка """
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Означає кінець введення
        else:
            self.current_char = self.text[self.pos]
    def skip_whitespace(self):
        """ Пропускаємо пробільні символи. """
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    def integer(self):
        """ Повертаємо ціле число, зібране з послідовності цифр. """
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)
    def get_next_token(self):
        """ Лексичний аналізатор, що розбиває вхідний рядок на токени. """
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.integer())
            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+')
            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-')
            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MUL, '*')
            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIV, '/')
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')')
            raise LexicalError(f'Помилка лексичного аналізу: непередбачений символ {self.current_char}')
        return Token(TokenType.EOF, None)
class ParsingError(Exception):
    pass
class AST:
    pass
class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    def error(self):
        raise ParsingError('Помилка синтаксичного аналізу')
    def eat(self, token_type):
        """ Порівнюємо поточний токен з очікуваним токеном і, якщо вони збігаються, 'поглинаємо' його і переходимо до наступного токена. """
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()
    def factor(self):
        """ Парсер для чисел та виразів у дужках """
        token = self.current_token
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Num(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
    def term(self):
        """ Парсер для термів, включаючи множення та ділення """
        node = self.factor()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)
            node = BinOp(left=node, op=token, right=self.factor())
        return node
    def expr(self):
        """ Парсер для виразів, включаючи додавання та віднімання """
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            node = BinOp(left=node, op=token, right=self.term())
        return node
    def parse(self):
        return self.expr()
class NodeVisitor:
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')
class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
    def visit_BinOp(self, node):
        if node.op.type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == TokenType.MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == TokenType.DIV:
            return self.visit(node.left) / self.visit(node.right)
    def visit_Num(self, node):
        return node.value
    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)
# Тестування
def test_interpreter(input_text, expected_result):
    lexer = Lexer(input_text)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    assert result == expected_result, f'Expected {expected_result}, but got {result}'
    print(f'Test passed: {input_text} = {result}')
# Приклади тестів
try:
    test_interpreter("3", 3)
    test_interpreter("2 + 7 * 4", 30)
    test_interpreter("7 - 3 + 2", 6)
        test_interpreter("14 + 2 * 3 - 6 / 2", 17)
    test_interpreter("(7 + 3) * (2 + 1)", 30)
    test_interpreter("7 * (2 + 3)", 35)
    print("All tests passed.")
except AssertionError as e:
    print(e)
except Exception as e:
    print(f"Error: {e}") 

