import PySimpleGUI as gui
import numpy as np
import pyaudio

_VARS = {
    'window': False,
    'stream': False,
    'audioData': np.array([])
}

dataSize = 100
dataRangeMin = 0
dataRangeMax = 100

gui.theme('DarkBlue')
AppFont = 'Any 16'

layout = [[gui.Graph(
    canvas_size=(500,500),
    graph_top_right=(102,102),
    graph_bottom_left=(-2,-2),
    background_color='#809AB6',
    key='graph'
)]]

_VARS['window'] = gui.Window('Sound', layout, finalize=True)
graph = _VARS['window']['graph']

CHUNK = 1024
RATE = 44100
INTERVAL = 1
TIMEOUT = 10
pAud = pyaudio.PyAudio()

def drawAxis(dataRangeMin=0, dataRangeMax=100):
    graph.DrawLine((dataRangeMin, 0), (dataRangeMax, 0))
    graph.DrawLine((0, dataRangeMin), (0, dataRangeMax))

def stop():
    if _VARS['stream']:
        _VARS['stream'].stop_stream()
        _VARS['stream'].close()
        _VARS['window']['-PROG-'].update(0)

def callback(in_data, frame_count, time_info, status):
    _VARS['audioData'] = np.frombuffer(in_data, dtype=np.int16)
    return (in_data, pyaudio.paContinue)

def listen():
    _VARS['stream'] = pAud.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=callback
    )
    _VARS['stream'].start_stream()

drawAxis()

while True:
    event, values = _VARS['window'].read(timeout=TIMEOUT)
    if event == gui.WIN_CLOSED or event == 'Exit':
        stop()
        pAud.terminate()
        break
    elif _VARS['audioData'].size != 0:
        _VARS['window']['-PROG-'].update(np.amax(_VARS['audioData']))

        graph.erase()
        drawAxis()

    for x in range(CHUNK):
        graph.DrawCircle((x, (_VARS['audioData'][x]/100)+50), 0.4, line_color='blue', fill_color='blue')

_VARS['window'].close()