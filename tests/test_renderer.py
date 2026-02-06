"""Testes para renderer.py."""

import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from binaural_generator.config import SessionConfig, LayerConfig, EnvelopeConfig
from binaural_generator.renderer import render_wav, get_metadata_from_config


@pytest.fixture
def stereo_signal() -> np.ndarray:
    """1 segundo de seno estéreo."""
    t = np.linspace(0, 1, 44100, endpoint=False)
    left = 0.5 * np.sin(2 * np.pi * 440 * t)
    right = 0.5 * np.sin(2 * np.pi * 445 * t)
    return np.column_stack((left, right))


class TestRenderWav:
    def test_creates_file(self, stereo_signal: np.ndarray, tmp_path: Path) -> None:
        out = tmp_path / "test.wav"
        result = render_wav(stereo_signal, out, 44100, 24)
        assert result.exists()
        assert result.suffix == ".wav"

    def test_file_readable(self, stereo_signal: np.ndarray, tmp_path: Path) -> None:
        out = tmp_path / "test.wav"
        render_wav(stereo_signal, out, 44100, 16)
        data, sr = sf.read(str(out))
        assert sr == 44100
        assert data.shape[0] == 44100
        assert data.shape[1] == 2

    def test_16bit(self, stereo_signal: np.ndarray, tmp_path: Path) -> None:
        out = tmp_path / "test16.wav"
        render_wav(stereo_signal, out, 44100, 16)
        info = sf.info(str(out))
        assert info.subtype == "PCM_16"

    def test_24bit(self, stereo_signal: np.ndarray, tmp_path: Path) -> None:
        out = tmp_path / "test24.wav"
        render_wav(stereo_signal, out, 44100, 24)
        info = sf.info(str(out))
        assert info.subtype == "PCM_24"

    def test_metadata_sidecar(self, stereo_signal: np.ndarray, tmp_path: Path) -> None:
        out = tmp_path / "meta_test.wav"
        meta = {"preset": "test", "version": "1.0"}
        render_wav(stereo_signal, out, 44100, metadata=meta)
        sidecar = out.with_suffix(".meta.json")
        assert sidecar.exists()
        loaded = json.loads(sidecar.read_text())
        assert loaded["preset"] == "test"

    def test_nested_dir(self, stereo_signal: np.ndarray, tmp_path: Path) -> None:
        out = tmp_path / "sub" / "dir" / "test.wav"
        render_wav(stereo_signal, out, 44100)
        assert out.exists()


class TestGetMetadata:
    def test_metadata_structure(self) -> None:
        config = SessionConfig(
            name="test_preset",
            description="Test",
            layers=[LayerConfig()],
        )
        meta = get_metadata_from_config(config)
        assert meta["generator"] == "binaural-generator"
        assert meta["preset"] == "test_preset"
        assert "layers" in meta
        assert len(meta["layers"]) == 1
