import sys
import threading
import time
import matplotlib

matplotlib.use('TkAgg')
import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
audioData = False
stream = False
extremes = [-10, 10]

pAud = pyaudio.PyAudio()

fig, mainPlot = plt.subplots(figsize=(12, 6), num="Test number: too many")


def callback(in_data, frame_count, time_info, status):
    global audioData
    audioData = np.frombuffer(in_data, dtype=np.int16, count=CHUNK)
    #print(audioData.size)
    #print(len(in_data))
    return (in_data, pyaudio.paContinue)


def listen():
    global stream
    stream = pAud.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=callback
    )


listen()

plt.gca().get_xaxis().set_visible(False)
#plt.gca().get_yaxis().set_visible(False)

plot, = mainPlot.plot(0, 0, color="blue")
plt.margins(0.05)

loopBool = True

_func = np.vectorize(lambda x: x / 100)

def stopLooping():
    global loopBool
    print("Stoping loop")
    pAud.terminate()
    plt.close()

def looping():
    global audioData
    global loopBool
    global extremes

    while loopBool:
        #print("looping")
        #listen()
        _data = _func(audioData)
        _tmpMin = np.min(_data)
        _tmpMax = np.max(_data)
        if _tmpMin < extremes[0]: extremes[0] = _tmpMin
        if _tmpMax > extremes[1]: extremes[1] = _tmpMax
        mainPlot.clear()
        mainPlot.set_ylim(extremes[0], extremes[1])
        mainPlot.plot(list(range(CHUNK)), _data, color="blue")
        plt.draw()

        time.sleep(0.05)

def preLoop():
    print("Prepping loop")

    thread = threading.Thread(target=looping)
    thread.daemon = True
    thread.start()

plt.show()

preLoop()
