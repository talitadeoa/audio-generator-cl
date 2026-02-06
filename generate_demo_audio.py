#!/usr/bin/env python3
"""Gera arquivos de áudio demo para escuta."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from binaural_generator.presets import get_builtin_preset
from binaural_generator.mixer import mix_session
from binaural_generator.renderer import render_wav, get_metadata_from_config


def main() -> None:
    configs = {
        "focus_30s": ("focus", "Concentração — Ondas Beta 14 Hz"),
        "meditation_30s": ("meditation", "Meditação — Ondas Theta 6 Hz"),
        "sleep_30s": ("sleep", "Sono — Ondas Delta 2 Hz"),
        "elevation_30s": ("elevation", "Elevação — 528 Hz Solfeggio"),
    }

    demo_dir = Path("demo_audio")
    demo_dir.mkdir(exist_ok=True)

    print("🎵 Gerando demos de áudio...\n")

    for filename, (preset_name, description) in configs.items():
        config = get_builtin_preset(preset_name)
        config.duration = 30  # 30 segundos
        
        print(f"  ⏳ {description}")
        signal = mix_session(config)
        meta = get_metadata_from_config(config)
        
        out_path = demo_dir / f"{filename}.wav"
        render_wav(signal, out_path, config.sample_rate, config.bit_depth, meta)
        
        size_mb = out_path.stat().st_size / (1024 * 1024)
        print(f"     ✅ {out_path.name} ({size_mb:.2f} MB)\n")

    print(f"📁 Arquivos em: {demo_dir.resolve()}\n")
    print("🎧 Use fones de ouvido para sentir o efeito binaural!\n")


if __name__ == "__main__":
    main()
