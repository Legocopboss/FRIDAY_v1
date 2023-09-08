import PySimpleGUI as gui
import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

_VARS = {
    'window': False,
    'stream': False,
    'fig_agg': False,
    'pltFig': False,
    'xData': False,
    'yData': False,
    'audioData': np.array([])
}

AppFont = 'Any 16'
gui.theme('DarkTeal')
layout = [
    [gui.Canvas(key='figCanvas')],
    [gui.Button('Listen', font=AppFont),
     gui.Button('Stop', font=AppFont),
     gui.Button('Exit', font=AppFont)]
]

_VARS['window'] = gui.Window('', layout, finalize=True, location=(400, 100))

CHUNK = 512
RATE = 44100
INTERVAL = 1
TIMEOUT = 10

pAud = pyaudio.PyAudio()

def draw_fig(canvas, figure):
    fig_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    fig_canvas_agg.draw()
    fig_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return fig_canvas_agg

def drawPlot():
    _VARS['pltFig'] = plt.figure()
    plt.plot(_VARS['xData'], _VARS['yData'], '--k')
    plt.ylim(-4000, 4000)
    _VARS['fig_agg'] = draw_fig(_VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])

def updatePlot(data):
    _VARS['fig_agg'].get_tk_widget().forget()
    plt.cla()
    plt.clf()
    plt.plot(_VARS['xData'], data, '--k')
    plt.ylim(-4000, 4000)
    _VARS['fig_agg'] = draw_fig(_VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])

def stop():
    if _VARS['stream']:
        _VARS['stream'].stop_stream()
        _VARS['stream'].close()
        _VARS['window']['Stop'].Update(disabled=True)
        _VARS['window']['Listen'].Update(disabled=False)

def callback(in_data, frame_count, time_info, status):
    _VARS['audioData'] = np.frombuffer(in_data, dtype=np.int16)
    return (in_data, pyaudio.paContinue)

def listen():
    _VARS['window']['Stop'].Update(disabled=False)
    _VARS['window']['Listen'].Update(disabled=True)
    _VARS['stream'] = pAud.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK,
                                stream_callback=callback)
    _VARS['stream'].start_stream()

plt.style.use('ggplot')
_VARS['xData'] = np.linspace(0, CHUNK, num=CHUNK, dtype=int)
_VARS['yData'] = np.zeros(CHUNK)
drawPlot()

while True:
    event, values = _VARS['window'].read(timeout=TIMEOUT)
    if event == gui.WIN_CLOSED or event == 'Exit':
        stop()
        pAud.terminate()
        break
    if event == 'Listen':
        listen()
    elif event == 'Stop':
        stop()
    elif _VARS['audioData'].size != 0:
        updatePlot(_VARS['audioData'])

_VARS['window'].close()