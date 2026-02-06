"""Testes para waveforms.py."""

import numpy as np
import pytest

from binaural_generator.config import WaveformType
from binaural_generator.waveforms import generate_waveform
from binaural_generator.utils import make_time_array


@pytest.fixture
def time_array() -> np.ndarray:
    """1 segundo a 44100 Hz."""
    return make_time_array(1.0, 44100)


class TestSineWave:
    def test_shape(self, time_array: np.ndarray) -> None:
        sig = generate_waveform(WaveformType.SINE, 440.0, time_array)
        assert sig.shape == (44100,)

    def test_amplitude(self, time_array: np.ndarray) -> None:
        sig = generate_waveform(WaveformType.SINE, 440.0, time_array, amplitude=0.5)
        assert np.max(np.abs(sig)) <= 0.5 + 1e-10

    def test_zero_amplitude(self, time_array: np.ndarray) -> None:
        sig = generate_waveform(WaveformType.SINE, 440.0, time_array, amplitude=0.0)
        assert np.allclose(sig, 0.0)

    def test_frequency_content(self, time_array: np.ndarray) -> None:
        """Verifica que o pico da FFT está próximo de 440 Hz."""
        sig = generate_waveform(WaveformType.SINE, 440.0, time_array)
        fft = np.abs(np.fft.rfft(sig))
        freqs = np.fft.rfftfreq(len(sig), 1 / 44100)
        peak_freq = freqs[np.argmax(fft)]
        assert abs(peak_freq - 440.0) < 2.0


class TestOtherWaveforms:
    @pytest.mark.parametrize("wf", [
        WaveformType.SAWTOOTH,
        WaveformType.SQUARE,
        WaveformType.TRIANGLE,
    ])
    def test_shape_and_bounds(self, time_array: np.ndarray, wf: WaveformType) -> None:
        sig = generate_waveform(wf, 440.0, time_array, amplitude=0.8)
        assert sig.shape == (44100,)
        assert np.max(np.abs(sig)) <= 0.8 + 1e-10


class TestNoise:
    def test_white_noise_shape(self, time_array: np.ndarray) -> None:
        sig = generate_waveform(WaveformType.WHITE_NOISE, 0.1, time_array, amplitude=0.5)
        assert sig.shape == (44100,)

    def test_pink_noise_shape(self, time_array: np.ndarray) -> None:
        sig = generate_waveform(WaveformType.PINK_NOISE, 0.1, time_array, amplitude=0.5)
        assert sig.shape == (44100,)

    def test_pink_noise_amplitude(self, time_array: np.ndarray) -> None:
        sig = generate_waveform(WaveformType.PINK_NOISE, 0.1, time_array, amplitude=0.6)
        assert np.max(np.abs(sig)) <= 0.6 + 1e-10

    def test_white_noise_nonzero(self, time_array: np.ndarray) -> None:
        sig = generate_waveform(WaveformType.WHITE_NOISE, 0.1, time_array, amplitude=0.5)
        assert np.std(sig) > 0.01


class TestInvalidWaveform:
    def test_invalid_type(self, time_array: np.ndarray) -> None:
        with pytest.raises((ValueError, AttributeError)):
            generate_waveform("invalid", 440.0, time_array)  # type: ignore[arg-type]
