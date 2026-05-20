"""Project scaffolding — `adarpc init`."""

from __future__ import annotations
from pathlib import Path
from .config import write_default_config

TEMPLATE_DIR = Path(__file__).parent / "templates"


def init_project(name: str, path: Path | None = None) -> Path:
    """Create a new Adar project scaffold."""
    target = (path or Path.cwd()) / name

    if target.exists():
        raise FileExistsError(f"Directory '{target}' already exists.")

    # Create directory structure
    src_dir = target / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    # Write config
    write_default_config(name, target)

    # Write templates
    _write_template("index.html", src_dir / "index.html", name=name)
    _write_template("style.adar", src_dir / "style.adar", project_name=name)

    # .gitignore
    gitignore = target / ".gitignore"
    gitignore_path = TEMPLATE_DIR / "gitignore"
    if gitignore_path.is_file():
        gitignore.write_bytes(gitignore_path.read_bytes())
        print(f"  Created {gitignore.name}")

    return target


def _write_template(template_name: str, dest: Path, **kwargs) -> None:
    """Render a template file with variables."""
    src = TEMPLATE_DIR / template_name
    content = src.read_text(encoding="utf-8")
    for key, val in kwargs.items():
        content = content.replace(f"{{{{ {key} }}}}", str(val))
    dest.write_text(content, encoding="utf-8")
    print(f"  Created {dest.relative_to(dest.parent.parent)}")
