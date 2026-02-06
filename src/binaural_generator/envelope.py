"""
envelope.py — Envelopes ADSR, fade in/out e janelas suavizantes.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .config import EnvelopeConfig
from .utils import seconds_to_samples


def apply_adsr(
    signal: NDArray[np.float64],
    env: EnvelopeConfig,
    sample_rate: int,
) -> NDArray[np.float64]:
    """
    Aplica envelope ADSR ao sinal.

    O sinal é multiplicado por uma curva que sobe de 0→1 (attack),
    desce de 1→sustain (decay), mantém sustain e cai para 0 (release).
    """
    n = len(signal)
    a = min(seconds_to_samples(env.attack, sample_rate), n)
    d = min(seconds_to_samples(env.decay, sample_rate), n - a)
    r = min(seconds_to_samples(env.release, sample_rate), n - a - d)
    s_len = max(n - a - d - r, 0)

    curve = np.ones(n, dtype=np.float64)
    # Attack: 0 → 1
    if a > 0:
        curve[:a] = np.linspace(0, 1, a, endpoint=False)
    # Decay: 1 → sustain
    if d > 0:
        curve[a:a + d] = np.linspace(1, env.sustain, d, endpoint=False)
    # Sustain
    if s_len > 0:
        curve[a + d:a + d + s_len] = env.sustain
    # Release: sustain → 0
    if r > 0:
        curve[a + d + s_len:a + d + s_len + r] = np.linspace(
            env.sustain, 0, r, endpoint=True,
        )
    # Qualquer resto → 0
    remaining = n - (a + d + s_len + r)
    if remaining > 0:
        curve[-(remaining):] = 0.0

    return signal * curve


def apply_fade(
    signal: NDArray[np.float64],
    fade_in_sec: float,
    fade_out_sec: float,
    sample_rate: int,
) -> NDArray[np.float64]:
    """
    Aplica fade in/out usando janela de Hann (meia‑janela).
    """
    n = len(signal)
    out = signal.copy()

    fi = seconds_to_samples(fade_in_sec, sample_rate)
    fo = seconds_to_samples(fade_out_sec, sample_rate)
    fi = min(fi, n)
    fo = min(fo, n)

    if fi > 0:
        # Meia janela Hann (parte crescente)
        window = np.hanning(2 * fi)[:fi]
        out[:fi] *= window

    if fo > 0:
        # Meia janela Hann (parte decrescente)
        window = np.hanning(2 * fo)[fo:]
        out[-fo:] *= window

    return out


def isochronic_gate(
    signal: NDArray[np.float64],
    rate: float,
    sample_rate: int,
    duty: float = 0.5,
) -> NDArray[np.float64]:
    """
    Aplica gating isocrônico (pulso on/off) ao sinal.

    Parameters
    ----------
    rate : float
        Frequência de pulsação em Hz.
    duty : float
        Duty cycle (0–1). 0.5 = metade on, metade off.
    """
    n = len(signal)
    t = np.arange(n, dtype=np.float64) / sample_rate
    # Gate: onda quadrada 0/1
    gate = (np.sin(2 * np.pi * rate * t) >= 0).astype(np.float64)
    # Suavizar bordas (mini crossfade de ~2 ms)
    smooth_samples = max(int(0.002 * sample_rate), 1)
    kernel = np.ones(smooth_samples) / smooth_samples
    gate = np.convolve(gate, kernel, mode="same")
    return signal * gate
