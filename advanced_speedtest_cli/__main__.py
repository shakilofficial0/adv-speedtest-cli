"""
Advanced Speedtest CLI - Main Entry Point
"""

import sys
from . import speedtest

if __name__ == "__main__":
    try:
        speedtest.main()
    except KeyboardInterrupt:
        print("\n\n[!] Test interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Error: {e}", file=sys.stderr)
        sys.exit(1)
