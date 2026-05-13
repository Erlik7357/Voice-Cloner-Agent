# Voice Cloner Setup & Test Guide

## Runtime Tracks

- Default modern track: `backend/requirements.txt` -> `backend/requirements_modern.txt`
- Legacy fallback track: `backend/requirements_legacy.txt`
- Windows note for legacy: Microsoft Visual C++ Build Tools 14+ may be required

## 📋 Project Overview

Local MVP voice cloning pipeline for Madara Uchiha character. Generate cloned voice audio from text without API keys—100% local processing.

**Architecture:**
- **Backend**: Python XTTS v2 (voice cloning engine)
- **Voice Source**: Local WAV file (10-60 second reference sample)
- **Output**: Generated WAV audio file
- **Status**: Ready for testing & integration

---

## 🚀 Quick Start (5 minutes)

### 1️⃣ Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**First-time setup note:** TTS model will download (~2GB) on first run—this is normal.

### 2️⃣ Prepare Madara Voice Sample

You need a reference voice clip (10-60 seconds of Madara Uchiha):

1. **Get the sample:**
   - YouTube: Extract audio from anime clip featuring Madara's voice
   - Audio library: Find high-quality Madara voice sample
   - Format: WAV or MP3

2. **Save to project:**
   ```
   voice_samples/madara_uchiha_sample.wav
   ```

3. **Quality tips:**
   - Clean audio (minimal background noise)
   - Consistent speaking speed
   - 30-60 seconds ideal for best results

### 3️⃣ Run the Test Pipeline

```bash
python test_madara.py
```

**What it does:**
- ✅ Verifies voice sample exists
- ✅ Initializes TTS model
- ✅ Generates speech from 1-minute script
- ✅ Saves output to `output/madara_test_output.wav`
- ✅ Provides quality assessment checklist

**Expected runtime:**
- First run: 2-5 minutes (model downloads/initializes)
- Subsequent runs: 30-60 seconds (cached models)

---

## 🎤 Voice Generation Pipeline

### How It Works

```
Reference Voice Sample (10-60 sec)
           ↓
    [XTTS v2 Model]
           ↓
    Voice Embedding
           ↓
    + Your Text
           ↓
   [Synthesis Engine]
           ↓
   Generated Audio
```

### Key Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Model | XTTS v2 | Multi-lingual, emotion-aware |
| Language | English (en) | Can support 13+ languages |
| Max text | 500 chars | Per generation request |
| Min voice sample | 6 seconds | 30-60 sec recommended |
| Output format | WAV | 24kHz sample rate |

---

## 🔧 Advanced Usage

### Running the API Server

```bash
cd backend
python tts_server.py
```

**Endpoints:**
- `GET /health` - Server status
- `GET /characters` - Available characters
- `GET /setup-status` - Voice sample setup check
- `POST /generate` - Generate speech

**Example request:**
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "I am Madara Uchiha", "character": "madara"}' \
  --output madara_speech.wav
```

### Using the Voice Cloner Class

```python
from voice_cloner import VoiceCloner

cloner = VoiceCloner(gpu=True)  # Set False for CPU-only
cloner.clone_voice(
    reference_audio_path='voice_samples/madara_uchiha_sample.wav',
    text='Your dialogue here',
    output_path='output/my_audio.wav',
    language='en'
)
```

---

## 📊 Quality Assessment

### Listen For:

✅ **Good Quality Indicators:**
- Clear, understandable speech
- Natural intonation and pacing
- Consistent voice characteristics
- Minimal artifacts or distortion
- Recognizable as Madara Uchiha

❌ **Poor Quality Red Flags:**
- Robotic or unnatural sounding
- Inconsistent pitch/tone
- Audio dropouts or artifacts
- Difficult to understand words
- Sounds nothing like reference voice

### If Quality Is Poor:

1. **Try different reference audio:**
   - Longer sample (45-60 sec)
   - Different scene/dialogue from anime
   - Higher audio quality (no compression)

2. **Check hardware:**
   - GPU availability (CUDA for NVIDIA)
   - System RAM (8GB+ recommended)
   - Disk space for models (~2GB)

3. **Adjust parameters:**
   - Try different language setting
   - Experiment with reference audio length

---

## 📁 Project Structure

```
voice_cloner/
├── backend/
│   ├── voice_cloner.py        # Main TTS pipeline
│   ├── tts_server.py          # Flask API server
│   ├── requirements.txt       # Python dependencies
│   └── models/                # Downloaded TTS models (auto-created)
├── voice_samples/
│   └── madara_uchiha_sample.wav  # Your reference voice
├── output/
│   ├── madara_test_output.wav    # Test output
│   └── cache/                     # Generated audio cache
├── test_madara.py             # Test script runner
├── requirements.md            # Project requirements
└── implementation-plan.md     # Development roadmap
```

---

## ⚡ Performance Optimization

### GPU Acceleration (Recommended)

If you have an NVIDIA GPU:

```bash
# Install CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Then set `gpu=True` in voice cloner.

### CPU-Only Mode

No GPU? No problem:

```python
cloner = VoiceCloner(gpu=False)
```

Trade-off: ~3-5x slower, but no GPU needed.

---

## 🐛 Troubleshooting

### Issue: Model download fails
**Solution:** Check internet connection, disk space (need ~2GB)

### Issue: CUDA not found
**Solution:** Either install CUDA or use CPU mode (`gpu=False`)

### Issue: Audio quality is poor
**Solution:** Use longer, cleaner reference sample (45-60 sec, minimal noise)

### Issue: Script hangs on first run
**Solution:** Normal—model is downloading. Wait 5-10 minutes.

### Issue: "Voice sample not found"
**Solution:** Ensure `voice_samples/madara_uchiha_sample.wav` exists and is readable

---

## 📈 Next Phase (Integration)

After successful MVP test, integrate with:

1. **Frontend Web UI** - React/HTML interface
2. **Real-time Generation** - API server for speech on demand
3. **Quick-Line Buttons** - Pre-defined Madara dialogue
4. **Speed/Intensity Controls** - Post-generation audio effects
5. **Screen Recording** - Capture audio for Instagram Reels

---

## 📞 Support

**Common Questions:**

Q: Can I use different characters?
A: Yes! Add more voice samples and character configs in `tts_server.py`

Q: How long can text be?
A: XTTS v2 works best with 50-500 chars. Longer texts may take more time.

Q: What languages are supported?
A: XTTS v2 supports 13+ languages (English, Spanish, French, German, etc.)

Q: Can I use an MP3 instead of WAV?
A: Yes, but WAV is preferred. Convert MP3 to WAV first if needed.

---

**Status:** ✅ Ready for MVP Testing  
**Last Updated:** 2026-04-28
