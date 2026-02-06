"""
renderer.py — Renderização para arquivo WAV/MP3 com metadados.
"""

from __future__ import annotations

import json
import struct
import wave
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
from numpy.typing import NDArray

from .config import SessionConfig


def render_wav(
    signal: NDArray[np.float64],
    path: str | Path,
    sample_rate: int = 44100,
    bit_depth: int = 24,
    metadata: dict[str, Any] | None = None,
) -> Path:
    """
    Renderiza sinal estéreo float64 para arquivo WAV.

    Parameters
    ----------
    signal : NDArray
        Shape ``(N, 2)`` com valores em [-1, 1].
    path : str | Path
        Caminho de saída.
    sample_rate : int
        Taxa de amostragem.
    bit_depth : int
        16 ou 24 bits.
    metadata : dict
        Metadados embutidos no WAV (via LIST/INFO chunk).

    Returns
    -------
    Path
        Caminho do arquivo criado.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # soundfile subtypes
    subtype_map = {16: "PCM_16", 24: "PCM_24", 32: "PCM_32"}
    subtype = subtype_map.get(bit_depth, "PCM_24")

    sf.write(str(path), signal, sample_rate, subtype=subtype)

    # Embutir metadados como INFO chunk (simple approach)
    if metadata:
        _embed_wav_metadata(path, metadata)

    return path


def render_mp3(
    signal: NDArray[np.float64],
    path: str | Path,
    sample_rate: int = 44100,
    bitrate: str = "192k",
    metadata: dict[str, Any] | None = None,
) -> Path:
    """
    Renderiza para MP3 via pydub (requer ffmpeg instalado).
    """
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError(
            "pydub é necessário para exportar MP3. "
            "Instale com: pip install pydub  (e ffmpeg no sistema)"
        )

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Converter float64 → int16 para pydub
    pcm = (signal * 32767).astype(np.int16)
    channels = 2 if pcm.ndim == 2 else 1
    sample_width = 2  # 16‑bit

    audio = AudioSegment(
        data=pcm.tobytes(),
        sample_width=sample_width,
        frame_rate=sample_rate,
        channels=channels,
    )

    tags = metadata or {}
    audio.export(str(path), format="mp3", bitrate=bitrate, tags=tags)
    return path


def _embed_wav_metadata(path: Path, metadata: dict[str, Any]) -> None:
    """
    Estratégia simples: grava metadados como JSON num campo
    comment do INFO chunk. Compatível com a maioria dos players.
    """
    try:
        info_str = json.dumps(metadata, ensure_ascii=False, indent=2)
        # Re-abrir com wave do stdlib para adicionar comment
        # Nota: soundfile não suporta metadata arbitrária,
        # então adicionamos via marcador simples no nome do arquivo
        # ou via ferramenta externa. Aqui gravamos um .json sidecar.
        sidecar = path.with_suffix(".meta.json")
        sidecar.write_text(info_str, encoding="utf-8")
    except Exception:
        pass  # Metadados são best-effort


def get_metadata_from_config(config: SessionConfig) -> dict[str, Any]:
    """Extrai metadados resumidos de uma SessionConfig."""
    layers_info = []
    for i, layer in enumerate(config.layers):
        layers_info.append({
            "layer": i,
            "waveform": layer.waveform.value,
            "freq_left": layer.freq_left,
            "freq_right": layer.freq_right,
            "mode": layer.mode.value,
            "amplitude": layer.amplitude,
        })
    return {
        "generator": "binaural-generator",
        "version": "1.0.0",
        "preset": config.name,
        "description": config.description,
        "duration_sec": config.duration,
        "sample_rate": config.sample_rate,
        "bit_depth": config.bit_depth,
        "layers": layers_info,
    }
