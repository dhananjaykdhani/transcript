# 🛠️ Installation Guide — CBCS Transcription Pipeline

> Complete setup instructions for **macOS** and **Windows**. Follow every step in order.
> 
> **Jump to your OS:**
> - [🍎 macOS Installation](#-macos-installation)
> - [🪟 Windows Installation](#-windows-installation)

---

## 🍎 macOS Installation

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | macOS 11 Big Sur | macOS 13 Ventura or later |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 2 GB free | 5 GB free |
| **Internet** | Required | Stable broadband |
| **Python** | 3.9+ | 3.11+ |
| **CPU** | Intel or Apple Silicon | Apple Silicon M1/M2/M3 |

---

## Software You Need to Install

### Required Software

| Software | Purpose | Download |
|----------|---------|---------|
| **Homebrew** | macOS package manager | [brew.sh](https://brew.sh) |
| **Python 3** | Runtime for all scripts | Via Homebrew |
| **ffmpeg** | Audio format conversion | Via Homebrew |
| **Xcode Command Line Tools** | C compiler (needed for webrtcvad) | Via Terminal |
| **Antigravity IDE** | AI coding assistant | Provided separately |

### Required Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `google-genai` | latest | Gemini AI API |
| `webrtcvad` | 2.0.10+ | Voice Activity Detection |
| `scipy` | latest | Audio resampling |
| `numpy` | latest | Signal processing |
| `openpyxl` | latest | Excel read/write |

---

## Step-by-Step Installation

### STEP 1 — Install Xcode Command Line Tools

Open **Terminal** (press `Cmd+Space`, type "Terminal", press Enter).

```bash
xcode-select --install
```

A popup will appear — click **Install** and wait (~5 minutes). This installs gcc/clang which is needed to compile `webrtcvad`.

**Verify:**
```bash
xcode-select -p
# Should print: /Library/Developer/CommandLineTools
```

---

### STEP 2 — Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen prompts. At the end, it will tell you to run two commands to add brew to your PATH — **run those commands**.

**Verify:**
```bash
brew --version
# Should print: Homebrew 4.x.x
```

---

### STEP 3 — Install Python 3

```bash
brew install python@3.11
```

After install, make it the default:
```bash
echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Verify:**
```bash
python3 --version
# Should print: Python 3.11.x
```

---

### STEP 4 — Install ffmpeg

ffmpeg is used for audio format handling.

```bash
brew install ffmpeg
```

This may take 5-10 minutes.

**Verify:**
```bash
ffmpeg -version
# Should print: ffmpeg version 7.x.x ...
```

---

### STEP 5 — Set Up the Project Folder

Create or navigate to your project directory:

```bash
# Create the folder if it doesn't exist
mkdir -p /Users/$(whoami)/Desktop/Transcript
cd /Users/$(whoami)/Desktop/Transcript
```

Place these files in this folder (they should already be there if shared with you):
- `gemini_transcriber.py`
- `process_transcription.py`
- `transliterator.py`
- `CBCS_Audio File Anshu.xlsx` (reference template)

---

### STEP 6 — Create Python Virtual Environment

A virtual environment keeps all Python packages isolated so they don't conflict with other projects.

```bash
cd /Users/$(whoami)/Desktop/Transcript

# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

You should now see `(venv)` at the start of your terminal prompt.

> ⚠️ **Important:** You must activate the venv every time you open a new terminal window before running the scripts.

---

### STEP 7 — Install Python Packages

With the venv activated:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install google-genai openpyxl numpy webrtcvad scipy
```

**Expected output** (last few lines):
```
Successfully installed google-genai-1.x.x webrtcvad-2.0.10 scipy-1.x.x numpy-2.x.x openpyxl-3.x.x
```

**Verify each package:**
```bash
python3 -c "import webrtcvad; print('webrtcvad ✅')"
python3 -c "from google import genai; print('google-genai ✅')"
python3 -c "import numpy; print('numpy ✅')"
python3 -c "import scipy; print('scipy ✅')"
python3 -c "import openpyxl; print('openpyxl ✅')"
```

All should print ✅.

---

### STEP 8 — Configure the Gemini API Key

The pipeline reads your Gemini API Key securely from a `.env` file in the project folder.

1. Open or create the `.env` file in `/Users/dhananjaykdhani/Desktop/Transcript/`:
```bash
echo 'GEMINI_API_KEY="your-gemini-api-key-here"' > .env
```

2. The scripts automatically load this file using `python-dotenv`.
3. The `.env` file is protected by `.gitignore` so your secret key will never be committed to GitHub.

#### How to Get a Free/Paid API Key:
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API Key** → **Create API key**
3. Copy the key and paste it into `.env`


---

### STEP 9 — Place Your Audio Files

Your audio folder should be at:
```
/Users/dhananjaykdhani/Downloads/Data_s4_hindi_p3/recorded_audio_Chandan/
```

Expected structure:
```
recorded_audio_Chandan/
├── 1.wav
├── 1_1.wav
├── 2.wav
├── 2_1.wav
...
├── 46.wav
├── Ref_men/        ← Reference recordings (not processed)
└── Ref_nomen/      ← Reference recordings (not processed)
```

**Audio file format requirements:**
- Format: WAV (`.wav`)
- Sample rate: Any (script handles resampling)
- Channels: Mono or Stereo (auto-converted to mono)
- Bit depth: 16-bit PCM preferred

---

### STEP 10 — Test the Installation

Run a quick test on a single file to confirm everything works:

```bash
cd /Users/$(whoami)/Desktop/Transcript
source venv/bin/activate

python3 -c "
from gemini_transcriber import get_gemini_client, transcribe_audio_gemini, vad_onset_offset, rms_onset_offset


audio = '/Users/$(whoami)/Downloads/Data_s4_hindi_p3/recorded_audio_Chandan/1_1.wav'

# Test system layers
vad_on, vad_off = vad_onset_offset(audio)
rms_on, rms_off = rms_onset_offset(audio)
print(f'VAD onset: {vad_on}s  offset: {vad_off}s')
print(f'RMS onset: {rms_on}s  offset: {rms_off}s')

# Test AI layer
client = get_gemini_client()
res = transcribe_audio_gemini(client, audio, '1_1')
print(f'Fused onset: {res[\"onset\"]}s')
print(f'Transcript: {res[\"roman\"]}')
print('Installation OK ✅')
"
```

Expected output:
```
VAD onset: 0.82s  offset: 5.0s
RMS onset: 0.81s  offset: 4.72s
Fused onset: 0.81s
Transcript: Bhaagte hue naavik ko ek sipaahi pakadne ki koshish kar raha hai
Installation OK ✅
```

---

## Installing Antigravity IDE

### What is Antigravity?
Antigravity is an AI coding assistant that integrates directly into your code editor. It can:
- Read and understand your code files
- Write, edit, and debug scripts
- Run terminal commands on your behalf
- Process audio files and analyze data

### Installation Steps

1. **Install VS Code** (if not already installed):
   - Download from [code.visualstudio.com](https://code.visualstudio.com)
   - Drag to Applications folder

2. **Install the Antigravity Extension:**
   - Open VS Code
   - Press `Cmd+Shift+X` to open Extensions
   - Search for "Antigravity"
   - Click **Install**

3. **Sign In:**
   - Click the Antigravity icon in the sidebar
   - Follow the sign-in flow

4. **Open Your Project:**
   ```bash
   code /Users/$(whoami)/Desktop/Transcript
   ```

5. **Open Relevant Files:**
   Open all three Python scripts in tabs:
   - `gemini_transcriber.py`
   - `process_transcription.py`
   - `transliterator.py`

---

## Troubleshooting

### Problem: `webrtcvad` fails to install

**Error:** `error: command '/usr/bin/clang' failed with exit code 1`

**Fix:**
```bash
xcode-select --install
# After installation completes:
pip install webrtcvad
```

---

### Problem: `ModuleNotFoundError: No module named 'google'`

**Fix:** You forgot to activate the venv:
```bash
source venv/bin/activate
# Then run again
```

---

### Problem: `404 NOT_FOUND` — Gemini model not found

**Error:** `This model models/gemini-X.X-flash is no longer available`

**Fix:** Update the model name in `gemini_transcriber.py` line 128:
```python
GEMINI_MODEL = "models/gemini-3.8-flash"   # ← update this if needed
```

To find available models:
```bash
source venv/bin/activate
python3 -c "
from google import genai
c = genai.Client(api_key='YOUR_API_KEY')
for m in c.models.list():
    if 'flash' in m.name.lower():
        print(m.name)
"
```

---

### Problem: `VAD` returns 0.0 onset for all files

**Cause:** WebRTC VAD is picking up room noise as speech (usually a short burst in the first 100ms).

**Fix:** Already handled in the code — the `vad_onset_offset()` function filters speech runs shorter than 150ms. If still occurring, increase `MIN_SPEECH_MS` in `gemini_transcriber.py`:
```python
MIN_SPEECH_MS = 200   # increase from 150 to 200ms
```

---

### Problem: RMS onset is too early (noise trigger)

**Cause:** Background noise level is higher than usual, causing a low threshold.

**Fix:** Increase the threshold multiplier in `gemini_transcriber.py` in `rms_onset_offset()`:
```python
# Change from:
thresh = max(noise_floor * 8.0, noise_floor + 0.25 * (max_rms - noise_floor))
# To:
thresh = max(noise_floor * 12.0, noise_floor + 0.35 * (max_rms - noise_floor))
```

---

### Problem: API rate limit errors

**Error:** `429 RESOURCE_EXHAUSTED`

**Fix:** Reduce concurrency:
```bash
python3 process_transcription.py --workers 2
```

---

### Problem: Excel file won't open / is corrupted

**Fix:** Delete the output file and re-run:
```bash
rm "/Users/$(whoami)/Desktop/Transcript/CBCS_Audio File Chandan.xlsx"
python3 process_transcription.py
```

---

## Directory Structure After Full Installation

```
/Users/dhananjaykdhani/
├── Desktop/
│   └── Transcript/
│       ├── README.md                      ← Project overview
│       ├── user_guide.md                  ← This guide's companion
│       ├── installation_guide.md          ← This file
│       ├── gemini_transcriber.py          ← Core 3-layer engine
│       ├── process_transcription.py       ← Batch runner
│       ├── transliterator.py             ← Hindi→Roman converter
│       ├── CBCS_Audio File Anshu.xlsx    ← Reference template
│       ├── CBCS_Audio File Chandan.xlsx  ← Generated output ✨
│       └── venv/                         ← Python virtual environment
│           ├── bin/python3
│           ├── lib/site-packages/
│           │   ├── google/genai/
│           │   ├── webrtcvad/
│           │   ├── scipy/
│           │   ├── numpy/
│           │   └── openpyxl/
│           └── ...
│
└── Downloads/
    └── Data_s4_hindi_p3/
        └── recorded_audio_Chandan/
            ├── 1.wav
            ├── 1_1.wav
            └── ... (80 audio files)
```

---

## Quick Setup Script

If you need to set up on a new Mac, save this as `setup.sh` and run it:

```bash
#!/bin/bash
set -e

echo "🚀 CBCS Transcription Setup"

# 1. Install Homebrew (if not present)
if ! command -v brew &>/dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# 2. Install system dependencies
brew install python@3.11 ffmpeg

# 3. Create project directory
mkdir -p ~/Desktop/Transcript
cd ~/Desktop/Transcript

# 4. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
pip install --upgrade pip
pip install google-genai openpyxl numpy webrtcvad scipy

echo ""
echo "✅ Setup complete!"
echo "Next steps:"
echo "  1. Copy gemini_transcriber.py, process_transcription.py, transliterator.py to ~/Desktop/Transcript/"
echo "  2. Copy CBCS_Audio File Anshu.xlsx to ~/Desktop/Transcript/"
echo "  3. Place audio files in ~/Downloads/Data_s4_hindi_p3/recorded_audio_Chandan/"
echo "  4. Run: source venv/bin/activate && python3 process_transcription.py"
```

Run it:
```bash
chmod +x setup.sh
./setup.sh
```

---

*macOS section last updated: October 2026 | Tested on macOS Ventura + Apple Silicon M1*

---
---

## 🪟 Windows Installation

> **Shell used throughout this section:** PowerShell (run as **Administrator** where noted).
> Press `Win+S`, type `PowerShell`, right-click → **Run as Administrator**.

---

### Windows — System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 (64-bit, v1903+) | Windows 11 64-bit |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 3 GB free | 5 GB free |
| **Internet** | Required | Stable broadband |
| **Python** | 3.9+ | 3.11+ |
| **CPU** | x64 processor | Intel Core i5 / AMD Ryzen 5 |

---

### Windows — Software You Need

| Software | Purpose | Download |
|----------|---------|----------|
| **Python 3.11** | Runtime for all scripts | [python.org](https://www.python.org/downloads/) |
| **Microsoft C++ Build Tools** | Compile `webrtcvad` native extension | [visualstudio.microsoft.com](https://visualstudio.microsoft.com/visual-cpp-build-tools/) |
| **ffmpeg** | Audio format handling | [ffmpeg.org](https://ffmpeg.org/download.html) |
| **Git for Windows** | (Optional) Version control | [git-scm.com](https://git-scm.com) |
| **Antigravity IDE** | AI coding assistant | Provided separately |

---

### STEP W1 — Install Python 3.11

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click **Download Python 3.11.x** (the latest 3.11 release)
3. Run the installer
4. ⚠️ **CRITICAL** — On the first screen, check **"Add Python 3.11 to PATH"** before clicking Install
5. Click **Install Now**

**Verify (in a new PowerShell window):**
```powershell
python --version
# Should print: Python 3.11.x

pip --version
# Should print: pip 24.x.x from ...
```

If `python` is not found, add it manually:
```powershell
# Find where Python installed:
$env:USERPROFILE + "\AppData\Local\Programs\Python\Python311"

# Add to PATH permanently:
[System.Environment]::SetEnvironmentVariable(
  "Path",
  $env:Path + ";$env:USERPROFILE\AppData\Local\Programs\Python\Python311;$env:USERPROFILE\AppData\Local\Programs\Python\Python311\Scripts",
  "User"
)
# Then restart PowerShell
```

---

### STEP W2 — Install Microsoft C++ Build Tools

`webrtcvad` is a C extension and **must be compiled** on Windows. This step is mandatory.

1. Download **Build Tools for Visual Studio** from:
   [visualstudio.microsoft.com/visual-cpp-build-tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Run `vs_BuildTools.exe`
3. In the installer, select the **"Desktop development with C++"** workload
4. Make sure these are checked:
   - ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools
   - ✅ Windows 11 SDK (or Windows 10 SDK)
   - ✅ C++ CMake tools for Windows
5. Click **Install** (~3-5 GB download, 5-10 min)

**Verify (restart PowerShell first):**
```powershell
cl
# Should print: Microsoft (R) C/C++ Optimizing Compiler Version ...
# If not found, open a "Developer PowerShell for VS 2022" instead
```

---

### STEP W3 — Install ffmpeg

**Option A — Using winget (Windows 11 / modern Windows 10):**
```powershell
winget install ffmpeg
```

**Option B — Manual install:**
1. Go to [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Click **Windows** → **Windows builds by BtbN**
3. Download `ffmpeg-release-essentials.zip`
4. Extract to `C:\ffmpeg\`
5. Add to PATH:
```powershell
# Run as Administrator:
[System.Environment]::SetEnvironmentVariable(
  "Path",
  $env:Path + ";C:\ffmpeg\bin",
  "Machine"
)
```
6. Restart PowerShell

**Verify:**
```powershell
ffmpeg -version
# Should print: ffmpeg version 7.x.x ...
```

---

### STEP W4 — Set Up the Project Folder

Open PowerShell (normal, not Admin) and run:

```powershell
# Create project folder on Desktop
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Desktop\Transcript"
Set-Location "$env:USERPROFILE\Desktop\Transcript"
```

Copy these files into the folder (use File Explorer or the command below):
```
Transcript\
├── gemini_transcriber.py
├── process_transcription.py
├── transliterator.py
└── CBCS_Audio File Anshu.xlsx
```

---

### STEP W5 — Create Python Virtual Environment

```powershell
Set-Location "$env:USERPROFILE\Desktop\Transcript"

# Create the virtual environment
python -m venv venv

# Activate it
venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your prompt.

> ⚠️ **If you see a script execution error:**
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> # Then try activating again:
> venv\Scripts\Activate.ps1
> ```

> ⚠️ **Important:** Every time you open a new PowerShell window, you must activate the venv again:
> ```powershell
> cd $env:USERPROFILE\Desktop\Transcript
> venv\Scripts\Activate.ps1
> ```

---

### STEP W6 — Install Python Packages

With the venv activated:

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all required packages
pip install google-genai openpyxl numpy scipy webrtcvad
```

> ⚠️ **If `webrtcvad` fails with a compile error:**
> Make sure you completed Step W2 (Build Tools) and run this in the
> **"Developer PowerShell for VS 2022"** (search for it in Start Menu).
>
> Alternative — install the pre-built wheel:
> ```powershell
> pip install webrtcvad-wheels
> ```
> Then in `gemini_transcriber.py`, change `import webrtcvad` — it's the same API.

**Verify all packages:**
```powershell
python -c "import webrtcvad; print('webrtcvad OK')"
python -c "from google import genai; print('google-genai OK')"
python -c "import numpy; print('numpy OK')"
python -c "import scipy; print('scipy OK')"
python -c "import openpyxl; print('openpyxl OK')"
```

---

### STEP W7 — Update File Paths in the Script

> The default paths in `process_transcription.py` use macOS-style paths. Update them for Windows.

Open `process_transcription.py` in any text editor (Notepad, VS Code, etc.) and find lines ~199–203:

```python
# BEFORE (macOS paths):
parser.add_argument('--audio-dir',     default='/Users/dhananjaykdhani/Downloads/Data_s4_hindi_p3/recorded_audio_Chandan')
parser.add_argument('--output-excel',  default='/Users/dhananjaykdhani/Desktop/Transcript/CBCS_Audio File Chandan.xlsx')
parser.add_argument('--template',      default='/Users/dhananjaykdhani/Desktop/Transcript/CBCS_Audio File Anshu.xlsx')
```

Change them to your Windows paths (replace `YourName` with your actual Windows username):

```python
# AFTER (Windows paths):
parser.add_argument('--audio-dir',     default=r'C:\Users\YourName\Downloads\Data_s4_hindi_p3\recorded_audio_Chandan')
parser.add_argument('--output-excel',  default=r'C:\Users\YourName\Desktop\Transcript\CBCS_Audio File Chandan.xlsx')
parser.add_argument('--template',      default=r'C:\Users\YourName\Desktop\Transcript\CBCS_Audio File Anshu.xlsx')
```

Also update the PATH line at the top of `process_transcription.py` (line 12):
```python
# BEFORE:
os.environ['PATH'] = '/opt/homebrew/bin:' + os.environ.get('PATH', '')

# AFTER (Windows — ffmpeg is already in PATH from Step W3):
os.environ['PATH'] = r'C:\ffmpeg\bin;' + os.environ.get('PATH', '')
```

---

### STEP W8 — Configure Gemini API Key

The pipeline reads your Gemini API Key from a `.env` file in the project folder.

In PowerShell:
```powershell
Set-Location "$env:USERPROFILE\Desktop\Transcript"
Set-Content -Path ".env" -Value "GEMINI_API_KEY=your-gemini-api-key-here"
```

The script will automatically detect and load `.env`. You can also set a system environment variable:
```powershell
[System.Environment]::SetEnvironmentVariable(
  "GEMINI_API_KEY",
  "your-gemini-api-key-here",
  "User"
)
```

---

### STEP W9 — Place Your Audio Files

Place your `.wav` files at:
```
C:\Users\YourName\Downloads\Data_s4_hindi_p3\recorded_audio_Chandan\
├── 1.wav
├── 1_1.wav
├── 2.wav
...
└── 46.wav
```

Use **File Explorer** to create the folder and copy/paste the audio files there.

---

### STEP W10 — Test the Installation

```powershell
Set-Location "$env:USERPROFILE\Desktop\Transcript"
venv\Scripts\Activate.ps1

python -c "
from gemini_transcriber import vad_onset_offset, rms_onset_offset


audio = r'C:\\Users\\YourName\\Downloads\\Data_s4_hindi_p3\\recorded_audio_Chandan\\1_1.wav'
vad_on, vad_off = vad_onset_offset(audio)
rms_on, rms_off = rms_onset_offset(audio)
print(f'VAD onset: {vad_on}s  offset: {vad_off}s')
print(f'RMS onset: {rms_on}s  offset: {rms_off}s')
print('System layers OK')
"
```

---

### STEP W11 — Run the Full Pipeline

```powershell
Set-Location "$env:USERPROFILE\Desktop\Transcript"
venv\Scripts\Activate.ps1

python process_transcription.py
```

Or with explicit paths:
```powershell
python process_transcription.py `
  --audio-dir "C:\Users\YourName\Downloads\Data_s4_hindi_p3\recorded_audio_Chandan" `
  --output-excel "C:\Users\YourName\Desktop\Transcript\CBCS_Audio File Chandan.xlsx" `
  --template "C:\Users\YourName\Desktop\Transcript\CBCS_Audio File Anshu.xlsx" `
  --workers 4
```

Output Excel will be at:
```
C:\Users\YourName\Desktop\Transcript\CBCS_Audio File Chandan.xlsx
```

---

### Installing Antigravity IDE on Windows

1. **Install VS Code:**
   - Download from [code.visualstudio.com](https://code.visualstudio.com)
   - Run the installer — check **"Add to PATH"** during setup

2. **Install the Antigravity Extension:**
   - Open VS Code
   - Press `Ctrl+Shift+X` to open Extensions
   - Search for **"Antigravity"**
   - Click **Install**

3. **Sign In** via the sidebar

4. **Open Your Project:**
   ```powershell
   code "$env:USERPROFILE\Desktop\Transcript"
   ```

5. **Open Relevant Files** in tabs:
   - `gemini_transcriber.py`
   - `process_transcription.py`
   - `transliterator.py`

---

### Windows — Troubleshooting

#### Problem: `webrtcvad` fails to compile
```
error: Microsoft Visual C++ 14.0 or greater is required
```
**Fix:** Install Build Tools (Step W2). Then open **Developer PowerShell for VS 2022** and run pip install there.

Alternative with no compilation:
```powershell
pip install webrtcvad-wheels
```

---

#### Problem: `venv\Scripts\Activate.ps1 cannot be loaded`
```
...Activate.ps1 is not digitally signed
```
**Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

#### Problem: `python` not recognized
```
python : The term 'python' is not recognized
```
**Fix:** Python was installed without adding to PATH. Reinstall Python and check the **"Add Python to PATH"** box on the first screen.

Or add manually:
```powershell
$pyPath = "$env:USERPROFILE\AppData\Local\Programs\Python\Python311"
[System.Environment]::SetEnvironmentVariable("Path", "$env:Path;$pyPath;$pyPath\Scripts", "User")
# Restart PowerShell
```

---

#### Problem: `ffmpeg` not found
```
FileNotFoundError: ffmpeg not found
```
**Fix:** Ensure ffmpeg is in PATH (Step W3). Test with:
```powershell
ffmpeg -version
```
If not found, restart PowerShell after setting PATH, or log out and back in.

---

#### Problem: `404 NOT_FOUND` — Gemini model unavailable
**Fix:** Update model name in `gemini_transcriber.py`:
```powershell
# Find available models:
python -c "
from google import genai
c = genai.Client(api_key='YOUR_KEY')
for m in c.models.list():
    if 'flash' in m.name.lower(): print(m.name)
"
```
Then update line with `GEMINI_MODEL = "models/gemini-X.X-flash"` in `gemini_transcriber.py`.

---

#### Problem: Script runs but onset shows 0.0 for all files
**Cause:** `webrtcvad` may be running but resampling is off.
**Fix:** Verify scipy installed correctly:
```powershell
python -c "from scipy.signal import resample_poly; print('scipy OK')"
```

---

### Windows — Quick Setup Script

Save this as `setup_windows.ps1` on your Desktop and run it in **PowerShell as Administrator**:

```powershell
# CBCS Transcription — Windows Setup Script
# Run in PowerShell as Administrator

Write-Host "CBCS Transcription Windows Setup" -ForegroundColor Cyan

# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Install Python via winget (if not present)
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Python 3.11..." -ForegroundColor Yellow
    winget install Python.Python.3.11
}

# Install ffmpeg
Write-Host "Installing ffmpeg..." -ForegroundColor Yellow
winget install ffmpeg

# Create project folder
$ProjectDir = "$env:USERPROFILE\Desktop\Transcript"
New-Item -ItemType Directory -Force -Path $ProjectDir | Out-Null
Set-Location $ProjectDir

# Create and activate venv
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install packages
Write-Host "Installing Python packages..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install google-genai openpyxl numpy scipy

# Try webrtcvad, fall back to wheels
try {
    pip install webrtcvad
    Write-Host "webrtcvad compiled OK" -ForegroundColor Green
} catch {
    Write-Host "Trying pre-built webrtcvad..." -ForegroundColor Yellow
    pip install webrtcvad-wheels
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Next steps:"
Write-Host "  1. Copy Python scripts and CBCS xlsx to: $ProjectDir"
Write-Host "  2. Update paths in process_transcription.py for Windows"
Write-Host "  3. Place audio .wav files in Downloads\Data_s4_hindi_p3\recorded_audio_Chandan\"
Write-Host "  4. Run: .\venv\Scripts\Activate.ps1 then python process_transcription.py"
```

Run it:
```powershell
powershell -ExecutionPolicy Bypass -File setup_windows.ps1
```

---

### Windows — Directory Structure After Setup

```
C:\Users\YourName\
├── Desktop\
│   └── Transcript\
│       ├── README.md
│       ├── user_guide.md
│       ├── installation_guide.md
│       ├── gemini_transcriber.py
│       ├── process_transcription.py
│       ├── transliterator.py
│       ├── CBCS_Audio File Anshu.xlsx
│       ├── CBCS_Audio File Chandan.xlsx   ← Generated output ✨
│       └── venv\
│           ├── Scripts\
│           │   ├── python.exe
│           │   └── Activate.ps1
│           └── Lib\site-packages\
│               ├── google\genai\
│               ├── webrtcvad\
│               ├── scipy\
│               ├── numpy\
│               └── openpyxl\
│
└── Downloads\
    └── Data_s4_hindi_p3\
        └── recorded_audio_Chandan\
            ├── 1.wav
            ├── 1_1.wav
            └── ... (80 audio files)
```

---

*macOS section: Tested on macOS Ventura + Apple Silicon M1*
*Windows section: Tested on Windows 11 (x64) + Python 3.11*
*Last updated: October 2026*
