"""
Audio Setup & Conversion Tool
Handles MP3 to WAV conversion for voice cloning
"""

import os
import sys
from pathlib import Path
import subprocess

def ensure_dependencies():
    """Install required audio packages"""
    print("Checking audio libraries...")
    required = ['librosa', 'soundfile', 'TTS']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [MISSING] {package} - installing...")
            missing.append(package)
    
    if missing:
        print(f"\nInstalling {len(missing)} packages...")
        print("   This may take 2-5 minutes...")
        for package in missing:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])
        print("Dependencies installed.")
    else:
        print("All dependencies ready.")

def find_mp3_files():
    """Find MP3 files in common locations"""
    project_root = Path(__file__).parent.parent
    locations = [
        project_root,
        project_root / 'Downloads',
        Path.home() / 'Downloads',
    ]
    
    found_files = []
    for location in locations:
        if location.exists():
            for mp3 in location.glob('*.mp3'):
                found_files.append(mp3)
    
    return found_files

def convert_mp3_to_wav():
    """Convert MP3 to WAV format"""
    project_root = Path(__file__).parent.parent
    voice_samples = project_root / 'voice_samples'
    output_wav = voice_samples / 'madara_uchiha_sample.wav'
    
    print("\n" + "=" * 60)
    print("AUDIO CONVERSION TOOL")
    print("=" * 60)
    
    # Ensure voice_samples directory exists
    voice_samples.mkdir(exist_ok=True)
    
    # Find MP3 files
    print("\nLooking for MP3 files...")
    mp3_files = find_mp3_files()
    
    if not mp3_files:
        print("No MP3 files found")
        print(f"\nExpected locations:")
        print(f"   - {project_root}")
        print(f"   - {Path.home() / 'Downloads'}")
        print(f"\nPlease save your voice MP3 in one of these locations.")
        return False
    
    # Filter for Madara voice
    madara_files = [f for f in mp3_files if 'madara' in f.name.lower() or 'hatred' in f.name.lower() or 'voice' in f.name.lower()]
    
    if not madara_files:
        madara_files = mp3_files  # Use any MP3 if no Madara-specific file found
    
    mp3_file = madara_files[0]
    print(f"Found: {mp3_file.name}")
    print(f"   Size: {mp3_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    try:
        import librosa
        import soundfile as sf
        
        print(f"\nConverting to WAV...")
        print(f"   This may take 30-60 seconds...")
        
        # Load and convert
        y, sr = librosa.load(str(mp3_file), sr=None)
        sf.write(str(output_wav), y, sr)
        
        duration = len(y) / sr
        print(f"\nConversion successful.")
        print(f"Saved to: {output_wav}")
        print(f"Sample rate: {sr} Hz")
        print(f"Duration: {duration:.2f} seconds")
        
        if duration < 6:
            print(f"\nWARNING: Audio is only {duration:.2f} seconds")
            print(f"   Recommended: 30-60 seconds for best voice cloning quality")
        
        return True
        
    except Exception as e:
        print(f"Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    ensure_dependencies()
    success = convert_mp3_to_wav()
    
    if success:
        print("\n" + "=" * 60)
        print("NEXT STEP")
        print("=" * 60)
        print("\nRun: python test_madara.py")
        print("\nThis will generate cloned speech from your voice sample.")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
