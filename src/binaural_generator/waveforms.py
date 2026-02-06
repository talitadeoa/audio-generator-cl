"""
waveforms.py — Geração de formas de onda puras e ruído.

Trade‑offs documentados
-----------------------
* **Sine** — beat mais suave e agradável; ideal para meditação/sono.
* **Square/Sawtooth** — harmônicos fortes; beat mais pronunciado, bom para foco intenso.
* **Triangle** — meio‑termo entre sine e square.
* **Pink noise** — sensação de "aconchego", bom para mascaramento.
* **White noise** — energia igual em todas as faixas; mais "brilhante".
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy import signal as scipy_signal

from .config import WaveformType


def generate_waveform(
    waveform: WaveformType,
    freq: float,
    t: NDArray[np.float64],
    amplitude: float = 1.0,
    *,
    phase: float = 0.0,
) -> NDArray[np.float64]:
    """
    Gera uma forma de onda no domínio do tempo.

    Parameters
    ----------
    waveform : WaveformType
        Tipo da onda.
    freq : float
        Frequência em Hz.
    t : NDArray
        Vetor de tempo em segundos.
    amplitude : float
        Amplitude de pico (0–1).
    phase : float
        Fase inicial em radianos.

    Returns
    -------
    NDArray[np.float64]
        Sinal com shape ``(len(t),)``.
    """
    match waveform:
        case WaveformType.SINE:
            return _sine(freq, t, amplitude, phase)
        case WaveformType.SAWTOOTH:
            return _sawtooth(freq, t, amplitude, phase)
        case WaveformType.SQUARE:
            return _square(freq, t, amplitude, phase)
        case WaveformType.TRIANGLE:
            return _triangle(freq, t, amplitude, phase)
        case WaveformType.PINK_NOISE:
            return _pink_noise(len(t), amplitude)
        case WaveformType.WHITE_NOISE:
            return _white_noise(len(t), amplitude)
        case _:
            raise ValueError(f"Forma de onda desconhecida: {waveform}")


# ── Ondas determinísticas ────────────────────────────────────────────

def _sine(
    freq: float, t: NDArray[np.float64], amp: float, phase: float,
) -> NDArray[np.float64]:
    return amp * np.sin(2 * np.pi * freq * t + phase)


def _sawtooth(
    freq: float, t: NDArray[np.float64], amp: float, phase: float,
) -> NDArray[np.float64]:
    return amp * scipy_signal.sawtooth(2 * np.pi * freq * t + phase)


def _square(
    freq: float, t: NDArray[np.float64], amp: float, phase: float,
) -> NDArray[np.float64]:
    return amp * scipy_signal.square(2 * np.pi * freq * t + phase)


def _triangle(
    freq: float, t: NDArray[np.float64], amp: float, phase: float,
) -> NDArray[np.float64]:
    return amp * scipy_signal.sawtooth(2 * np.pi * freq * t + phase, width=0.5)


# ── Ruídos ───────────────────────────────────────────────────────────

def _white_noise(n_samples: int, amp: float) -> NDArray[np.float64]:
    rng = np.random.default_rng()
    return amp * rng.standard_normal(n_samples)


def _pink_noise(n_samples: int, amp: float) -> NDArray[np.float64]:
    """
    Gera ruído rosa usando filtro Voss‑McCartney simplificado (16 fontes).
    """
    n_sources = 16
    rng = np.random.default_rng()
    out = np.zeros(n_samples, dtype=np.float64)
    for i in range(n_sources):
        step = 2 ** i
        source = rng.standard_normal(n_samples // step + 1)
        out += np.repeat(source, step)[:n_samples]
    # Normalizar para amplitude desejada
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * amp
    return out
