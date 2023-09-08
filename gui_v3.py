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

def stopLooping(event):
    global loopBool
    print("Stoping loop")
    pAud.terminate()
    plt.close()

def looping(event):
    global audioData
    global loopBool
    global extremes

    while loopBool:
        print("looping")
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

        time.sleep(0.1)

def preLoop(event):
    print("Prepping loop")

    thread = threading.Thread(target=looping, args=(event,))
    thread.daemon = True
    thread.start()


axStopButton = plt.axes([0.15, 0.05, 0.1, 0.06])
bClose = widgets.Button(axStopButton, "Stop", hovercolor="0.975", color="red")
bClose.on_clicked(stopLooping)
axStartButton = plt.axes([0.05, 0.05, 0.1, 0.06])
bStart = widgets.Button(axStartButton, "Start", hovercolor="0.975", color="lime")
bStart.on_clicked(preLoop)

plt.show()
