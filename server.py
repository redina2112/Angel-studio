#!/usr/bin/env python3
"""Angel Studios — development/production server.

Run it with::

    py server.py                # http://127.0.0.1:8000
    py server.py --port 5000    # custom port
    py server.py --open         # also open the browser

Only the Python standard library is required (Python 3.9+).
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
import webbrowser
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import DB_PATH, DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD, init_db  # noqa: E402
from app.web import AngelRequestHandler  # noqa: E402

BANNER = r"""
   ___    _   _  ____ _____ _     ____  ___  _   _ ___ _____ ____
  / _ \  | \ | |/ ___| ____| |   / ___|/ _ \| | | |_ _|_   _/ ___|
 | |_| | |  \| | |  _|  _| | |   \___ \ (_) | | | || |  | | \___ \
 |  _  | | |\  | |_| | |___| |___ ___) \__, | |_| || |  | |  ___) |
 |_| |_| |_| \_|\____|_____|_____|____/  /_/ \___/|___| |_| |____/
"""


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Serve the Angel Studios website and API.")
    parser.add_argument("--host", default=os.environ.get("ANGEL_HOST", "127.0.0.1"),
                        help="Interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("ANGEL_PORT", "8000")),
                        help="Port to listen on (default: 8000)")
    parser.add_argument("--open", action="store_true", help="Open the site in a browser after start")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-request logging")
    parser.add_argument("--reset-db", action="store_true",
                        help="Delete the database file before starting (destructive)")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.reset_db and DB_PATH.exists():
        for suffix in ("", "-wal", "-shm"):
            candidate = DB_PATH.with_name(DB_PATH.name + suffix)
            if candidate.exists():
                candidate.unlink()
        print(f"Removed existing database at {DB_PATH}")

    init_db()

    server = ThreadingHTTPServer((args.host, args.port), AngelRequestHandler)
    server.daemon_threads = True
    server.quiet = args.quiet

    url = f"http://{'127.0.0.1' if args.host in ('0.0.0.0', '') else args.host}:{args.port}/"
    print(BANNER)
    print(f"  Angel Studios is running at  {url}")
    print(f"  Database                     {DB_PATH}")
    print(f"  Administrator login          {DEFAULT_ADMIN_EMAIL}")
    print(f"  Administrator password       {DEFAULT_ADMIN_PASSWORD}")
    print("  (Change the administrator password after first sign-in.)")
    print("\n  Press Ctrl+C to stop.\n")

    if args.open:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Angel Studios…")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
