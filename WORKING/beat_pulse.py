import numpy as np
import pygame
import wave
import struct

class BeatPulseController:
    """
    Detects kick drum transients from a .wav file and plays audio in a loop.
    Triggers an on_kick() callback when a kick is detected.
    Returns a smoothed amplitude value for visual/gameplay effects.
    """
    def __init__(self, audio_path: str, decay: float = 0.85, sensitivity: float = 1.8):
        self.decay = decay
        self.sensitivity = sensitivity
        self.energy_history = []
        self.max_history = 50
        self.last_amplitude = 1.0

        self.samples = self._load_audio(audio_path)
        self.sample_rate = 44100
        self.frame_size = 1024
        self.frame_index = 0

        self.audio_path = audio_path
        self._playback_started = False
        self._on_kick = None

        pygame.mixer.init()

    def _load_audio(self, path: str):
        with wave.open(path, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            samples = struct.unpack_from("%dh" % wf.getnframes(), frames)
            samples = np.array(samples, dtype=np.float32)
            samples /= np.max(np.abs(samples))
            if wf.getnchannels() == 2:
                samples = samples[::2]
            return samples

    def start_audio(self):
        if not self._playback_started:
            pygame.mixer.music.load(self.audio_path)
            pygame.mixer.music.play(loops=-1)  # Loop forever
            self._playback_started = True

    def set_on_kick(self, callback_fn):
        """Registers a callback to be triggered on kick detection."""
        self._on_kick = callback_fn

    def update(self, dt: float) -> float:
        self.start_audio()

        start = self.frame_index
        end = start + self.frame_size
        self.frame_index += self.frame_size

        if end >= len(self.samples):
            self.frame_index = 0

        frame = self.samples[start:end]
        if len(frame) < self.frame_size:
            frame = np.pad(frame, (0, self.frame_size - len(frame)))

        fft_data = np.abs(np.fft.rfft(frame))
        freqs = np.fft.rfftfreq(len(frame), 1 / self.sample_rate)

        kick_band = fft_data[(freqs >= 20) & (freqs <= 100)]
        energy = np.sum(kick_band)

        self.energy_history.append(energy)
        if len(self.energy_history) > self.max_history:
            self.energy_history.pop(0)

        avg_energy = np.mean(self.energy_history)
        threshold = avg_energy * self.sensitivity

        if energy > threshold:
            self.last_amplitude = 1.5
            if self._on_kick:
                self._on_kick()
        else:
            self.last_amplitude *= self.decay

        return self.last_amplitude