from pathlib import Path
from datetime import datetime
import re
import frontmatter

# =========================
# CONFIG
# =========================

VAULT_PATH = Path(r"C:\Loz")

AREAS = [
    "Areas",
    "Projects",
    "Research",
    "People",
    "Daily",
    "Inbox",
    "Reports",
    "MOCs"
]


# =========================
# OBSIDIAN CONNECTOR
# =========================

class ObsidianConnector:

    def __init__(self, vault_path):
        self.vault = Path(vault_path)
        self.ensure_structure()

    def ensure_structure(self):
        """
        Create standard Obsidian folders if missing.
        """
        for area in AREAS:
            (self.vault / area).mkdir(
                parents=True,
                exist_ok=True
            )

    def sanitize_filename(self, name):
        """
        Remove invalid Windows filename characters.
        """
        return re.sub(
            r'[\\/*?:"<>|]',
            "",
            name
        )

    def note_path(self, folder, title):
        """
        Build path for markdown note.
        """
        title = self.sanitize_filename(title)

        return (
            self.vault /
            folder /
            f"{title}.md"
        )

    def create_note(
        self,
        folder,
        title,
        content,
        tags=None
    ):

        note_file = self.note_path(folder, title)

        metadata = {
            "created": datetime.now().isoformat(),
            "tags": tags or []
        }

        post = frontmatter.Post(
            content,
            **metadata
        )

        with open(
            note_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                frontmatter.dumps(post)
            )

        print(f"Created: {note_file}")

    def append_note(
        self,
        folder,
        title,
        content
    ):

        note_file = self.note_path(folder, title)

        if not note_file.exists():
            self.create_note(
                folder,
                title,
                ""
            )

        with open(
            note_file,
            "a",
            encoding="utf-8"
        ) as f:

            f.write("\n\n")
            f.write(content)

        print(f"Updated: {note_file}")

    def create_daily_note(self):

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        path = self.note_path(
            "Daily",
            today
        )

        if not path.exists():

            self.create_note(
                "Daily",
                today,
                f"# Daily Note — {today}\n"
            )

    def auto_link(
        self,
        text,
        concepts
    ):
        """
        Convert keywords into Obsidian wikilinks.
        """

        for concept in concepts:

            text = re.sub(
                rf"\b{re.escape(concept)}\b",
                f"[[{concept}]]",
                text,
                flags=re.IGNORECASE
            )

        return text


# =========================
# MAIN EXECUTION
# =========================

if __name__ == "__main__":

    obsidian = ObsidianConnector(
        VAULT_PATH
    )

    # Ensure today's note exists
    obsidian.create_daily_note()

    # =========================
    # RESEARCH CONTENT
    # =========================

    research = """
# Signal Garden + Obsidian Research

Signal Garden can maintain persistent research memory.

Obsidian works extremely well for markdown knowledge graphs.

AI agents benefit from long-term linked memory systems.

MCP servers allow AI agents to interface with:
- tools
- filesystems
- APIs
- databases
- external services

## Ideas

- Overnight autonomous research
- Voice capture pipelines
- Semantic memory retrieval
- AI-generated MOCs
- Persistent linked cognition

## Related

- MCP
- Signal Garden
- Obsidian
- AI agents
- Knowledge Graphs
"""

    linked = obsidian.auto_link(
        research,
        [
            "Signal Garden",
            "Obsidian",
            "MCP",
            "AI agents",
            "Knowledge Graphs"
        ]
    )

    # =========================
    # CREATE RESEARCH NOTE
    # =========================

    obsidian.create_note(
        folder="Research",
        title="Signal Garden Integration Test",
        content=linked,
        tags=[
            "signal-garden",
            "obsidian",
            "ai",
            "research"
        ]
    )

    # =========================
    # CREATE INBOX CAPTURE NOTE
    # =========================

    obsidian.create_note(
        folder="Inbox",
        title="Voice Capture",
        content="""
Need to research MCP workflows.

Ideas:
- Connect Signal Garden to Obsidian
- Add voice ingestion
- Explore overnight research agents
- Add semantic search
- Build autonomous synthesis
"""
    )

    # =========================
    # UPDATE DAILY NOTE
    # =========================

    obsidian.append_note(
        folder="Daily",
        title=datetime.now().strftime(
            "%Y-%m-%d"
        ),
        content="""
## Signal Garden Research Session

Created:
- Research note
- Inbox capture note

Explored:
- MCP workflows
- AI memory systems
- Obsidian graph structures
"""
    )

    print("\nDone.")
