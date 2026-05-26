from pathlib import Path
import argparse
import os
import subprocess
import sys


PROJECT_PATH = Path(__file__).resolve().parent


def script_path(name):
    return PROJECT_PATH / name


def run_python(script, args):
    command = [sys.executable, str(script_path(script)), *args]
    return subprocess.call(command, cwd=PROJECT_PATH)


def add_common_path_args(parser):
    parser.add_argument("--vault", help="Obsidian vault path. Overrides SIGNAL_GARDEN_VAULT_PATH.")
    parser.add_argument("--config", help="areas.json path. Overrides SIGNAL_GARDEN_CONFIG_PATH.")


def apply_env_overrides(args):
    env_updates = {}
    if getattr(args, "vault", None):
        env_updates["SIGNAL_GARDEN_VAULT_PATH"] = args.vault
    if getattr(args, "config", None):
        env_updates["SIGNAL_GARDEN_CONFIG_PATH"] = args.config
    os.environ.update(env_updates)


def command_run(args):
    apply_env_overrides(args)
    forwarded = []
    if args.test_email:
        forwarded.append("--test-email")
    return run_python("research_agent.py", forwarded)


def command_validate(args):
    forwarded = []
    if args.vault:
        forwarded.extend(["--vault", args.vault])
    if args.config:
        forwarded.extend(["--config", args.config])
    return run_python("validate_signal_garden.py", forwarded)


def command_repair(args):
    forwarded = []
    if args.apply:
        forwarded.append("--apply")
    if args.vault:
        forwarded.extend(["--vault", args.vault])
    return run_python("repair_signal_garden.py", forwarded)


def command_podcast(args):
    apply_env_overrides(args)
    return run_python("monitor_open_notebook_podcast.py", [])


def command_upload(args):
    apply_env_overrides(args)
    forwarded = []
    if args.latest:
        forwarded.append("--latest")
    forwarded.extend(args.paths)
    return run_python("upload_drive_artifacts.py", forwarded)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="signal-garden",
        description="Signal Garden command line interface."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the research agent.")
    add_common_path_args(run_parser)
    run_parser.add_argument("--test-email", action="store_true", help="Send a test email without a full research run.")
    run_parser.set_defaults(func=command_run)

    validate_parser = subparsers.add_parser("validate", help="Validate semantic state and artifacts.")
    add_common_path_args(validate_parser)
    validate_parser.set_defaults(func=command_validate)

    repair_parser = subparsers.add_parser("repair", help="Repair lightweight semantic state.")
    repair_parser.add_argument("--vault", help="Obsidian vault path. Overrides SIGNAL_GARDEN_VAULT_PATH.")
    repair_parser.add_argument("--apply", action="store_true", help="Write repairs instead of dry-running.")
    repair_parser.set_defaults(func=command_repair)

    podcast_parser = subparsers.add_parser("podcast", help="Poll Open Notebook podcast status and download audio when ready.")
    podcast_parser.add_argument("--vault", help="Obsidian vault path. Overrides SIGNAL_GARDEN_VAULT_PATH.")
    podcast_parser.set_defaults(func=command_podcast)

    upload_parser = subparsers.add_parser("upload", help="Upload report artifacts through the configured Drive integration.")
    upload_parser.add_argument("paths", nargs="*", help="Specific artifacts to upload.")
    upload_parser.add_argument("--vault", help="Obsidian vault path. Overrides SIGNAL_GARDEN_VAULT_PATH.")
    upload_parser.add_argument("--latest", action="store_true", help="Upload the latest daily PDF and podcast MP3.")
    upload_parser.set_defaults(func=command_upload)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
