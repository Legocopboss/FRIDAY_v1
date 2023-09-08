from math import sqrt
import numpy as np
import pygame
import pyaudio


pygame.init()

RATE = 44100
CHUNKS_PER_SECOND = 60
CHUNK = int(1 / CHUNKS_PER_SECOND) * RATE
FORMAT = pyaudio.paInt16

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((600, SCREEN_HEIGHT))

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            break

    screen.fill((0, 0, 0))

    pygame.display.flip()


    buffer = stream.read(CHUNK)
    waveform = np.frombuffer(buffer, dtype=np.int16)

    fft_complex = np.fft.fft(waveform, n=CHUNK)

    color = (0, 128, 0)

    max_val = sqrt(max(v.real * v.real + v.imag * v.imag for v in fft_complex))
    scale_value = SCREEN_HEIGHT / max_val

    for i, v in enumerate(fft_complex):
        dist = sqrt(v.real * v.real + v.imag * v.imag)
        mapped_dist = dist * scale_value

        pygame.draw.line(screen, color, (i, SCREEN_HEIGHT), (i,
                                                             SCREEN_HEIGHT - mapped_dist))