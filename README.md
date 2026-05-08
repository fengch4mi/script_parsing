# Game Script Parsing

Parse game scripts for character quotes and optionally analyze them with Gemini.

## Requirements

- Python 3.10+ recommended (tested with a local venv)
- `google-generativeai` (only for analysis)

## Setup

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install google-generativeai
```

You can also run dockerfile

```powershell
docker compose up --build
```

## Quote Extraction

Run the quote finder and point it to a script file:

```powershell
python scrap.py
```

Run the quote finder and point it to a script file with GUI for easier use:

```powershell
python ui.py
```

Prompts:

- Script filename (example: `script_1.txt` or `script_2.txt`)
- Character name
- Search mode:
  - Line: single lines containing the name
  - Paragraph: full paragraphs containing the name
  - Dialogue: blocks in `Name: text` format

When saving results, the script suggests a safe default filename that includes the script name and character name. It will auto-pick a unique name if the default already exists.

## Character Analysis (Gemini)

Analyze a character using a quotes `.txt` file:

```powershell
python chara_analysis.py
```

Prompts:

- Google API key (or set `GOOGLE_API_KEY`)
- Character name
- Quotes file path (must be `.txt`)

Output is saved as `{character}_gemini_analysis.txt` in the current folder.

### Model selection

By default the analyzer uses `gemini-1.5-flash`. You can override it with:

```powershell
$env:GEMINI_MODEL = "gemini-1.5-pro"
```

### NOTE

In this particular project, i use Google's Gemini API Key. But, you can also use other Gen AI API Keys with specified model via GUI

## Example Workflow

1. Extract quotes from `script_1.txt` and save them.
2. Extract quotes from `script_2.txt` for the same character; a unique filename is created automatically.
3. Run `chara_analysis.py` and point it to the quotes file you want to analyze.

## Files

- [scrap.py](scrap.py) - Quote finder
- [chara_analysis.py](chara_analysis.py) - AI character analyzer
- [ui.py](ui.py) - GUI for easier use
