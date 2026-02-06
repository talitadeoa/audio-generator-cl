"""Testes para cli.py — parsing de comandos."""

from click.testing import CliRunner
import pytest

from binaural_generator.cli import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestCLIListPresets:
    def test_list_presets(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["list-presets"])
        assert result.exit_code == 0
        assert "focus" in result.output
        assert "meditation" in result.output
        assert "sleep" in result.output


class TestCLIGenerate:
    def test_generate_default(self, runner: CliRunner, tmp_path) -> None:
        out = str(tmp_path / "test.wav")
        result = runner.invoke(cli, [
            "generate", "--preset", "focus",
            "--duration", "2",
            "--out", out,
        ])
        assert result.exit_code == 0
        assert "Salvo em" in result.output

    def test_generate_custom_freq(self, runner: CliRunner, tmp_path) -> None:
        out = str(tmp_path / "custom.wav")
        result = runner.invoke(cli, [
            "generate",
            "--freq-left", "440",
            "--freq-right", "450",
            "--duration", "1",
            "--out", out,
        ])
        assert result.exit_code == 0

    def test_generate_with_waveform(self, runner: CliRunner, tmp_path) -> None:
        out = str(tmp_path / "square.wav")
        result = runner.invoke(cli, [
            "generate",
            "--waveform", "square",
            "--duration", "1",
            "--out", out,
        ])
        assert result.exit_code == 0

    def test_generate_16bit(self, runner: CliRunner, tmp_path) -> None:
        out = str(tmp_path / "16bit.wav")
        result = runner.invoke(cli, [
            "generate", "--preset", "focus",
            "--duration", "1",
            "--bit-depth", "16",
            "--out", out,
        ])
        assert result.exit_code == 0


class TestCLIBatch:
    def test_batch_specific(self, runner: CliRunner, tmp_path) -> None:
        result = runner.invoke(cli, [
            "batch",
            "--presets", "focus",
            "--presets", "sleep",
            "--duration", "1",
            "--outdir", str(tmp_path),
        ])
        assert result.exit_code == 0
        assert "Batch completo" in result.output

    def test_batch_no_presets(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["batch"])
        assert result.exit_code != 0 or "Especifique" in result.output


class TestCLIVersion:
    def test_version(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--version"])
        assert "1.0.0" in result.output
