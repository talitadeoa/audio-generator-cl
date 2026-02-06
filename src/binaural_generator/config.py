"""
config.py — Constantes, valores padrão e dataclasses de configuração.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ── Limites globais ──────────────────────────────────────────────────
MIN_FREQ_HZ: float = 0.1
MAX_FREQ_HZ: float = 20_000.0
DEFAULT_SAMPLE_RATE: int = 44_100
DEFAULT_BIT_DEPTH: int = 24
DEFAULT_DURATION: float = 300.0  # 5 min
DEFAULT_AMPLITUDE: float = 0.8
MAX_AMPLITUDE: float = 1.0


class WaveformType(str, Enum):
    """Tipos de forma de onda suportados."""
    SINE = "sine"
    SAWTOOTH = "sawtooth"
    SQUARE = "square"
    TRIANGLE = "triangle"
    PINK_NOISE = "pink_noise"
    WHITE_NOISE = "white_noise"


class Mode(str, Enum):
    """Modos de geração de áudio."""
    BINAURAL = "binaural"
    MONAURAL = "monaural"
    ISOCHRONIC = "isochronic"
    MONO = "mono"


@dataclass
class EnvelopeConfig:
    """Envelope ADSR em segundos."""
    attack: float = 0.01
    decay: float = 0.05
    sustain: float = 1.0    # nível (0–1)
    release: float = 0.05
    fade_in: float = 2.0
    fade_out: float = 2.0


@dataclass
class LayerConfig:
    """Configuração de uma camada de áudio."""
    waveform: WaveformType = WaveformType.SINE
    freq_left: float = 200.0
    freq_right: float = 210.0
    amplitude: float = DEFAULT_AMPLITUDE
    mode: Mode = Mode.BINAURAL
    isochronic_rate: float = 10.0      # Hz — taxa de pulsação isocrônica
    am_depth: float = 0.0              # 0 = sem AM, 1 = 100 %
    am_rate: float = 0.0               # Hz
    fm_depth: float = 0.0              # Hz de desvio
    fm_rate: float = 0.0               # Hz
    pan_left: float = 1.0              # 0–1
    pan_right: float = 1.0             # 0–1
    envelope: EnvelopeConfig = field(default_factory=EnvelopeConfig)


@dataclass
class SessionConfig:
    """Configuração completa de uma sessão de geração."""
    name: str = "custom"
    description: str = ""
    duration: float = DEFAULT_DURATION
    sample_rate: int = DEFAULT_SAMPLE_RATE
    bit_depth: int = DEFAULT_BIT_DEPTH
    layers: list[LayerConfig] = field(default_factory=lambda: [LayerConfig()])
    loop: bool = False
    output_file: Optional[str] = None
    format: str = "wav"                # wav | mp3

    @property
    def beat_frequency(self) -> float:
        """Retorna o beat da primeira camada."""
        if self.layers:
            l = self.layers[0]
            return abs(l.freq_left - l.freq_right)
        return 0.0
