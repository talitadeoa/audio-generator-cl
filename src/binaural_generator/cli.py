"""
cli.py — Interface de linha de comando (Click) para o binaural‑generator.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import click

from .config import (
    DEFAULT_AMPLITUDE,
    DEFAULT_BIT_DEPTH,
    DEFAULT_DURATION,
    DEFAULT_SAMPLE_RATE,
    EnvelopeConfig,
    LayerConfig,
    Mode,
    SessionConfig,
    WaveformType,
)
from .mixer import mix_session
from .presets import (
    BUILTIN_PRESETS,
    get_builtin_preset,
    list_presets,
    load_preset,
)
from .renderer import get_metadata_from_config, render_mp3, render_wav
from .utils import validate_frequency


# ── Grupo principal ──────────────────────────────────────────────────

@click.group()
@click.version_option("1.0.0", prog_name="binaural-generator")
def cli() -> None:
    """🧠 Binaural Generator — Sons binaurais/isochrônicos para cura, foco e elevação."""
    pass


# ── Comando: generate ────────────────────────────────────────────────

@cli.command()
@click.option("--preset", "-p", default=None, help="Nome do preset (focus, meditation, sleep, elevation, live).")
@click.option("--freq-left", "-fl", type=float, default=None, help="Frequência do canal esquerdo (Hz).")
@click.option("--freq-right", "-fr", type=float, default=None, help="Frequência do canal direito (Hz).")
@click.option("--waveform", "-w", type=click.Choice([w.value for w in WaveformType], case_sensitive=False), default="sine", help="Forma de onda.")
@click.option("--mode", "-m", type=click.Choice([m.value for m in Mode], case_sensitive=False), default="binaural", help="Modo de geração.")
@click.option("--duration", "-d", type=float, default=None, help="Duração em segundos.")
@click.option("--sample-rate", "-sr", type=int, default=DEFAULT_SAMPLE_RATE, help="Sample rate (Hz).")
@click.option("--bit-depth", type=click.Choice(["16", "24"]), default="24", help="Bit depth do WAV.")
@click.option("--amplitude", "-a", type=float, default=DEFAULT_AMPLITUDE, help="Amplitude (0.0–1.0).")
@click.option("--isochronic-rate", type=float, default=10.0, help="Taxa isocrônica (Hz).")
@click.option("--attack", type=float, default=0.01, help="Tempo de attack (s).")
@click.option("--release", type=float, default=0.05, help="Tempo de release (s).")
@click.option("--fade-in", type=float, default=2.0, help="Fade in (s).")
@click.option("--fade-out", type=float, default=2.0, help="Fade out (s).")
@click.option("--format", "-f", "fmt", type=click.Choice(["wav", "mp3"]), default="wav", help="Formato de saída.")
@click.option("--out", "-o", type=click.Path(), default=None, help="Arquivo de saída.")
def generate(**kwargs: object) -> None:
    """Gera um arquivo de áudio binaural/isocrônico."""
    config = _build_config_from_opts(kwargs)

    click.echo(f"🎵 Gerando: {config.name}")
    click.echo(f"   Duração: {config.duration:.0f}s | SR: {config.sample_rate} | {config.bit_depth}-bit")
    if config.layers:
        l0 = config.layers[0]
        click.echo(f"   Freq L: {l0.freq_left} Hz | Freq R: {l0.freq_right} Hz | Beat: {abs(l0.freq_left - l0.freq_right):.2f} Hz")
        click.echo(f"   Waveform: {l0.waveform.value} | Modo: {l0.mode.value}")

    t0 = time.time()
    signal = mix_session(config)
    elapsed_mix = time.time() - t0
    click.echo(f"   ✅ Síntese concluída em {elapsed_mix:.2f}s")

    # Determinar arquivo de saída
    out_path = kwargs.get("out") or kwargs.get("output_file")
    fmt = str(kwargs.get("fmt", "wav"))
    if out_path is None:
        out_path = f"{config.name}.{fmt}"
    out_path = Path(str(out_path))

    meta = get_metadata_from_config(config)

    t0 = time.time()
    if fmt == "mp3":
        render_mp3(signal, out_path, config.sample_rate, metadata=meta)
    else:
        render_wav(signal, out_path, config.sample_rate, config.bit_depth, metadata=meta)
    elapsed_render = time.time() - t0

    click.echo(f"   💾 Salvo em: {out_path} ({elapsed_render:.2f}s)")
    click.echo("   🎧 Use fones de ouvido para efeito binaural!")


# ── Comando: play ────────────────────────────────────────────────────

@cli.command()
@click.option("--preset", "-p", default="live", help="Nome do preset.")
@click.option("--freq-left", "-fl", type=float, default=None)
@click.option("--freq-right", "-fr", type=float, default=None)
@click.option("--waveform", "-w", type=click.Choice([w.value for w in WaveformType], case_sensitive=False), default="sine")
@click.option("--mode", "-m", type=click.Choice([m.value for m in Mode], case_sensitive=False), default="binaural")
@click.option("--duration", "-d", type=float, default=600)
@click.option("--loop/--no-loop", default=True, help="Loop contínuo.")
@click.option("--amplitude", "-a", type=float, default=DEFAULT_AMPLITUDE)
def play(**kwargs: object) -> None:
    """▶️  Reproduz áudio binaural em tempo real (requer sounddevice)."""
    from .playback import Player

    config = _build_config_from_opts(kwargs)
    config.loop = bool(kwargs.get("loop", True))

    click.echo(f"▶️  Reproduzindo: {config.name} {'(loop)' if config.loop else ''}")
    click.echo(f"   Beat: {config.beat_frequency:.2f} Hz")
    click.echo("   Pressione Ctrl+C para parar.\n")

    signal = mix_session(config)
    player = Player(signal, config.sample_rate, config.loop)
    player.play()

    try:
        while player.playing:
            elapsed = player.current_time
            mins, secs = divmod(int(elapsed), 60)
            hrs, mins = divmod(mins, 60)
            click.echo(f"\r   ⏱  {hrs:02d}:{mins:02d}:{secs:02d}", nl=False)
            time.sleep(0.5)
    except KeyboardInterrupt:
        player.stop()
        click.echo("\n\n   ⏹  Parado.")


# ── Comando: batch ───────────────────────────────────────────────────

@cli.command()
@click.option("--presets", "-p", multiple=True, default=None, help="Presets para gerar (pode repetir).")
@click.option("--all", "all_presets", is_flag=True, help="Gerar todos os presets disponíveis.")
@click.option("--duration", "-d", type=float, default=None, help="Duração override (s).")
@click.option("--format", "-f", "fmt", type=click.Choice(["wav", "mp3"]), default="wav")
@click.option("--outdir", type=click.Path(), default="output", help="Diretório de saída.")
def batch(**kwargs: object) -> None:
    """📦 Gera múltiplos arquivos em lote."""
    outdir = Path(str(kwargs.get("outdir", "output")))
    outdir.mkdir(parents=True, exist_ok=True)
    fmt = str(kwargs.get("fmt", "wav"))
    duration_override = kwargs.get("duration")

    preset_names: list[str] = []
    if kwargs.get("all_presets"):
        preset_names = list(BUILTIN_PRESETS.keys()) + list_presets()
        preset_names = list(dict.fromkeys(preset_names))  # dedup
    elif kwargs.get("presets"):
        preset_names = list(kwargs["presets"])  # type: ignore[arg-type]
    else:
        click.echo("❌ Especifique --presets ou --all")
        sys.exit(1)

    click.echo(f"📦 Batch: {len(preset_names)} preset(s) → {outdir}/")

    for name in preset_names:
        try:
            config = _load_any_preset(name)
        except (FileNotFoundError, KeyError) as e:
            click.echo(f"   ⚠️  {name}: {e}")
            continue

        if duration_override is not None:
            config.duration = float(duration_override)

        click.echo(f"   🎵 {name}...", nl=False)
        signal = mix_session(config)
        out_path = outdir / f"{name}.{fmt}"
        meta = get_metadata_from_config(config)

        if fmt == "mp3":
            render_mp3(signal, out_path, config.sample_rate, metadata=meta)
        else:
            render_wav(signal, out_path, config.sample_rate, config.bit_depth, metadata=meta)

        click.echo(f" ✅ {out_path}")

    click.echo("📦 Batch completo!")


# ── Comando: list-presets ────────────────────────────────────────────

@cli.command("list-presets")
def list_presets_cmd() -> None:
    """📋 Lista todos os presets disponíveis."""
    click.echo("📋 Presets embutidos:")
    for name, data in BUILTIN_PRESETS.items():
        desc = data.get("description", "")
        click.echo(f"   • {name:20s} — {desc}")

    file_presets = list_presets()
    if file_presets:
        click.echo("\n📁 Presets em arquivo:")
        for name in file_presets:
            click.echo(f"   • {name}")


# ── Comando: tui ─────────────────────────────────────────────────────

@cli.command()
def tui() -> None:
    """🖥  Abre a interface interativa (TUI)."""
    try:
        from .tui import BinauralApp
        app = BinauralApp()
        app.run()
    except ImportError:
        click.echo("❌ textual não instalado. Instale com: pip install textual")
        sys.exit(1)


# ── Helpers ──────────────────────────────────────────────────────────

def _build_config_from_opts(opts: dict) -> SessionConfig:
    """Constrói SessionConfig a partir das opções da CLI."""
    preset_name = opts.get("preset")

    if preset_name:
        config = _load_any_preset(str(preset_name))
    else:
        config = SessionConfig()

    # Overrides explícitos
    if opts.get("freq_left") is not None:
        for layer in config.layers:
            layer.freq_left = float(opts["freq_left"])  # type: ignore[arg-type]
    if opts.get("freq_right") is not None:
        for layer in config.layers:
            layer.freq_right = float(opts["freq_right"])  # type: ignore[arg-type]
    if opts.get("waveform"):
        wf = WaveformType(str(opts["waveform"]))
        for layer in config.layers:
            layer.waveform = wf
    if opts.get("mode"):
        md = Mode(str(opts["mode"]))
        for layer in config.layers:
            layer.mode = md
    if opts.get("duration") is not None:
        config.duration = float(opts["duration"])  # type: ignore[arg-type]
    if opts.get("sample_rate"):
        config.sample_rate = int(opts["sample_rate"])  # type: ignore[arg-type]
    if opts.get("bit_depth"):
        config.bit_depth = int(opts["bit_depth"])  # type: ignore[arg-type]
    if opts.get("amplitude") is not None:
        amp = float(opts["amplitude"])  # type: ignore[arg-type]
        for layer in config.layers:
            layer.amplitude = amp
    if opts.get("isochronic_rate"):
        for layer in config.layers:
            layer.isochronic_rate = float(opts["isochronic_rate"])  # type: ignore[arg-type]
    # Envelope overrides
    for layer in config.layers:
        if opts.get("attack") is not None:
            layer.envelope.attack = float(opts["attack"])  # type: ignore[arg-type]
        if opts.get("release") is not None:
            layer.envelope.release = float(opts["release"])  # type: ignore[arg-type]
        if opts.get("fade_in") is not None:
            layer.envelope.fade_in = float(opts["fade_in"])  # type: ignore[arg-type]
        if opts.get("fade_out") is not None:
            layer.envelope.fade_out = float(opts["fade_out"])  # type: ignore[arg-type]

    return config


def _load_any_preset(name: str) -> SessionConfig:
    """Tenta carregar de arquivo, depois de builtin."""
    try:
        return load_preset(name)
    except FileNotFoundError:
        return get_builtin_preset(name)


# ── Entry point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()
