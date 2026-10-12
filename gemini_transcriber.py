"""
gemini_transcriber.py — CBCS Triple-Layer Hybrid Onset/Offset Detection
========================================================================

  LAYER 1: WebRTC VAD (Google C-library, 10ms frames, 16kHz)
    - Runs at aggressiveness=3 (strict)
    - Uses a "sustained speech" filter:
        * Skip any run of speech that lasts <200ms (transient noise)
        * The TRUE onset = first frame of the first sustained speech run
        * The TRUE offset = end of the last speech cluster

  LAYER 2: RMS Energy Envelope (5ms step, 20ms window)
    - 90th-percentile noise floor from first 500ms
    - Threshold: max(8× noise_floor, +25% dynamic range)
    - 3 consecutive frames required to confirm onset

  LAYER 3: Gemini AI (gemini-3.8-flash multimodal)
    - Full transcript with pauses, fumbles, Hindi+Roman
    - Also provides its own onset/offset estimate

  FUSION (rules, in priority order):
    1. If VAD and RMS agree within 200ms → mean of those two (system wins)
    2. If all three available → median
    3. Two available and close (<300ms) → mean
    4. Two available but diverge → smaller for onset, larger for offset
    5. Only one → use it
"""

import os, re, json, time, wave, struct
import numpy as np


# ─── LAYER 2: RMS Energy Envelope ─────────────────────────────────────────────

def rms_onset_offset(audio_path):
    """5ms-step RMS with 90th-pct noise floor and 3-frame confirmation."""
    try:
        with wave.open(audio_path, 'r') as w:
            sr  = w.getframerate()
            n   = w.getnframes()
            raw = w.readframes(n)
            ch  = w.getnchannels()
            sw  = w.getsampwidth()

        fmt = {1: 'b', 2: 'h', 4: 'i'}[sw]
        samples = np.array(struct.unpack(f'<{n*ch}{fmt}', raw), dtype=np.float32)
        if ch > 1:
            samples = samples.reshape(-1, ch).mean(axis=1)

        frame_len = int(0.020 * sr)
        step      = int(0.005 * sr)

        rms_arr, times_arr = [], []
        for i in range(0, len(samples) - frame_len, step):
            chunk = samples[i:i + frame_len]
            rms_arr.append(float(np.sqrt(np.mean(chunk ** 2))))
            times_arr.append(i / float(sr))

        rms_arr   = np.array(rms_arr)
        times_arr = np.array(times_arr)
        if len(rms_arr) == 0:
            return None, None

        noise_n     = max(1, int(0.5 / 0.005))
        noise_floor = np.percentile(rms_arr[:noise_n], 90)
        max_rms     = float(np.max(rms_arr))
        if max_rms <= noise_floor:
            return None, None

        thresh = max(noise_floor * 8.0, noise_floor + 0.25 * (max_rms - noise_floor))
        active = np.where(rms_arr > thresh)[0]
        if len(active) == 0:
            return None, None

        # 3-frame confirmation for onset
        onset_idx = None
        for k in range(len(active) - 2):
            if active[k+1] == active[k]+1 and active[k+2] == active[k]+2:
                onset_idx = active[k]
                break
        if onset_idx is None:
            onset_idx = active[0]

        onset  = float(times_arr[onset_idx])
        offset = float(times_arr[active[-1]]) + 0.020
        return round(onset, 3), round(offset, 3)
    except Exception as e:
        print(f"[RMS] Error: {e}")
        return None, None


# ─── LAYER 1: WebRTC VAD ──────────────────────────────────────────────────────

def _resample_to_16k(samples_f32, src_sr):
    """Resample float32 mono to int16 @ 16kHz."""
    if src_sr == 16000:
        return np.clip(samples_f32, -32768, 32767).astype(np.int16)
    try:
        from scipy.signal import resample_poly
        from math import gcd
        g = gcd(16000, src_sr)
        up, down = 16000 // g, src_sr // g
        resampled = resample_poly(samples_f32, up, down)
        return np.clip(resampled, -32768, 32767).astype(np.int16)
    except ImportError:
        ratio = src_sr / 16000
        idxs  = np.round(np.arange(0, len(samples_f32), ratio)).astype(int)
        idxs  = idxs[idxs < len(samples_f32)]
        return np.clip(samples_f32[idxs], -32768, 32767).astype(np.int16)


def _group_runs(speech_frames):
    """
    Group consecutive frame indices into runs.
    Returns list of (start_frame, end_frame) tuples.
    """
    if not speech_frames:
        return []
    runs = []
    run_start = speech_frames[0]
    prev = speech_frames[0]
    for f in speech_frames[1:]:
        if f == prev + 1:
            prev = f
        else:
            runs.append((run_start, prev))
            run_start = f
            prev = f
    runs.append((run_start, prev))
    return runs


def vad_onset_offset(audio_path, aggressiveness=3):
    """
    WebRTC VAD onset/offset with sustained-speech filtering.
    
    Key improvement over naive VAD:
    - Groups speech frames into 'runs'
    - Skips any run lasting < MIN_SPEECH_MS (filters noise transients)
    - TRUE onset = first frame of first sustained run
    - TRUE offset = end of last run
    """
    MIN_SPEECH_MS = 150   # ignore speech blobs shorter than 150ms
    FRAME_MS      = 10

    try:
        import webrtcvad
    except ImportError:
        return None, None

    try:
        with wave.open(audio_path, 'r') as w:
            sr  = w.getframerate()
            n   = w.getnframes()
            raw = w.readframes(n)
            ch  = w.getnchannels()
            sw  = w.getsampwidth()

        fmt = {1: 'b', 2: 'h', 4: 'i'}[sw]
        samples = np.array(struct.unpack(f'<{n*ch}{fmt}', raw), dtype=np.float32)
        if ch > 1:
            samples = samples.reshape(-1, ch).mean(axis=1)

        s16 = _resample_to_16k(samples, sr)
        SR_VAD    = 16000
        frame_len = SR_VAD * FRAME_MS // 1000   # 160 samples

        vad = webrtcvad.Vad(aggressiveness)
        speech_frames = []
        i = 0; fidx = 0
        while i + frame_len <= len(s16):
            fb = s16[i:i + frame_len].tobytes()
            try:
                is_speech = vad.is_speech(fb, SR_VAD)
            except Exception:
                is_speech = False
            if is_speech:
                speech_frames.append(fidx)
            i += frame_len
            fidx += 1

        if not speech_frames:
            return None, None

        # Group into runs, filter short bursts (noise)
        min_frames = MIN_SPEECH_MS // FRAME_MS   # 15 frames = 150ms
        runs = _group_runs(speech_frames)
        sustained = [(s, e) for s, e in runs if (e - s + 1) >= min_frames]

        if not sustained:
            # Fall back to longest run if none are sustained enough
            sustained = [max(runs, key=lambda r: r[1]-r[0])]

        onset  = round(sustained[0][0] * FRAME_MS / 1000.0, 3)
        offset = round((sustained[-1][1] + 1) * FRAME_MS / 1000.0, 3)
        return onset, offset

    except Exception as e:
        print(f"[VAD] Error: {e}")
        return None, None


# ─── LAYER 3: Gemini AI ───────────────────────────────────────────────────────

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

# gemini-flash-lite-latest = cheapest multimodal model with audio support.
# Pricing: $0.30 per 1M audio tokens (~10x cheaper than gemini-3.8-flash).
# Total batch of 80 audios costs only ~₹1 to ₹2 INR ($0.015 USD).
GEMINI_MODEL = "models/gemini-flash-lite-latest"

def get_gemini_client(api_key=None):
    from google import genai
    key = api_key or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not key:
        raise ValueError("GEMINI_API_KEY not found! Please set GEMINI_API_KEY in your .env file or environment.")
    return genai.Client(api_key=key)


def _gemini_transcribe_raw(client, audio_path, label, template_hint):
    from google.genai import types

    prompt = f"""You are an expert psycholinguist research assistant transcribing Hindi audio recordings from a CBCS sentence production picture description experiment.

Trial ID: {label}
Target Visual Stimulus Scene: {template_hint}

Listen carefully to the audio. Your job has THREE parts:

PART A — Transcription (most important):
1. Accuracy: 100% faithful to what the speaker actually says.
2. Pause & Hesitation Detection:
   - Insert "(with pause)" ONLY if there is a noticeable, prolonged silence strictly greater than 400 milliseconds (0.4s) mid-sentence where the speaker hesitates.
   - Do NOT insert "(with pause)" for fluent continuous speech, normal word boundaries, or natural brief breaths (<400ms).
   - Insert "(little fumble)" at false starts, stutters, or speech repairs (e.g. "Waitress (little fumble) aadmi ko laat maar rahi h").
3. Roman Hindi: Natural conversational Hinglish matching CBCS conventions (e.g. "Police tairak ka peecha kr rhi h", "Chef chor ko goli maar raha h", "Aadmi doctor ko mukka maar raha h").
4. Hindi (Devanagari): Exact Devanagari transcription.

PART B — Timing (secondary; be precise):
5. Onset: Seconds from audio start at which the FIRST spoken word begins. Ignore noise/silence before speech.
6. Offset: Seconds at which the LAST word ends.

PART C — Linguistic Analysis (based on the transcript you produce):
7. Patient Position:
   - "Right" : If Patient appears AFTER the Agent in the spoken sentence (canonical order: Agent...Patient...Verb).
   - "Left"  : If Patient appears BEFORE the Agent in the spoken sentence (e.g. Patient...Agent...Verb, or Patient...Agent ke dwara...Verb).
   - "NA"    : If spatial scene description (e.g. 'Teer taare ke dahini taraf hai') or no transitive patient.

   Example: "Ram Shyam ko maar raha hai" → Agent=Ram (1st), Patient=Shyam (2nd) → Patient Position = Right
   Example: "Shyam ko Ram maar raha hai" → Patient=Shyam (1st), Agent=Ram (2nd) → Patient Position = Left
   Example: "Chor ko police ke dwara pakda gaya" → Patient=Chor (1st), Agent=police (2nd) → Patient Position = Left

8. Sentence Structure:
   - "SOV"   : Subject then Object then Verb (when Patient is 'Right', e.g. "Ram Shyam ko maar raha hai")
   - "OSV"   : Object then Subject then Verb (when Patient is 'Left', e.g. "Shyam ko Ram maar raha hai" or "Nrataki ko nun ke dwara dhakka mara ja raha h")
   - "SVO"   : Subject then Verb then Object
   - "OVS"   : Object then Verb then Subject
   - "VSO"   : Verb then Subject then Object
   - "VOS"   : Verb then Object then Subject
   - "NA"    : If spatial scene description of shapes or incomplete utterance

Respond ONLY in valid JSON (no extra text):
{{
  "onset": 1.50,
  "offset": 5.80,
  "pause_detected": true,
  "hindi": "...",
  "roman": "...",
  "patient_position": "Right",
  "sentence_structure": "SOV"
}}
"""
    for attempt in range(3):
        try:
            with open(audio_path, 'rb') as f:
                audio_bytes = f.read()

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type='audio/wav'),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.05
                )
            )
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```(?:json)?", "", raw)
                raw = re.sub(r"```$",          "", raw).strip()
            return json.loads(raw)

        except Exception as e:
            time.sleep(1.0 + attempt)
            if attempt == 2:
                print(f"[Gemini] Error on {audio_path}: {e}")
    return None


# ─── FUSION ───────────────────────────────────────────────────────────────────

def _fuse(vad_v, rms_v, ai_v, mode="onset"):
    """
    Consensus fusion. See module docstring for rules.
    """
    vals = {
        'vad': vad_v if (vad_v is not None and vad_v > 0) else None,
        'rms': rms_v if (rms_v is not None and rms_v > 0) else None,
        'ai':  ai_v  if (ai_v  is not None and ai_v  > 0) else None,
    }
    avail = [v for v in vals.values() if v is not None]

    if not avail:
        return 0.0
    if len(avail) == 1:
        return round(avail[0], 2)

    # Rule 1: two system layers agree within 200ms → system wins
    if vals['vad'] is not None and vals['rms'] is not None:
        if abs(vals['vad'] - vals['rms']) <= 0.200:
            return round(float(np.mean([vals['vad'], vals['rms']])), 2)

    # Rule 2: all three → median
    if len(avail) == 3:
        return round(float(np.median(avail)), 2)

    # Rule 3/4: two available
    diff = abs(avail[0] - avail[1])
    if diff < 0.300:
        return round(float(np.mean(avail)), 2)
    return round(min(avail) if mode == "onset" else max(avail), 2)


# ─── PUBLIC API ──────────────────────────────────────────────────────────────

def calculate_precise_acoustic_onset(audio_path):
    """Returns (onset, offset) using system layers only (no AI)."""
    vad_on, vad_off = vad_onset_offset(audio_path)
    rms_on, rms_off = rms_onset_offset(audio_path)
    onset  = _fuse(vad_on, rms_on, None, "onset")
    offset = _fuse(vad_off, rms_off, None, "offset")
    return onset or None, offset or None


def classify_sentence_linguistics(sentence_roman, ai_struct='NA', ai_pos='NA'):
    """
    Determines Sentence Structure (SOV/OSV/NA) and Patient Position (Right/Left/NA)
    according to CBCS psycholinguistic experimental conventions.
    """
    if not sentence_roman or not sentence_roman.strip():
        return ai_struct or 'NA', ai_pos or 'NA'

    s = re.sub(r'\(.*?\)', '', sentence_roman.lower()).strip()
    s = re.sub(r'[.,;!?]', '', s)
    tokens = s.split()

    # 1. Spatial scene filler check (e.g. shapes and directions)
    spatial_markers = ['taraf', 'sthit', 'upar', 'neeche', 'dayi', 'bai', 'baaye', 'dahine', 'dayne', 'daya', 'baya', 'corner']
    spatial_shapes = ['teer', 'tara', 'tare', 'star', 'ashtad', 'var', 'varg', 'dil', 'triangle', 'trikon', 'fool', 'vastu', 'gend']
    has_marker = any(any(m in t for m in spatial_markers) for t in tokens)
    has_shape  = any(any(sh in t for sh in spatial_shapes) for t in tokens)
    if has_marker and has_shape:
        return 'NA', 'NA'

    # 2. Passive check ('ke dwara' / 'dwara')
    if 'dwara' in s or 'dwaara' in s:
        return 'OSV', 'Left'

    # 3. Animate entities in CBCS stimuli
    nouns = [
        'police', 'policeman', 'sipahi', 'siphahi', 'sainik',
        'nabik', 'naavik', 'naabhik', 'tairak',
        'bawarchi', 'rasoyia', 'chaf', 'chef',
        'aadmi', 'vyakti', 'ladka', 'gayak', 'kalakar', 'aatankwadi',
        'doctor', 'teacher', 'judge',
        'sadhu', 'nun', 'nan', 'nrataki', 'nartaki', 'nartak', 'aurat', 'mahila', 'ladki',
        'chor'
    ]

    ko_indices = [i for i, t in enumerate(tokens) if t == 'ko']
    if ko_indices:
        first_ko = ko_indices[0]
        nouns_before_ko = [t for t in tokens[:first_ko] if any(n in t for n in nouns)]
        nouns_after_ko  = [t for t in tokens[first_ko+1:] if any(n in t for n in nouns)]

        if len(nouns_before_ko) == 1 and len(nouns_after_ko) >= 1:
            return 'OSV', 'Left'
        elif len(nouns_before_ko) >= 2:
            return 'SOV', 'Right'
        elif len(nouns_after_ko) >= 1:
            return 'OSV', 'Left'
        elif len(nouns_before_ko) == 1 and len(nouns_after_ko) == 0:
            return 'SOV', 'Right'

    # Fallback to AI response
    if ai_struct not in ['NA', '']:
        struct = ai_struct
        pos = ai_pos
        if pos == 'Left' and struct == 'SOV': struct = 'OSV'
        elif pos == 'Right' and struct == 'OSV': struct = 'SOV'
        return struct, pos

    return 'SOV', 'Right'


def transcribe_audio_gemini(client, audio_path, label, template_hint=""):
    """
    Full hybrid transcription: VAD + RMS + Gemini, fused for best accuracy.
    Returns dict or None.
    """
    vad_on,  vad_off  = vad_onset_offset(audio_path)
    rms_on,  rms_off  = rms_onset_offset(audio_path)
    ai_data            = _gemini_transcribe_raw(client, audio_path, label, template_hint)

    ai_on  = float(ai_data.get('onset',  0)) if ai_data else None
    ai_off = float(ai_data.get('offset', 0)) if ai_data else None
    if ai_on  == 0.0: ai_on  = None
    if ai_off == 0.0: ai_off = None

    final_onset  = _fuse(vad_on, rms_on, ai_on,  "onset")
    final_offset = _fuse(vad_off, rms_off, ai_off, "offset")

    base = {
        'onset':      final_onset,
        'offset':     final_offset,
        # Debug: individual layer values
        'vad_onset':  round(vad_on,  3) if vad_on  is not None else None,
        'rms_onset':  round(rms_on,  3) if rms_on  is not None else None,
        'ai_onset':   round(ai_on,   3) if ai_on   is not None else None,
        'vad_offset': round(vad_off, 3) if vad_off is not None else None,
        'rms_offset': round(rms_off, 3) if rms_off is not None else None,
        'ai_offset':  round(ai_off,  3) if ai_off  is not None else None,
    }

    if ai_data:
        roman_txt = ai_data.get('roman', '')
        ai_st = ai_data.get('sentence_structure', 'NA')
        ai_po = ai_data.get('patient_position', 'NA')
        s_struct, p_pos = classify_sentence_linguistics(roman_txt, ai_st, ai_po)

        base.update({
            'pause_detected':     ai_data.get('pause_detected', False),
            'hindi':              ai_data.get('hindi', ''),
            'roman':              roman_txt,
            'sentence_structure': s_struct,
            'patient_position':   p_pos,
        })
    elif rms_on is not None or vad_on is not None:
        base.update({
            'pause_detected': False, 'hindi': '', 'roman': '',
            'sentence_structure': 'NA', 'patient_position': 'NA',
        })
    else:
        return None

    return base
