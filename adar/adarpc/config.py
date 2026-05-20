"""adarpc.toml configuration parser."""

from __future__ import annotations
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .package import Dependency


@dataclass
class BuildConfig:
    output: str = "dist"
    minify: bool = False
    scope: bool = False
    source: str = "src"


@dataclass
class DevConfig:
    port: int = 8080
    watch: bool = True
    livereload: bool = True


@dataclass
class ProjectConfig:
    name: str = ""
    version: str = "0.1.0"
    description: str = ""
    author: str = ""


@dataclass
class AdarpcConfig:
    project: ProjectConfig = field(default_factory=ProjectConfig)
    build: BuildConfig = field(default_factory=BuildConfig)
    dev: DevConfig = field(default_factory=DevConfig)
    dependencies: list[Dependency] = field(default_factory=list)
    _root: Path = field(default_factory=Path.cwd)

    @property
    def root(self) -> Path:
        return self._root

    @root.setter
    def root(self, path: Path) -> None:
        self._root = path.resolve()

    @property
    def src_dir(self) -> Path:
        return self.root / self.build.source

    @property
    def out_dir(self) -> Path:
        return self.root / self.build.output


_default_toml = """\
[project]
name = "{name}"
version = "0.1.0"
description = ""
author = ""

[build]
output = "output"
minify = false
scope = true
source = "src"

[dev]
port = 8080
watch = true
livereload = true

[dependencies]
# Add libraries from the adarlib ecosystem:
# adar-ui-core = "0.1.0"
# adar-ui-fancy = "0.1.0"
# adar-ui-pro = "0.1.0"
"""


def find_config(path: Path | None = None) -> Path | None:
    """Walk up directories to find adarpc.toml."""
    start = path or Path.cwd()
    for parent in [start] + list(start.parents):
        candidate = parent / "adarpc.toml"
        if candidate.is_file():
            return candidate
    return None


def load_config(path: Path | None = None) -> AdarpcConfig:
    """Load and return project configuration."""
    config_path = find_config(path)
    if config_path is None:
        raise FileNotFoundError(
            "adarpc.toml not found. Run 'adarpc init' to create one."
        )

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    cfg = AdarpcConfig()
    cfg.root = config_path.parent

    proj = data.get("project", {})
    cfg.project.name = proj.get("name", "")
    cfg.project.version = proj.get("version", "0.1.0")
    cfg.project.description = proj.get("description", "")
    cfg.project.author = proj.get("author", "")

    build = data.get("build", {})
    cfg.build.output = build.get("output", "dist")
    cfg.build.minify = build.get("minify", False)
    cfg.build.scope = build.get("scope", False)
    cfg.build.source = build.get("source", "src")

    dev = data.get("dev", {})
    cfg.dev.port = dev.get("port", 8080)
    cfg.dev.watch = dev.get("watch", True)
    cfg.dev.livereload = dev.get("livereload", True)

    deps = data.get("dependencies", {})
    cfg.dependencies = [
        Dependency(name=k, version=str(v) if not isinstance(v, dict) else v.get("version", "*"))
        for k, v in deps.items()
    ]

    return cfg


def write_default_config(name: str, path: Path) -> Path:
    """Write a default adarpc.toml to the given directory."""
    config_path = path / "adarpc.toml"
    content = _default_toml.format(name=name)
    config_path.write_text(content, encoding="utf-8")
    return config_path
