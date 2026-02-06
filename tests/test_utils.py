"""Testes para utils.py."""

import numpy as np
import pytest

from binaural_generator.utils import (
    validate_frequency,
    validate_amplitude,
    validate_duration,
    validate_sample_rate,
    normalize_audio,
    soft_clip,
    db_to_linear,
    linear_to_db,
    seconds_to_samples,
    make_time_array,
)


class TestValidation:
    def test_valid_frequency(self) -> None:
        assert validate_frequency(440.0) == 440.0
        assert validate_frequency(0.1) == 0.1
        assert validate_frequency(20000.0) == 20000.0

    def test_invalid_frequency_low(self) -> None:
        with pytest.raises(ValueError):
            validate_frequency(0.01)

    def test_invalid_frequency_high(self) -> None:
        with pytest.raises(ValueError):
            validate_frequency(25000.0)

    def test_valid_amplitude(self) -> None:
        assert validate_amplitude(0.5) == 0.5
        assert validate_amplitude(0.0) == 0.0
        assert validate_amplitude(1.0) == 1.0

    def test_invalid_amplitude(self) -> None:
        with pytest.raises(ValueError):
            validate_amplitude(1.5)
        with pytest.raises(ValueError):
            validate_amplitude(-0.1)

    def test_valid_duration(self) -> None:
        assert validate_duration(10.0) == 10.0

    def test_invalid_duration(self) -> None:
        with pytest.raises(ValueError):
            validate_duration(0.0)
        with pytest.raises(ValueError):
            validate_duration(-1.0)

    def test_valid_sample_rate(self) -> None:
        assert validate_sample_rate(44100) == 44100

    def test_invalid_sample_rate(self) -> None:
        with pytest.raises(ValueError):
            validate_sample_rate(1000)


class TestNormalization:
    def test_normalize(self) -> None:
        sig = np.array([0.5, -1.0, 0.3])
        normed = normalize_audio(sig, target_peak=0.9)
        assert abs(np.max(np.abs(normed)) - 0.9) < 1e-10

    def test_zero_signal(self) -> None:
        sig = np.zeros(100)
        normed = normalize_audio(sig)
        np.testing.assert_allclose(normed, 0.0)


class TestSoftClip:
    def test_no_clip_needed(self) -> None:
        sig = np.array([0.1, 0.2, -0.3])
        clipped = soft_clip(sig, threshold=0.95)
        np.testing.assert_allclose(clipped, sig)

    def test_clips_loud_signal(self) -> None:
        sig = np.array([2.0, -2.0])
        clipped = soft_clip(sig, threshold=0.5)
        assert np.max(np.abs(clipped)) < 2.0


class TestConversions:
    def test_db_roundtrip(self) -> None:
        assert abs(db_to_linear(0.0) - 1.0) < 1e-10
        assert abs(db_to_linear(-6.0) - 0.5012) < 0.01
        assert abs(linear_to_db(1.0)) < 1e-10

    def test_seconds_to_samples(self) -> None:
        assert seconds_to_samples(1.0, 44100) == 44100
        assert seconds_to_samples(0.5, 22050) == 11025

    def test_make_time_array(self) -> None:
        t = make_time_array(1.0, 44100)
        assert len(t) == 44100
        assert t[0] == 0.0
        assert t[-1] < 1.0
