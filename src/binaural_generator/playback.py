"""
playback.py — Playback em tempo real via sounddevice (streaming por blocos).
"""

from __future__ import annotations

import threading
import time
from typing import Optional, Callable

import numpy as np
import sounddevice as sd
from numpy.typing import NDArray

from .config import SessionConfig
from .mixer import mix_session


class Player:
    """
    Player de áudio com streaming por blocos.

    Suporta play, stop, loop e callback de progresso.
    """

    def __init__(
        self,
        signal: NDArray[np.float64],
        sample_rate: int = 44100,
        loop: bool = False,
        on_progress: Optional[Callable[[float], None]] = None,
    ) -> None:
        self.signal = signal
        self.sample_rate = sample_rate
        self.loop = loop
        self.on_progress = on_progress
        self._position = 0
        self._playing = False
        self._stream: Optional[sd.OutputStream] = None
        self._thread: Optional[threading.Thread] = None

    @property
    def playing(self) -> bool:
        return self._playing

    @property
    def duration(self) -> float:
        return len(self.signal) / self.sample_rate

    @property
    def current_time(self) -> float:
        return self._position / self.sample_rate

    def play(self) -> None:
        """Inicia playback em thread separada."""
        if self._playing:
            return
        self._playing = True
        self._position = 0
        self._thread = threading.Thread(target=self._play_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Para o playback."""
        self._playing = False
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

    def _play_loop(self) -> None:
        block_size = 2048
        channels = self.signal.shape[1] if self.signal.ndim == 2 else 1

        self._stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=channels,
            dtype="float32",
            blocksize=block_size,
        )
        self._stream.start()

        total = len(self.signal)

        while self._playing:
            end = self._position + block_size
            if end >= total:
                if self.loop:
                    # Pegar o que falta + reiniciar
                    chunk = np.vstack([
                        self.signal[self._position:total],
                        self.signal[:end - total],
                    ])
                    self._position = end - total
                else:
                    chunk = self.signal[self._position:total]
                    self._playing = False
            else:
                chunk = self.signal[self._position:end]
                self._position = end

            if len(chunk) == 0:
                break

            self._stream.write(chunk.astype(np.float32))

            if self.on_progress:
                progress = (self._position % total) / total
                self.on_progress(progress)

        self.stop()


def play_session(config: SessionConfig) -> Player:
    """
    Gera e reproduz uma sessão completa.

    Returns
    -------
    Player
        Instância do player (permite stop).
    """
    signal = mix_session(config)
    player = Player(signal, config.sample_rate, config.loop)
    player.play()
    return player


def play_signal(
    signal: NDArray[np.float64],
    sample_rate: int = 44100,
    loop: bool = False,
) -> Player:
    """Reproduz um sinal estéreo diretamente."""
    player = Player(signal, sample_rate, loop)
    player.play()
    return player
