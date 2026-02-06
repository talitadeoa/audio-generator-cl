"""
presets.py — Carregamento e gerenciamento de presets YAML/JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .config import (
    EnvelopeConfig,
    LayerConfig,
    Mode,
    SessionConfig,
    WaveformType,
)

# Diretório padrão de presets (relativo à raiz do projeto)
_PRESETS_DIR = Path(__file__).resolve().parent.parent.parent / "presets"


def list_presets(presets_dir: Path | None = None) -> list[str]:
    """Retorna nomes dos presets disponíveis."""
    d = presets_dir or _PRESETS_DIR
    if not d.exists():
        return []
    names: list[str] = []
    for f in sorted(d.iterdir()):
        if f.suffix in (".yaml", ".yml", ".json"):
            names.append(f.stem)
    return names


def load_preset(
    name: str,
    presets_dir: Path | None = None,
) -> SessionConfig:
    """
    Carrega um preset pelo nome e retorna SessionConfig.

    Procura por ``<name>.yaml`` ou ``<name>.json`` no diretório de presets.
    """
    d = presets_dir or _PRESETS_DIR
    for ext in (".yaml", ".yml", ".json"):
        path = d / f"{name}{ext}"
        if path.exists():
            return load_preset_file(path)
    raise FileNotFoundError(f"Preset '{name}' não encontrado em {d}")


def load_preset_file(path: Path) -> SessionConfig:
    """Carrega um arquivo de preset (YAML ou JSON)."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    return _dict_to_session(data)


def save_preset(
    config: SessionConfig,
    path: Path,
) -> Path:
    """Salva SessionConfig como YAML."""
    data = _session_to_dict(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


# ── Presets embutidos (programáticos) ────────────────────────────────

BUILTIN_PRESETS: dict[str, dict[str, Any]] = {
    "focus": {
        "name": "focus",
        "description": "Ondas beta (14 Hz) para concentração profunda",
        "duration": 3600,
        "layers": [
            {
                "waveform": "sine",
                "freq_left": 200.0,
                "freq_right": 214.0,
                "amplitude": 0.7,
                "mode": "binaural",
            },
            {
                "waveform": "pink_noise",
                "freq_left": 100.0,
                "freq_right": 100.0,
                "amplitude": 0.15,
                "mode": "mono",
            },
        ],
    },
    "meditation": {
        "name": "meditation",
        "description": "Ondas theta (6 Hz) para meditação profunda",
        "duration": 1800,
        "layers": [
            {
                "waveform": "sine",
                "freq_left": 150.0,
                "freq_right": 156.0,
                "amplitude": 0.6,
                "mode": "binaural",
                "envelope": {"fade_in": 10.0, "fade_out": 10.0},
            },
        ],
    },
    "sleep": {
        "name": "sleep",
        "description": "Ondas delta (2 Hz) para indução do sono",
        "duration": 7200,
        "layers": [
            {
                "waveform": "sine",
                "freq_left": 100.0,
                "freq_right": 102.0,
                "amplitude": 0.5,
                "mode": "binaural",
                "envelope": {"fade_in": 30.0, "fade_out": 60.0},
            },
            {
                "waveform": "pink_noise",
                "freq_left": 80.0,
                "freq_right": 80.0,
                "amplitude": 0.2,
                "mode": "mono",
            },
        ],
    },
    "elevation": {
        "name": "elevation",
        "description": "528 Hz (frequência Solfeggio) + 7.83 Hz (Schumann) para elevação vibracional",
        "duration": 3600,
        "layers": [
            {
                "waveform": "sine",
                "freq_left": 528.0,
                "freq_right": 535.83,
                "amplitude": 0.6,
                "mode": "binaural",
                "envelope": {"fade_in": 15.0, "fade_out": 15.0},
            },
            {
                "waveform": "triangle",
                "freq_left": 396.0,
                "freq_right": 396.0,
                "amplitude": 0.15,
                "mode": "mono",
            },
        ],
    },
    "live": {
        "name": "live",
        "description": "Modo live stream contínuo (alpha 10 Hz)",
        "duration": 600,
        "layers": [
            {
                "waveform": "sine",
                "freq_left": 200.0,
                "freq_right": 210.0,
                "amplitude": 0.65,
                "mode": "binaural",
            },
            {
                "waveform": "pink_noise",
                "freq_left": 100.0,
                "freq_right": 100.0,
                "amplitude": 0.1,
                "mode": "mono",
            },
        ],
    },
}


def get_builtin_preset(name: str) -> SessionConfig:
    """Retorna um preset embutido pelo nome."""
    if name not in BUILTIN_PRESETS:
        available = ", ".join(BUILTIN_PRESETS.keys())
        raise KeyError(f"Preset '{name}' não encontrado. Disponíveis: {available}")
    return _dict_to_session(BUILTIN_PRESETS[name])


# ── Conversões dict ↔ SessionConfig ─────────────────────────────────

def _dict_to_session(data: dict[str, Any]) -> SessionConfig:
    """Converte dicionário (do YAML/JSON) para SessionConfig."""
    layers_data = data.get("layers", [{}])
    layers: list[LayerConfig] = []
    for ld in layers_data:
        env_data = ld.get("envelope", {})
        env = EnvelopeConfig(
            attack=env_data.get("attack", 0.01),
            decay=env_data.get("decay", 0.05),
            sustain=env_data.get("sustain", 1.0),
            release=env_data.get("release", 0.05),
            fade_in=env_data.get("fade_in", 2.0),
            fade_out=env_data.get("fade_out", 2.0),
        )
        layers.append(LayerConfig(
            waveform=WaveformType(ld.get("waveform", "sine")),
            freq_left=ld.get("freq_left", 200.0),
            freq_right=ld.get("freq_right", 210.0),
            amplitude=ld.get("amplitude", 0.8),
            mode=Mode(ld.get("mode", "binaural")),
            isochronic_rate=ld.get("isochronic_rate", 10.0),
            am_depth=ld.get("am_depth", 0.0),
            am_rate=ld.get("am_rate", 0.0),
            fm_depth=ld.get("fm_depth", 0.0),
            fm_rate=ld.get("fm_rate", 0.0),
            pan_left=ld.get("pan_left", 1.0),
            pan_right=ld.get("pan_right", 1.0),
            envelope=env,
        ))
    return SessionConfig(
        name=data.get("name", "custom"),
        description=data.get("description", ""),
        duration=data.get("duration", 300.0),
        sample_rate=data.get("sample_rate", 44100),
        bit_depth=data.get("bit_depth", 24),
        layers=layers,
        loop=data.get("loop", False),
        output_file=data.get("output_file"),
        format=data.get("format", "wav"),
    )


def _session_to_dict(config: SessionConfig) -> dict[str, Any]:
    """Converte SessionConfig para dicionário serializável."""
    layers_out = []
    for layer in config.layers:
        ld: dict[str, Any] = {
            "waveform": layer.waveform.value,
            "freq_left": layer.freq_left,
            "freq_right": layer.freq_right,
            "amplitude": layer.amplitude,
            "mode": layer.mode.value,
        }
        if layer.isochronic_rate != 10.0:
            ld["isochronic_rate"] = layer.isochronic_rate
        if layer.am_depth > 0:
            ld["am_depth"] = layer.am_depth
            ld["am_rate"] = layer.am_rate
        if layer.fm_depth > 0:
            ld["fm_depth"] = layer.fm_depth
            ld["fm_rate"] = layer.fm_rate
        if layer.pan_left != 1.0 or layer.pan_right != 1.0:
            ld["pan_left"] = layer.pan_left
            ld["pan_right"] = layer.pan_right
        env = layer.envelope
        if any([
            env.attack != 0.01, env.decay != 0.05,
            env.sustain != 1.0, env.release != 0.05,
            env.fade_in != 2.0, env.fade_out != 2.0,
        ]):
            ld["envelope"] = {
                "attack": env.attack,
                "decay": env.decay,
                "sustain": env.sustain,
                "release": env.release,
                "fade_in": env.fade_in,
                "fade_out": env.fade_out,
            }
        layers_out.append(ld)
    return {
        "name": config.name,
        "description": config.description,
        "duration": config.duration,
        "sample_rate": config.sample_rate,
        "bit_depth": config.bit_depth,
        "layers": layers_out,
        "loop": config.loop,
        "format": config.format,
    }
