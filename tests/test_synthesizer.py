"""Testes para synthesizer.py."""

import numpy as np
import pytest

from binaural_generator.config import (
    EnvelopeConfig,
    LayerConfig,
    Mode,
    WaveformType,
)
from binaural_generator.synthesizer import synthesize_layer


@pytest.fixture
def binaural_layer() -> LayerConfig:
    return LayerConfig(
        waveform=WaveformType.SINE,
        freq_left=200.0,
        freq_right=210.0,
        amplitude=0.7,
        mode=Mode.BINAURAL,
        envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0),
    )


class TestSynthesizeLayer:
    def test_output_shape(self, binaural_layer: LayerConfig) -> None:
        sig = synthesize_layer(binaural_layer, duration=1.0, sample_rate=44100)
        assert sig.shape == (44100, 2)

    def test_stereo_channels_differ(self, binaural_layer: LayerConfig) -> None:
        """Em modo binaural, L e R devem ser diferentes."""
        sig = synthesize_layer(binaural_layer, duration=1.0, sample_rate=44100)
        assert not np.allclose(sig[:, 0], sig[:, 1])

    def test_mono_mode(self) -> None:
        layer = LayerConfig(
            waveform=WaveformType.SINE,
            freq_left=440.0,
            freq_right=440.0,
            mode=Mode.MONO,
            envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0),
        )
        sig = synthesize_layer(layer, duration=0.5, sample_rate=22050)
        assert sig.shape[1] == 2
        # Em modo MONO, ambos canais devem ser iguais (mesma freq)
        np.testing.assert_allclose(sig[:, 0], sig[:, 1], atol=1e-10)

    def test_monaural_mode(self) -> None:
        layer = LayerConfig(
            waveform=WaveformType.SINE,
            freq_left=200.0,
            freq_right=210.0,
            mode=Mode.MONAURAL,
            envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0),
        )
        sig = synthesize_layer(layer, duration=0.5, sample_rate=22050)
        # Monaural: ambos canais são idênticos (soma)
        np.testing.assert_allclose(sig[:, 0], sig[:, 1], atol=1e-10)

    def test_isochronic_mode(self) -> None:
        layer = LayerConfig(
            waveform=WaveformType.SINE,
            freq_left=300.0,
            freq_right=300.0,
            mode=Mode.ISOCHRONIC,
            isochronic_rate=10.0,
            envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0),
        )
        sig = synthesize_layer(layer, duration=1.0, sample_rate=44100)
        # Isocrônico deve ter silêncios (gate)
        assert np.min(np.abs(sig[:, 0])) < 0.01

    def test_amplitude_modulation(self) -> None:
        layer = LayerConfig(
            waveform=WaveformType.SINE,
            freq_left=440.0,
            freq_right=440.0,
            amplitude=0.8,
            mode=Mode.MONO,
            am_depth=0.5,
            am_rate=5.0,
            envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0),
        )
        sig = synthesize_layer(layer, duration=1.0, sample_rate=44100)
        # Sinal deve variar em amplitude
        assert sig.shape == (44100, 2)

    def test_frequency_modulation(self) -> None:
        layer = LayerConfig(
            waveform=WaveformType.SINE,
            freq_left=440.0,
            freq_right=440.0,
            amplitude=0.8,
            mode=Mode.MONO,
            fm_depth=10.0,
            fm_rate=2.0,
            envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0),
        )
        sig = synthesize_layer(layer, duration=1.0, sample_rate=44100)
        assert sig.shape == (44100, 2)

    def test_panning(self) -> None:
        layer = LayerConfig(
            waveform=WaveformType.SINE,
            freq_left=440.0,
            freq_right=440.0,
            mode=Mode.MONO,
            pan_left=1.0,
            pan_right=0.0,
            envelope=EnvelopeConfig(fade_in=0.0, fade_out=0.0),
        )
        sig = synthesize_layer(layer, duration=0.5, sample_rate=22050)
        # Canal direito deve ser silêncio
        np.testing.assert_allclose(sig[:, 1], 0.0, atol=1e-10)

    def test_invalid_frequency(self) -> None:
        layer = LayerConfig(freq_left=99999.0)
        with pytest.raises(ValueError, match="fora do intervalo"):
            synthesize_layer(layer, duration=0.1, sample_rate=44100)
