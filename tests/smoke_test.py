from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import replace_text_in_json_files


def test_key_folders_exist():
    for folder in ["input", "output", "backup", "work", "demo"]:
        assert Path(folder).exists(), f"Missing folder: {folder}"


def test_app_help_runs():
    import subprocess

    result = subprocess.run([sys.executable, "app.py", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "dry-run" in result.stdout


def test_replacement_function_with_sample_json(tmp_path: Path):
    sample = tmp_path / "example.json"
    sample.write_text('{"name":"OldValue","note":"OldValue"}', encoding="utf-8")

    summary = replace_text_in_json_files(tmp_path, "OldValue", "NewValue", dry_run=False)

    assert summary.files_scanned == 1
    assert summary.files_changed == 1
    assert summary.replacements_count == 2
    assert "NewValue" in sample.read_text(encoding="utf-8")
