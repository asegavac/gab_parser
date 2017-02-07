import unittest
from gab_parser import tokenizer

number = tokenizer.Token('number', '\d+', lambda x, _: int(x.value))
alt_number = tokenizer.Token(
    'number',
    '\d+',
    lambda x, t: tokenizer.TokenizerToken(
        x.token_type, int(x.value), x.pos, x.context))
plus = tokenizer.Token('plus', '\+')
minus = tokenizer.Token('minus', '-')
multiply = tokenizer.Token('mult', '\*')
divide = tokenizer.Token('divide', '/')
equals = tokenizer.Token('eq', '=')
lparen = tokenizer.Token('lparen', '\(')
rparen = tokenizer.Token('rparen', '\)')


def error_function(token, _tokenizer):
    _tokenizer.skip(1)
    return tokenizer.TokenizerToken('error', '?', token.pos, token.context)


base_state = tokenizer.State(
    'base',
    [number, plus, minus, multiply, divide, equals, lparen, rparen],
    ignore=' ')

base_state_with_error = tokenizer.State(
    'base',
    [number, plus, minus, multiply, divide, equals, lparen, rparen],
    ignore=' ', error_function=error_function)

alt_base_state = tokenizer.State(
    'base',
    [alt_number, plus, minus, multiply, divide, equals, lparen, rparen],
    ignore=' ')


class TestBasicCalculator(unittest.TestCase):
    def test_types(self):
        t = tokenizer.Tokenizer([base_state])
        t.input('1 + 1 = 2')
        result = [token for token in t]
        assert (['number', 'plus', 'number', 'eq', 'number'] ==
                [token.token_type for token in result])

    def test_values(self):
        t = tokenizer.Tokenizer([base_state])
        t.input('1 + 1 = 2')
        result = [token for token in t]
        assert [1, '+', 1, '=', 2] == [token.value for token in result]

    def test_invalid(self):
        t = tokenizer.Tokenizer([base_state])
        t.input('1 + q = 2')
        with self.assertRaises(tokenizer.TokenizerError):
            result = [token for token in t]

    def test_specify_full_token(self):
        t = tokenizer.Tokenizer([alt_base_state])
        t.input('1 + 1 = 2')
        result = [token for token in t]
        assert [1, '+', 1, '=', 2] == [token.value for token in result]

    def test_error(self):
        t = tokenizer.Tokenizer([base_state_with_error])
        t.input('1 + q = 2')
        result = [token for token in t]
        assert [1, '+', '?', '=', 2] == [token.value for token in result]

if __name__ == '__main__':
    unittest.main()
