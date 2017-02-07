import unittest
from gab_parser import tokenizer

# Same as a normal calc, except that multiply and divide only exist
# between brackets []
number = tokenizer.Token('number', '\d+', lambda x, _: int(x.value))
plus = tokenizer.Token('plus', '\+')
minus = tokenizer.Token('minus', '-')
multiply = tokenizer.Token('mult', '\*')
divide = tokenizer.Token('divide', '/')
equals = tokenizer.Token('eq', '=')
lparen = tokenizer.Token('lparen', '\(')
rparen = tokenizer.Token('rparen', '\)')
lbrack_include = tokenizer.Token(
    'lbrack', '\[', lambda _, t: t.push_state('inclusive'))
lbrack_exclude = tokenizer.Token(
    'lbrack', '\[', lambda _, t: t.push_state('exclusive'))
lbrack_set_exclude = tokenizer.Token(
    'lbrack', '\[', lambda _, t: t.set_state('exclusive'))
lbrack_set_invalid = tokenizer.Token(
    'lbrack', '\[', lambda _, t: t.set_state('invalid'))
rbrack = tokenizer.Token('rbrack', '\]', lambda _, t: t.pop_state())


base_inclusive = tokenizer.State(
    'base',
    [number, plus, minus, equals, lparen, rparen, lbrack_include, rbrack],
    ignore=' ')
mult_divide_inclusive = tokenizer.State(
    'inclusive',
    [multiply, divide],
    inclusive=True,
    ignore=' ')
base_exclusive = tokenizer.State(
    'base',
    [number, plus, minus, equals, lparen, rparen, lbrack_exclude],
    ignore=' ')
mult_divide_exclusive = tokenizer.State(
    'exclusive',
    [number, multiply, divide, rbrack],  # rbrack must be in the state to exit
    inclusive=False,
    ignore=' ')
base_set_exclusive = tokenizer.State(
    'base',
    [number, plus, minus, equals, lparen, rparen, lbrack_set_exclude],
    ignore=' ')
base_set_invalid = tokenizer.State(
    'base',
    [number, plus, minus, equals, lparen, rparen, lbrack_set_invalid],
    ignore=' ')


class TestMultistate(unittest.TestCase):
    def test_inclusive(self):
        t = tokenizer.Tokenizer([base_inclusive, mult_divide_inclusive])
        t.input('1 + [1 + 2 * 4] = 2')
        result = [token for token in t]
        assert (['number', 'plus', 'number', 'plus', 'number',
                 'mult', 'number', 'eq', 'number'] ==
                [token.token_type for token in result])

    def test_exclusive(self):
        t = tokenizer.Tokenizer([base_exclusive, mult_divide_exclusive])
        t.input('1 + [2 * 4] = 2')
        result = [token for token in t]
        assert (['number', 'plus', 'number',
                 'mult', 'number', 'eq', 'number'] ==
                [token.token_type for token in result])

    def test_exclusive_hide_substates(self):
        t = tokenizer.Tokenizer([base_exclusive, mult_divide_exclusive])
        t.input('1 + [1 + 2 * 4] = 2')
        with self.assertRaises(tokenizer.TokenizerError):
            result = [token for token in t]

    def test_exclusive_set(self):
        t = tokenizer.Tokenizer([base_set_exclusive, mult_divide_exclusive])
        t.input('1 + [2 * 4]')
        result = [token for token in t]
        assert (['number', 'plus', 'number', 'mult', 'number'] ==
                [token.token_type for token in result])

    def test_no_state(self):
        t = tokenizer.Tokenizer([base_set_exclusive, mult_divide_exclusive])
        t.input('1 + [2 * 4] + 1')
        with self.assertRaises(tokenizer.TokenizerError):
            result = [token for token in t]

    def test_invalid(self):
        t = tokenizer.Tokenizer([base_set_invalid, mult_divide_exclusive])
        t.input('1 + [2 * 4] + 1')
        with self.assertRaises(ValueError):
            result = [token for token in t]


if __name__ == '__main__':
    unittest.main()
