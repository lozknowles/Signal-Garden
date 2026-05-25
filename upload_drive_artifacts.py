from pathlib import Path
import argparse
import json
import os
import re
import shutil
import subprocess

from dotenv import load_dotenv


VAULT_PATH = Path(r"C:\Loz")

load_dotenv()


def drive_filename(path):
    match = re.match(
        r"^(Signal Garden Podcast - \d{4}-\d{2}-\d{2})(?:-\d{6})?\.mp3$",
        Path(path).name,
        re.IGNORECASE,
    )
    if match:
        return f"{match.group(1)}.mp3"
    return Path(path).name


def enabled():
    return os.getenv("GOOGLE_DRIVE_UPLOAD_ENABLED", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def upload(path):
    result = {
        "path": str(path),
        "uploaded": False,
        "method": None,
        "destination": None,
        "error": None,
    }

    path = Path(path)
    if not path.exists():
        result["error"] = "Artifact not found."
        return result

    local_folder = os.getenv("GOOGLE_DRIVE_LOCAL_FOLDER", "").strip()
    if local_folder:
        try:
            destination_dir = Path(local_folder)
            destination_dir.mkdir(parents=True, exist_ok=True)
            destination = destination_dir / drive_filename(path)
            shutil.copy2(path, destination)
            result.update(
                {
                    "uploaded": True,
                    "method": "local-folder",
                    "destination": str(destination),
                }
            )
            return result
        except Exception as exc:
            result["error"] = str(exc)
            return result

    remote = os.getenv("GOOGLE_DRIVE_RCLONE_REMOTE", "").strip()
    if remote:
        try:
            subprocess.run(
                ["rclone", "copyto", str(path), f"{remote.rstrip('/')}/{drive_filename(path)}"],
                check=True,
                capture_output=True,
                text=True,
            )
            result.update(
                {
                    "uploaded": True,
                    "method": "rclone",
                    "destination": remote,
                }
            )
            return result
        except Exception as exc:
            result["error"] = str(exc)
            return result

    result["error"] = "Set GOOGLE_DRIVE_LOCAL_FOLDER or GOOGLE_DRIVE_RCLONE_REMOTE."
    return result


def latest(pattern):
    matches = sorted(
        (VAULT_PATH / "Reports").glob(pattern),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return matches[0] if matches else None


def main():
    parser = argparse.ArgumentParser(
        description="Upload Signal Garden report artifacts to Google Drive sync/rclone destination."
    )
    parser.add_argument("paths", nargs="*", help="Specific files to upload.")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Upload the latest daily PDF and latest podcast MP3.",
    )
    args = parser.parse_args()

    if not enabled():
        print("GOOGLE_DRIVE_UPLOAD_ENABLED is not true.")

    paths = [Path(item) for item in args.paths]
    if args.latest:
        paths.extend(
            [
                latest("Daily Brief - *.pdf"),
                latest("Signal Garden Podcast - *.mp3"),
            ]
        )

    paths = [path for path in paths if path]
    if not paths:
        raise SystemExit("No upload paths supplied.")

    results = [upload(path) for path in paths]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
