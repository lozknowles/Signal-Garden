import re


def normalize_note_title(title, max_length=72):
    """Normalize article titles for readable Obsidian source filenames."""
    cleaned = re.sub(
        r"\s+",
        " ",
        str(title).strip()
    )

    cleaned = re.sub(
        r'[\\/*?:"<>|]',
        "",
        cleaned
    )

    if not cleaned:
        return "Untitled"

    if len(cleaned) <= max_length:
        return cleaned

    if ":" in cleaned:
        prefix = cleaned.split(":", 1)[0].strip()

        if 10 <= len(prefix) <= max_length:
            return prefix

    trimmed = cleaned[: max_length - 1].rstrip()

    return f"{trimmed}…"


def normalize_topic_label(value):
    """Return the stable lowercase key used for topic matching."""
    return re.sub(
        r"\s+",
        " ",
        str(value).strip()
    ).lower()
