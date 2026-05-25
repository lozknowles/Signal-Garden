from pathlib import Path
import json
import os
import re
import requests


VAULT_PATH = Path(r"C:\Loz")


def api_url():
    return os.getenv("OPEN_NOTEBOOK_API_URL", "http://localhost:5055").rstrip("/")


def latest_handoff():
    audio_dir = VAULT_PATH / "Audio"
    notes = sorted(
        audio_dir.glob("Open Notebook Podcast Handoff - *.md"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )
    return notes[0] if notes else None


def extract_job_id(text):
    match = re.search(r"Job ID:\s*([^\s]+)", text)
    return match.group(1).strip() if match else ""


def find_nested(payload, keys):
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in keys and value:
                return value
            found = find_nested(value, keys)
            if found:
                return found
    if isinstance(payload, list):
        for item in payload:
            found = find_nested(item, keys)
            if found:
                return found
    return None


def main():
    handoff = latest_handoff()
    if not handoff:
        print("No Open Notebook podcast handoff note found.")
        return

    text = handoff.read_text(encoding="utf-8")
    job_id = extract_job_id(text)
    if not job_id:
        print(f"No job ID found in {handoff}")
        return

    status = requests.get(f"{api_url()}/api/podcasts/jobs/{job_id}", timeout=30)
    status.raise_for_status()
    payload = status.json()
    episode_id = find_nested(payload, {"episode_id", "episodeId"})

    status_block = json.dumps(payload, indent=2)
    updated = text
    marker = "\n## Latest Podcast Job Status\n"
    updated = updated.split(marker, 1)[0]
    updated += marker + "\n```json\n" + status_block + "\n```\n"

    if episode_id:
        audio_url = f"{api_url()}/api/podcasts/episodes/{episode_id}/audio"
        audio = requests.get(audio_url, timeout=60)
        audio.raise_for_status()
        reports = VAULT_PATH / "Reports"
        reports.mkdir(parents=True, exist_ok=True)
        audio_path = reports / f"{handoff.stem}.mp3"
        audio_path.write_bytes(audio.content)
        updated += f"\n## Downloaded Audio\n\n- Local file: {audio_path}\n- API URL: {audio_url}\n"
        print(f"Downloaded podcast audio: {audio_path}")
    else:
        print("Podcast job has not exposed an episode ID yet.")

    handoff.write_text(updated, encoding="utf-8")
    print(f"Updated handoff note: {handoff}")


if __name__ == "__main__":
    main()
