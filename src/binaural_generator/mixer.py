"""
mixer.py — Mixagem de múltiplas camadas com controle de volume.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .config import SessionConfig
from .synthesizer import synthesize_layer
from .utils import normalize_audio, soft_clip


def mix_session(config: SessionConfig) -> NDArray[np.float64]:
    """
    Sintetiza e mixa todas as camadas de uma SessionConfig.

    Retorna array estéreo ``(N, 2)`` float64 normalizado.
    """
    if not config.layers:
        raise ValueError("SessionConfig deve ter pelo menos uma camada.")

    n_samples = int(round(config.duration * config.sample_rate))
    mix = np.zeros((n_samples, 2), dtype=np.float64)

    for layer in config.layers:
        stereo = synthesize_layer(layer, config.duration, config.sample_rate)
        # Garantir mesmo comprimento
        length = min(len(stereo), n_samples)
        mix[:length] += stereo[:length]

    # Normalização segura
    mix = normalize_stereo(mix)
    return mix


def normalize_stereo(
    signal: NDArray[np.float64],
    target_peak: float = 0.95,
) -> NDArray[np.float64]:
    """Normaliza sinal estéreo (N, 2) pelo pico global."""
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal * (target_peak / peak)


def mix_layers_realtime(
    layers_signals: list[NDArray[np.float64]],
    volumes: list[float],
) -> NDArray[np.float64]:
    """
    Mixa lista de sinais estéreo com volumes individuais.
    Útil para streaming/buffer em tempo real.
    """
    if not layers_signals:
        raise ValueError("Lista de sinais vazia.")

    max_len = max(s.shape[0] for s in layers_signals)
    mix = np.zeros((max_len, 2), dtype=np.float64)

    for sig, vol in zip(layers_signals, volumes):
        length = sig.shape[0]
        mix[:length] += sig * vol

    mix = soft_clip(mix)
    return mix
