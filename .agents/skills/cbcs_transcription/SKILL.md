---
name: cbcs_transcription
description: Expert skill for executing, troubleshooting, and extending the CBCS Hindi psycholinguistic audio transcription and acoustic timing pipeline.
---

# CBCS Audio Transcription Pipeline Skill

## Purpose
This skill equips the Antigravity agent to operate the CBCS (Center for Behavioural and Cognitive Sciences) audio transcription pipeline with high accuracy and low cost.

## Quick Workflow

### 1. Verification of Environment
Before running transcription:
1. Ensure virtual environment is activated: `source venv/bin/activate` (or `venv\Scripts\Activate.ps1` on Windows).
2. Ensure `.env` exists with `GEMINI_API_KEY="your-key"`. If not, create from `.env.example`.
3. Confirm `webrtcvad`, `scipy`, `numpy`, `openpyxl`, `google-genai`, and `python-dotenv` are installed.

### 2. Processing a Participant
To run transcription on a participant's audio folder:
```bash
python3 process_transcription.py \
  --audio-dir "/path/to/recorded_audio_folder" \
  --output-excel "CBCS_Audio File <Name>.xlsx" \
  --template "CBCS_Audio File Anshu.xlsx" \
  --workers 4
```

### 3. Cost Control Rule
- The model in `gemini_transcriber.py` is locked to `models/gemini-flash-lite-latest`.
- Never switch to larger preview models (e.g. `gemini-3.8-flash` or Pro) because they incur ~10x higher multimodal audio token costs.
- The cost per 80 recordings must remain under **~₹1.50 INR ($0.015 USD)**.

### 4. Linguistic Column Rules
When modifying or reviewing outputs:
- **`Sentence Structure`**:
  - `SOV`: Canonical Hindi order (Subject...Object...Verb).
  - `OSV`: Fronted object / Patient first (e.g. *"Bhagte hue navik ko ek sipahi pakadne ki koshish..."* or passive with *"dwara"*).
  - `NA`: Spatial filler trials (arrows, stars, shapes).
- **`Patient Position`**:
  - `Right`: Patient appears AFTER the Agent.
  - `Left`: Patient appears BEFORE the Agent.
  - `NA`: Inanimate spatial descriptions or no transitive patient.

### 5. Acoustic Timing Rules
- Never use AI-only timestamps. The acoustic ground truth is derived from **Layer 1 (WebRTC VAD)** + **Layer 2 (RMS Energy Envelope)**.
- If VAD and RMS agree within 200ms, the system mean is used.
- Gemini AI timing is used only as a secondary validator in consensus fusion.
