"""Build system — compiles Adar sources to CSS."""

from __future__ import annotations
from pathlib import Path

from .config import AdarpcConfig
from .resolve_imports import resolve_imports_for_file
from adar.lexer.lexer import Lexer
from adar.parser.parser import Parser
from adar.checker.checker import Checker
from adar.resolver.resolver import Resolver
from adar.codegen.codegen import CodeGenerator


import json
import shutil


def build(config: AdarpcConfig) -> int:
    """Compile .adar files and copy HTML/assets to output/."""
    src_dir = config.src_dir
    out_dir = config.out_dir
    style_dir = out_dir / "style"

    if not src_dir.is_dir():
        print(f"  {_RED}Error:{_RESET} source directory '{src_dir}' not found.")
        return 1

    # Clean output dir if it exists
    # if out_dir.exists():
    #     shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    adar_files = sorted(src_dir.rglob("*.adar"))
    style_dir.mkdir(parents=True, exist_ok=True)
    failed = 0
    ok = 0
    
    all_mappings: dict[str, dict[str, str]] = {}

    print(f"\n  {_CYAN}Building project '{config.project.name}'...{_RESET}")

    # 1. Compile Adar files
    for adar_path in adar_files:
        rel = adar_path.relative_to(src_dir)
        css_name = rel.with_suffix(".css")
        css_path = style_dir / css_name
        css_path.parent.mkdir(parents=True, exist_ok=True)

        comp_result = _compile_file_with_mapping(adar_path, config)
        if comp_result is None:
            failed += 1
            continue
        
        css_content, mapping = comp_result
        css_path.write_text(css_content, encoding="utf-8")
        
        if mapping:
            all_mappings[str(rel).replace("\\", "/")] = mapping

        print(f"    {_GREEN}ok{_RESET}  {rel} -> style/{css_name}")
        ok += 1

    # Write adar-modules.json if scoping is enabled
    if config.build.scope and all_mappings:
        modules_json = out_dir / "adar-modules.json"
        modules_json.write_text(json.dumps(all_mappings, indent=2), encoding="utf-8")
        print(f"    {_GREEN}ok{_RESET}  generated adar-modules.json for JS integration")

    # 2. Copy HTML files and other assets
    asset_count = 0
    for asset in src_dir.rglob("*"):
        if asset.is_file() and asset.suffix not in (".adar", ".css"):
            rel = asset.relative_to(src_dir)
            dest = out_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(asset, dest)
            asset_count += 1

    print(f"\n  {_GREEN}{ok} style(s) compiled, {asset_count} asset(s) copied.{_RESET}")
    if failed:
        print(f"  {_RED}{failed} build(s) failed.{_RESET}")
    
    return failed


def check_project(config: AdarpcConfig) -> int:
    """Type-check all .adar files in the project."""
    src_dir = config.src_dir
    if not src_dir.is_dir():
        print(f"  {_RED}Error:{_RESET} source directory '{src_dir}' not found.")
        return 1

    adar_files = sorted(src_dir.rglob("*.adar"))
    failed = 0
    ok = 0

    print(f"\n  {_CYAN}Checking project '{config.project.name}'...{_RESET}")

    for adar_path in adar_files:
        rel = adar_path.relative_to(src_dir)
        source = adar_path.read_text(encoding="utf-8")

        try:
            lexer = Lexer(source, filename=str(adar_path))
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            ast = resolve_imports_for_file(ast, adar_path, config.src_dir, config.root)
            
            checker = Checker()
            res = checker.check(ast)
            if res.ok:
                print(f"    {_GREEN}PASS{_RESET}  {rel}")
                ok += 1
            else:
                print(f"    {_RED}FAIL{_RESET}  {rel}")
                for err in res.errors:
                    print(f"      - {err.message} [{err.location}]")
                failed += 1
        except Exception as e:
            print(f"    {_RED}ERR{_RESET}   {rel}: {e}")
            failed += 1

    print(f"\n  {_GREEN}{ok} passed{_RESET}, {_RED}{failed} failed{_RESET}")
    return 1 if failed else 0


_RESET = "\x1b[0m"
_RED = "\x1b[31m"
_GREEN = "\x1b[32m"
_CYAN = "\x1b[36m"



def _compile_file_with_mapping(path: Path, config: AdarpcConfig) -> tuple[str, dict[str, str]] | None:
    source = path.read_text(encoding="utf-8")

    try:
        lexer = Lexer(source, filename=str(path))
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        # Resolve imports — inline library files
        ast = resolve_imports_for_file(
            ast, path, config.src_dir, config.root,
        )

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
            source_file=str(path.relative_to(config.src_dir)),
            project_name=config.project.name,
        )
        css = gen.generate(resolved)
        return css, gen.mapping

    except Exception as e:
        print(f"\n  [FAIL] {path.name}: {e}")
        return None

