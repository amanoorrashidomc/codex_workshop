from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# USER EDIT: set your PBIX file path
PBIX_PATH = Path("input/report.pbix")
# USER EDIT: set output folder
OUTPUT_FOLDER = Path("output")
# USER EDIT: set backup folder
BACKUP_FOLDER = Path("backup")
# USER EDIT: set work folder
WORK_FOLDER = Path("work")
# USER EDIT: text to find
FIND_TEXT = "OldValue"
# USER EDIT: replacement text
REPLACE_TEXT = "NewValue"
# USER EDIT: output artifact type (PBIT default)
OUTPUT_ARTIFACT_TYPE = "PBIT"  # allowed: PBIT or PBIX


@dataclass
class ReplacementSummary:
    files_scanned: int = 0
    files_changed: int = 0
    replacements_count: int = 0


def log(message: str) -> None:
    print(f"[INFO] {message}")


def warn(message: str) -> None:
    print(f"[WARNING] {message}")


def fail(message: str, next_step: str = "") -> None:
    print(f"[ERROR] {message}")
    if next_step:
        print(f"[NEXT STEP] {next_step}")
    raise SystemExit(1)


def check_pbix_exists(pbix_path: Path) -> None:
    if not pbix_path.exists():
        fail(
            f"PBIX file was not found: {pbix_path}",
            "Place your PBIX file at input/report.pbix or update PBIX_PATH at the top of app.py.",
        )


def ensure_pbi_tools_available() -> None:
    try:
        result = subprocess.run(
            ["pbi-tools", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        version = result.stdout.strip() or result.stderr.strip()
        log(f"pbi-tools detected: {version}")
    except FileNotFoundError:
        fail(
            "pbi-tools is not installed or not in your PATH.",
            "Install pbi-tools first, then run: pbi-tools --version",
        )
    except subprocess.CalledProcessError as exc:
        fail(
            "pbi-tools command failed.",
            f"Try running this manually: pbi-tools --version\nDetails: {exc.stderr.strip()}",
        )


def create_backup(pbix_path: Path, backup_folder: Path) -> Path:
    backup_folder.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_folder / f"{pbix_path.stem}_{timestamp}{pbix_path.suffix}"
    shutil.copy2(pbix_path, backup_path)
    log(f"Backup created: {backup_path}")
    return backup_path


def run_pbi_tools(command: list[str]) -> None:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print(result.stdout.strip())
    except subprocess.CalledProcessError as exc:
        details = exc.stderr.strip() or exc.stdout.strip() or "No extra details available."
        fail("pbi-tools command failed.", f"Command: {' '.join(command)}\nDetails: {details}")


def extract_pbix(pbix_path: Path, work_folder: Path) -> None:
    if work_folder.exists():
        shutil.rmtree(work_folder)
    work_folder.mkdir(parents=True, exist_ok=True)
    log("Extracting PBIX into the work folder...")
    run_pbi_tools(["pbi-tools", "extract", str(pbix_path), "-outPath", str(work_folder)])


def replace_text_in_json_files(base_folder: Path, find_text: str, replace_text: str, dry_run: bool) -> ReplacementSummary:
    summary = ReplacementSummary()

    for json_file in base_folder.rglob("*.json"):
        summary.files_scanned += 1
        content = json_file.read_text(encoding="utf-8")
        count = content.count(find_text)

        if count > 0:
            summary.files_changed += 1
            summary.replacements_count += count
            if not dry_run:
                json_file.write_text(content.replace(find_text, replace_text), encoding="utf-8")

    return summary


def build_artifact(work_folder: Path, output_folder: Path, artifact_type: str) -> Path:
    output_folder.mkdir(parents=True, exist_ok=True)
    artifact_type = artifact_type.upper()
    if artifact_type not in {"PBIT", "PBIX"}:
        fail("Invalid OUTPUT_ARTIFACT_TYPE.", "Use PBIT (default) or PBIX.")

    output_path = output_folder / f"rebuilt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{artifact_type.lower()}"
    log(f"Rebuilding output artifact ({artifact_type})...")
    run_pbi_tools(
        [
            "pbi-tools",
            "compile",
            str(work_folder),
            "-outPath",
            str(output_path),
        ]
    )
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safe PBIX text replacement workflow using pbi-tools.")
    parser.add_argument("--dry-run", action="store_true", help="Scan and report changes without writing files or building output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    log("Starting workflow...")
    check_pbix_exists(PBIX_PATH)
    ensure_pbi_tools_available()
    create_backup(PBIX_PATH, BACKUP_FOLDER)

    extract_pbix(PBIX_PATH, WORK_FOLDER)
    summary = replace_text_in_json_files(WORK_FOLDER, FIND_TEXT, REPLACE_TEXT, args.dry_run)

    if summary.replacements_count == 0:
        warn("No matching text was found in extracted JSON files.")

    output_path = None
    if args.dry_run:
        warn("Dry run enabled: skipping rebuild step.")
    else:
        output_path = build_artifact(WORK_FOLDER, OUTPUT_FOLDER, OUTPUT_ARTIFACT_TYPE)

    log("Workflow complete.")
    print("\n=== Summary ===")
    print(f"JSON files scanned: {summary.files_scanned}")
    print(f"JSON files changed: {summary.files_changed}")
    print(f"Total replacements: {summary.replacements_count}")
    print(f"Output artifact: {output_path if output_path else 'Not created (dry run)'}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        fail("Process canceled by user.", "Run the script again when ready.")
