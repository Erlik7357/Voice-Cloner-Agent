# 🎙️ MP3 to WAV Setup - Step by Step

## Your Madara Uchiha Voice File

You've uploaded: **Voicy_Hatred Is Born To Protect Love.mp3**

This file needs to be:
1. ✅ Located or accessible
2. ✅ Converted to WAV format  
3. ✅ Saved to: `voice_samples/madara_uchiha_sample.wav`

---

## 🚀 Automated Setup (Recommended)

### Option 1: Run Setup Script (Windows)
```
Double-click: setup_audio.bat
```

This will:
- Install audio libraries (librosa, soundfile)
- Search for your MP3 file
- Automatically convert to WAV
- Save to the correct location

### Option 2: Run Setup Script (Python)
```bash
python setup_audio.py
```

---

## 📁 Where to Place the MP3

If the script can't find your file automatically, place it in one of these locations:

1. **Project folder** (easiest):
   ```
   d:\Anti Gravity\graphify\Voice cloner\Voicy_Hatred Is Born To Protect Love.mp3
   ```

2. **Downloads folder**:
   ```
   C:\Users\[YourUsername]\Downloads\Voicy_Hatred Is Born To Protect Love.mp3
   ```

Then run: `python setup_audio.py`

---

## ✅ Verification

After running setup, you should see:
```
✅ Conversion successful!
📁 Saved to: d:\Anti Gravity\graphify\Voice cloner\voice_samples\madara_uchiha_sample.wav
⏱️  Duration: X.XX seconds
```

---

## 🎧 Quality Check

If duration is shown as **less than 6 seconds**:
- ⚠️ Sample is too short
- ✅ But it might still work  
- 💡 For better results, use a 30-60 second sample

---

## Next Step After Setup

Once WAV file is in place:
```bash
python test_madara.py
```

This will generate speech from your Madara voice!

---

## Need Help?

If the script can't find the file:
1. Check file name: `Voicy_Hatred Is Born To Protect Love.mp3`
2. Make sure it's in the project folder (same level as this file)
3. Run `python setup_audio.py` again
4. Watch for error messages about file location

