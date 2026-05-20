"""Build adar.exe and adarpc.exe with PyInstaller."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
DIST = ROOT / "dist-exe"
WORK = ROOT / "build"


def build_exe(name: str, entry: str) -> None:
    print(f"Building {name}.exe ...")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller",
         "--onefile", "--console",
         "--name", name,
         "--distpath", str(DIST),
         "--workpath", str(WORK),
         "--specpath", str(WORK),
         str(entry)],
        capture_output=True, text=True, cwd=ROOT,
    )
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit(f"Failed to build {name}.exe")
    print(f"  -> {DIST / (name + '.exe')}")


def main():
    DIST.mkdir(parents=True, exist_ok=True)
    build_exe("adar", ROOT / "adar" / "cli.py")
    build_exe("adarpc", ROOT / "adarpc_entry.py")
    print("\nDone! .exe files in dist-exe/")


if __name__ == "__main__":
    main()
