"""Testes para mixer.py."""

import numpy as np
import pytest

from binaural_generator.config import (
    EnvelopeConfig,
    LayerConfig,
    Mode,
    SessionConfig,
    WaveformType,
)
from binaural_generator.mixer import mix_session, mix_layers_realtime, normalize_stereo


class TestMixSession:
    def test_basic_mix(self) -> None:
        config = SessionConfig(
            duration=0.5,
            sample_rate=22050,
            layers=[
                LayerConfig(
                    waveform=WaveformType.SINE,
                    freq_left=200.0,
                    freq_right=210.0,
                    amplitude=0.6,
                    mode=Mode.BINAURAL,
                    envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0),
                ),
            ],
        )
        signal = mix_session(config)
        assert signal.shape == (11025, 2)
        assert signal.dtype == np.float64

    def test_multi_layer_mix(self) -> None:
        config = SessionConfig(
            duration=0.5,
            sample_rate=22050,
            layers=[
                LayerConfig(
                    waveform=WaveformType.SINE,
                    freq_left=200.0,
                    freq_right=210.0,
                    amplitude=0.5,
                    envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0),
                ),
                LayerConfig(
                    waveform=WaveformType.PINK_NOISE,
                    freq_left=100.0,
                    freq_right=100.0,
                    amplitude=0.2,
                    mode=Mode.MONO,
                    envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0),
                ),
            ],
        )
        signal = mix_session(config)
        assert signal.shape == (11025, 2)
        # Normalizado, pico deve estar próximo de 0.95
        assert np.max(np.abs(signal)) <= 0.96

    def test_no_layers_raises(self) -> None:
        config = SessionConfig(layers=[])
        with pytest.raises(ValueError):
            mix_session(config)

    def test_no_clipping(self) -> None:
        """Múltiplas camadas não devem causar clipping."""
        config = SessionConfig(
            duration=0.5,
            sample_rate=22050,
            layers=[
                LayerConfig(amplitude=0.9, envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0)),
                LayerConfig(amplitude=0.9, freq_left=300, freq_right=310, envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0)),
                LayerConfig(amplitude=0.9, freq_left=500, freq_right=520, envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0)),
            ],
        )
        signal = mix_session(config)
        assert np.max(np.abs(signal)) <= 1.0


class TestNormalizeStereo:
    def test_normalize(self) -> None:
        sig = np.random.randn(1000, 2)
        normed = normalize_stereo(sig, target_peak=0.9)
        assert abs(np.max(np.abs(normed)) - 0.9) < 0.01

    def test_zero_signal(self) -> None:
        sig = np.zeros((100, 2))
        normed = normalize_stereo(sig)
        np.testing.assert_allclose(normed, 0.0)


class TestMixLayersRealtime:
    def test_basic_realtime(self) -> None:
        s1 = np.random.randn(1000, 2) * 0.3
        s2 = np.random.randn(1000, 2) * 0.3
        mixed = mix_layers_realtime([s1, s2], [0.5, 0.5])
        assert mixed.shape == (1000, 2)

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            mix_layers_realtime([], [])
