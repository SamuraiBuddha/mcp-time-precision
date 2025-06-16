#!/usr/bin/env python3
"""
MCP Time Precision Server entry point.
"""

import argparse
import asyncio
import logging
import sys
from .server import TimePrecisionServer


def setup_logging(debug: bool = False):
    """Configure logging based on debug flag."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )


async def run_server(instance_id: str, debug: bool = False):
    """Run the MCP time precision server."""
    setup_logging(debug)
    
    server = TimePrecisionServer(instance_id=instance_id)
    await server.run()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MCP Time Precision Server - Microsecond-accurate timestamps"
    )
    parser.add_argument(
        "--instance-id",
        default="Default-001",
        help="Unique instance identifier (e.g., Melchior-001, Balthasar-001, Caspar-001)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run_server(args.instance_id, args.debug))
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
