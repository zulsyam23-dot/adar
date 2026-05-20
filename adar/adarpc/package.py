"""Package data structures for the Adar library ecosystem."""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Dependency:
    """A declared dependency in adarpc.toml."""
    name: str
    version: str = "*"
    source: str = "registry"  # "registry" | "path"


@dataclass
class PackageInfo:
    """Metadata about an available package from the registry."""
    name: str
    version: str
    description: str
    repo: str
    path: str
    author: str = ""


@dataclass
class InstalledPackage:
    """A package that has been installed locally."""
    name: str
    version: str
    path: Path
    description: str = ""


ADARLIB_REGISTRY_URL = (
    "https://raw.githubusercontent.com/"
    "zulsyam23-dot/adarlib/main/registry.json"
)

ADARLIB_REPO = "zulsyam23-dot/adarlib"
ADARLIB_BASE = f"https://github.com/{ADARLIB_REPO}"

MODULES_DIR = "adar_modules"
