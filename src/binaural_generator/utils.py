"""
utils.py — Utilitários: validação, normalização, conversão.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .config import MIN_FREQ_HZ, MAX_FREQ_HZ, MAX_AMPLITUDE


def validate_frequency(freq: float, label: str = "freq") -> float:
    """Valida se a frequência está no intervalo permitido."""
    if not MIN_FREQ_HZ <= freq <= MAX_FREQ_HZ:
        raise ValueError(
            f"{label}={freq} Hz fora do intervalo "
            f"[{MIN_FREQ_HZ}, {MAX_FREQ_HZ}] Hz"
        )
    return freq


def validate_amplitude(amp: float, label: str = "amplitude") -> float:
    """Valida amplitude entre 0 e MAX_AMPLITUDE."""
    if not 0.0 <= amp <= MAX_AMPLITUDE:
        raise ValueError(f"{label}={amp} fora de [0, {MAX_AMPLITUDE}]")
    return amp


def validate_duration(dur: float) -> float:
    """Duração deve ser positiva."""
    if dur <= 0:
        raise ValueError(f"Duração deve ser > 0, recebeu {dur}")
    return dur


def validate_sample_rate(sr: int) -> int:
    """Sample rate deve ser >= 8000."""
    if sr < 8000:
        raise ValueError(f"Sample rate deve ser >= 8000, recebeu {sr}")
    return sr


def normalize_audio(
    signal: NDArray[np.float64],
    target_peak: float = 0.95,
) -> NDArray[np.float64]:
    """
    Normaliza o sinal para que o pico absoluto = *target_peak*.
    Evita clipping sem alterar a dinâmica relativa.
    """
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal * (target_peak / peak)


def soft_clip(
    signal: NDArray[np.float64],
    threshold: float = 0.95,
) -> NDArray[np.float64]:
    """Aplica soft‑clipping (tanh) acima do limiar."""
    mask = np.abs(signal) > threshold
    if not np.any(mask):
        return signal
    out = signal.copy()
    out[mask] = threshold * np.tanh(signal[mask] / threshold)
    return out


def db_to_linear(db: float) -> float:
    """Converte dB para fator linear."""
    return 10.0 ** (db / 20.0)


def linear_to_db(linear: float) -> float:
    """Converte fator linear para dB."""
    if linear <= 0:
        return -120.0
    return 20.0 * np.log10(linear)


def seconds_to_samples(seconds: float, sample_rate: int) -> int:
    """Converte duração em segundos para número de amostras."""
    return int(round(seconds * sample_rate))


def make_time_array(
    duration: float,
    sample_rate: int,
) -> NDArray[np.float64]:
    """Cria vetor de tempo."""
    n = seconds_to_samples(duration, sample_rate)
    return np.linspace(0, duration, n, endpoint=False, dtype=np.float64)
