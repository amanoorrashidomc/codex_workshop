# Beginner PBIX Text Replace Tool (Local + Safe)

## 1) What this app does
This tiny Python app helps you safely update text inside a Power BI report package:
1. Takes your `.pbix` file
2. Uses `pbi-tools` to extract files
3. Finds and replaces text in extracted `.json` files
4. Rebuilds an output artifact (default: `.pbit`)
5. Keeps your original `.pbix` untouched
6. Creates a timestamped backup before doing any work

## 2) What file you need
You need one **Power BI PBIX file** (for example: `report.pbix`).

## 3) Where to place your PBIX file
Put your file here:

```text
input/report.pbix
```

You can also change this path at the top of `app.py`.

## 4) Step-by-step setup

### Step A: Create a virtual environment
```bash
python -m venv .venv
```

### Step B: Activate it
- **Windows (PowerShell)**
  ```bash
  .venv\Scripts\Activate.ps1
  ```
- **macOS/Linux**
  ```bash
  source .venv/bin/activate
  ```

### Step C: Install requirements
```bash
pip install -r requirements.txt
```

### Step D: Install pbi-tools (separate from Python)
This project calls `pbi-tools` from your terminal.

After installing `pbi-tools`, verify it with:
```bash
pbi-tools --version
```

> If this command fails, install/fix `pbi-tools` first.

### Step E: Run the script
```bash
python app.py
```

Optional safe preview (no file edits in work folder, no rebuild):
```bash
python app.py --dry-run
```

## 5) What output to expect
The app prints simple logs in plain English and a final summary:
- JSON files scanned
- JSON files changed
- Total replacement count
- Final output artifact path

## 6) Where output files appear
- **Backup copy** of original PBIX: `backup/`
- **Extracted working files**: `work/`
- **Rebuilt artifact** (`.pbit` by default): `output/`

## 7) How to run the demo notebook
Open notebook:
```bash
jupyter notebook demo/demo_workflow.ipynb
```

The notebook includes a simulated workflow using:
`demo/sample_data/extracted_mock/example.json`

## 8) Exactly 3 common mistakes + fixes
1. **Mistake:** `PBIX file was not found`
   - **Fix:** Put your file at `input/report.pbix` or edit `PBIX_PATH` in `app.py`.

2. **Mistake:** `pbi-tools` command not found
   - **Fix:** Install `pbi-tools` and verify with `pbi-tools --version`.

3. **Mistake:** Script runs but shows `No matching text was found`
   - **Fix:** Update `FIND_TEXT` in `app.py` to text that actually exists in extracted JSON.

## 9) Beginner note about safety
- Original `.pbix` is **never overwritten** by default.
- A timestamped backup is always created before extraction.
- This tool is local-only (no cloud, no database, no authentication).
