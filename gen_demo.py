#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pathlib import Path
from binaural_generator.presets import get_builtin_preset
from binaural_generator.mixer import mix_session
from binaural_generator.renderer import render_wav, get_metadata_from_config

# Gerar 4 arquivos de 30 segundos
demos = [
    ("focus", "Concentração Beta 14Hz"),
    ("meditation", "Meditação Theta 6Hz"),
    ("sleep", "Sono Delta 2Hz"),
    ("elevation", "Elevação 528Hz Solfeggio"),
]

Path("demo_audio").mkdir(exist_ok=True)

print("\n🎵 Gerando arquivos de áudio demo...\n")
for preset, desc in demos:
    config = get_builtin_preset(preset)
    config.duration = 30
    signal = mix_session(config)
    meta = get_metadata_from_config(config)
    out = Path("demo_audio") / f"{preset}_30s.wav"
    render_wav(signal, out, config.sample_rate, config.bit_depth, meta)
    size = out.stat().st_size / (1024*1024)
    print(f"  ✅ {preset}_30s.wav ({size:.2f}MB) — {desc}")

print("\n🎧 Demos geradas em: demo_audio/\n")
