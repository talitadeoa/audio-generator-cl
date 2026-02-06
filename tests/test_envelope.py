"""Testes para envelope.py."""

import numpy as np
import pytest

from binaural_generator.config import EnvelopeConfig
from binaural_generator.envelope import apply_adsr, apply_fade, isochronic_gate


SR = 44100


class TestADSR:
    def test_attack_ramp(self) -> None:
        env = EnvelopeConfig(attack=0.1, decay=0.0, sustain=1.0, release=0.0)
        signal = np.ones(SR, dtype=np.float64)
        result = apply_adsr(signal, env, SR)
        # Início deve ser ~0
        assert abs(result[0]) < 0.01
        # Após attack, deve estar ~1
        attack_end = int(0.1 * SR)
        assert result[attack_end] > 0.9

    def test_release_ramp(self) -> None:
        env = EnvelopeConfig(attack=0.0, decay=0.0, sustain=1.0, release=0.1)
        signal = np.ones(SR, dtype=np.float64)
        result = apply_adsr(signal, env, SR)
        # Final deve ser ~0
        assert abs(result[-1]) < 0.05

    def test_sustain_level(self) -> None:
        env = EnvelopeConfig(attack=0.01, decay=0.01, sustain=0.5, release=0.01)
        signal = np.ones(SR, dtype=np.float64)
        result = apply_adsr(signal, env, SR)
        # Meio do sinal deve estar ~0.5
        mid = SR // 2
        assert 0.4 < result[mid] < 0.6

    def test_preserves_shape(self) -> None:
        env = EnvelopeConfig()
        signal = np.ones(1000, dtype=np.float64)
        result = apply_adsr(signal, env, SR)
        assert result.shape == (1000,)


class TestFade:
    def test_fade_in(self) -> None:
        signal = np.ones(SR, dtype=np.float64)
        result = apply_fade(signal, fade_in_sec=0.1, fade_out_sec=0.0, sample_rate=SR)
        assert result[0] < 0.01
        # Após fade, deve ser ~1
        assert result[SR // 2] > 0.99

    def test_fade_out(self) -> None:
        signal = np.ones(SR, dtype=np.float64)
        result = apply_fade(signal, fade_in_sec=0.0, fade_out_sec=0.1, sample_rate=SR)
        assert result[-1] < 0.01
        assert result[SR // 4] > 0.99

    def test_both_fades(self) -> None:
        signal = np.ones(SR, dtype=np.float64)
        result = apply_fade(signal, 0.1, 0.1, SR)
        assert result[0] < 0.01
        assert result[-1] < 0.01
        assert result[SR // 2] > 0.99


class TestIsochronicGate:
    def test_gate_has_silence(self) -> None:
        signal = np.ones(SR, dtype=np.float64)
        gated = isochronic_gate(signal, rate=10.0, sample_rate=SR)
        # Deve ter regiões próximas de zero
        assert np.min(gated) < 0.1

    def test_gate_preserves_shape(self) -> None:
        signal = np.ones(2000, dtype=np.float64)
        gated = isochronic_gate(signal, rate=5.0, sample_rate=SR)
        assert gated.shape == (2000,)

    def test_zero_rate(self) -> None:
        signal = np.ones(1000, dtype=np.float64)
        # Rate 0 → gate constante (sem oscilação)
        gated = isochronic_gate(signal, rate=0.0, sample_rate=SR)
        assert gated.shape == (1000,)
