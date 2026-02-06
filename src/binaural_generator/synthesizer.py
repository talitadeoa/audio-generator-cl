"""
synthesizer.py — Motor de síntese: monta cada camada estéreo.

Modos suportados:
* **binaural**  — freq_left e freq_right em canais separados; o beat é percebido
  pelo cérebro quando se usa fones de ouvido.
* **monaural** — ambas as portadoras somadas em mono, gerando beat audível.
* **isochronic** — tom puro com amplitude gating (pulso on/off).
* **mono** — freq_left apenas, duplicado nos dois canais.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .config import LayerConfig, Mode, WaveformType
from .waveforms import generate_waveform
from .envelope import apply_adsr, apply_fade, isochronic_gate
from .utils import (
    validate_frequency,
    validate_amplitude,
    make_time_array,
)


def synthesize_layer(
    layer: LayerConfig,
    duration: float,
    sample_rate: int,
) -> NDArray[np.float64]:
    """
    Sintetiza uma camada estéreo ``(N, 2)``.

    Retorna array float64 com shape ``(n_samples, 2)``.
    """
    # ── Validação ────────────────────────────────────────────────
    validate_frequency(layer.freq_left, "freq_left")
    validate_frequency(layer.freq_right, "freq_right")
    validate_amplitude(layer.amplitude, "amplitude")

    t = make_time_array(duration, sample_rate)
    n = len(t)

    # ── Modulação FM (aplicada à frequência instantânea) ─────────
    fm_mod = np.zeros(n, dtype=np.float64)
    if layer.fm_depth > 0 and layer.fm_rate > 0:
        fm_mod = layer.fm_depth * np.sin(2 * np.pi * layer.fm_rate * t)

    # ── Gerar portadoras ─────────────────────────────────────────
    left = _gen_carrier(layer.waveform, layer.freq_left + fm_mod, t, layer.amplitude)
    right = _gen_carrier(layer.waveform, layer.freq_right + fm_mod, t, layer.amplitude)

    # ── Modulação AM ─────────────────────────────────────────────
    if layer.am_depth > 0 and layer.am_rate > 0:
        am_env = 1.0 - layer.am_depth * 0.5 * (
            1.0 - np.cos(2 * np.pi * layer.am_rate * t)
        )
        left *= am_env
        right *= am_env

    # ── Montagem por modo ────────────────────────────────────────
    match layer.mode:
        case Mode.BINAURAL:
            stereo = _stereo(left, right)
        case Mode.MONAURAL:
            mono = (left + right) * 0.5
            stereo = _stereo(mono, mono)
        case Mode.ISOCHRONIC:
            mono = generate_waveform(
                layer.waveform, layer.freq_left, t, layer.amplitude,
            )
            gated = isochronic_gate(mono, layer.isochronic_rate, sample_rate)
            stereo = _stereo(gated, gated)
        case Mode.MONO:
            stereo = _stereo(left, left)
        case _:
            raise ValueError(f"Modo desconhecido: {layer.mode}")

    # ── Panning independente ─────────────────────────────────────
    stereo[:, 0] *= layer.pan_left
    stereo[:, 1] *= layer.pan_right

    # ── Envelope ADSR ────────────────────────────────────────────
    stereo[:, 0] = apply_adsr(stereo[:, 0], layer.envelope, sample_rate)
    stereo[:, 1] = apply_adsr(stereo[:, 1], layer.envelope, sample_rate)

    # ── Fades ────────────────────────────────────────────────────
    stereo[:, 0] = apply_fade(
        stereo[:, 0],
        layer.envelope.fade_in,
        layer.envelope.fade_out,
        sample_rate,
    )
    stereo[:, 1] = apply_fade(
        stereo[:, 1],
        layer.envelope.fade_in,
        layer.envelope.fade_out,
        sample_rate,
    )

    return stereo


# ── Helpers internos ─────────────────────────────────────────────────

def _gen_carrier(
    waveform: WaveformType,
    freq: float | NDArray[np.float64],
    t: NDArray[np.float64],
    amp: float,
) -> NDArray[np.float64]:
    """
    Gera portadora; se *freq* for array (FM), calcula fase instantânea.
    """
    if isinstance(freq, np.ndarray):
        # Fase instantânea = integral da freq instantânea
        dt = t[1] - t[0] if len(t) > 1 else 1.0
        phase = 2 * np.pi * np.cumsum(freq) * dt
        return amp * np.sin(phase)
    return generate_waveform(waveform, freq, t, amp)


def _stereo(
    left: NDArray[np.float64],
    right: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Empilha L/R em array (N, 2)."""
    return np.column_stack((left, right))
