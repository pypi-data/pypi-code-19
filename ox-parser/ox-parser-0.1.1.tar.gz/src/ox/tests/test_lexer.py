import pytest
import ox
from mock import patch

number = lambda x: ox.Token('NUMBER', x)
op = lambda x: ox.Token('OP', x)


class TestLexer:
    @pytest.fixture
    def rules(self):
        return [
            ('NUMBER', r'\d+([.]\d*)?'),
            ('OP', r'[-+*/]'),
        ]

    @pytest.fixture
    def ply_lexer(self, rules):
        return ox.make_lexer(rules, which='ply')

    @pytest.fixture
    def simple_lexer(self, rules):
        return ox.make_lexer(rules, which='simple')

    def test_can_parse_simple_expression(self, ply_lexer, simple_lexer):
        ex = '1 + 2.0 * 3.'
        tokens = [number('1'), op('+'), number('2.0'), op('*'), number('3.')]
        assert ply_lexer(ex) == tokens
        assert simple_lexer(ex) == tokens

    def test_tokenize_function_tokenizes_in_a_single_run(self, rules):
        ex = '1 + 2.0 * 3.'
        tokens = [number('1'), op('+'), number('2.0'), op('*'), number('3.')]
        assert ox.tokenize(rules, ex) == tokens

    def test_raises_syntax_error_on_malformed_expression(self, ply_lexer, simple_lexer):
        ex = '1 ^ 2'
        with pytest.raises(SyntaxError):
            ply_lexer(ex)
        with pytest.raises(SyntaxError):
            simple_lexer(ex)
        
    def test_select_simple_lexer_if_ply_not_present(self, rules):
        def _import(x):
            raise ImportError

        with patch('ox.lexer._import', _import):
            lexer = ox.make_lexer(rules)
            assert lexer.which == 'simple'

    def test_issues_an_error_with_invalid_lexer_name(self, rules):
        with pytest.raises(ValueError):
            ox.make_lexer(rules, which='foobar')

    def test_lexer_module_main_function(self, ply_lexer):
        inputs = ['1 + 2', '42', '']
        results = []

        def fake_input(x):
            return inputs.pop(0)

        def fake_print(x):
            results.append(str(x))

        with patch('ox.lexer._print', fake_print):
            with patch('ox.lexer._input', fake_input):
                ox.lexer.main(ply_lexer)  # runs the main loop

        assert results == [
            '[NUMBER(1), OP(+), NUMBER(2)]',
            '[NUMBER(42)]',
        ]