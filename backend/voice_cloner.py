"""
Voice Cloner using XTTS v2 - Local MVP.
Clones voice from reference audio and generates speech.
"""

import os
from pathlib import Path
import re
import warnings
import wave
from typing import Callable

from TTS.api import TTS

warnings.filterwarnings("ignore")

# Enable non-interactive model download/initialization in automated runs.
os.environ.setdefault("COQUI_TOS_AGREED", "1")


class VoiceCloner:
    def __init__(
        self,
        model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2",
        gpu: bool = True,
    ) -> None:
        """Initialize the voice cloning pipeline."""
        print(f"[voice-cloner] Initializing with model: {model_name}")

        device = "cuda" if gpu else "cpu"
        try:
            self.tts = TTS(model_name, gpu=gpu, progress_bar=True)
            self.device = device
            print(f"[voice-cloner] Model loaded on {device}")
        except Exception as e:
            print(f"[voice-cloner] GPU load failed: {e}")
            print("[voice-cloner] Falling back to CPU...")
            self.tts = TTS(model_name, gpu=False, progress_bar=True)
            self.device = "cpu"
            print("[voice-cloner] Model loaded on cpu")

    @staticmethod
    def split_into_sentence_chunks(text: str, max_chars: int = 220) -> list[str]:
        """Split text into sentence-aware chunks for real progress tracking."""
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []

        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", normalized) if part.strip()]
        chunks: list[str] = []
        current = ""

        for sentence in sentences:
            sentence_parts = [sentence]
            if len(sentence) > max_chars:
                sentence_parts = []
                words = sentence.split()
                buffer = ""
                for word in words:
                    candidate = f"{buffer} {word}".strip()
                    if len(candidate) <= max_chars or not buffer:
                        buffer = candidate
                    else:
                        sentence_parts.append(buffer)
                        buffer = word
                if buffer:
                    sentence_parts.append(buffer)

            for part in sentence_parts:
                candidate = f"{current} {part}".strip()
                if len(candidate) <= max_chars or not current:
                    current = candidate
                else:
                    chunks.append(current)
                    current = part

        if current:
            chunks.append(current)

        return chunks

    @staticmethod
    def stitch_wav_files(input_paths: list[str], output_path: str) -> bool:
        """Concatenate multiple WAV files into a single output WAV."""
        if not input_paths:
            return False

        try:
            with wave.open(input_paths[0], "rb") as first_wav:
                params = first_wav.getparams()
                frames = [first_wav.readframes(first_wav.getnframes())]
                base_format = (
                    params.nchannels,
                    params.sampwidth,
                    params.framerate,
                    params.comptype,
                    params.compname,
                )

            for wav_path in input_paths[1:]:
                with wave.open(wav_path, "rb") as chunk_wav:
                    chunk_params = chunk_wav.getparams()
                    chunk_format = (
                        chunk_params.nchannels,
                        chunk_params.sampwidth,
                        chunk_params.framerate,
                        chunk_params.comptype,
                        chunk_params.compname,
                    )
                    if chunk_format != base_format:
                        raise ValueError("WAV chunk format mismatch during stitch")
                    frames.append(chunk_wav.readframes(chunk_wav.getnframes()))

            with wave.open(output_path, "wb") as merged_wav:
                merged_wav.setparams(params)
                for frame_block in frames:
                    merged_wav.writeframes(frame_block)

            return True
        except Exception as e:
            print(f"[voice-cloner] Error stitching audio chunks: {e}")
            return False

    def clone_voice(
        self,
        reference_audio_path: str,
        text: str,
        output_path: str,
        language: str = "en",
    ) -> bool:
        """Clone voice from reference audio and generate speech."""
        try:
            if not os.path.exists(reference_audio_path):
                print(f"[voice-cloner] Reference audio not found: {reference_audio_path}")
                return False

            snippet = text[:100] + ("..." if len(text) > 100 else "")
            print("[voice-cloner] Generating speech")
            print(f"[voice-cloner] Text preview: {snippet}")
            print(f"[voice-cloner] Reference: {Path(reference_audio_path).name}")
            print(f"[voice-cloner] Output: {output_path}")

            self.tts.tts_to_file(
                text=text,
                speaker_wav=reference_audio_path,
                language=language,
                file_path=output_path,
            )

            print(f"[voice-cloner] Voice generated successfully: {output_path}")
            return True
        except Exception as e:
            print(f"[voice-cloner] Error during voice generation: {e}")
            return False

    def clone_voice_in_chunks(
        self,
        reference_audio_path: str,
        text: str,
        output_path: str,
        language: str = "en",
        *,
        chunk_prefix: str,
        on_chunk_complete: Callable[[int, int, str], None] | None = None,
    ) -> bool:
        """Generate audio chunk by chunk, then stitch the WAVs together."""
        if not os.path.exists(reference_audio_path):
            print(f"[voice-cloner] Reference audio not found: {reference_audio_path}")
            return False

        chunks = self.split_into_sentence_chunks(text)
        if not chunks:
            print("[voice-cloner] No text chunks were produced")
            return False

        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        chunk_paths: list[str] = []

        try:
            total_chunks = len(chunks)
            print(f"[voice-cloner] Generating {total_chunks} audio chunks")

            for index, chunk_text in enumerate(chunks, start=1):
                chunk_path = str(output_dir / f"{chunk_prefix}_part_{index:03d}.wav")
                snippet = chunk_text[:100] + ("..." if len(chunk_text) > 100 else "")
                print(f"[voice-cloner] Chunk {index}/{total_chunks}: {snippet}")
                self.tts.tts_to_file(
                    text=chunk_text,
                    speaker_wav=reference_audio_path,
                    language=language,
                    file_path=chunk_path,
                )
                chunk_paths.append(chunk_path)

                if on_chunk_complete is not None:
                    on_chunk_complete(index, total_chunks, chunk_path)

            success = self.stitch_wav_files(chunk_paths, output_path)
            if success:
                print(f"[voice-cloner] Voice generated successfully: {output_path}")
            return success
        except Exception as e:
            print(f"[voice-cloner] Error during chunked voice generation: {e}")
            return False
        finally:
            for chunk_path in chunk_paths:
                try:
                    Path(chunk_path).unlink(missing_ok=True)
                except OSError:
                    pass


def main() -> None:
    """Manual smoke test for the voice cloner."""
    project_root = Path(__file__).parent.parent
    voice_samples_dir = project_root / "voice_samples"
    output_dir = project_root / "output"

    voice_samples_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    reference_voice = voice_samples_dir / "madara_uchiha_sample.wav"
    output_file = output_dir / "madara_cloned_test.wav"

    test_script = (
        "Power is not determined by abstract concepts. "
        "The world is cruel, yet beautiful. "
        "I will create a world without pain and conflict. "
        "This is the path I have chosen."
    )

    print("=" * 60)
    print("VOICE CLONER - MADARA UCHIHA MVP")
    print("=" * 60)

    if not reference_voice.exists():
        print("Setup required:")
        print(f"- Place a 10-60s WAV sample at: {reference_voice}")
        return

    cloner = VoiceCloner(gpu=True)
    success = cloner.clone_voice_in_chunks(
        reference_audio_path=str(reference_voice),
        text=test_script,
        output_path=str(output_file),
        language="en",
        chunk_prefix="madara-test",
    )

    if success:
        print("Test completed")
        print(f"Output: {output_file}")
    else:
        print("Voice generation failed. Check errors above.")


if __name__ == "__main__":
    main()
