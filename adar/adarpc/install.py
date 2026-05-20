"""Package installation — download and manage library packages."""

from __future__ import annotations
import zipfile
import io
import urllib.request
import urllib.error
from pathlib import Path

from .package import (
    ADARLIB_REPO, ADARLIB_BASE, MODULES_DIR,
    PackageInfo, InstalledPackage, Dependency,
)
from .registry import fetch_registry, get_package


def _modules_dir(root: Path) -> Path:
    return root / MODULES_DIR


def _package_dir(root: Path, name: str) -> Path:
    return _modules_dir(root) / name


def installed_packages(root: Path) -> list[InstalledPackage]:
    """List currently installed packages in the project."""
    mod_dir = _modules_dir(root)
    if not mod_dir.is_dir():
        return []
    result = []
    for pkg_dir in sorted(mod_dir.iterdir()):
        if pkg_dir.is_dir():
            meta_file = pkg_dir / "adarpc.toml"
            version = "0.1.0"
            description = ""
            if meta_file.is_file():
                for line in meta_file.read_text(encoding="utf-8").splitlines():
                    if line.startswith("version "):
                        version = line.split("=", 1)[1].strip().strip('"')
                    elif line.startswith("description "):
                        description = line.split("=", 1)[1].strip().strip('"')
            name = pkg_dir.name
            # Strip .git suffix if present
            if name.endswith(".git"):
                name = name[:-4]
            result.append(InstalledPackage(
                name=name,
                version=version,
                path=pkg_dir,
                description=description,
            ))
    return result


def is_installed(root: Path, name: str) -> bool:
    """Check if a package is installed."""
    return _package_dir(root, name).is_dir()


def install_package(
    root: Path,
    dep: Dependency,
    force: bool = False,
) -> bool:
    """Install a single package by downloading from adarlib GitHub."""
    mod_dir = _modules_dir(root)
    mod_dir.mkdir(parents=True, exist_ok=True)

    target = _package_dir(root, dep.name)
    if target.is_dir():
        if not force:
            print(f"  Package '{dep.name}' already installed.")
            return True
        print(f"  Reinstalling '{dep.name}'...")

    pkg_info = get_package(dep.name)
    if pkg_info is None:
        print(f"  Error: package '{dep.name}' not found in registry.")
        return False

    # Download the library from GitHub as a ZIP of the specific directory
    zip_url = (
        f"https://api.github.com/repos/{ADARLIB_REPO}/"
        f"zipball/main"
    )
    print(f"  Downloading '{dep.name}' from {ADARLIB_REPO}...")

    try:
        req = urllib.request.Request(
            zip_url,
            headers={"User-Agent": "adarpc/0.1.0", "Accept": "application/vnd.github.v3+json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            zip_data = resp.read()
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        print(f"  Error downloading package: {e}")
        return False

    # Extract only the library directory
    lib_path_in_repo = pkg_info.path.replace("\\", "/")
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            # Find the directory prefix (GitHub zip has a root folder)
            prefix = None
            for name in zf.namelist():
                if name.endswith("/"):
                    parts = name.rstrip("/").split("/", 1)
                    if len(parts) == 2 and parts[1] == lib_path_in_repo:
                        prefix = parts[0]
                        break

            if prefix is None:
                print(f"  Error: could not find library path '{lib_path_in_repo}' in repository.")
                return False

            target.mkdir(parents=True, exist_ok=True)
            extracted = 0
            for name in zf.namelist():
                if name.startswith(f"{prefix}/{lib_path_in_repo}/"):
                    rel_path = name[len(f"{prefix}/{lib_path_in_repo}/"):]
                    if not rel_path:
                        continue
                    dest = target / rel_path
                    if name.endswith("/"):
                        dest.mkdir(parents=True, exist_ok=True)
                    else:
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        dest.write_bytes(zf.read(name))
                        extracted += 1

            print(f"  Installed '{dep.name}' ({extracted} files)")
            return True
    except (zipfile.BadZipFile, OSError) as e:
        print(f"  Error extracting package: {e}")
        return False


def install_dependencies(
    root: Path,
    dependencies: list[Dependency],
    force: bool = False,
) -> int:
    """Install all dependencies listed in adarpc.toml.

    Returns the number of failed installs.
    """
    failed = 0
    installed = 0

    for dep in dependencies:
        if is_installed(root, dep.name) and not force:
            installed += 1
            continue
        if install_package(root, dep, force=force):
            installed += 1
        else:
            failed += 1

    if failed:
        print(f"\n  {installed} installed, {failed} failed")
    else:
        print(f"\n  {installed} package(s) installed")
    return failed


def uninstall_package(root: Path, name: str) -> bool:
    """Remove an installed package."""
    target = _package_dir(root, name)
    if not target.is_dir():
        print(f"  Package '{name}' is not installed.")
        return False

    import shutil
    shutil.rmtree(target)
    print(f"  Removed '{name}'.")
    return True


def update_registry_and_install(
    root: Path,
    dependencies: list[Dependency],
) -> int:
    """Force-refresh registry and install/update all dependencies."""
    from .registry import clear_cache, fetch_registry
    clear_cache()
    fetch_registry(force=True)
    return install_dependencies(root, dependencies, force=True)
