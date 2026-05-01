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
        with wave.open(path, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            samples = struct.unpack_from("%dh" % wf.getnframes(), frames)
            samples = np.array(samples, dtype=np.float32)
            samples /= np.max(np.abs(samples))
            if wf.getnchannels() == 2:
                samples = samples[::2]
            return samples

    def startAudio(self):
        if not self._playbackStarted:
            pygame.mixer.music.load(self.audioPath)
            pygame.mixer.music.play(loops=-1)  # Loop forever
            self._playbackStarted = True

    def setOnKick(self, callbackFn):
        """Registers a callback to be triggered on kick detection."""
        self._onKick = callbackFn

    def update(self, dt: float) -> float:
        self.startAudio()

        start = self.frameIndex
        end = start + self.frameSize
        self.frameIndex += self.frameSize

        if end >= len(self.samples):
            self.frameIndex = 0

        frame = self.samples[start:end]
        if len(frame) < self.frameSize:
            frame = np.pad(frame, (0, self.frameSize - len(frame)))

        fftData = np.abs(np.fft.rfft(frame))
        freqs = np.fft.rfftfreq(len(frame), 1 / self.sampleRate)

        kickBand = fftData[(freqs >= 20) & (freqs <= 100)]
        energy = np.sum(kickBand)

        self.energyHistory.append(energy)
        if len(self.energyHistory) > self.maxHistory:
            self.energyHistory.pop(0)

        avgEnergy = np.mean(self.energyHistory)
        threshold = avgEnergy * self.sensitivity

        if energy > threshold:
            self.lastAmplitude = 1.5
            if self._onKick:
                self._onKick()
        else:
            self.lastAmplitude *= self.decay

        return self.lastAmplitude
