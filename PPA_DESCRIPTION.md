# Advanced Speedtest CLI - PPA Description

## About This PPA

This PPA (Personal Package Archive) provides the **Advanced Speedtest CLI** - a sophisticated command-line utility for measuring internet speed with precision.

### PPA Name
`ppa:shakilofficial0/adv-speedtest-cli`

### Quick Installation

```bash
# Add the PPA
sudo add-apt-repository ppa:shakilofficial0/adv-speedtest-cli

# Update package list
sudo apt-get update

# Install the package
sudo apt-get install adv-speedtest-cli

# Run it
adv-speedtest-cli
```

## Features

### Precision Latency Testing
- WebSocket-based ping measurement for accurate latency assessment
- Real-time latency monitoring during tests
- TCP-based RTT metrics with advanced statistics

### Adaptive Download Testing
- Multi-threaded parallel connections (configurable 1-64 threads)
- Smart stabilization detection
- Real-time concurrent ping monitoring
- Adaptive test duration (10-30 seconds)

### Dynamic Upload Testing
- Parallel upload streams with real-time progress
- Dynamic file sizing for optimal testing
- 15-second test duration with variable measurement window (3-12s)
- Concurrent ping monitoring during upload

### Server Management
- Automatic server selection based on location
- Manual server selection with search capabilities
- Support for custom speedtest servers
- Server diversity for accurate results

### Authentication
- Dual-mode authentication (registered users and anonymous)
- Cookie-based session persistence
- Secure credential handling
- Local credential storage (Windows/macOS/Linux compatible)

### Result Sharing
- Direct sharing to speedtest.net with one-command result posting
- Automatic hash generation for result integrity
- Full API integration with speedtest.net
- JSON-based payload with comprehensive metrics

### User Interface
- Color-coded results and progress indicators
- Real-time progress visualization with tqdm
- Performance indicators and status messages
- Cross-platform terminal compatibility (Windows, macOS, Linux)

## Supported Systems

### Ubuntu Versions
- Ubuntu 20.04 LTS (Focal)
- Ubuntu 22.04 LTS (Jammy)
- Ubuntu 24.04 LTS (Noble)
- Debian 11+ (Bullseye and later)

### Python
- Python 3.7 or later
- Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13+

## Dependencies

Automatically installed with the package:
- `python3` (>= 3.7)
- `python3-requests` - HTTP library for API calls
- `python3-websockets` - WebSocket support for ping testing
- `python3-colorama` - Terminal color support
- `python3-tqdm` - Progress bar visualization

## Usage Examples

### Basic Speed Test
```bash
adv-speedtest-cli
```


## Performance Metrics

The tool provides:
- **Ping/Latency**: Milliseconds with jitter and RTT statistics
- **Download Speed**: Mbps with real-time progress
- **Upload Speed**: Mbps with concurrent monitoring
- **ISP Information**: Automatic ISP detection
- **Server Information**: Location, sponsor, distance metrics

## Result Sharing

Results can be automatically shared to speedtest.net with a unique share link for:
- Sharing with others
- Storing test history

## Technical Details

### Architecture
- **Language**: Python 3 (Cross-platform)
- **Concurrency**: Multi-threaded with thread pool
- **Network**: WebSocket for ping, HTTP for speed tests
- **Data Format**: JSON-based payload for API
- **Storage**: Local cookie persistence for session management

### Speedtest.net Integration
- Official API support
- Automatic server discovery
- Result verification via MD5 hash
- Cookie-based authentication
- Full latency data structure support

## Troubleshooting

### Command not found after installation
```bash
# Refresh PATH
exec $SHELL

# Or manually run
python3 -m advanced_speedtest_cli
```

### Import errors
```bash
# Ensure dependencies are installed
sudo apt-get install -f

# Reinstall the package
sudo apt-get install --reinstall adv-speedtest-cli
```

### Network issues
- Check your internet connection
- Try with `--threads 1` for slower connections
- Use `--verbose` to see detailed output

## Support

- **GitHub Repository**: https://github.com/shakilofficial0/adv-speedtest-cli
- **Issue Tracker**: https://github.com/shakilofficial0/adv-speedtest-cli/issues
- **Email**: shakilofficial0@gmail.com

## License

MIT License - See LICENSE file in repository for details

## Version Information

- **Current Version**: 2.1.0
- **Latest Update**: January 2026
- **Debian Compatibility**: Level 12+
- **Release Status**: Stable

## Changelog

### Version 2.1.0
- Enhanced Result Sharing with full speedtest.net API integration
- Improved latency data structure with TCP metrics
- Cookie-based authentication support
- Adaptive download testing with stabilization detection
- WebSocket ping testing functionality
- Configurable parallel connections (1-64)
- Color-coded result visualization
- Production-ready code
- Comprehensive error handling and user feedback

## Contributing

Contributions are welcome! Please visit the GitHub repository to:
- Report bugs
- Suggest features
- Submit pull requests
- Contribute documentation

## Security

The application:
- ✅ Never stores passwords in plain text
- ✅ Uses secure HTTP/HTTPS for all connections
- ✅ Implements proper certificate validation
- ✅ Follows Python security best practices
- ✅ Regular dependency updates for security patches

---

**Maintained by**: Shakil Ahmed (shakilofficial0@gmail.com)  
**Repository**: https://github.com/shakilofficial0/adv-speedtest-cli  
**PPA**: ppa:shakilofficial0/adv-speedtest-cli
