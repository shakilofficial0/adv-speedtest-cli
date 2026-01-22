#!/bin/bash
# Advanced Speedtest CLI - PPA Repository Setup Script
# This script helps set up the PPA repository on Launchpad

set -e

echo "Advanced Speedtest CLI - PPA Setup"
echo "==================================="
echo ""

# Check if running on Linux
if [[ ! "$OSTYPE" == "linux"* ]]; then
    echo "Error: This script must be run on Linux"
    exit 1
fi

# Check for required tools
if ! command -v gpg &> /dev/null; then
    echo "Error: GPG is not installed"
    echo "Install with: sudo apt install gnupg"
    exit 1
fi

echo "PPA Repository URL:"
echo "  ppa:shakilofficial0/adv-speedtest-cli"
echo ""

echo "Supported distributions:"
echo "  - Ubuntu 20.04 LTS (Focal)"
echo "  - Ubuntu 22.04 LTS (Jammy)"
echo "  - Ubuntu 24.04 LTS (Noble)"
echo "  - Debian 11 (Bullseye)"
echo "  - Debian 12 (Bookworm)"
echo ""

echo "To add this PPA, run:"
echo "  sudo add-apt-repository ppa:shakilofficial0/adv-speedtest-cli"
echo "  sudo apt update"
echo ""

echo "To install Advanced Speedtest CLI:"
echo "  sudo apt install adv-speedtest-cli"
echo ""

echo "To remove this PPA:"
echo "  sudo add-apt-repository --remove ppa:shakilofficial0/adv-speedtest-cli"
echo ""

echo "PPA Setup Information"
echo "===================="
echo "Repository: https://launchpad.net/~shakilofficial0/+archive/ubuntu/adv-speedtest-cli"
echo "Maintainer: Shakil Ahmed <shakilofficial0@gmail.com>"
echo "Source: https://github.com/shakilofficial0/adv-speedtest-cli"
echo ""
