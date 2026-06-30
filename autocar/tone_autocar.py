class Tone:
    def __init__(self, volume=0.5, rate=48000, channels=1):
        self.volume = volume
        self.rate = rate
        self.channels = channels
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=self.channels, rate=self.rate, output=True)

    def play(self, octave=3, note=1, duration=2):
        f = 2**(octave) * 55 * 2**(((note)-10)/12)
        sample = (np.sin(2 * np.pi * np.arange(self.rate*duration) * f/self.rate)).astype(np.float32)
        self.stream.write(self.volume * sample)

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

tone = Tone()
for n in [1, 3, 5, 7, 8, 10, 12]:
    tone.play(3, n, 4)
tone.stop()
