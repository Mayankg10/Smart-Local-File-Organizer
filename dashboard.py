#!/usr/bin/env python3
"""
File Organizer Dashboard — Server Entry Point
Usage: python3 dashboard.py [--port 8787]
"""

import json
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from lib.config import SCAN_DIRS
from lib.dashboard_html import DASHBOARD_HTML
from lib.dashboard_api import (
    load_history, load_logs, get_stats,
    scan_reclaimable, delete_files,
    run_organizer, run_undo,
)


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        path = urlparse(self.path).path

        if path in ("/", ""):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())

        elif path == "/api/stats":
            self._json_response(get_stats(load_history()))

        elif path == "/api/logs":
            self._json_response(load_logs())

        elif path == "/api/reclaim/scan":
            self._json_response(scan_reclaimable())

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if path == "/api/reclaim/delete":
            paths = body.get("paths", [])
            category = body.get("category", "unknown")
            deleted, freed = delete_files(paths, category)
            self._json_response({"deleted": deleted, "freed": freed})

        elif path == "/api/organize":
            outputs = [run_organizer(d) for d in SCAN_DIRS]
            combined = "\n".join(outputs)
            moved = combined.count("\u2713")
            msg = f"Organized {moved} files from Downloads & Desktop" if moved > 0 else "No new files to organize"
            self._json_response({"success": moved > 0, "message": msg})

        elif path == "/api/undo":
            undo_all = body.get("all", False)
            out = run_undo(undo_all)
            restored = out.count("\u21a9")
            label = "all operations" if undo_all else "last operation"
            msg = f"Restored {restored} files ({label})" if restored > 0 else "Nothing to undo"
            self._json_response({"success": restored > 0, "message": msg})

        else:
            self.send_response(404)
            self.end_headers()


def main():
    parser = argparse.ArgumentParser(description="File Organizer Dashboard")
    parser.add_argument("--port", type=int, default=8787, help="Port (default: 8787)")
    args = parser.parse_args()

    server = HTTPServer(("127.0.0.1", args.port), DashboardHandler)
    url = f"http://localhost:{args.port}"

    print()
    print(f"  \033[1m\033[36m╔══════════════════════════════════╗\033[0m")
    print(f"  \033[1m\033[36m║    File Organizer Dashboard      ║\033[0m")
    print(f"  \033[1m\033[36m╚══════════════════════════════════╝\033[0m")
    print()
    print(f"  \033[1mRunning at: \033[32m{url}\033[0m")
    print(f"  \033[90mPress Ctrl+C to stop\033[0m")
    print()

    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n  \033[33mDashboard stopped.\033[0m\n")
        server.server_close()


if __name__ == "__main__":
    main()
