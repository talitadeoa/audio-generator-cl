"""Testes para presets.py."""

from pathlib import Path

import pytest
import yaml

from binaural_generator.config import Mode, SessionConfig, WaveformType
from binaural_generator.presets import (
    BUILTIN_PRESETS,
    get_builtin_preset,
    list_presets,
    load_preset,
    load_preset_file,
    save_preset,
    _dict_to_session,
    _session_to_dict,
)


class TestBuiltinPresets:
    def test_all_builtins_exist(self) -> None:
        expected = {"focus", "meditation", "sleep", "elevation", "live"}
        assert expected.issubset(set(BUILTIN_PRESETS.keys()))

    @pytest.mark.parametrize("name", list(BUILTIN_PRESETS.keys()))
    def test_load_builtin(self, name: str) -> None:
        config = get_builtin_preset(name)
        assert isinstance(config, SessionConfig)
        assert config.name == name
        assert len(config.layers) >= 1
        assert config.duration > 0

    def test_missing_builtin(self) -> None:
        with pytest.raises(KeyError):
            get_builtin_preset("nonexistent")

    def test_focus_preset_values(self) -> None:
        config = get_builtin_preset("focus")
        assert config.layers[0].freq_left == 200.0
        assert config.layers[0].freq_right == 214.0
        assert config.beat_frequency == 14.0


class TestPresetFiles:
    def test_list_presets(self) -> None:
        # Deve encontrar os YAML que criamos
        names = list_presets()
        assert isinstance(names, list)

    def test_load_yaml_preset(self, tmp_path: Path) -> None:
        data = {
            "name": "test",
            "description": "teste",
            "duration": 60,
            "layers": [{
                "waveform": "sine",
                "freq_left": 100.0,
                "freq_right": 110.0,
                "mode": "binaural",
            }],
        }
        path = tmp_path / "test.yaml"
        path.write_text(yaml.dump(data))
        config = load_preset_file(path)
        assert config.name == "test"
        assert config.layers[0].freq_left == 100.0

    def test_save_and_load(self, tmp_path: Path) -> None:
        config = get_builtin_preset("focus")
        path = tmp_path / "saved.yaml"
        save_preset(config, path)
        assert path.exists()
        loaded = load_preset_file(path)
        assert loaded.name == config.name
        assert loaded.layers[0].freq_left == config.layers[0].freq_left


class TestConversions:
    def test_roundtrip(self) -> None:
        config = get_builtin_preset("meditation")
        d = _session_to_dict(config)
        restored = _dict_to_session(d)
        assert restored.name == config.name
        assert restored.duration == config.duration
        assert len(restored.layers) == len(config.layers)
        assert restored.layers[0].freq_left == config.layers[0].freq_left

    def test_defaults(self) -> None:
        config = _dict_to_session({})
        assert config.name == "custom"
        assert len(config.layers) == 1
