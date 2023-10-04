import sys
import threading
import time
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use('TkAgg')
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
plt.switch_backend('agg')




FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
audioData = False
stream = False
extremes = [-10, 10]

window = False
aiText = False
userText = False

pAud = pyaudio.PyAudio()

fig, mainPlot = plt.subplots(figsize=(12, 6), num="Test number: too many")


def callback(in_data, frame_count, time_info, status):
    global audioData
    audioData = np.frombuffer(in_data, dtype=np.int16, count=CHUNK)
    # print(audioData.size)
    # print(len(in_data))
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
plt.gca().get_yaxis().set_visible(False)

plot, = mainPlot.plot(0, 0, color="blue")
plt.margins(0.05)

loopBool = True

_func = np.vectorize(lambda x: x / 100)


def stopLooping():
    print("Stoping loop")
    pAud.terminate()
    plt.close()
    window.destroy()
    exit(-1)


def looping():
    global audioData
    global loopBool
    global extremes

    while loopBool:
        # print("looping")
        _data = _func(audioData)
        _tmpMin = np.min(_data)
        _tmpMax = np.max(_data)
        if _tmpMin < extremes[0]: extremes[0] = _tmpMin
        if _tmpMax > extremes[1]: extremes[1] = _tmpMax
        mainPlot.clear()
        mainPlot.set_ylim(extremes[0], extremes[1])
        mainPlot.plot(list(range(CHUNK)), _data, color="blue")
        canvas.draw_idle()
        # plt.draw()
        # window.after(1000, looping)
        time.sleep(0.05)


def preLoop():
    print("Prepping loop")
    thread = threading.Thread(target=looping)
    thread.daemon = True
    thread.start()


def setAiText(text):
    aiText.config(text=text)


def setUserText(text):
    userText.config(text=text)


# plt.show()

def startGUIWindow():
    try:
        global userText, aiText, canvas, window
        window = Tk()
        window.configure(background='light blue')
        window.title("FRIDAY GUI")
        window.state('zoomed')
        # window.geometry('1200x1000')
        # window.resizable(True, True)

        wordsFrame = LabelFrame(window, text='', background='light grey', height=300)
        plottingFrame = LabelFrame(window, text='', bg='blue', width=300, height=400, bd=5, relief=SUNKEN)
        wordsFrame.pack(fill='both', expand=True, side=BOTTOM, padx=20, pady=10)
        plottingFrame.pack(fill='both', expand=True, side=TOP, padx=20, pady=5)
        wordsFrame.grid_columnconfigure((0, 1), weight=1)

        aiText = Label(wordsFrame, bg='alice blue', anchor=W, text="", font=("Courier", 15), wraplength = window.winfo_width()-30)
        aiText.grid(row=1, column=0, sticky='w')
        userText = Label(wordsFrame, bg='azure1', anchor=W, text="", font=("Courier", 15), wraplength = window.winfo_width()-30)
        userText.grid(row=0, column=0, sticky='w')

        exit_button = Button(wordsFrame, text='Close', width=10, height=2, borderwidth=3, command=window.destroy, bg='red')
        exit_button.grid(row=0, column=10, sticky='e')

        canvas = FigureCanvasTkAgg(fig, master=plottingFrame)
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        canvas.draw()

        window.mainloop()
    except:
        pass

# preLoop()
