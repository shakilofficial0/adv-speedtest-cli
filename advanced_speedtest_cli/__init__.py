"""
Advanced Speedtest CLI
A sophisticated command-line utility for measuring internet speed with precision.
"""

__version__ = "2.2.1"
__author__ = "Shakil Ahmed"
__email__ = "shakilofficial0@gmail.com"
__license__ = "MIT"

# Import main speedtest module when package is imported
from . import speedtest

__all__ = ["speedtest"]
