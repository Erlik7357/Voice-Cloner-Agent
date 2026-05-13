"""Unit tests for the VoiceCloner engine."""

import sys
from pathlib import Path
# Add backend to import path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from voice_cloner import VoiceCloner


class TestSplitIntoSentenceChunks:
    """Tests for the text chunking logic used before synthesis."""

    def test_empty_string_returns_empty_list(self):
        assert VoiceCloner.split_into_sentence_chunks("") == []

    def test_whitespace_only_returns_empty_list(self):
        assert VoiceCloner.split_into_sentence_chunks("   \n\t  ") == []

    def test_single_short_sentence(self):
        result = VoiceCloner.split_into_sentence_chunks("Hello world.")
        assert result == ["Hello world."]

    def test_multiple_sentences_within_limit(self):
        text = "First sentence. Second sentence. Third sentence."
        result = VoiceCloner.split_into_sentence_chunks(text, max_chars=200)
        assert len(result) == 1
        assert "First sentence" in result[0]
        assert "Third sentence" in result[0]

    def test_sentences_split_when_exceeding_limit(self):
        text = "A short sentence. " * 20
        result = VoiceCloner.split_into_sentence_chunks(text.strip(), max_chars=60)
        assert len(result) > 1
        for chunk in result:
            assert len(chunk) <= 60 or " " not in chunk

    def test_long_single_sentence_splits_by_words(self):
        text = "word " * 100
        result = VoiceCloner.split_into_sentence_chunks(text.strip(), max_chars=50)
        assert len(result) > 1

    def test_preserves_all_content(self):
        text = "Alpha. Bravo. Charlie. Delta. Echo."
        result = VoiceCloner.split_into_sentence_chunks(text, max_chars=20)
        reconstructed = " ".join(result)
        for word in ["Alpha", "Bravo", "Charlie", "Delta", "Echo"]:
            assert word in reconstructed

    def test_normalizes_whitespace(self):
        text = "Hello   world.   How   are   you?"
        result = VoiceCloner.split_into_sentence_chunks(text, max_chars=500)
        assert result == ["Hello world. How are you?"]

    def test_handles_special_characters(self):
        text = "What?! No way! Yes, really."
        result = VoiceCloner.split_into_sentence_chunks(text, max_chars=500)
        assert len(result) >= 1
        assert "What?!" in result[0]

    def test_default_max_chars_is_220(self):
        # Build text that's over 220 chars with multiple sentences
        text = ("This is a moderately long sentence that takes up space. " * 6).strip()
        result = VoiceCloner.split_into_sentence_chunks(text)
        for chunk in result:
            assert len(chunk) <= 220 or " " not in chunk


class TestStitchWavFiles:
    """Tests for WAV file concatenation."""

    def test_empty_list_returns_false(self):
        assert VoiceCloner.stitch_wav_files([], "output.wav") is False

    def test_nonexistent_file_returns_false(self):
        result = VoiceCloner.stitch_wav_files(
            ["/nonexistent/path.wav"], "/tmp/out.wav"
        )
        assert result is False
