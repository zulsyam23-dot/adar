"""adarpc CLI — entry point for the Adar package manager."""

from __future__ import annotations
import sys
import argparse
from pathlib import Path

from . import __version__
from .config import load_config
from .project import init_project
from .build import build
from .dev import serve, watch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="adarpc",
        description="Adar Package Manager — build tool for Adar projects",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"adarpc {__version__}",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # init
    init_p = sub.add_parser("init", help="Create a new Adar project")
    init_p.add_argument("name", help="Project name")
    init_p.add_argument(
        "--path", "-p",
        default=".",
        help="Parent directory (default: current dir)",
    )

    # build
    build_p = sub.add_parser("build", help="Compile project to CSS")
    build_p.add_argument(
        "--config", "-c",
        help="Path to adarpc.toml (default: search up from cwd)",
    )

    # watch
    watch_p = sub.add_parser("watch", help="Watch & rebuild on changes")
    watch_p.add_argument(
        "--config", "-c",
        help="Path to adarpc.toml",
    )

    # serve
    serve_p = sub.add_parser("serve", help="Start dev server with live reload")
    serve_p.add_argument(
        "--port", "-p",
        type=int,
        default=None,
        help="Port (default: from config or 8080)",
    )
    serve_p.add_argument(
        "--config", "-c",
        help="Path to adarpc.toml",
    )

    args = parser.parse_args(argv)

    if args.command == "init":
        return _handle_init(args.name, Path(args.path))

    cfg = _load_config(args.config)
    if cfg is None:
        return 1

    if args.command == "build":
        return build(cfg)
    elif args.command == "watch":
        watch(cfg)
        return 0
    elif args.command == "serve":
        if args.port is not None:
            cfg.dev.port = args.port
        serve(cfg)
        return 0

    return 0


def _handle_init(name: str, parent: Path) -> int:
    try:
        target = init_project(name, parent)
        print(f"\n  [OK] Created Adar project '{name}'")
        print(f"\n  cd {name}")
        print(f"  adarpc build   # Build to output/")
        print(f"  adarpc serve   # Dev server on :8080")
        return 0
    except FileExistsError as e:
        print(f"  Error: {e}")
        return 1


def _load_config(config_path: str | None) -> object | None:
    try:
        if config_path:
            return load_config(Path(config_path).resolve())
        return load_config()
    except FileNotFoundError as e:
        print(f"  Error: {e}")
        return None
    except Exception as e:
        print(f"  Error reading config: {e}")
        return None


if __name__ == "__main__":
    sys.exit(main())
