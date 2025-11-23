# setup.py - robust, import-safe version resolution for builds
import os
import re
from pathlib import Path
from setuptools import setup, find_packages

def get_version(package_name="your_package"):
    """
    Try to obtain version reliably at build-time without importing the package.
    Order:
      1) parse __version__ from package/__init__.py
      2) read VERSION file at repo root
      3) read SETUPTOOLS_SCM_PRETEND_VERSION env var (useful in CI)
    """
    root = Path(__file__).parent.resolve()

    # 1) parse from package __init__.py
    init_path = root / package_name / "__init__.py"
    if init_path.exists():
        text = init_path.read_text(encoding="utf8")
        m = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", text, re.M)
        if m:
            return m.group(1)

    # 2) fallback to VERSION file in repo root
    version_file = root / "VERSION"
    if version_file.exists():
        version = version_file.read_text(encoding="utf8").strip()
        if version:
            return version

    # 3) fallback to env var (useful in CI/Render when .git is missing)
    env_version = os.environ.get("SETUPTOOLS_SCM_PRETEND_VERSION") or os.environ.get("PROJECT_VERSION")
    if env_version:
        return env_version

    raise RuntimeError(
        "Could not determine package version. Ensure one of the following is present:\n"
        " - __version__ in {pkg}/__init__.py\n"
        " - a VERSION file at project root\n"
        " - SETUPTOOLS_SCM_PRETEND_VERSION or PROJECT_VERSION env var (useful for CI builds)\n"
        .format(pkg=package_name)
    )

# --- CONFIG: change these to match your project ---
PACKAGE_NAME = "your_package"         # folder that contains __init__.py
PROJECT_NAME = "your-project-name"    # package / distribution name
# ------------------------------------------------

VERSION = get_version(PACKAGE_NAME)

here = Path(__file__).parent.resolve()
long_description = ""
readme = here / "README.md"
if readme.exists():
    long_description = readme.read_text(encoding="utf8")

setup(
    name=PROJECT_NAME,
    version=VERSION,
    description="A short description of your project",
    long_description=long_description,
    long_description_content_type="text/markdown" if long_description else None,
    packages=find_packages(exclude=("tests", "docs")),
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
    entry_points={
        "console_scripts": [
            # example: "run-my-app = your_package.app:main"
        ]
    },
)
