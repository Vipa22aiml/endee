"""Endee MCP Framework - Entry point."""

import asyncio

from .server import main


def run():
    """Run the MCP server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
