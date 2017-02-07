import unittest
from gab_parser import tokenizer

number = tokenizer.Token('number', '\d+', lambda x, _: int(x.value))

plus = tokenizer.Token('plus', '\+')
minus = tokenizer.Token('minus', '-')
multiply = tokenizer.Token('mult', '\*')
divide = tokenizer.Token('divide', '/')
equals = tokenizer.Token('eq', '=')
lparen = tokenizer.Token('lparen', '\(')
rparen = tokenizer.Token('rparen', '\)')


base_state = tokenizer.State(
    'base',
    [number, plus, minus, multiply, divide, equals, lparen, rparen],
    ignore=' ')


class TestValidStrings(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
