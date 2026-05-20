"""Build system — compiles Adar sources to CSS."""

from __future__ import annotations
from pathlib import Path

from .config import AdarpcConfig
from adar.lexer.lexer import Lexer
from adar.parser.parser import Parser
from adar.checker.checker import Checker
from adar.resolver.resolver import Resolver
from adar.codegen.codegen import CodeGenerator


def build(config: AdarpcConfig) -> int:
    """Compile .adar files to output/style/. No HTML copying."""
    src_dir = config.src_dir
    style_dir = config.out_dir / "style"

    if not src_dir.is_dir():
        print(f"Error: source directory '{src_dir}' not found.")
        return 1

    adar_files = sorted(src_dir.rglob("*.adar"))
    style_dir.mkdir(parents=True, exist_ok=True)
    failed = 0
    ok = 0

    for adar_path in adar_files:
        rel = adar_path.relative_to(src_dir)
        css_name = rel.with_suffix(".css")
        css_path = style_dir / css_name
        css_path.parent.mkdir(parents=True, exist_ok=True)

        result = _compile_file(adar_path, config)
        if result is None:
            failed += 1
            continue

        css_path.write_text(result, encoding="utf-8")
        print(f"  [OK] {rel} -> style/{css_name}")
        ok += 1

    print(f"\n  {ok} file(s) OK", end="")
    if failed:
        print(f", {failed} failed", end="")
    print()

    return failed


def _compile_file(path: Path, config: AdarpcConfig) -> str | None:
    source = path.read_text(encoding="utf-8")

    try:
        lexer = Lexer(source, filename=str(path))
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        checker = Checker()
        check_result = checker.check(ast)

        if not check_result.ok:
            print(f"\n  [FAIL] {path.name}")
            for err in check_result.errors:
                print(f"    Error: {err.message}")
            return None

        resolver = Resolver()
        resolved = resolver.resolve(ast)

        gen = CodeGenerator(
            scoped=config.build.scope,
            pretty=not config.build.minify,
        )
        return gen.generate(resolved)

    except Exception as e:
        print(f"\n  [FAIL] {path.name}: {e}")
        return None
