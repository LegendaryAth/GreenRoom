# setup.py - safe, import-free version resolution (reads VERSION)
from pathlib import Path
from setuptools import setup, find_packages

ROOT = Path(__file__).parent.resolve()

def get_version():
    vfile = ROOT / "VERSION"
    if vfile.exists():
        return vfile.read_text(encoding="utf8").strip()
    # final fallback
    raise RuntimeError("VERSION file not found. Create a VERSION file with a version like '0.1.0'.")

VERSION = get_version()

long_description = ""
readme = ROOT / "README.md"
if readme.exists():
    long_description = readme.read_text(encoding="utf8")

setup(
    name="your-flask-app",
    version=VERSION,
    description="Flask app for Gemini image analysis",
    long_description=long_description,
    long_description_content_type="text/markdown" if long_description else None,
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "Flask==3.0.0",
        "python-dotenv==1.0.0",
        "google-generativeai==0.3.2",
        "Pillow==10.1.0",
        "Markdown==3.5.1",
        "requests",
        "Flask-Cors",
    ],
)
