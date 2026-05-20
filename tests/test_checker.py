from adar.lexer import Lexer
from adar.parser import Parser
from adar.checker import Checker, CSSSpec


def compile_and_check(source: str):
    lexer = Lexer(source, "test")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    spec = CSSSpec()
    checker = Checker(spec)
    return checker.check(ast)


def test_valid_color():
    source = ".foo { color: red }"
    result = compile_and_check(source)
    assert result.ok, f"Expected no errors, got: {result.errors}"


def test_valid_hex_color():
    source = ".foo { color: #ff0000 }"
    result = compile_and_check(source)
    assert result.ok, f"Expected no errors, got: {result.errors}"


def test_invalid_color_type():
    source = ".foo { color: 16px }"
    result = compile_and_check(source)
    assert not result.ok, "Expected type error for color: 16px"
    assert any("Type mismatch" in e.message for e in result.errors), \
        f"Expected type mismatch error, got: {[e.message for e in result.errors]}"


def test_valid_width():
    source = ".foo { width: 100px }"
    result = compile_and_check(source)
    assert result.ok


def test_valid_width_percent():
    source = ".foo { width: 50% }"
    result = compile_and_check(source)
    assert result.ok


def test_invalid_width_color():
    source = ".foo { width: #ff0000 }"
    result = compile_and_check(source)
    assert not result.ok
    assert any("Type mismatch" in e.message for e in result.errors)


def test_variable_usage():
    source = """
    $primary = #3b82f6
    .foo { color: $primary }
    """
    result = compile_and_check(source)
    assert result.ok, f"Expected no errors, got: {result.errors}"


def test_unknown_property():
    source = ".foo { unknown-prop: 1 }"
    result = compile_and_check(source)
    assert not result.ok
    assert any("Unknown" in e.message for e in result.errors)


def test_custom_property():
    source = ".foo { --custom-prop: 1 }"
    result = compile_and_check(source)
    assert result.ok


def test_mixin():
    source = """
    mixin card { color: red }
    .foo { include card }
    """
    result = compile_and_check(source)
    assert result.ok


def test_type_error_in_binary():
    source = ".foo { width: 10px + red }"
    result = compile_and_check(source)
    assert not result.ok
