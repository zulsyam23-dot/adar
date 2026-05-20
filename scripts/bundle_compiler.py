"""Copy the Adar compiler source into docs/compiler/ for Pyodide playground."""
from __future__ import annotations

import shutil
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
DOCS_COMPILER = ROOT / "docs" / "compiler"
ADAR_SRC = ROOT / "adar"

# dirs to include (relative to adar/)
INCLUDE_DIRS = ["lexer", "parser", "checker", "resolver", "codegen", "optimizer", "adarpc"]
INCLUDE_FILES = ["__init__.py", "cli.py"]


def clean_compiler_dir():
    if DOCS_COMPILER.exists():
        shutil.rmtree(DOCS_COMPILER)
    DOCS_COMPILER.mkdir(parents=True)


def ignore_pycache(dir: str, contents: list[str]) -> list[str]:
    return ["__pycache__"] if "__pycache__" in contents else []

def copy_package(srcdir: Path, dstdir: Path):
    for item in srcdir.iterdir():
        if item.name == "__pycache__":
            continue
        dest = dstdir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=ignore_pycache)
        else:
            shutil.copy2(item, dest)


def main():
    clean_compiler_dir()

    # Copy all .py files from adar/
    copy_package(ADAR_SRC, DOCS_COMPILER)

    print(f"Copied Adar compiler to {DOCS_COMPILER}")
    py_files = list(DOCS_COMPILER.rglob("*.py"))
    print(f"  {len(py_files)} .py files")


if __name__ == "__main__":
    main()
