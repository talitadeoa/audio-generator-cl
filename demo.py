#!/usr/bin/env python3
"""
demo.py — Script de demonstração completo do Binaural Generator.

Mostra:
1. Geração de áudio com diferentes presets
2. Análise de parâmetros
3. Exemplos de uso da biblioteca Python
4. Criação de visualizações
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import numpy as np
from binaural_generator.config import (
    LayerConfig, Mode, SessionConfig, WaveformType, EnvelopeConfig,
)
from binaural_generator.mixer import mix_session
from binaural_generator.renderer import render_wav, get_metadata_from_config
from binaural_generator.presets import get_builtin_preset, BUILTIN_PRESETS
from binaural_generator.utils import make_time_array


def print_header(text: str) -> None:
    """Imprime cabeçalho com formatação."""
    print("\n" + "═" * 70)
    print(f"  {text}")
    print("═" * 70)


def analyze_preset(name: str) -> None:
    """Analisa e mostra info de um preset."""
    config = get_builtin_preset(name)
    print(f"\n📋 Preset: {name}")
    print(f"   Descrição: {config.description}")
    print(f"   Duração: {config.duration}s | SR: {config.sample_rate} Hz")
    print(f"   Camadas: {len(config.layers)}")
    
    for i, layer in enumerate(config.layers):
        beat = abs(layer.freq_left - layer.freq_right)
        print(f"\n   Layer {i}:")
        print(f"      Waveform: {layer.waveform.value}")
        print(f"      Freq L: {layer.freq_left} Hz | Freq R: {layer.freq_right} Hz")
        print(f"      Beat: {beat:.2f} Hz")
        print(f"      Modo: {layer.mode.value}")
        print(f"      Amplitude: {layer.amplitude}")


def demo_presets() -> None:
    """Demo 1: Analisar todos os presets."""
    print_header("DEMO 1: Análise de Presets Embutidos")
    
    for name in BUILTIN_PRESETS.keys():
        analyze_preset(name)


def demo_custom_generation() -> None:
    """Demo 2: Gerar áudio customizado."""
    print_header("DEMO 2: Geração Customizada")
    
    examples = [
        {
            "name": "theta_meditation",
            "freq_l": 150,
            "freq_r": 156,
            "beat_hz": 6,
            "duration": 10,
            "description": "Ondas theta (6 Hz) para meditação",
        },
        {
            "name": "gamma_clarity",
            "freq_l": 300,
            "freq_r": 340,
            "beat_hz": 40,
            "duration": 10,
            "description": "Pulsos gamma (40 Hz) para clareza",
        },
        {
            "name": "schumann_resonance",
            "freq_l": 100,
            "freq_r": 107.83,
            "beat_hz": 7.83,
            "duration": 10,
            "description": "Frequência Schumann (7.83 Hz) — ressonância terrestre",
        },
    ]
    
    for ex in examples:
        print(f"\n🎛  {ex['name']}")
        print(f"    {ex['description']}")
        print(f"    Portadora: {ex['freq_l']} / {ex['freq_r']} Hz")
        print(f"    Beat: {ex['beat_hz']} Hz")
        
        config = SessionConfig(
            name=ex["name"],
            description=ex["description"],
            duration=ex["duration"],
            layers=[
                LayerConfig(
                    waveform=WaveformType.SINE,
                    freq_left=ex["freq_l"],
                    freq_right=ex["freq_r"],
                    amplitude=0.65,
                    mode=Mode.BINAURAL,
                    envelope=EnvelopeConfig(fade_in=1.0, fade_out=1.0),
                ),
            ],
        )
        
        signal = mix_session(config)
        out_path = Path("demo_output") / f"{ex['name']}.wav"
        render_wav(signal, out_path, config.sample_rate, config.bit_depth)
        print(f"    ✅ Gerado: {out_path}")


def demo_waveforms() -> None:
    """Demo 3: Comparar diferentes formas de onda."""
    print_header("DEMO 3: Comparação de Formas de Onda")
    
    waveforms = [
        (WaveformType.SINE, "sine — suave, relaxante"),
        (WaveformType.TRIANGLE, "triangle — meio-termo"),
        (WaveformType.SQUARE, "square — agressivo, pronunciado"),
        (WaveformType.SAWTOOTH, "sawtooth — harmônicos ricos"),
    ]
    
    for wf, desc in waveforms:
        print(f"\n🎵 {desc}")
        config = SessionConfig(
            name=f"waveform_{wf.value}",
            duration=5,
            layers=[
                LayerConfig(
                    waveform=wf,
                    freq_left=200,
                    freq_right=210,
                    amplitude=0.65,
                    mode=Mode.BINAURAL,
                    envelope=EnvelopeConfig(fade_in=0.5, fade_out=0.5),
                ),
            ],
        )
        
        signal = mix_session(config)
        out_path = Path("demo_output") / f"waveform_{wf.value}.wav"
        render_wav(signal, out_path, config.sample_rate, config.bit_depth)
        print(f"    ✅ {out_path}")


def demo_modes() -> None:
    """Demo 4: Diferentes modos (binaural vs isochronic)."""
    print_header("DEMO 4: Diferentes Modos de Geração")
    
    modes_info = [
        (Mode.BINAURAL, "Binaural — percebido pelo cérebro com fones"),
        (Mode.MONAURAL, "Monaural — beat audível central (sem fones)"),
        (Mode.ISOCHRONIC, "Isochronic — pulsos de amplitude (sem fones)"),
    ]
    
    for mode, desc in modes_info:
        print(f"\n🔊 {desc}")
        config = SessionConfig(
            name=f"mode_{mode.value}",
            duration=5,
            layers=[
                LayerConfig(
                    waveform=WaveformType.SINE,
                    freq_left=200,
                    freq_right=210,
                    amplitude=0.65,
                    mode=mode,
                    isochronic_rate=10.0,
                    envelope=EnvelopeConfig(fade_in=0.5, fade_out=0.5),
                ),
            ],
        )
        
        signal = mix_session(config)
        out_path = Path("demo_output") / f"mode_{mode.value}.wav"
        render_wav(signal, out_path, config.sample_rate, config.bit_depth)
        print(f"    ✅ {out_path}")


def demo_frequency_sweep() -> None:
    """Demo 5: Progressão de frequências (delta → gamma)."""
    print_header("DEMO 5: Progressão de Frequências")
    
    print("\n🎚  Gerando progressão delta → gamma...")
    
    progression = [
        ("delta", 100.0, 102.0, "sono profundo"),
        ("theta", 150.0, 156.0, "meditação"),
        ("alpha", 200.0, 210.0, "relaxamento"),
        ("beta", 200.0, 214.0, "foco"),
        ("gamma", 300.0, 340.0, "clareza"),
    ]
    
    for stage, fl, fr, desc in progression:
        beat = abs(fl - fr)
        print(f"\n   {stage.upper()}: {beat:.1f} Hz ({desc})")
        config = SessionConfig(
            name=f"progression_{stage}",
            duration=8,
            layers=[
                LayerConfig(
                    waveform=WaveformType.SINE,
                    freq_left=fl,
                    freq_right=fr,
                    amplitude=0.6,
                    mode=Mode.BINAURAL,
                    envelope=EnvelopeConfig(fade_in=2.0, fade_out=2.0),
                ),
                LayerConfig(
                    waveform=WaveformType.PINK_NOISE,
                    freq_left=100.0,
                    freq_right=100.0,
                    amplitude=0.08,
                    mode=Mode.MONO,
                ),
            ],
        )
        
        signal = mix_session(config)
        out_path = Path("demo_output") / f"progression_{stage}.wav"
        render_wav(signal, out_path, config.sample_rate, config.bit_depth)
        print(f"      ✅ {out_path}")


def demo_analysis() -> None:
    """Demo 6: Análise de sinal."""
    print_header("DEMO 6: Análise de Sinal (Focus Preset)")
    
    config = get_builtin_preset("focus")
    config.duration = 1.0  # 1 segundo para análise rápida
    
    signal = mix_session(config)
    print(f"\n📊 Sinal estéreo (focus preset, 1s)")
    print(f"   Shape: {signal.shape}")
    print(f"   Dtype: {signal.dtype}")
    print(f"   Pico abs: {np.max(np.abs(signal)):.4f}")
    print(f"   RMS: {np.sqrt(np.mean(signal**2)):.4f}")
    
    # FFT do canal esquerdo
    fft = np.abs(np.fft.rfft(signal[:, 0]))
    freqs = np.fft.rfftfreq(len(signal), 1 / 44100)
    
    # Encontrar picos
    threshold = np.max(fft) * 0.1
    peaks_idx = np.where(fft > threshold)[0]
    
    if len(peaks_idx) > 0:
        print(f"\n   Frequências principais (picos > 10%):")
        for idx in peaks_idx[:5]:  # Top 5
            f = freqs[idx]
            mag = fft[idx]
            print(f"      {f:7.1f} Hz (magnitude: {mag:8.0f})")


def print_summary() -> None:
    """Imprime resumo da demo."""
    print_header("📋 RESUMO DA DEMONSTRAÇÃO")
    
    demo_dir = Path("demo_output")
    wav_files = sorted(demo_dir.glob("*.wav"))
    
    print(f"\n✅ {len(wav_files)} arquivos WAV gerados:")
    total_size = 0
    for wav in wav_files:
        size_mb = wav.stat().st_size / (1024 * 1024)
        total_size += wav.stat().st_size
        print(f"   • {wav.name:40s} ({size_mb:5.2f} MB)")
    
    print(f"\n   Total: {total_size / (1024*1024):.1f} MB")
    
    print("\n🎧 Próximos passos:")
    print("   1. Escute os arquivos com fones de ouvido")
    print("   2. Teste a CLI: binaural --help")
    print("   3. Experimente a TUI: binaural tui")
    print("   4. Veja o README para mais exemplos")


def main() -> None:
    """Executa todas as demos."""
    demo_dir = Path("demo_output")
    demo_dir.mkdir(exist_ok=True)
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "🧠 BINAURAL GENERATOR — DEMO COMPLETA" + " " * 15 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        demo_presets()
        demo_custom_generation()
        demo_waveforms()
        demo_modes()
        demo_frequency_sweep()
        demo_analysis()
        print_summary()
        
        print("\n✨ Demo concluída com sucesso!")
        print(f"📁 Arquivos em: {demo_dir.resolve()}\n")
        
    except Exception as e:
        print(f"\n❌ Erro durante a demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
