from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import argparse
import json
import mimetypes
import os
import re
import shutil
import time

from dotenv import load_dotenv


PROJECT_PATH = Path(__file__).resolve().parent
APP_PATH = PROJECT_PATH / "admin_app"
CONFIG_PATH = PROJECT_PATH / "areas.json"

load_dotenv()


def vault_path():
    return Path(
        os.getenv(
            "SIGNAL_GARDEN_VAULT_PATH",
            r"C:\Loz"
        )
    )


def inbox_path():
    path = vault_path() / "Inbox"
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path, default):
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def backup_file(path):
    if not path.exists():
        return

    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = path.with_suffix(f".{stamp}.bak")
    shutil.copy2(path, backup)


def extract_urls(text):
    return [
        match.rstrip(".,);]")
        for match in re.findall(r"https?://[^\s<>\"]+", text or "")
    ]


def normalize_clip(item):
    if isinstance(item, str):
        urls = extract_urls(item)
        return [
            {
                "url": url,
                "topic": "",
                "reason": item.strip()
            }
            for url in urls
        ]

    if not isinstance(item, dict):
        return []

    url = str(item.get("url", "")).strip()
    if not url:
        return []

    return [
        {
            "url": url,
            "title": str(item.get("title", "")).strip(),
            "topic": str(item.get("topic", "")).strip(),
            "reason": str(item.get("reason", "")).strip()
        }
    ]


def normalize_personal_source(item):
    if isinstance(item, str):
        urls = extract_urls(item)
        return [
            {
                "type": "url",
                "url": url,
                "title": "",
                "topic": "",
                "reason": item.strip()
            }
            for url in urls
        ]

    if not isinstance(item, dict):
        return []

    source_type = str(item.get("type", "url")).strip().lower() or "url"
    url = str(item.get("url") or item.get("feed_url") or "").strip()

    if not url:
        return []

    record = {
        "type": source_type,
        "title": str(item.get("title", "")).strip(),
        "topic": str(item.get("topic", "")).strip(),
        "reason": str(item.get("reason", "")).strip()
    }

    if source_type in {"rss", "atom", "feed", "x"}:
        record["feed_url"] = url
    else:
        record["url"] = url

    return [record]


def merge_by_url(existing, incoming):
    merged = []
    seen = set()

    for item in existing + incoming:
        key = (
            item.get("url") or
            item.get("feed_url") or
            item.get("handle") or
            json.dumps(item, sort_keys=True)
        )

        if key in seen:
            continue

        seen.add(key)
        merged.append(item)

    return merged


class AdminHandler(BaseHTTPRequestHandler):
    server_version = "SignalGardenAdmin/0.1"

    def send_json(self, payload, status=200):
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}

        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/state":
            self.send_json(
                {
                    "config": read_json(CONFIG_PATH, {}),
                    "manual_clips": read_json(
                        inbox_path() / "manual_clips.json",
                        []
                    ),
                    "personal_sources": read_json(
                        inbox_path() / "personal_sources.json",
                        {"sources": []}
                    ),
                    "paths": {
                        "config": str(CONFIG_PATH),
                        "vault": str(vault_path()),
                        "inbox": str(inbox_path())
                    }
                }
            )
            return

        relative = parsed.path.lstrip("/") or "index.html"
        target = (APP_PATH / relative).resolve()

        if not str(target).startswith(str(APP_PATH.resolve())):
            self.send_error(403)
            return

        if not target.exists() or target.is_dir():
            target = APP_PATH / "index.html"

        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            payload = self.read_body_json()
            parsed = urlparse(self.path)

            if parsed.path == "/api/config":
                config = payload.get("config")

                if not isinstance(config, dict):
                    self.send_json({"error": "config must be an object"}, status=400)
                    return

                backup_file(CONFIG_PATH)
                write_json(CONFIG_PATH, config)
                self.send_json({"ok": True, "config": config})
                return

            if parsed.path == "/api/manual-clips":
                items = payload.get("items", [])
                if isinstance(items, (str, dict)):
                    items = [items]

                incoming = []
                for item in items:
                    incoming.extend(normalize_clip(item))

                path = inbox_path() / "manual_clips.json"
                existing = read_json(path, [])
                if isinstance(existing, dict):
                    existing = existing.get("clips", [])
                if not isinstance(existing, list):
                    existing = []

                merged = merge_by_url(existing, incoming)
                write_json(path, merged)
                self.send_json({"ok": True, "manual_clips": merged})
                return

            if parsed.path == "/api/personal-sources":
                items = payload.get("items", [])
                if isinstance(items, (str, dict)):
                    items = [items]

                incoming = []
                for item in items:
                    incoming.extend(normalize_personal_source(item))

                path = inbox_path() / "personal_sources.json"
                payload_existing = read_json(path, {"sources": []})
                existing = payload_existing.get("sources", []) if isinstance(payload_existing, dict) else []
                if not isinstance(existing, list):
                    existing = []

                merged = merge_by_url(existing, incoming)
                output = {"sources": merged}
                write_json(path, output)
                self.send_json({"ok": True, "personal_sources": output})
                return

            self.send_json({"error": "Not found"}, status=404)

        except Exception as exc:
            self.send_json({"error": str(exc)}, status=500)


def main():
    parser = argparse.ArgumentParser(
        description="Run the Signal Garden React admin app."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), AdminHandler)
    print(f"Signal Garden admin running at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping admin server.")


if __name__ == "__main__":
    main()
