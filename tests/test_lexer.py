from adar.lexer import Lexer, TokenType


def token_types(source: str) -> list[str]:
    lexer = Lexer(source, "test")
    return [t.type.name for t in lexer.tokenize()]


def test_empty():
    assert token_types("") == ["EOF"]


def test_variable():
    types = token_types("$primary = #3b82f6")
    assert "VARIABLE" in types
    assert "ASSIGN" in types
    assert "COLOR_HEX" in types


def test_rule():
    types = token_types(".btn { color: red }")
    assert "DOT" in types
    assert "IDENTIFIER" in types
    assert "LBRACE" in types
    assert "COLON" in types
    assert "RBRACE" in types


def test_nesting():
    types = token_types(".btn { &:hover { color: red } }")
    assert "AMPERSAND" in types
    assert "COLON" in types


def test_dimensions():
    types = token_types("16px 2rem 50% 100vh")
    assert "DIMENSION" in types


def test_numbers():
    types = token_types("42 3.14 -5")
    assert "NUMBER" in types


def test_keywords():
    types = token_types("theme mixin function include return")
    assert "THEME" in types
    assert "MIXIN" in types
    assert "FUNCTION" in types
    assert "INCLUDE" in types
    assert "RETURN" in types


def test_media():
    types = token_types("@media (max-width: 768px) { }")
    assert "AT" in types
    assert "IDENTIFIER" in types


def test_strings():
    tokens = Lexer('"hello world"', "test").tokenize()
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "hello world"


def test_comments():
    result = token_types("// comment\n.btn { }")
    assert "DOT" in result
    assert "IDENTIFIER" in result


def test_complex():
    source = """
    $primary = #3b82f6

    theme dark {
        $primary = #60a5fa
    }

    .btn {
        include card-base
        color: $primary
        padding: 16px

        &:hover {
            opacity: 0.9
        }
    }
    """
    types = token_types(source)
    assert "VARIABLE" in types
    assert "THEME" in types
    assert "MIXIN" not in types  # card-base is an ident in include context
    assert "DOT" in types
    assert "AMPERSAND" in types
