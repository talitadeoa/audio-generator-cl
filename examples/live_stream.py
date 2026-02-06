#!/usr/bin/env python3
"""
live_stream.py — Exemplo de geração contínua tipo "live stream".

Gera blocos de áudio binaural em loop infinito e reproduz em tempo real,
similar à live contínua do canal Brain Waves (YouTube).

Uso:
    python examples/live_stream.py
    python examples/live_stream.py --freq-left 528 --freq-right 535.83
"""

from __future__ import annotations

import argparse
import sys
import time

import numpy as np

# Adicionar src ao path se executando diretamente
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent / "src"))

from binaural_generator.config import (
    EnvelopeConfig,
    LayerConfig,
    Mode,
    SessionConfig,
    WaveformType,
)
from binaural_generator.mixer import mix_session
from binaural_generator.playback import Player


def main() -> None:
    parser = argparse.ArgumentParser(description="🎧 Live Binaural Stream")
    parser.add_argument("--freq-left", type=float, default=200.0, help="Freq canal esquerdo (Hz)")
    parser.add_argument("--freq-right", type=float, default=210.0, help="Freq canal direito (Hz)")
    parser.add_argument("--waveform", choices=["sine", "triangle", "sawtooth"], default="sine")
    parser.add_argument("--noise-level", type=float, default=0.1, help="Volume do ruído rosa (0–1)")
    parser.add_argument("--block-duration", type=float, default=300.0, help="Duração de cada bloco (s)")
    args = parser.parse_args()

    beat = abs(args.freq_left - args.freq_right)
    print("═" * 60)
    print("  🧠 BINAURAL GENERATOR — Live Stream Mode")
    print("═" * 60)
    print(f"  Freq L: {args.freq_left} Hz | Freq R: {args.freq_right} Hz")
    print(f"  Beat: {beat:.2f} Hz | Waveform: {args.waveform}")
    print(f"  Bloco: {args.block_duration}s | Ruído rosa: {args.noise_level}")
    print("  🎧 Use fones de ouvido para efeito binaural!")
    print("  Pressione Ctrl+C para parar.")
    print("═" * 60)

    # Configuração da sessão
    layers = [
        LayerConfig(
            waveform=WaveformType(args.waveform),
            freq_left=args.freq_left,
            freq_right=args.freq_right,
            amplitude=0.65,
            mode=Mode.BINAURAL,
            envelope=EnvelopeConfig(fade_in=3.0, fade_out=3.0),
        ),
    ]
    if args.noise_level > 0:
        layers.append(LayerConfig(
            waveform=WaveformType.PINK_NOISE,
            freq_left=100.0,
            freq_right=100.0,
            amplitude=args.noise_level,
            mode=Mode.MONO,
            envelope=EnvelopeConfig(fade_in=5.0, fade_out=5.0),
        ))

    config = SessionConfig(
        name="live-stream",
        description="Modo live stream contínuo",
        duration=args.block_duration,
        layers=layers,
        loop=True,
    )

    # Gerar sinal
    print("\n  ⏳ Gerando buffer inicial...")
    signal = mix_session(config)
    print(f"  ✅ Buffer pronto ({len(signal)} amostras)")

    # Reproduzir em loop
    player = Player(signal, config.sample_rate, loop=True)
    player.play()

    start_time = time.time()
    try:
        while player.playing:
            elapsed = time.time() - start_time
            hrs, rem = divmod(int(elapsed), 3600)
            mins, secs = divmod(rem, 60)
            bar_width = 30
            progress = (player.current_time % config.duration) / config.duration
            filled = int(bar_width * progress)
            bar = "█" * filled + "░" * (bar_width - filled)
            print(
                f"\r  ▶ {hrs:02d}:{mins:02d}:{secs:02d}  "
                f"[{bar}] "
                f"Beat: {beat:.1f} Hz  ",
                end="",
                flush=True,
            )
            time.sleep(0.5)
    except KeyboardInterrupt:
        player.stop()
        elapsed = time.time() - start_time
        mins, secs = divmod(int(elapsed), 60)
        print(f"\n\n  ⏹ Parado após {mins}m {secs}s.")
        print("  🙏 Namastê!")


if __name__ == "__main__":
    main()
