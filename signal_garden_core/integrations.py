from datetime import datetime
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import time

import requests


def parse_bool_env(name, default=False):

    value = os.getenv(name)

    if value is None:

        return default

    return str(value).strip().lower() in {
        "1",
        "true",
        "yes",
        "on"
    }


def signal_garden_vault_path():

    return Path(
        os.getenv(
            "SIGNAL_GARDEN_VAULT_PATH",
            r"C:\Loz"
        )
    )


def open_notebook_base_url():

    return os.getenv(
        "OPEN_NOTEBOOK_BASE_URL",
        "http://localhost:8502"
    ).rstrip("/")


def open_notebook_api_url():

    return os.getenv(
        "OPEN_NOTEBOOK_API_URL",
        "http://localhost:5055"
    ).rstrip("/")


def open_notebook_headers():

    headers = {
        "Content-Type": "application/json"
    }

    token = os.getenv(
        "OPEN_NOTEBOOK_API_TOKEN",
        ""
    ).strip()

    if token:

        headers["Authorization"] = f"Bearer {token}"

    return headers


def open_notebook_request(
    method,
    path,
    payload=None,
    timeout=30
):

    url = f"{open_notebook_api_url()}{path}"

    response = requests.request(
        method,
        url,
        headers=open_notebook_headers(),
        json=payload,
        timeout=timeout
    )

    response.raise_for_status()

    if not response.content:

        return None

    return response.json()


def open_notebook_enabled():

    return parse_bool_env(
        "OPEN_NOTEBOOK_SYNC_ENABLED",
        False
    )


def open_notebook_generate_enabled():

    return parse_bool_env(
        "OPEN_NOTEBOOK_GENERATE_PODCAST",
        False
    )


def open_notebook_notebook_name():

    return os.getenv(
        "OPEN_NOTEBOOK_NOTEBOOK_NAME",
        "Signal Garden"
    ).strip() or "Signal Garden"


def open_notebook_episode_profile():

    return os.getenv(
        "OPEN_NOTEBOOK_EPISODE_PROFILE",
        "signal_forecast"
    ).strip() or "signal_forecast"


def open_notebook_speaker_profile():

    return os.getenv(
        "OPEN_NOTEBOOK_SPEAKER_PROFILE",
        "single_forecaster"
    ).strip() or "single_forecaster"


def get_or_create_open_notebook():

    notebook_name = open_notebook_notebook_name()
    notebooks = open_notebook_request(
        "GET",
        "/api/notebooks",
        timeout=30
    ) or []

    for notebook in notebooks:

        if notebook.get("name") == notebook_name:

            return notebook

    return open_notebook_request(
        "POST",
        "/api/notebooks",
        {
            "name": notebook_name,
            "description": "Signal Garden generated reading and podcast sources."
        },
        timeout=30
    )


def sync_open_notebook_sources(bundle, notebook_id):

    synced = []

    for source in bundle.get("sources", []):

        url = source.get("url", "")
        title = source.get("title") or source.get("note_title") or url

        if not url:

            continue

        payload = {
            "type": "link",
            "url": url,
            "title": title,
            "notebooks": [
                notebook_id
            ],
            "embed": False,
            "async_processing": True
        }

        created = open_notebook_request(
            "POST",
            "/api/sources/json",
            payload,
            timeout=60
        )

        synced.append(
            {
                "source_id": created.get("id") if isinstance(created, dict) else None,
                "title": title,
                "url": url
            }
        )

    return synced


def open_notebook_content_from_bundle(bundle):

    lines = [
        bundle.get("title", "Signal Garden Podcast Bundle"),
        "",
        bundle.get("podcast_prompt", ""),
        ""
    ]

    for index, source in enumerate(
        bundle.get("sources", []),
        start=1
    ):

        concepts = ", ".join(
            source.get("matched_concepts", [])[:5]
        )

        lines.extend(
            [
                f"Source {index}: {source.get('title', '')}",
                f"Section: {source.get('section', '')}",
                f"URL: {source.get('url', '')}",
                f"Topic: {source.get('topic', '')}",
                f"Why included: {source.get('why_included', '')}",
                f"Concepts: {concepts}",
                ""
            ]
        )

    return "\n".join(lines)


def find_nested_value(payload, target_keys):

    if isinstance(payload, dict):

        for key, value in payload.items():

            if key in target_keys and value:

                return value

            found = find_nested_value(
                value,
                target_keys
            )

            if found:

                return found

    if isinstance(payload, list):

        for item in payload:

            found = find_nested_value(
                item,
                target_keys
            )

            if found:

                return found

    return None


def open_notebook_podcast_links(
    handoff_title,
    handoff_uri,
    bundle_path,
    automation_result
):

    podcast_job = automation_result.get("podcast_job") or {}
    job_status = automation_result.get("podcast_job_status") or {}
    job_id = podcast_job.get("job_id") if isinstance(podcast_job, dict) else None
    episode_id = find_nested_value(
        job_status,
        {
            "episode_id",
            "episodeId"
        }
    )

    audio_url = (
        f"{open_notebook_api_url()}/api/podcasts/episodes/{episode_id}/audio"
        if episode_id else ""
    )

    job_url = (
        f"{open_notebook_api_url()}/api/podcasts/jobs/{job_id}"
        if job_id else ""
    )

    return {
        "handoff_title": handoff_title,
        "handoff_uri": handoff_uri,
        "bundle_path": str(bundle_path),
        "bundle_uri": Path(bundle_path).resolve().as_uri(),
        "open_notebook_app": open_notebook_base_url(),
        "job_id": job_id or "",
        "job_url": job_url,
        "episode_id": episode_id or "",
        "audio_url": audio_url,
        "error": automation_result.get("error") or "",
        "sync_enabled": automation_result.get("enabled"),
        "generate_enabled": automation_result.get("generate_podcast")
    }


def download_open_notebook_audio_if_ready(podcast_links, today_stamp):

    audio_url = podcast_links.get("audio_url")

    if not audio_url:

        return ""

    reports_dir = signal_garden_vault_path() / "Reports"
    reports_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    audio_path = reports_dir / f"Signal Garden Podcast - {today_stamp}.mp3"

    try:

        response = requests.get(
            audio_url,
            timeout=60
        )
        response.raise_for_status()

        if not response.content:

            return ""

        with open(
            audio_path,
            "wb"
        ) as f:

            f.write(response.content)

        return str(audio_path)

    except Exception:

        return ""


def generate_open_notebook_podcast(bundle, notebook_id=None):

    episode_name = bundle.get("title", "Signal Garden Podcast")

    payload = {
        "episode_profile": open_notebook_episode_profile(),
        "speaker_profile": open_notebook_speaker_profile(),
        "episode_name": episode_name,
        "content": open_notebook_content_from_bundle(bundle),
        "briefing_suffix": bundle.get("podcast_prompt", "")
    }

    if notebook_id:

        payload["notebook_id"] = notebook_id

    return open_notebook_request(
        "POST",
        "/api/podcasts/generate",
        payload,
        timeout=60
    )


def poll_open_notebook_podcast_job(job_id):

    if not job_id:

        return None

    poll_seconds_raw = os.getenv(
        "OPEN_NOTEBOOK_PODCAST_POLL_SECONDS",
        "240"
    )

    try:

        poll_seconds = int(poll_seconds_raw)

    except ValueError:

        poll_seconds = 20

    if poll_seconds <= 0:

        return None

    deadline = time.time() + poll_seconds
    latest_status = None

    while time.time() <= deadline:

        latest_status = open_notebook_request(
            "GET",
            f"/api/podcasts/jobs/{job_id}",
            timeout=30
        )

        status_text = str(
            find_nested_value(
                latest_status,
                {
                    "status",
                    "state"
                }
            ) or ""
        ).lower()

        if status_text in {
            "completed",
            "complete",
            "done",
            "finished",
            "success",
            "failed",
            "error"
        }:

            return latest_status

        time.sleep(5)

    return latest_status


def maybe_automate_open_notebook(bundle):

    result = {
        "enabled": open_notebook_enabled(),
        "generate_podcast": open_notebook_generate_enabled(),
        "notebook": None,
        "synced_sources": [],
        "podcast_job": None,
        "podcast_job_status": None,
        "error": None
    }

    if not result["enabled"] and not result["generate_podcast"]:

        return result

    try:

        notebook = None

        if result["enabled"]:

            notebook = get_or_create_open_notebook()
            result["notebook"] = notebook

            if notebook and notebook.get("id"):

                result["synced_sources"] = sync_open_notebook_sources(
                    bundle,
                    notebook["id"]
                )

        if result["generate_podcast"]:

            result["podcast_job"] = generate_open_notebook_podcast(
                bundle,
                notebook.get("id") if notebook else None
            )

            result["podcast_job_status"] = poll_open_notebook_podcast_job(
                result["podcast_job"].get("job_id")
                if isinstance(result["podcast_job"], dict)
                else None
            )

    except Exception as exc:

        result["error"] = str(exc)

    return result


def build_open_notebook_podcast_bundle(
    bundle_title,
    reading_issue_title,
    audio_script_title,
    issue,
    source_limit=10
):

    sections = issue.get("sections", {})
    sources = []
    seen_ids = set()

    for section_name in [
        "Deep Reads",
        "Practical Reads",
        "New Area",
        "Wildcard",
        "Follow-up From Last Week"
    ]:

        for item in sections.get(section_name, []):

            record = item["record"]
            record_id = record.get("id")

            if record_id in seen_ids:

                continue

            seen_ids.add(record_id)
            sources.append(
                {
                    "section": section_name,
                    "note_title": record.get("note_title", ""),
                    "title": record.get("full_title") or record.get("title") or record.get("note_title", ""),
                    "url": record.get("url", ""),
                    "domain": record.get("domain", ""),
                    "topic": record.get("topic", ""),
                    "why_included": item.get("reason") or "Selected by Signal Garden source ranking.",
                    "matched_concepts": item.get("matched_concepts", []),
                    "tier": item.get("focus_label", item.get("tier", "")),
                    "quality": item.get("quality", {})
                }
            )

            if len(sources) >= source_limit:

                break

        if len(sources) >= source_limit:

            break

    return {
        "title": bundle_title,
        "generated_at": datetime.now().isoformat(),
        "target": "Open Notebook podcast generation",
        "open_notebook": {
            "app_url": open_notebook_base_url(),
            "api_url": open_notebook_api_url()
        },
        "reading_issue": reading_issue_title,
        "audio_script": audio_script_title,
        "podcast_prompt": (
            "Create a single-voice Signal Garden audio bulletin from these sources. "
            "Use one calm narrator only. Do not use a radio show format, host banter, guest dialogue, jokes, or dramatic transitions. "
            "Make it precise, measured, and sparse, with the restrained cadence of a shipping forecast or field report. "
            "Start with the date, the active area, and the strongest signal in one sentence. "
            "Then cover: what matters now, what is increasing, what is connected, and what should be researched next. "
            "Mention the wildcard source only if it genuinely adds a useful change of direction. "
            "Use short sentences, concrete nouns, and source-grounded claims. "
            "End with a concise outlook, not a sign-off."
        ),
        "sources": sources
    }


def save_open_notebook_podcast_bundle(bundle, today_stamp):

    reports_dir = signal_garden_vault_path() / "Reports"
    reports_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    bundle_path = reports_dir / f"Open Notebook Podcast Bundle - {today_stamp}.json"

    with open(
        bundle_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            bundle,
            f,
            indent=2
        )

    return bundle_path


def render_open_notebook_handoff_markdown(
    handoff_title,
    reading_issue_title,
    audio_script_title,
    bundle_path,
    bundle,
    automation_result,
    issue,
    source_limit=10
):

    sections = issue.get("sections", {})
    ordered_items = []
    seen_ids = set()

    for section_name in [
        "Deep Reads",
        "Practical Reads",
        "New Area",
        "Wildcard",
        "Follow-up From Last Week"
    ]:

        for item in sections.get(section_name, []):

            record_id = item["record"].get("id")

            if record_id in seen_ids:

                continue

            seen_ids.add(record_id)
            ordered_items.append(
                (
                    section_name,
                    item
                )
            )

            if len(ordered_items) >= source_limit:

                break

        if len(ordered_items) >= source_limit:

            break

    lines = [
        f"# {handoff_title}",
        "",
        f"Generated: {datetime.now().isoformat()}",
        f"Reading issue: [[{reading_issue_title}]]",
        f"Local audio script: [[{audio_script_title}]]",
        f"Open Notebook app: {open_notebook_base_url()}",
        f"Open Notebook API: {open_notebook_api_url()}",
        f"Podcast bundle: {bundle_path}",
        "",
        "## Open Notebook Podcast Link",
        "",
        "- Open Notebook podcast URL:",
        "- Downloaded audio file:",
        "- Public access checked:",
        "",
        "## Automation Status",
        "",
        f"- Source sync enabled: {automation_result.get('enabled')}",
        f"- Podcast generation enabled: {automation_result.get('generate_podcast')}",
        f"- Error: {automation_result.get('error') or 'None'}",
        "",
    ]

    notebook = automation_result.get("notebook") or {}

    if notebook:

        lines.extend(
            [
                f"- Notebook: {notebook.get('name', '')}",
                f"- Notebook ID: {notebook.get('id', '')}",
                ""
            ]
        )

    synced_sources = automation_result.get("synced_sources") or []

    if synced_sources:

        lines.extend(
            [
                "### Synced Sources",
                ""
            ]
        )

        for synced in synced_sources:

            lines.append(
                f"- {synced.get('title', '')} ({synced.get('source_id', '')})"
            )

        lines.append("")

    podcast_job = automation_result.get("podcast_job") or {}

    if podcast_job:

        job_id = podcast_job.get("job_id", "")

        lines.extend(
            [
                "### Podcast Job",
                "",
                f"- Job ID: {job_id}",
                f"- Status: {podcast_job.get('status', '')}",
                f"- Message: {podcast_job.get('message', '')}",
                f"- Poll endpoint: {open_notebook_api_url()}/api/podcasts/jobs/{job_id}",
                f"- Audio endpoint after completion: {open_notebook_api_url()}/api/podcasts/episodes/{{episode_id}}/audio",
                ""
            ]
        )

    lines.extend(
        [
        "## Workflow",
        "",
        "1. Open Open Notebook and create or select a Signal Garden notebook.",
        "2. Add the source URLs below, or use the JSON podcast bundle in Reports for automation.",
        "3. Configure your podcast episode profile, speakers, and TTS provider in Open Notebook.",
        "4. Use the custom prompt below when generating the podcast.",
        "5. Copy the generated podcast link or downloaded audio file path into the Open Notebook Podcast Link section above.",
        "",
        "## Custom Prompt",
        "",
        bundle.get("podcast_prompt", ""),
        "",
        "## Source Bundle",
        ""
        ]
    )

    if not ordered_items:

        lines.append(
            "- No sources were available for Open Notebook handoff."
        )
        return "\n".join(lines)

    for index, (section_name, item) in enumerate(
        ordered_items,
        start=1
    ):

        record = item["record"]
        title = record.get("full_title") or record.get("title") or record.get("note_title")
        reason = item.get("reason") or "Selected by Signal Garden source ranking."
        concepts = item.get("matched_concepts", [])
        concept_text = (
            f" Concepts: {', '.join(concepts[:5])}."
            if concepts else ""
        )

        lines.extend(
            [
                f"### {index}. {section_name}",
                "",
                f"- Note: [[{record['note_title']}]]",
                f"- Title: {title}",
                f"- URL: {record.get('url', '')}",
                f"- Why included: {reason}{concept_text}",
                ""
            ]
        )

    return "\n".join(lines)


def drive_upload_enabled():

    return parse_bool_env(
        "GOOGLE_DRIVE_UPLOAD_ENABLED",
        False
    )


def google_drive_local_folder():

    value = os.getenv(
        "GOOGLE_DRIVE_LOCAL_FOLDER",
        ""
    ).strip()

    return Path(value) if value else None


def google_drive_rclone_remote():

    return os.getenv(
        "GOOGLE_DRIVE_RCLONE_REMOTE",
        ""
    ).strip()


def google_drive_artifact_name(path):

    name = Path(path).name
    match = re.match(
        r"^(Signal Garden Podcast - \d{4}-\d{2}-\d{2})(?:-\d{6})?\.mp3$",
        name,
        re.IGNORECASE
    )

    if match:

        return f"{match.group(1)}.mp3"

    return name


def upload_artifact_to_google_drive(path):

    result = {
        "path": str(path),
        "uploaded": False,
        "method": None,
        "destination": None,
        "error": None
    }

    if not drive_upload_enabled():

        result["error"] = "Google Drive upload disabled."
        return result

    path = Path(path)

    if not path.exists():

        result["error"] = "Artifact not found."
        return result

    local_folder = google_drive_local_folder()

    if local_folder:

        try:

            local_folder.mkdir(
                parents=True,
                exist_ok=True
            )
            destination = local_folder / google_drive_artifact_name(path)
            shutil.copy2(
                path,
                destination
            )
            result.update(
                {
                    "uploaded": True,
                    "method": "local-folder",
                    "destination": str(destination),
                    "error": None
                }
            )
            return result

        except Exception as exc:

            result["error"] = str(exc)
            return result

    remote = google_drive_rclone_remote()

    if remote:

        try:

            completed = subprocess.run(
                [
                    "rclone",
                    "copyto",
                    str(path),
                    f"{remote.rstrip('/')}/{google_drive_artifact_name(path)}"
                ],
                check=True,
                capture_output=True,
                text=True
            )
            result.update(
                {
                    "uploaded": True,
                    "method": "rclone",
                    "destination": remote,
                    "error": completed.stderr.strip() or None
                }
            )
            return result

        except Exception as exc:

            result["error"] = str(exc)
            return result

    result["error"] = "Set GOOGLE_DRIVE_LOCAL_FOLDER or GOOGLE_DRIVE_RCLONE_REMOTE."
    return result


def upload_report_artifacts_to_google_drive(paths):

    return [
        upload_artifact_to_google_drive(path)
        for path in paths
        if path
    ]
