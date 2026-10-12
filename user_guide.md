# 📖 User Guide — CBCS Transcription Pipeline

> How to use **Antigravity IDE**, tag files in chat, and run the full transcription workflow.

---

## Part 1: Using Antigravity IDE

Antigravity is an AI-powered coding assistant embedded in your IDE. Think of it as a senior developer + research assistant sitting next to you.

### 1.1 Opening the Chat Panel

- Click the **Antigravity icon** in your IDE sidebar (it looks like a chat bubble ✦)
- Or use the keyboard shortcut (usually `Cmd+Shift+A` on Mac)
- The chat panel opens on the right side of your screen

---

### 1.2 Tagging Files in the Chat (`@[...]` syntax)

The most powerful feature of Antigravity is **tagging files directly in your message**. This gives the AI full context about the file before you ask your question.

#### How to Tag a File

Type `@` in the chat input box and a file picker will appear. Select the file you want to reference.

```
@[/path/to/your/file.py]
```

Or type the `@` symbol and start typing the filename — autocomplete will show matching files.

#### Examples Used in This Project

```
@[/Users/dhananjaykdhani/Desktop/Transcript/CBCS_Audio File Anshu.xlsx]
here is the reference file, use it as the template for output

@[/Users/dhananjaykdhani/Downloads/Data_s4_hindi_p3/recorded_audio_Chandan]
here are the audio files to transcribe
```

> **Tip:** You can tag **multiple files** in a single message:
> ```
> @[file1.py] @[file2.xlsx] can you compare these two?
> ```

#### What you can tag:
| Tag Type | What it does |
|----------|-------------|
| `@[file.py]` | Shares the entire file content with the AI |
| `@[folder/]` | Shares the directory listing |
| `@[file.xlsx]` | For Excel files, AI reads the structure and data |
| `@[audio_folder/]` | Shows AI what audio files are available |

---

### 1.3 Good Prompting Practices with Antigravity

**Be specific about your expected output:**
```
❌ Bad:  "transcribe the audio"
✅ Good: "@[audio_folder] transcribe all .wav files and output an Excel matching 
         the format in @[CBCS_Audio File Anshu.xlsx] — include onset timing, 
         Roman Hindi, and Devanagari columns"
```

**Reference existing files when asking for improvements:**
```
"the onset timing in @[CBCS_Audio File Chandan.xlsx] column F is off — 
 the actual speech starts at 1.26s but it shows 0.47s. Fix the detection."
```

**Ask for explanations:**
```
"explain why the VAD layer is returning 0.0 for onset on the first file"
```

---

### 1.5 Recommended IDE Extension: View Excel Files in the IDE

To preview and inspect the output `.xlsx` files directly inside your IDE without switching to Microsoft Excel:

1. Open the Extensions view (`Cmd+Shift+X` on Mac / `Ctrl+Shift+X` on Windows).
2. Search for: **`XLSX, CSV, TSV & Markdown Editor`** (by GrapeCity / MESCIUS).
3. Click **Install**.
4. Once installed, simply click on `CBCS_Audio File Chandan.xlsx` in your file tree, and it will open directly inside the IDE as an interactive spreadsheet with full formatting!

---

## Part 2: Running the Transcription

### 2.1 Step-by-Step Workflow

#### Step 1: Prepare Your Audio Files

Organize your `.wav` files in a folder. The naming convention expected:

```
recorded_audio_Chandan/
├── 1.wav          ← Trial 1 (normal condition)
├── 1_1.wav        ← Trial 1 repeat / alternate
├── 2.wav
├── 2_1.wav
...
├── 46.wav
└── Ref_men/       ← Reference recordings (not processed)
    └── Ref_nomen/
```

> **Important:** Files are processed in **natural sort order**: 1, 1_1, 2, 2_1, 3, ... 10, 10_1 (not 1, 10, 11...)

#### Step 2: Activate the Virtual Environment

```bash
cd /Users/dhananjaykdhani/Desktop/Transcript
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

#### Step 3: Run the Pipeline

**Default (uses built-in paths):**
```bash
python3 process_transcription.py
```

**Custom paths:**
```bash
python3 process_transcription.py \
  --audio-dir /path/to/your/audio/folder \
  --output-excel /path/to/output.xlsx \
  --template /path/to/reference.xlsx \
  --workers 4
```

#### Step 4: Monitor Progress

The terminal shows real-time progress:
```
[  1/80] 1.wav      | 1.21 - 5.58   | 8.23s  | Bhaagte hue naavik ko (with pause)...
[  2/80] 1_1.wav    | 0.81 - 4.86   | 6.11s  | Bhaagte hue naavik ko ek sipaahi...
```

- **Column 1**: `[file_number/total]` and filename
- **Column 2**: `onset - offset` in seconds
- **Column 3**: Processing time per file
- **Column 4**: Transcription preview

#### Step 5: Open the Output

The Excel file is saved at:
```
/Users/dhananjaykdhani/Desktop/Transcript/CBCS_Audio File Chandan.xlsx
```

Open it in Excel or Numbers. Fill in the remaining columns:
- **B (INDEX)**: Trial number
- **C (Condition I)**: e.g., Active / Passive
- **D (Condition II)**: e.g., Canonical / Non-canonical
- **E (Story)**: Stimulus scene description
- **H (Sentence Structure)**: e.g., SVO, OVS
- **I (Patient Position)**: e.g., Post-verbal, Pre-verbal

---

### 2.2 Command-Line Options Reference

```bash
python3 process_transcription.py --help
```

| Option | Default | Description |
|--------|---------|-------------|
| `--audio-dir` | `Downloads/...Chandan` | Folder with `.wav` files |
| `--output-excel` | `Desktop/...Chandan.xlsx` | Where to save the output |
| `--template` | `Desktop/...Anshu.xlsx` | Reference template file |
| `--gemini-api-key` | Built-in | Your Gemini API key |
| `--workers` | `4` | Concurrent threads (1-8) |

---

### 2.3 Understanding the Output

#### Onset Timing Column (Column F)
Format: `ONSET - OFFSET` (both in seconds from start of audio)

```
1.21 - 5.58
```
This means:
- Speaker started talking at **1.21 seconds** into the recording
- Speaker stopped at **5.58 seconds**
- Speech duration = **4.37 seconds**

#### Pause Annotations
In the Sentence column, you'll see inline annotations:

| Annotation | Meaning |
|-----------|---------|
| `(with pause)` | Speaker paused between words at this position |
| `(little fumble)` | False start, self-correction, or word stumble |

#### Examples:
```
Bhaagte hue naavik ko (with pause) ek sipahi pakadne ki koshish kar raha
                       ↑ speaker paused here before continuing

Ek (little fumble) sainik ek naavik ko mukka maar raha hai
    ↑ speaker stumbled or self-corrected here
```

---

### 2.4 How the Triple-Layer System Decides Timing

For each audio file, **three independent systems** run simultaneously:

```
🔵 WebRTC VAD    │ onset=1.21  offset=5.58
🟢 RMS Energy    │ onset=1.86  offset=5.07
🤖 Gemini AI     │ onset=1.82  offset=5.54
                 │
    Fusion: VAD=1.21 vs RMS=1.86 → differ by 0.65s (>200ms)
            All three available → MEDIAN([1.21, 1.82, 1.86]) = 1.82
                 │
         Final: onset=1.82  ✅
```

The system **always explains its decision** in the terminal output. If you see `[VAD]` or `[RMS]` error messages, those layers failed gracefully and the other layers compensated.

---

### 2.5 Handling Special Cases

#### If a file returns "Error" in onset timing:
The audio may be silent, corrupted, or too quiet. Check the file:
```bash
source venv/bin/activate
python3 -c "
import wave
with wave.open('path/to/file.wav', 'r') as w:
    print('Duration:', w.getnframes() / w.getframerate(), 'seconds')
    print('Channels:', w.getnchannels())
    print('Sample rate:', w.getframerate())
"
```

#### If you want to re-run just one file:
```python
# In Python interactive shell:
cd /Users/dhananjaykdhani/Desktop/Transcript
source venv/bin/activate
python3 -c "
import os
os.environ['GEMINI_API_KEY'] = 'YOUR_KEY_HERE'
from gemini_transcriber import get_gemini_client, transcribe_audio_gemini

client = get_gemini_client()
res = transcribe_audio_gemini(client, '/path/to/file.wav', '1_1')
print(res)
"
```

#### Adjusting concurrency:
- Start with `--workers 4` (default)
- If you get API rate limit errors, reduce to `--workers 2`
- If your machine is powerful and API allows, try `--workers 6`

---

### 2.6 Telling Antigravity to Fix Problems

If you find issues with the output, **tag the Excel file and describe the problem**:

```
@[/Desktop/Transcript/CBCS_Audio File Chandan.xlsx]
The onset timing for file 35.wav shows 3.90 - 6.01 but listening to it, 
the speech actually starts around 2.5s. Fix the threshold or detection logic.
```

Or if transcript quality is wrong:

```
@[/Desktop/Transcript/gemini_transcriber.py]
The Gemini model is sometimes transcribing reference sentences instead of 
what the speaker actually said. Improve the prompt to prevent this.
```

---

## Part 3: Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│           CBCS TRANSCRIPTION — QUICK REFERENCE       │
├─────────────────────────────────────────────────────┤
│  ACTIVATE ENV:  source venv/bin/activate             │
│  RUN PIPELINE:  python3 process_transcription.py     │
│  OUTPUT FILE:   CBCS_Audio File Chandan.xlsx         │
├─────────────────────────────────────────────────────┤
│  TAG FILES IN CHAT:  @[/path/to/file]               │
│  SHOW PROGRESS:  Watch terminal during run           │
│  OUTPUT FORMAT:  Label | Onset-Offset | Sentence     │
├─────────────────────────────────────────────────────┤
│  PAUSES:         "(with pause)" in sentence column   │
│  FUMBLES:        "(little fumble)" in sentence       │
│  TIMING UNIT:    Seconds from start of audio         │
└─────────────────────────────────────────────────────┘
```
