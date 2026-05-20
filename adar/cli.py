from __future__ import annotations
import sys
import argparse
from pathlib import Path
from adar.lexer import Lexer
from adar.parser import Parser
from adar.checker import Checker, CSSSpec
from adar.resolver import Resolver
from adar.codegen import CodeGenerator
from adar.adarpc.resolve_imports import resolve_imports_for_file


def compile_file(
    input_path: Path,
    output_path: Path | None = None,
    scoped: bool = True,
    pretty: bool = True,
    check_only: bool = False,
    src_dir: Path | None = None,
) -> tuple[bool, str]:
    source = input_path.read_text(encoding="utf-8")
    filename = str(input_path)

    lexer = Lexer(source, filename)
    try:
        tokens = lexer.tokenize()
    except SyntaxError as e:
        print(f"  {_RED}Lexer Error:{_RESET} {e}")
        return False, ""

    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except SyntaxError as e:
        print(f"  {_RED}Parser Error:{_RESET} {e}")
        return False, ""

    # Resolve imports relative to input file and source directory
    _src = src_dir or input_path.parent
    _root = _src.parent
    ast = resolve_imports_for_file(ast, input_path, _src, _root)

    spec = CSSSpec()
    checker = Checker(spec)
    result = checker.check(ast)

    if result.errors:
        for err in result.errors:
            loc = f" [{err.location}]" if err.location else ""
            print(f"  {_RED}Type Error{loc}:{_RESET} {err.message}")
        return False, ""

    if result.warnings:
        for warn in result.warnings:
            loc = f" [{warn.location}]" if warn.location else ""
            print(f"  {_YELLOW}Warning{loc}:{_RESET} {warn.message}")

    if check_only:
        print(f"  {_GREEN}OK{_RESET} — no type errors")
        return True, ""

    resolver = Resolver()
    resolved = resolver.resolve(ast)

    codegen = CodeGenerator(scoped=scoped, pretty=pretty, source_file=filename)
    css = codegen.generate(resolved)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(css, encoding="utf-8")
        print(f"  {_GREEN}->{_RESET} Wrote {output_path}")

        mapping = codegen.mapping
        if mapping:
            mapping_file = output_path.with_suffix(".modules.json")
            import json
            mapping_file.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
    else:
        print(css)

    return True, css


def cmd_build(args: argparse.Namespace) -> None:
    src_dir = Path(args.src)
    out_dir = Path(args.out) if args.out else src_dir.parent / "dist"

    if src_dir.is_file():
        files = [src_dir]
    else:
        files = sorted(src_dir.rglob("*.adar"))

    if not files:
        print(f"  {_YELLOW}No .adar files found in {src_dir}{_RESET}")
        return

    success_count = 0
    fail_count = 0

    for f in files:
        rel = f.relative_to(src_dir.parent) if src_dir.is_dir() else f.name
        print(f"\n  {_CYAN}{rel}{_RESET}")
        out = out_dir / f.with_suffix(".css").name
        ok, _ = compile_file(f, out, scoped=not args.no_scope, pretty=not args.minify, check_only=args.check, src_dir=src_dir)
        if ok:
            success_count += 1
        else:
            fail_count += 1

    print(f"\n  {_GREEN}{success_count} files OK{_RESET}", end="")
    if fail_count:
        print(f", {_RED}{fail_count} files failed{_RESET}")
    else:
        print()


def cmd_check(args: argparse.Namespace) -> None:
    path = Path(args.path)
    if path.is_file():
        files = [path]
    else:
        files = sorted(path.rglob("*.adar"))

    success = 0
    failed = 0
    for f in files:
        rel = f.relative_to(path.parent) if path.is_dir() else f.name
        print(f"  Checking {rel}...", end="")
        ok, _ = compile_file(f, check_only=True, src_dir=path)
        if ok:
            success += 1
        else:
            failed += 1

    print(f"\n  {_GREEN}{success} passed{_RESET}", end="")
    if failed:
        print(f", {_RED}{failed} failed{_RESET}")
    else:
        print()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="adar",
        description="Adar — Modern CSS-like styling language compiler",
    )
    sub = parser.add_subparsers(dest="command")

    build = sub.add_parser("build", help="Compile .adar files to CSS")
    build.add_argument("src", help="Source .adar file or directory")
    build.add_argument("-o", "--out", help="Output directory (default: dist/)")
    build.add_argument("--no-scope", action="store_true", help="Disable CSS Modules scoping")
    build.add_argument("--minify", action="store_true", help="Minify output")
    build.add_argument("--check", action="store_true", help="Type-check only, no output")

    check = sub.add_parser("check", help="Type-check .adar files without generating CSS")
    check.add_argument("path", help="File or directory to check")

    args = parser.parse_args(argv)

    if args.command == "build":
        cmd_build(args)
    elif args.command == "check":
        cmd_check(args)
    else:
        parser.print_help()


_RESET = "\x1b[0m"
_RED = "\x1b[31m"
_GREEN = "\x1b[32m"
_YELLOW = "\x1b[33m"
_CYAN = "\x1b[36m"


if __name__ == "__main__":
    main()
