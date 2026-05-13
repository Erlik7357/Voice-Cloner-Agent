"""
Audio conversion utility - Convert MP3 to WAV
"""
import sys
from pathlib import Path

def convert_mp3_to_wav():
    """Convert MP3 attachment to WAV format"""
    
    # Paths
    project_root = Path(__file__).parent.parent
    voice_samples = project_root / 'voice_samples'
    output_wav = voice_samples / 'madara_uchiha_sample.wav'
    
    # Look for MP3 files in project root
    mp3_files = list(project_root.glob('*.mp3'))
    
    if not mp3_files:
        print("No MP3 files found in project root")
        print(f"Looking in: {project_root}")
        return False
    
    mp3_file = mp3_files[0]  # Use first MP3 found
    print(f"Found MP3: {mp3_file.name}")
    
    try:
        # Try librosa first (best option)
        import librosa
        import soundfile as sf
        
        print(f"Converting {mp3_file.name} to WAV...")
        
        # Load audio
        y, sr = librosa.load(str(mp3_file), sr=None)
        
        # Save as WAV
        sf.write(str(output_wav), y, sr)
        
        print(f"Conversion successful.")
        print(f"Saved to: {output_wav}")
        print(f"Sample rate: {sr} Hz")
        print(f"Duration: {len(y) / sr:.2f} seconds")
        
        return True
        
    except ImportError:
        # Fallback to pydub
        print("librosa not available, trying pydub...")
        try:
            from pydub import AudioSegment
            
            print(f"Converting {mp3_file.name} to WAV...")
            audio = AudioSegment.from_mp3(str(mp3_file))
            audio.export(str(output_wav), format='wav')
            
            print(f"Conversion successful.")
            print(f"Saved to: {output_wav}")
            print(f"Duration: {len(audio) / 1000:.2f} seconds")
            
            return True
        except ImportError:
            print("Neither librosa nor pydub available")
            print("   Install with: pip install librosa pydub")
            return False
    except Exception as e:
        print(f"Conversion failed: {e}")
        return False

if __name__ == '__main__':
    success = convert_mp3_to_wav()
    sys.exit(0 if success else 1)
