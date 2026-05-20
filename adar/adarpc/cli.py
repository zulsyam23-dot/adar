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
from .registry import search_packages, get_package
from .install import (
    install_dependencies, install_package, uninstall_package,
    installed_packages, update_registry_and_install,
)
from .package import Dependency, MODULES_DIR


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

    # install
    install_p = sub.add_parser("install", help="Install library packages")
    install_p.add_argument(
        "packages", nargs="*",
        help="Package names to install (from registry). Empty = install all from adarpc.toml",
    )
    install_p.add_argument(
        "--config", "-c",
        help="Path to adarpc.toml",
    )
    install_p.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force reinstall",
    )

    # uninstall
    uninstall_p = sub.add_parser("uninstall", help="Remove a library package")
    uninstall_p.add_argument("name", help="Package name to remove")

    # list
    sub.add_parser("list", help="List installed packages")

    # search
    search_p = sub.add_parser("search", help="Search available packages")
    search_p.add_argument("query", help="Search query")

    # check
    check_p = sub.add_parser("check", help="Type-check project files")
    check_p.add_argument(
        "--config", "-c",
        help="Path to adarpc.toml",
    )

    args = parser.parse_args(argv)

    if args.command == "init":
        return _handle_init(args.name, Path(args.path))

    if args.command == "list":
        return _handle_list()
    if args.command == "search":
        return _handle_search(args.query)
    if args.command == "uninstall":
        return _handle_uninstall(args.name)
    if args.command == "install":
        cfg = _load_config(args.config) if not args.packages else None
        return _handle_install(args.packages, cfg, args.force)

    cfg = _load_config(args.config)
    if cfg is None:
        return 1

    if args.command == "build":
        return build(cfg)
    elif args.command == "check":
        from .build import check_project
        return check_project(cfg)
    elif args.command == "watch":
        watch(cfg)
        return 0
    elif args.command == "serve":
        if args.port is not None:
            cfg.dev.port = args.port
        serve(cfg)
        return 0

    return 0


def _handle_install(
    packages: list[str], cfg: object | None, force: bool,
) -> int:
    root = Path.cwd()
    if packages:
        # Install specific packages from registry
        failed = 0
        for name in packages:
            dep = Dependency(name=name, version="*")
            if not install_package(root, dep, force=force):
                failed += 1
        if failed:
            print(f"  {failed} package(s) failed to install")
            return 1
        return 0

    # Install all from adarpc.toml
    if cfg is None:
        print("  Error: no adarpc.toml found.")
        return 1
    from .config import AdarpcConfig
    config = cfg  # type: AdarpcConfig
    if not config.dependencies:
        print("  No dependencies in adarpc.toml.")
        print("  Add them with: adarpc install <package-name>")
        print("  Or edit [dependencies] in adarpc.toml")
        return 0
    return install_dependencies(root, config.dependencies, force=force)


def _handle_uninstall(name: str) -> int:
    root = Path.cwd()
    if uninstall_package(root, name):
        return 0
    return 1


def _handle_list() -> int:
    root = Path.cwd()
    packages = installed_packages(root)
    if not packages:
        print("  No packages installed.")
        print(f"  Install with: adarpc install <package-name>")
        return 0
    print(f"  Installed packages in {MODULES_DIR}/:")
    for pkg in packages:
        print(f"    {pkg.name} v{pkg.version}")
        if pkg.description:
            print(f"      {pkg.description}")
    return 0


def _handle_search(query: str) -> int:
    results = search_packages(query)
    if not results:
        print(f"  No packages found for '{query}'.")
        print("  Check https://github.com/zulsyam23-dot/adarlib for available libraries.")
        return 0
    print(f"  Available packages matching '{query}':")
    for pkg in results:
        print(f"    {pkg.name} v{pkg.version}")
        if pkg.description:
            print(f"      {pkg.description}")
        print(f"      https://github.com/{pkg.repo}/tree/main/{pkg.path}")
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
