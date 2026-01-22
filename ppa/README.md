# Advanced Speedtest CLI - Ubuntu PPA Repository

This PPA (Personal Package Archive) provides easy installation of Advanced Speedtest CLI on Ubuntu and Debian-based systems.

## Adding the PPA

```bash
sudo add-apt-repository ppa:shakilofficial0/adv-speedtest-cli
sudo apt update
```

## Installation

```bash
sudo apt install adv-speedtest-cli
```

## Usage

```bash
# Interactive mode
adv-speedtest-cli

# Quick mode
adv-speedtest-cli --q
```

## Supported Distributions

- Ubuntu 20.04 LTS (Focal)
- Ubuntu 22.04 LTS (Jammy)
- Ubuntu 24.04 LTS (Noble)
- Debian 11 (Bullseye)
- Debian 12 (Bookworm)

## Removing the PPA

```bash
sudo apt remove adv-speedtest-cli
sudo add-apt-repository --remove ppa:shakilofficial0/adv-speedtest-cli
```

## Support

For issues and feature requests, visit: https://github.com/shakilofficial0/adv-speedtest-cli
