#!/usr/bin/env python3
"""
frequency_progression.py — Geração programática de progressões de frequência.

Gera uma sessão que alterna entre diferentes faixas de ondas cerebrais,
criando uma "jornada" meditativa:
  Beta (alerta) → Alpha (relaxamento) → Theta (meditação) → Delta (sono)

Uso:
    python examples/frequency_progression.py
"""

from __future__ import annotations

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent / "src"))

import numpy as np
from binaural_generator.config import (
    EnvelopeConfig,
    LayerConfig,
    Mode,
    SessionConfig,
    WaveformType,
)
from binaural_generator.mixer import mix_session
from binaural_generator.renderer import render_wav, get_metadata_from_config
from binaural_generator.utils import normalize_audio


# Progressão: cada etapa (nome, beat_hz, duração_min)
PROGRESSION = [
    ("Beta — Alerta",        14.0, 5),
    ("Alpha — Relaxamento",  10.0, 10),
    ("Theta — Meditação",     6.0, 15),
    ("Deep Theta",            4.5, 10),
    ("Delta — Sono profundo", 2.0, 20),
]

BASE_FREQ = 180.0  # Portadora base (Hz)
SAMPLE_RATE = 44100


def main() -> None:
    print("═" * 60)
    print("  🧠 Progressão de Frequências — Jornada Meditativa")
    print("═" * 60)

    all_segments: list[np.ndarray] = []

    for name, beat, duration_min in PROGRESSION:
        duration_sec = duration_min * 60
        freq_right = BASE_FREQ + beat

        print(f"  ⏳ {name}: {beat} Hz beat, {duration_min} min...")

        config = SessionConfig(
            name=name,
            duration=duration_sec,
            sample_rate=SAMPLE_RATE,
            layers=[
                LayerConfig(
                    waveform=WaveformType.SINE,
                    freq_left=BASE_FREQ,
                    freq_right=freq_right,
                    amplitude=0.6,
                    mode=Mode.BINAURAL,
                    envelope=EnvelopeConfig(
                        fade_in=min(10.0, duration_sec / 4),
                        fade_out=min(10.0, duration_sec / 4),
                    ),
                ),
                LayerConfig(
                    waveform=WaveformType.PINK_NOISE,
                    freq_left=100.0,
                    freq_right=100.0,
                    amplitude=0.08,
                    mode=Mode.MONO,
                    envelope=EnvelopeConfig(
                        fade_in=5.0,
                        fade_out=5.0,
                    ),
                ),
            ],
        )
        segment = mix_session(config)
        all_segments.append(segment)
        print(f"     ✅ {len(segment)} amostras")

    # Concatenar todos os segmentos
    print("\n  🔗 Concatenando segmentos...")
    full_signal = np.vstack(all_segments)

    # Crossfade entre segmentos (2 segundos)
    # (simplificado — os fades já aplicados fazem a transição suave)

    total_min = sum(d for _, _, d in PROGRESSION)
    print(f"  📊 Total: {total_min} min ({len(full_signal)} amostras)")

    # Salvar
    out_path = "meditation_journey.wav"
    meta = {
        "generator": "binaural-generator",
        "type": "frequency_progression",
        "stages": [{"name": n, "beat_hz": b, "minutes": m} for n, b, m in PROGRESSION],
    }
    render_wav(full_signal, out_path, SAMPLE_RATE, 24, meta)
    print(f"\n  💾 Salvo em: {out_path}")
    print("  🎧 Use fones de ouvido!")
    print("═" * 60)


if __name__ == "__main__":
    main()
