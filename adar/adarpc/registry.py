"""Package registry client — fetches library index from adarlib."""

from __future__ import annotations
import json
import urllib.request
import urllib.error
from pathlib import Path

from .package import ADARLIB_REGISTRY_URL, PackageInfo


_REGISTRY_CACHE: dict[str, list[PackageInfo]] | None = None


def fetch_registry(
    url: str = ADARLIB_REGISTRY_URL,
    force: bool = False,
) -> list[PackageInfo]:
    """Fetch the package registry from adarlib GitHub repo.

    Returns a list of available PackageInfo entries.
    Caches results in memory for the session.
    """
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None and not force:
        return list(_REGISTRY_CACHE.values())

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "adarpc/0.1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError,
            json.JSONDecodeError, OSError) as e:
        print(f"  Warning: could not fetch registry ({e})")
        print(f"  Using cached or empty registry.")
        return []

    libraries = data.get("libraries", {})
    result = {}
    for name, info in libraries.items():
        result[name] = PackageInfo(
            name=name,
            version=info.get("version", "0.1.0"),
            description=info.get("description", ""),
            repo=info.get("repo", "zulsyam23-dot/adarlib"),
            path=info.get("path", f"libraries/{name}"),
            author=info.get("author", ""),
        )
    _REGISTRY_CACHE = result
    return list(result.values())


def search_packages(query: str) -> list[PackageInfo]:
    """Search available packages by name or description."""
    packages = fetch_registry()
    query = query.lower()
    results = []
    for pkg in packages:
        if query in pkg.name.lower() or query in pkg.description.lower():
            results.append(pkg)
    return results


def get_package(name: str) -> PackageInfo | None:
    """Get a single package by name from the registry."""
    packages = fetch_registry()
    for pkg in packages:
        if pkg.name == name:
            return pkg
    return None


def clear_cache() -> None:
    """Clear the in-memory registry cache."""
    global _REGISTRY_CACHE
    _REGISTRY_CACHE = None
