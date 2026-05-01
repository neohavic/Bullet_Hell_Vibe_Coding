"""Audio analysis and beat detection for rhythm-synchronized effects."""

import numpy as np
import pygame
import wave
import struct


class BeatPulseController:
    """
    Detects kick drum transients from a .wav file and plays audio in a loop.
    Returns a smoothed amplitude value for visual/gameplay effects.
    """
    def __init__(self, audioPath: str, decay: float = 0.85, sensitivity: float = 1.8):
        self.decay = decay
        self.sensitivity = sensitivity
        self.energyHistory = []
        self.maxHistory = 50
        self.lastAmplitude = 1.0

        self.samples = self._loadAudio(audioPath)
        self.sampleRate = 44100
        self.frameSize = 1024
        self.frameIndex = 0

        self.audioPath = audioPath
        self._playbackStarted = False
        self._onKick = None

        pygame.mixer.init()

    def _loadAudio(self, path: str):
        """Load and normalize audio samples from a WAV file."""
        with wave.open(path, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            samples = struct.unpack_from("%dh" % wf.getnframes(), frames)
            samples = np.array(samples, dtype=np.float32)
            samples /= np.max(np.abs(samples))
            if wf.getnchannels() == 2:
                samples = samples[::2]  # Convert stereo to mono
            return samples

    def startAudio(self):
        """Start audio playback (loops indefinitely)."""
        if not self._playbackStarted:
            pygame.mixer.music.load(self.audioPath)
            pygame.mixer.music.play(loops=-1)
            self._playbackStarted = True

    def update(self, dt: float) -> float:
        """Update beat detection and return smoothed amplitude."""
        self.startAudio()

        start = self.frameIndex
        end = start + self.frameSize
        self.frameIndex += self.frameSize

        if end >= len(self.samples):
            self.frameIndex = 0

        frame = self.samples[start:end]
        if len(frame) < self.frameSize:
            frame = np.pad(frame, (0, self.frameSize - len(frame)))

        # Analyze kick band (20-100 Hz)
        fftData = np.abs(np.fft.rfft(frame))
        freqs = np.fft.rfftfreq(len(frame), 1 / self.sampleRate)
        kickBand = fftData[(freqs >= 20) & (freqs <= 100)]
        energy = np.sum(kickBand)

        # Update energy history for adaptive thresholding
        self.energyHistory.append(energy)
        if len(self.energyHistory) > self.maxHistory:
            self.energyHistory.pop(0)

        avgEnergy = np.mean(self.energyHistory)
        threshold = avgEnergy * self.sensitivity

        # Update amplitude with decay
        if energy > threshold:
            self.lastAmplitude = 1.5
        else:
            self.lastAmplitude *= self.decay

        return self.lastAmplitude
