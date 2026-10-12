# 🧠 Antigravity Workspace Memory & Guidelines — CBCS Transcription

> **Workspace Memory for Antigravity AI Assistants.**  
> Automatically loaded whenever any Antigravity agent operates in this repository.

---

## 🎯 1. Project Context & Objectives
This repository contains the **CBCS (Center for Behavioural and Cognitive Sciences) Audio Transcription & Linguistic Analysis Pipeline**.
It processes spoken Hindi audio recordings from psycholinguistic sentence-production picture-description experiments and outputs standardized, publication-ready Excel workbooks.

### Key Outputs:
1. **High-Precision Timing**: Exact speech onset and offset range (`onset - offset` in seconds) using acoustic signal analysis + AI consensus.
2. **Dual-Orthography Transcription**:
   - `Sentence `: Conversational Roman Hindi / Hinglish matching CBCS conventions (e.g. *"Police tairak ka peecha kr rhi h"*, *"Waitress chor ko laat maar rahi h"*).
   - `Sentence (Hindi)`: Exact Devanagari Hindi (e.g. *"पुलिस तैराक का पीछा कर रही है"*).
3. **Disfluency Detection**:
   - `(with pause)`: Mid-sentence hesitations or inter-word pauses.
   - `(little fumble)`: False starts, stuttering, or self-repairs.
4. **Linguistic Syntactic Analysis**:
   - `Sentence Structure`: Word order pattern (`SOV`, `OSV`, `SVO`, `NA`).
   - `Patient Position`: Position of the grammatical patient relative to the agent (`Right`, `Left`, `NA`).

---

## 🏗️ 2. Core Architecture: Triple-Layer Hybrid System
Do NOT rely on AI alone for audio timing. The pipeline combines three layers:

```
Audio (.wav)
   ├── Layer 1: WebRTC VAD (10ms frames, 16kHz, aggressiveness=3, min 150ms speech)
   ├── Layer 2: RMS Energy Envelope (5ms step, 20ms window, 90th-pct noise floor)
   └── Layer 3: Gemini Flash-Lite Multimodal (Audio content, text, pauses, fumbles)
          │
          ▼
   Consensus Fusion Engine:
   • If VAD and RMS agree within 200ms → Acoustic system mean wins (ground truth).
   • If all 3 available → Median value (immune to single outlier).
   • AI timing is secondary; acoustic waveform is primary.
```

---

## 💰 3. Cost & Model Selection Rules (CRITICAL)
- **Always use `models/gemini-flash-lite-latest`** (or `gemini-3.5-flash-lite`).
- **Never switch to `gemini-3.8-flash` or Pro models** without explicit confirmation from the user.
- **Cost Benchmark**:
  - `gemini-flash-lite-latest`: **$0.30 per 1M audio tokens** → Entire 80-file batch costs only **~₹1.20 INR ($0.014 USD)**.
  - Previous tests on `3.8-flash` cost ~₹70 INR because of premium multimodal rates. Flash-Lite is 10x cheaper and maintains excellent accuracy for Hindi transcription.

---

## 🔐 4. API Key & Security Standards
- **Never hardcode API keys in Python files, Markdown docs, or scripts.**
- The API key is stored in `.env` as:
  ```env
  GEMINI_API_KEY="your-api-key-here"
  ```
- Both `gemini_transcriber.py` and `process_transcription.py` load credentials automatically via `python-dotenv` (with an automatic line-by-line fallback reader).
- `.env` is listed in `.gitignore` and must **never** be included in git commits or zip archives.
- A clean template is provided in `.env.example`.

---

## 📊 5. Excel Schema Specification
The generated Excel file (e.g. `CBCS_Audio File Chandan.xlsx`) must strictly maintain these 10 columns:

| Col | Header | Format / Rule |
|:---:|:---|:---|
| **A** | `RECORDING_SESSION_LABEL` | Audio trial label (e.g. `1`, `1_1`, `2`, sorted naturally) |
| **B** | `INDEX` | Reserved |
| **C** | `Condition I` | Reserved |
| **D** | `Condition II` | Reserved |
| **E** | `Story` | Reserved |
| **F** | `Onset timing` | Format: `1.85 - 5.51` (seconds, 2 decimal places) |
| **G** | `Sentence ` | Roman Hindi (with `(with pause)` or `(little fumble)`) |
| **H** | `Sentence Structure` | `SOV` (canonical), `OSV` (fronted/passive), or `NA` |
| **I** | `Patient Position` | `Right` (Agent before Patient), `Left` (Patient before Agent), or `NA` |
| **J** | `Sentence (Hindi)` | Devanagari Hindi transcription |

### Linguistic Parsing Rules (`classify_sentence_linguistics`):
- **Agent**: The entity performing the action (e.g., *police, waitress, teacher, aadmi, chef, nun, rasoyia*).
- **Patient**: The entity receiving the action, typically marked with *ko* (e.g., *tairak ko, chor ko, doctor ko, ladki ko*).
- **Patient Position = `Right`**: Agent appears before Patient (e.g., *"Waitress chor ko laat maar rahi h"* → `SOV`, `Right`).
- **Patient Position = `Left`**: Patient appears before Agent (e.g., *"Bhagte hue navik ko ek sipahi pakadne ki koshish..."* or passives with *"dwara"* → `OSV`, `Left`).
- **Spatial Fillers = `NA`**: Non-action spatial descriptions of shapes (arrows, stars, squares, e.g. *"Teer taare ke dahini taraf hai"*) → `NA`, `NA`.

---

## 🚀 6. How to Run the Pipeline

### Standard Execution:
```bash
# 1. Activate environment
source venv/bin/activate  # macOS / Linux
# venv\Scripts\Activate.ps1  # Windows PowerShell

# 2. Run batch transcription
python3 process_transcription.py
```

### Custom Arguments:
```bash
python3 process_transcription.py \
  --audio-dir "/path/to/recorded_audio_folder" \
  --output-excel "CBCS_Audio File ParticipantName.xlsx" \
  --template "CBCS_Audio File Anshu.xlsx" \
  --workers 4
```

---

## 🛠️ 7. Key Files in Workspace
- `gemini_transcriber.py`: Core triple-layer acoustic & AI engine, consensus fusion, and syntactic classifier.
- `process_transcription.py`: Multithreaded batch processing script, naturally sorted trial sequencing, and Excel workbook generator.
- `transliterator.py`: Auxiliary transliteration utilities.
- `CBCS_Audio File Anshu.xlsx`: Experiment stimuli reference sheet.
- `CBCS_Audio File Chandan.xlsx`: Completed reference dataset (78 trials processed).
- `requirements.txt`: Python package dependencies.
- `user_guide.md`: Detailed end-user workflow instructions.
- `installation_guide.md`: Cross-platform setup guide for macOS and Windows.

---

## 🖥️ 8. Recommended IDE Extension
To open, inspect, and edit `.xlsx` workbooks directly inside Antigravity / VS Code:
- Recommend users install **`XLSX, CSV, TSV & Markdown Editor`** (by GrapeCity / MESCIUS) from the Extensions view (`Cmd+Shift+X` / `Ctrl+Shift+X`).
- This allows full visual spreadsheet preview inside the editor without external Microsoft Excel.

