"""adarpc publish — verify and prepare library for submission."""

from __future__ import annotations
from pathlib import Path
from .config import AdarpcConfig
from .build import check_project

_RESET = "\x1b[0m"
_RED = "\x1b[31m"
_GREEN = "\x1b[32m"
_CYAN = "\x1b[36m"
_BOLD = "\x1b[1m"


def publish_library(config: AdarpcConfig) -> int:
    """Validate library and provide submission instructions."""
    print(f"\n  {_CYAN}{_BOLD}Adar Library Submission Assistant{_RESET}")
    print(f"  Preparing '{config.project.name}' for publication...\n")

    # 1. Basic Metadata Validation
    if not config.project.description:
        print(f"  {_RED}Error:{_RESET} 'description' is missing in adarpc.toml.")
        return 1
    
    if len(config.project.description) < 10:
        print(f"  {_RED}Error:{_RESET} 'description' is too short. Please provide a helpful summary.")
        return 1

    # 2. Source Code Validation
    index_adar = config.src_dir / "index.adar"
    if not index_adar.exists():
        print(f"  {_RED}Error:{_RESET} 'index.adar' (entry point) not found in {config.src_dir}/.")
        return 1

    # 3. Type Checking
    print(f"  {_CYAN}Step 1: Running type check...{_RESET}")
    if check_project(config) != 0:
        print(f"\n  {_RED}Validation failed.{_RESET} Please fix the errors above before publishing.")
        return 1

    # 4. Instructions
    print(f"\n  {_GREEN}{_BOLD}Verification Successful!{_RESET}")
    print(f"  Your library '{config.project.name}' is ready to be shared.\n")
    
    print(f"  {_BOLD}Next Steps to Publish:{_RESET}")
    print(f"  1. Ensure your library is pushed to a public GitHub repository.")
    print(f"  2. Go to: {_CYAN}https://github.com/zulsyam23-dot/adarlib{_RESET}")
    print(f"  3. Open a New Issue or Pull Request.")
    print(f"  4. Provide the following information:")
    print(f"     - Name: {config.project.name}")
    print(f"     - Version: {config.project.version}")
    print(f"     - Repo: (your github repo link)")
    
    print(f"\n  Thank you for contributing to the Adar ecosystem!")
    return 0
