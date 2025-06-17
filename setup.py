from pathlib import Path
from setuptools import setup, find_packages

# Read the long description from README.md
here = Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="lazyrun",
    version="0.2.0",
    author="PJ H.",
    author_email="archood2@gmail.com",
    description="Task Runner With Memory: Save and run your most-used shell commands as one-word shortcuts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArchooD2/lazyrun",
    license="MPL-2.0",
    classifiers=[
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    packages=find_packages(exclude=["tests*", "examples*"]),
    install_requires=[
        "snaparg",
        "appdirs",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "lazyrun=lazyrun.cli:cli",
        ],
    },
)
