"""
Test Script Runner - Madara Uchiha speech generation.
Generates cloned voice output for testing and validation.
"""

import argparse
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from voice_cloner import VoiceCloner


DEFAULT_MADARA_TEST_SCRIPT = """
Power isn't determined by some abstract concept. The true power lies in one's hands.
Obsessed with creating a utopia? The world is not as simple as that.
A shinobi's life is about shedding blood, but that doesn't mean we have to live with regret.

The world is cruel, yet beautiful. That is what makes life worth living.
I will create a world of my own design. A world without pain, without conflict. Without despair.
In this world, everyone can achieve their dreams without sacrifice.

This is the path I have chosen. This is my truth. And it is one I do not regret.
Look around you. The five great ninja villages divide the world into territories.
They fight for supremacy, sending shinobi to their deaths for the sake of pride.

The Uchiha clan was among the mightiest. Yet we fell. We were crushed.
Even now, memories of those days remain. They haunt me like shadows in the darkness.
But I will not live in the past. I will move forward. I will create my own destiny.

Some say that the path of a shinobi is paved with blood and suffering.
But I say that the path of a shinobi is one of redemption. Of second chances.
For in the depths of darkness, there is always a glimmer of light.

This is the truth I have come to understand. This is the power that drives me forward.
And with this power, I shall reshape the world. I shall be the architect of a new age.
An age of peace. An age of understanding. An age where all can live as one.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Madara voice test clip.")
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Inline script text to synthesize.",
    )
    parser.add_argument(
        "--text-file",
        type=Path,
        default=None,
        help="Path to a UTF-8 text file containing the script to synthesize.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output") / "madara_test_output.wav",
        help="Output WAV path (default: output/madara_test_output.wav).",
    )
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Force CPU mode (default tries GPU first with automatic fallback).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    project_root = Path(__file__).parent
    voice_samples = project_root / "voice_samples"
    output_dir = project_root / "output"

    voice_samples.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    reference_voice = voice_samples / "madara_uchiha_sample.wav"
    output_file = (project_root / args.output).resolve()

    if args.text_file:
        madara_test_script = args.text_file.read_text(encoding="utf-8").strip()
    elif args.text:
        madara_test_script = args.text.strip()
    else:
        madara_test_script = DEFAULT_MADARA_TEST_SCRIPT.strip()

    print("\n" + "=" * 70)
    print("MADARA UCHIHA - VOICE CLONING TEST")
    print("=" * 70)

    if not reference_voice.exists():
        print("\nSETUP REQUIRED - Voice sample not found")
        print(f"Expected location: {reference_voice}")
        print("\nTo proceed:")
        print("1. Download or extract Madara Uchiha voice sample (10-60 seconds)")
        print("2. Ensure it is in WAV format")
        print("3. Place it at: voice_samples/madara_uchiha_sample.wav")
        return 1

    print(f"\nVoice sample found: {reference_voice.name}")
    print(f"Test script length: {len(madara_test_script.split())} words")
    print(f"Output path: {output_file}")

    try:
        cloner = VoiceCloner(gpu=not args.cpu)
        print("\nGenerating cloned voice... (first run may take time)")

        success = cloner.clone_voice(
            reference_audio_path=str(reference_voice),
            text=madara_test_script,
            output_path=str(output_file),
            language="en",
        )

        if success and output_file.exists() and output_file.stat().st_size > 0:
            print("\n" + "=" * 70)
            print("TEST COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print(f"Output file: {output_file}")
            print(f"File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
            return 0

        print("\nTest failed - output file missing or empty")
        return 1

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
