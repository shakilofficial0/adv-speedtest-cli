#!/usr/bin/env python3
"""
Advanced Speedtest CLI Setup
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
readme_file = Path(__file__).parent / "readme.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="adv-speedtest-cli",
    version="2.1.0",
    author="Shakil Ahmed",
    author_email="shakilofficial0@gmail.com",
    description="Advanced Speedtest CLI - A cross-platform speedtest utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shakilofficial0/adv-speedtest-cli",
    project_urls={
        "Bug Tracker": "https://github.com/shakilofficial0/adv-speedtest-cli/issues",
        "Documentation": "https://github.com/shakilofficial0/adv-speedtest-cli",
        "Source Code": "https://github.com/shakilofficial0/adv-speedtest-cli",
    },
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "adv-speedtest-cli=advanced_speedtest_cli.speedtest:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "websockets>=10.0",
        "colorama>=0.4.5",
        "tqdm>=4.64.0",
    ],
    keywords="speedtest internet speed cli network bandwidth",
    license="MIT",
)
