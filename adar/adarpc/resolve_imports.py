"""Import resolution — resolves import statements in .adar files.

Scans source and library directories to find imported files,
then inlines their parsed AST into the importing file.
"""

from __future__ import annotations
from pathlib import Path

from adar.lexer.lexer import Lexer
from adar.parser.parser import Parser
from adar.parser.ast import Stylesheet, ImportStmt

from .package import MODULES_DIR


def find_import_file(
    name: str,
    current_file: Path,
    src_dirs: list[Path],
    lib_dirs: list[Path],
    searched: set[Path] | None = None,
) -> Path | None:
    """Resolve an import name to an actual file path.

    Search order:
    1. Relative to the current file's directory
    2. Source directories (project src/)
    3. Library directories (adar_modules/)
    """
    if searched is None:
        searched = set()

    # Normalize: strip .adar extension if present, add it back for search
    stem = name
    if stem.endswith(".adar"):
        stem = stem[:-5]

    candidates = [
        current_file.parent / f"{stem}.adar",
    ]
    for sd in src_dirs:
        candidates.append(sd / f"{stem}.adar")
        candidates.append(sd / stem / "index.adar")
    for ld in lib_dirs:
        candidates.append(ld / f"{stem}.adar")
        candidates.append(ld / stem / "index.adar")
        candidates.append(ld / f"{stem}.adar")
        candidates.append(ld / "index.adar")

    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_file() and resolved not in searched:
            return resolved

    return None


def resolve_imports_in_ast(
    stylesheet: Stylesheet,
    current_file: Path,
    src_dirs: list[Path],
    lib_dirs: list[Path],
    searched: set[Path] | None = None,
) -> Stylesheet:
    """Walk the AST and inline all import statements.

    Each ImportStmt is replaced by the contents of the imported file.
    Recursively resolves nested imports.
    """
    if searched is None:
        searched = set()
    searched.add(current_file.resolve())

    resolved_children = []
    for child in stylesheet.children:
        if isinstance(child, ImportStmt):
            import_path = child.path.strip('"').strip("'")
            imported_file = find_import_file(
                import_path, current_file, src_dirs, lib_dirs, searched
            )
            if imported_file is None:
                print(
                    f"  Warning: import '{import_path}' not found "
                    f"(from {current_file.name})"
                )
                continue

            if imported_file.resolve() in searched:
                print(f"  Warning: circular import detected for '{import_path}'")
                continue

            try:
                source = imported_file.read_text(encoding="utf-8")
                lexer = Lexer(source, filename=str(imported_file))
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                imported_ast = parser.parse()
                resolved = resolve_imports_in_ast(
                    imported_ast, imported_file,
                    src_dirs, lib_dirs, searched,
                )
                resolved_children.extend(resolved.children)
            except Exception as e:
                print(f"  Warning: error importing '{import_path}': {e}")
        else:
            resolved_children.append(child)

    stylesheet.children = resolved_children
    return stylesheet


def collect_library_dirs(root: Path) -> list[Path]:
    """Collect all library directories from adar_modules/."""
    modules_dir = root / MODULES_DIR
    if not modules_dir.is_dir():
        return [modules_dir]
    result = []
    for pkg_dir in sorted(modules_dir.iterdir()):
        if pkg_dir.is_dir():
            result.append(pkg_dir)
    result.append(modules_dir)
    return result


def resolve_imports_for_file(
    stylesheet: Stylesheet,
    file_path: Path,
    src_dir: Path,
    root: Path,
) -> Stylesheet:
    """Convenience wrapper to resolve imports for a single file."""
    lib_dirs = collect_library_dirs(root)
    src_dirs = [src_dir]
    return resolve_imports_in_ast(
        stylesheet, file_path, src_dirs, lib_dirs, searched=None,
    )
