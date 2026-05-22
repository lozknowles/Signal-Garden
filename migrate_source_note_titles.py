from pathlib import Path
from datetime import datetime
import argparse
import hashlib
import re
import shutil


VAULT_PATH = Path(r"C:\Loz")
SOURCES_PATH = VAULT_PATH / "Sources"


def normalize_note_title(title, max_length=72):

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


def sanitize_filename(title):

    return re.sub(
        r'[\\/*?:"<>|]',
        "",
        str(title)
    ).strip()


def _parse_scalar(raw_value):

    value = raw_value.strip()

    if not value:

        return ""

    if value.startswith(("'", '"')) and value.endswith(("'", '"')):

        return value[1:-1]

    if value.lower() == "true":

        return True

    if value.lower() == "false":

        return False

    if value.lower() == "null":

        return None

    if re.fullmatch(r"-?\d+", value):

        try:

            return int(value)

        except ValueError:

            pass

    if re.fullmatch(r"-?\d+\.\d+", value):

        try:

            return float(value)

        except ValueError:

            pass

    return value


def _parse_frontmatter_block(block_text):

    metadata = {}
    current_list = None

    for raw_line in block_text.splitlines():

        line = raw_line.rstrip()

        if not line:

            continue

        if line.startswith("- ") and current_list is not None:

            current_list.append(_parse_scalar(line[2:].strip()))

            continue

        current_list = None

        if ":" not in line:

            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if not key:

            continue

        if not value:

            metadata[key] = []
            current_list = metadata[key]
            continue

        metadata[key] = _parse_scalar(value)

    return metadata


def _split_leading_frontmatter(text):

    if not text.startswith("---"):

        return {}, text

    lines = text.splitlines(keepends=True)

    if not lines or not lines[0].strip() == "---":

        return {}, text

    end_index = None

    for index in range(1, len(lines)):

        if lines[index].strip() == "---":

            end_index = index
            break

    if end_index is None:

        return {}, text

    block_text = "".join(lines[1:end_index])
    remainder = "".join(lines[end_index + 1 :])

    return _parse_frontmatter_block(block_text), remainder


def _load_markdown_metadata(note_path):

    raw_text = note_path.read_text(encoding="utf-8")
    outer_meta, remainder = _split_leading_frontmatter(raw_text)
    inner_meta, content = _split_leading_frontmatter(remainder.lstrip("\n\r"))

    metadata = dict(outer_meta)
    metadata.update(inner_meta)

    return metadata, content.lstrip("\n\r")


def _format_scalar(value):

    if value is None:

        return '""'

    if isinstance(value, bool):

        return "true" if value else "false"

    if isinstance(value, (int, float)):

        return str(value)

    return repr(str(value))


def _dump_frontmatter(metadata):

    lines = ["---"]

    for key, value in metadata.items():

        if isinstance(value, list):

            lines.append(f"{key}:")

            for item in value:

                lines.append(f"- {_format_scalar(item)}")

            continue

        lines.append(f"{key}: {_format_scalar(value)}")

    lines.append("---")

    return "\n".join(lines)


def load_note(note_path):

    metadata, content = _load_markdown_metadata(note_path)

    return metadata, content


def unique_target_path(target_path, source_path):

    if not target_path.exists():

        return target_path

    if target_path.resolve() == source_path.resolve():

        return target_path

    stem = target_path.stem
    suffix = target_path.suffix

    digest = hashlib.sha1(
        str(source_path).encode("utf-8")
    ).hexdigest()[:6]

    candidate = target_path.with_name(f"{stem} ~{digest}{suffix}")

    if not candidate.exists():

        return candidate

    for index in range(2, 100):

        numbered = target_path.with_name(
            f"{stem} ({index}){suffix}"
        )

        if not numbered.exists():

            return numbered

    raise RuntimeError(
        f"Could not find a unique filename for {source_path}"
    )


def migrate_source_titles(max_length=72, apply=False):

    if not SOURCES_PATH.exists():

        raise FileNotFoundError(f"Missing sources folder: {SOURCES_PATH}")

    candidates = sorted(SOURCES_PATH.glob("*.md"))
    planned = []

    for note_path in candidates:

        metadata, content = load_note(note_path)
        full_title = (
            metadata.get("full_title")
            or metadata.get("title")
            or note_path.stem
        )
        desired_title = normalize_note_title(
            full_title,
            max_length=max_length
        )

        safe_title = sanitize_filename(desired_title)

        if not safe_title:

            safe_title = "Untitled"

        if note_path.stem == safe_title:

            continue

        target_path = unique_target_path(
            note_path.with_name(f"{safe_title}.md"),
            note_path
        )

        planned.append(
            {
                "source": note_path,
                "target": target_path,
                "full_title": full_title,
                "short_title": safe_title,
                "content": content,
                "metadata": metadata
            }
        )

    if not planned:

        print("No source note titles need migration.")
        return

    print(f"Planned {len(planned)} title migrations:")

    for item in planned:

        print(
            f"- {item['source'].name} -> {item['target'].name}"
            f" (short: {item['short_title']})"
        )

    if not apply:

        print("")
        print("Dry run only. Re-run with --apply to make the changes.")
        return

    for item in planned:

        metadata = dict(item["metadata"])
        metadata["title"] = item["short_title"]
        metadata["full_title"] = item["full_title"]
        metadata["migrated_at"] = datetime.now().isoformat()

        if item["source"].resolve() != item["target"].resolve():

            shutil.move(
                str(item["source"]),
                str(item["target"])
            )

        with open(
            item["target"],
            "w",
            encoding="utf-8"
        ) as f:

            f.write(_dump_frontmatter(metadata))
            f.write("\n\n")
            f.write(item["content"].lstrip("\n\r"))

        print(f"Updated: {item['target']}")


def main():

    parser = argparse.ArgumentParser(
        description="Normalize oversized source note filenames in the Signal Garden vault."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the migration instead of doing a dry run."
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=72,
        help="Maximum length for the normalized title."
    )

    args = parser.parse_args()

    migrate_source_titles(
        max_length=args.max_length,
        apply=args.apply
    )


if __name__ == "__main__":
    main()
