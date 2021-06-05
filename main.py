import time
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from jupyter_dash import JupyterDash
import torch
import requests
from google.cloud import speech
import numpy as np
import librosa
from librosa import display as librosadisplay
import sys
import requests
import os
import logging
import math
import statistics
import sys
from IPython.display import Audio, Javascript
from scipy.io import wavfile
from base64 import b64decode
import music21
import pyaudio
import wave
import soundfile
import playsound

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5

word_count = 1

credential_path = "E:\\학교\\2021\\1학기\\종합설계\\json\\ornate-magnet-270605-fd7a3a4c42d3.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

def record_voice(input_name):
    print("now recording")
    WAVE_OUTPUT_FILENAME = input_name
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print("recording end")
    return WAVE_OUTPUT_FILENAME


def send_chatbot_request(query_data):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer ya29.a0AfH6SMCqh6aGz05HaHUbL_0DD_NhZJk6SHE-oDT4rfLCaNhp9RWUTLWkT-i0N5Mq1SLSk-064eRp-j57Ajo5quwQrHXv4uwrWEax4WTfKV2x2oOP5-0wD2NDeEFlVSoxRPVbReOXuKM00zxhWVq_8IZ8AccsKoCyowWZng',
    }
    data = ('{"queryInput":{"text":{"text":"' + query_data + '","languageCode":"ko"}},"queryParams":{"source":"DIALOGFLOW_CONSOLE","timeZone":"Asia/Seoul","sentimentAnalysisRequestConfig":{"analyzeQueryTextSentiment":true}}}').encode('utf-8')

    response = requests.post('https://dialogflow.clients6.google.com/v2/projects/newagent-tert/agent/sessions/80e12c39-b0f7-bb09-d4f3-10e3ad44fa81:detectIntent',headers=headers, data=data)
    print(response.json())
    answer = response.json()["queryResult"]["fulfillmentText"]
    print(answer)
    return str(answer)


def google_speech_to_text(file_name):
    client = speech.SpeechClient()

    with open(file_name, 'rb') as fp:
        audio_f = fp.read()

    audio = speech.RecognitionAudio(content=audio_f)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ko-KR",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        return result.alternatives[0].transcript


def kakao_speech(text, audio_name):
    kakao_speech_url = "https://kakaoi-newtone-openapi.kakao.com/v1/synthesize"

    rest_api_key = '9d0eae41906de495bcb46d11839db95f'

    headers = {
        "Content-Type": "application/xml",
        "Authorization": "KakaoAK " + rest_api_key,
    }
    speech_text = "<speak> " + text + "</speak>"
    res = requests.post(kakao_speech_url, headers=headers, data=speech_text.encode('utf-8'))
    audio_name = audio_name + ".mp3"
    with open(audio_name, 'wb') as f:
        f.write(res.content)
    return audio_name

def voice_play(path):
    playsound.playsound(path, True)

def textbox(text, box="other"):
    style = {
        "max-width": "55%",
        "width": "max-content",
        "padding": "10px 15px",
        "border-radius": "25px",
    }

    if box == "self":
        style["margin-left"] = "auto"
        style["margin-right"] = 0

        color = "primary"
        inverse = True

    elif box == "other":
        style["margin-left"] = 0
        style["margin-right"] = "auto"

        color = "light"
        inverse = False

    else:
        raise ValueError("Incorrect option for `box`.")

    return dbc.Card(text, style=style, body=True, color=color, inverse=inverse)


conversation = html.Div(
    style={
        "width": "80%",
        "max-width": "800px",
        "height": "70vh",
        "margin": "auto",
        "overflow-y": "auto",
    },
    id="display-conversation",
)

audio_div = html.Audio(
    id="audio_player",
    src="",
)

controls = dbc.InputGroup(
    style={"width": "80%", "max-width": "800px", "margin": "auto"},
    children=[
        dbc.Input(id="user-input", placeholder="음성으로 입력받는 중...", type="text", value=""),
        dbc.InputGroupAddon(dbc.Button("음성 입력", id="submit")),
    ],
)

# Define app
app = JupyterDash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Define Layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        html.H1("AI Call Center"),
        html.Hr(),
        dcc.Store(id="store-conversation", data=""),
        conversation,
        controls,
        audio_div,
    ],
)


@app.callback(
    Output("display-conversation", "children"), [Input("store-conversation", "data")]
)
def update_display(chat_history):
    chat_list = chat_history.split("|")
    return [
        textbox(x, box="self") if i % 2 == 0 else textbox(x, box="other")
        for i, x in enumerate(chat_list)
    ]


@app.callback(
    [Output("store-conversation", "data"), Output("user-input", "value")],
    [Input("submit", "n_clicks")],
    [State("user-input", "value"), State("store-conversation", "data")]
)
def run_chatbot(n_clicks, user_input, chat_history):
    print(n_clicks)
    if n_clicks == 0:
        return "", ""

    voice_name = "input" + str(n_clicks) + ".wav"
    uploaded_file_name = record_voice(voice_name)
    data, samplerate = soundfile.read(uploaded_file_name)
    soundfile.write(uploaded_file_name, data, samplerate, subtype='PCM_16')
    user_input = google_speech_to_text(uploaded_file_name)

    if user_input is None or user_input == "":
        return chat_history, ""
    audio_name = "output" + str(n_clicks)
    chat_output = send_chatbot_request(user_input)
    audio_path = kakao_speech(chat_output, audio_name)
    voice_play(audio_path)
    if chat_history is None or chat_history == "":
        return user_input + "|" + chat_output, ""
    else:
        return chat_history + "|" + user_input + "|" + chat_output, ""



app.run_server(mode='external')
