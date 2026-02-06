"""
tui.py — Interface interativa (TUI) com Textual.

Funcionalidades:
- Escolha de presets
- Sliders de frequência, volume, duração
- Visualização ASCII da forma de onda
- Botões para render e playback
"""

from __future__ import annotations

import math
import threading
from typing import Optional

import numpy as np

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
    from textual.widgets import (
        Button,
        Footer,
        Header,
        Label,
        OptionList,
        Static,
        Select,
        Input,
        ProgressBar,
    )
    from textual.widgets.option_list import Option
    from textual.reactive import reactive
    from textual import on

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False


if TEXTUAL_AVAILABLE:

    from .config import (
        Mode,
        WaveformType,
        DEFAULT_SAMPLE_RATE,
    )
    from .presets import BUILTIN_PRESETS, get_builtin_preset
    from .mixer import mix_session
    from .renderer import render_wav, get_metadata_from_config

    class WaveformDisplay(Static):
        """Widget que mostra forma de onda em ASCII."""

        signal_data: reactive[str] = reactive("")

        def render(self) -> str:
            return self.signal_data or "  Nenhum sinal gerado ainda..."

        def update_waveform(self, signal: np.ndarray, width: int = 70, height: int = 12) -> None:
            """Gera representação ASCII de uma forma de onda."""
            if signal.ndim == 2:
                mono = signal[:, 0]  # canal esquerdo
            else:
                mono = signal

            # Downsample para caber na largura
            n = len(mono)
            step = max(n // width, 1)
            samples = mono[::step][:width]

            # Normalizar para [0, height-1]
            mn, mx = samples.min(), samples.max()
            if mx - mn == 0:
                norm = np.full_like(samples, height // 2)
            else:
                norm = ((samples - mn) / (mx - mn) * (height - 1)).astype(int)

            # Desenhar
            lines: list[str] = []
            for row in range(height - 1, -1, -1):
                chars: list[str] = []
                for col in range(len(norm)):
                    if int(norm[col]) == row:
                        chars.append("█")
                    elif row == height // 2:
                        chars.append("─")
                    else:
                        chars.append(" ")
                lines.append("│" + "".join(chars) + "│")
            lines.insert(0, "┌" + "─" * len(norm) + "┐")
            lines.append("└" + "─" * len(norm) + "┘")

            self.signal_data = "\n".join(lines)

    class SpectrogramDisplay(Static):
        """Mini espectrograma ASCII."""

        spectrum_data: reactive[str] = reactive("")

        def render(self) -> str:
            return self.spectrum_data or "  Espectrograma..."

        def update_spectrum(self, signal: np.ndarray, sample_rate: int = 44100) -> None:
            """Gera mini espectrograma ASCII."""
            if signal.ndim == 2:
                mono = signal[:, 0]
            else:
                mono = signal

            # FFT de um trecho
            chunk = mono[:4096]
            fft = np.abs(np.fft.rfft(chunk))
            freqs = np.fft.rfftfreq(len(chunk), 1 / sample_rate)

            # Agrupar em bandas
            bands = [
                ("Sub", 0, 20),
                ("Delta", 0.5, 4),
                ("Theta", 4, 8),
                ("Alpha", 8, 14),
                ("Beta", 14, 30),
                ("Gamma", 30, 100),
                ("Low", 100, 500),
                ("Mid", 500, 2000),
                ("High", 2000, 8000),
            ]

            max_bar = 30
            lines: list[str] = ["  ╔══ Espectro ══════════════════════╗"]
            global_max = fft.max() if fft.max() > 0 else 1

            for name, lo, hi in bands:
                mask = (freqs >= lo) & (freqs < hi)
                if mask.any():
                    power = fft[mask].mean() / global_max
                else:
                    power = 0
                bar_len = int(power * max_bar)
                bar = "▓" * bar_len + "░" * (max_bar - bar_len)
                lines.append(f"  ║ {name:6s} │{bar}║")

            lines.append("  ╚═════════════════════════════════════╝")
            self.spectrum_data = "\n".join(lines)

    class BinauralApp(App):
        """Aplicação TUI principal."""

        CSS = """
        Screen {
            layout: vertical;
        }
        #main-container {
            layout: horizontal;
            height: 1fr;
        }
        #left-panel {
            width: 35;
            border: solid green;
            padding: 1;
        }
        #right-panel {
            width: 1fr;
            border: solid cyan;
            padding: 1;
        }
        .param-row {
            layout: horizontal;
            height: 3;
            margin-bottom: 1;
        }
        .param-label {
            width: 14;
            padding-top: 1;
        }
        .param-input {
            width: 1fr;
        }
        Button {
            margin: 1;
        }
        #status-bar {
            height: 3;
            border: solid yellow;
            padding: 1;
        }
        #waveform-display {
            height: 16;
            border: solid blue;
        }
        #spectrum-display {
            height: 14;
            border: solid magenta;
        }
        .action-buttons {
            layout: horizontal;
            height: 5;
        }
        """

        TITLE = "🧠 Binaural Generator"
        SUB_TITLE = "Sons binaurais para cura, foco e elevação"

        BINDINGS = [
            ("q", "quit", "Sair"),
            ("g", "generate", "Gerar WAV"),
            ("p", "play_audio", "Reproduzir"),
            ("r", "refresh", "Atualizar forma de onda"),
        ]

        current_preset: reactive[str] = reactive("focus")
        status_text: reactive[str] = reactive("Pronto. Escolha um preset e ajuste os parâmetros.")

        def compose(self) -> ComposeResult:
            yield Header()

            with Container(id="main-container"):
                with Vertical(id="left-panel"):
                    yield Label("🎛  PRESETS", classes="section-title")
                    yield Select(
                        [(name, name) for name in BUILTIN_PRESETS.keys()],
                        value="focus",
                        id="preset-select",
                    )

                    yield Label("\n⚙️  PARÂMETROS", classes="section-title")

                    with Horizontal(classes="param-row"):
                        yield Label("Freq L (Hz):", classes="param-label")
                        yield Input(value="200.0", id="freq-left", classes="param-input")
                    with Horizontal(classes="param-row"):
                        yield Label("Freq R (Hz):", classes="param-label")
                        yield Input(value="210.0", id="freq-right", classes="param-input")
                    with Horizontal(classes="param-row"):
                        yield Label("Amplitude:", classes="param-label")
                        yield Input(value="0.7", id="amplitude", classes="param-input")
                    with Horizontal(classes="param-row"):
                        yield Label("Duração (s):", classes="param-label")
                        yield Input(value="300", id="duration", classes="param-input")
                    with Horizontal(classes="param-row"):
                        yield Label("Waveform:", classes="param-label")
                        yield Select(
                            [(w.value, w.value) for w in WaveformType],
                            value="sine",
                            id="waveform-select",
                        )
                    with Horizontal(classes="param-row"):
                        yield Label("Modo:", classes="param-label")
                        yield Select(
                            [(m.value, m.value) for m in Mode],
                            value="binaural",
                            id="mode-select",
                        )

                    yield Label("")
                    with Horizontal(classes="action-buttons"):
                        yield Button("🎵 Gerar WAV", variant="success", id="btn-generate")
                        yield Button("▶️ Play", variant="primary", id="btn-play")
                    with Horizontal(classes="action-buttons"):
                        yield Button("👁 Preview", variant="warning", id="btn-preview")
                        yield Button("⏹ Stop", variant="error", id="btn-stop")

                with Vertical(id="right-panel"):
                    yield Label("📊 FORMA DE ONDA (preview 1s)")
                    yield WaveformDisplay(id="waveform-display")
                    yield Label("\n📈 ESPECTRO")
                    yield SpectrogramDisplay(id="spectrum-display")

            yield Static(self.status_text, id="status-bar")
            yield Footer()

        def on_mount(self) -> None:
            self._load_preset_params("focus")

        @on(Select.Changed, "#preset-select")
        def preset_changed(self, event: Select.Changed) -> None:
            if event.value and event.value != Select.BLANK:
                self._load_preset_params(str(event.value))

        def _load_preset_params(self, name: str) -> None:
            try:
                config = get_builtin_preset(name)
                if config.layers:
                    l0 = config.layers[0]
                    self.query_one("#freq-left", Input).value = str(l0.freq_left)
                    self.query_one("#freq-right", Input).value = str(l0.freq_right)
                    self.query_one("#amplitude", Input).value = str(l0.amplitude)
                    self.query_one("#duration", Input).value = str(int(config.duration))
                beat = abs(l0.freq_left - l0.freq_right)
                self._update_status(
                    f"Preset: {name} | Beat: {beat:.2f} Hz | {config.description}"
                )
            except Exception as e:
                self._update_status(f"Erro ao carregar preset: {e}")

        def _get_current_config(self) -> "SessionConfig":
            from .config import SessionConfig, LayerConfig, EnvelopeConfig

            fl = float(self.query_one("#freq-left", Input).value or "200")
            fr = float(self.query_one("#freq-right", Input).value or "210")
            amp = float(self.query_one("#amplitude", Input).value or "0.7")
            dur = float(self.query_one("#duration", Input).value or "300")
            wf_select = self.query_one("#waveform-select", Select)
            mode_select = self.query_one("#mode-select", Select)

            wf = WaveformType(str(wf_select.value)) if wf_select.value != Select.BLANK else WaveformType.SINE
            mode = Mode(str(mode_select.value)) if mode_select.value != Select.BLANK else Mode.BINAURAL

            layer = LayerConfig(
                waveform=wf,
                freq_left=fl,
                freq_right=fr,
                amplitude=amp,
                mode=mode,
                envelope=EnvelopeConfig(fade_in=2.0, fade_out=2.0),
            )
            return SessionConfig(
                name="tui-custom",
                duration=dur,
                layers=[layer],
            )

        @on(Button.Pressed, "#btn-preview")
        def action_refresh(self) -> None:
            """Gera preview de 1 segundo e atualiza visualização."""
            try:
                config = self._get_current_config()
                config.duration = 1.0  # Preview curto
                signal = mix_session(config)

                wd = self.query_one("#waveform-display", WaveformDisplay)
                wd.update_waveform(signal)

                sd = self.query_one("#spectrum-display", SpectrogramDisplay)
                sd.update_spectrum(signal, config.sample_rate)

                beat = abs(config.layers[0].freq_left - config.layers[0].freq_right)
                self._update_status(f"Preview gerado | Beat: {beat:.2f} Hz")
            except Exception as e:
                self._update_status(f"Erro no preview: {e}")

        @on(Button.Pressed, "#btn-generate")
        def action_generate(self) -> None:
            """Gera arquivo WAV."""
            self._update_status("Gerando WAV... aguarde.")

            def _gen() -> None:
                try:
                    config = self._get_current_config()
                    signal = mix_session(config)
                    meta = get_metadata_from_config(config)
                    path = render_wav(signal, "output_tui.wav", config.sample_rate, metadata=meta)
                    self.call_from_thread(
                        self._update_status,
                        f"✅ WAV salvo em: {path}",
                    )
                except Exception as e:
                    self.call_from_thread(
                        self._update_status,
                        f"❌ Erro: {e}",
                    )

            threading.Thread(target=_gen, daemon=True).start()

        @on(Button.Pressed, "#btn-play")
        def action_play_audio(self) -> None:
            """Reproduz áudio."""
            self._update_status("Reproduzindo... Pressione Stop para parar.")

            def _play() -> None:
                try:
                    from .playback import Player
                    config = self._get_current_config()
                    config.duration = min(config.duration, 60)  # Limitar preview
                    signal = mix_session(config)
                    self._player = Player(signal, config.sample_rate)
                    self._player.play()
                except Exception as e:
                    self.call_from_thread(
                        self._update_status,
                        f"❌ Erro playback: {e}",
                    )

            threading.Thread(target=_play, daemon=True).start()

        @on(Button.Pressed, "#btn-stop")
        def action_stop(self) -> None:
            if hasattr(self, "_player") and self._player:
                self._player.stop()
                self._update_status("⏹ Parado.")

        def _update_status(self, text: str) -> None:
            try:
                self.query_one("#status-bar", Static).update(text)
            except Exception:
                pass

else:
    # Fallback se textual não estiver disponível
    class BinauralApp:  # type: ignore[no-redef]
        def run(self) -> None:
            print("❌ textual não está instalado.")
            print("   Instale com: pip install textual")
            print("   Ou use a CLI: binaural generate --preset focus")
