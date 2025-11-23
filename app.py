# setup.py - auto-detect package + import-safe version resolution
import os
import re
from pathlib import Path
from setuptools import setup, find_packages

ROOT = Path(__file__).parent.resolve()

def detect_package_name():
    """
    Auto-detect the package directory by looking for folders that contain __init__.py
    Excludes common non-package dirs.
    Returns the first candidate or raises if none found.
    """
    exclude = {"tests", "docs", ".github", ".venv", "venv", "__pycache__"}
    candidates = []
    for p in ROOT.iterdir():
        if p.is_dir() and p.name not in exclude:
            if (p / "__init__.py").exists():
                candidates.append(p.name)
    if not candidates:
        # also try nested packages (src layout)
        src = ROOT / "src"
        if src.exists():
            for p in src.iterdir():
                if p.is_dir() and (p / "__init__.py").exists():
                    candidates.append(p.name)
    if not candidates:
        raise RuntimeError("Could not auto-detect package folder. Ensure a package folder with __init__.py exists.")
    # choose the first one (common case: single package)
    return candidates[0]

def read_version_from_init(package_name):
    init_path = ROOT / package_name / "__init__.py"
    if not init_path.exists():
        # try src layout
        init_path = ROOT / "src" / package_name / "__init__.py"
        if not init_path.exists():
            return None
    text = init_path.read_text(encoding="utf8")
    m = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", text, re.M)
    if m:
        return m.group(1)
    return None

def get_version():
    """
    Acquire a version at build time without importing package.
    Order:
      1) parse __version__ from package/__init__.py
      2) read VERSION file
      3) env vars SETUPTOOLS_SCM_PRETEND_VERSION or PROJECT_VERSION
    """
    pkg = detect_package_name()
    v = read_version_from_init(pkg)
    if v:
        return v

    version_file = ROOT / "VERSION"
    if version_file.exists():
        v = version_file.read_text(encoding="utf8").strip()
        if v:
            return v

    env_version = os.environ.get("SETUPTOOLS_SCM_PRETEND_VERSION") or os.environ.get("PROJECT_VERSION")
    if env_version:
        return env_version

    # final helpful message with debugging hints
    raise RuntimeError(
        "Could not determine package version for build.\n"
        "Detected package candidates: {}\n"
        "Ensure one of:\n"
        "  - __version__ = 'x.y.z' in <package>/__init__.py\n"
        "  - a VERSION file at project root\n"
        "  - SETUPTOOLS_SCM_PRETEND_VERSION or PROJECT_VERSION env var\n".format(
            ", ".join([p.name for p in ROOT.iterdir() if (p.is_dir() and (p / '__init__.py').exists())])
        )
    )

# Attempt to detect package name now (used below)
try:
    PACKAGE_NAME = detect_package_name()
except Exception:
    PACKAGE_NAME = None

VERSION = get_version()

long_description = ""
readme = ROOT / "README.md"
if readme.exists():
    long_description = readme.read_text(encoding="utf8")

setup(
    name=PACKAGE_NAME or "my_project",
    version=VERSION,
    description="Your project description",
    long_description=long_description,
    long_description_content_type="text/markdown" if long_description else None,
    packages=find_packages(where=".", exclude=("tests", "docs")),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "flask",
        "requests",
        "python-dotenv",
        "Werkzeug",
        "flask-cors",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
