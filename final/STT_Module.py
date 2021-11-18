import json
import requests
import shutil
import pyaudio
import wave
import time
import dialogflow
from google.api_core.exceptions import InvalidArgument
import os
from array import array

class STTModule:
    custumNum = 0;
    
    def __init__(self):
        now = time.localtime()
        
        self.audio = None
        self.data = None
        self.sttResult = None
        
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1024
        self.ECORD_SECONDS = 5
        self.WAVE_OUTPUT_FILENAME = None
        self.directory = str(now.tm_year) + "_" + str(now.tm_mon) + "_" + str(now.tm_mday)
        po = pyaudio.PyAudio()
        
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            
        print("Today's data directory: " + self.directory + "\n")
        
        for index in range(po.get_device_count()): 
            desc = po.get_device_info_by_index(index)
            print ("DEVICE: %s  INDEX:  %s  RATE:  %s " %  (desc["name"], index,  int(desc["defaultSampleRate"])))
    
    def noTalkingSetting(self):
        print("start defaultSetting... Don't talk...")
        frames = []
        count = 0
        self.data = None
        self.lowerBound = 0
        try:
            while (True):

                self.data = self.stream.read(self.CHUNK)

                frames.append(self.data)

                vol = max(array('h', self.data))

                if count > 50:
                    break
                else:
                    if vol > self.lowerBound:
                        self.lowerBound = vol
                    count+=1
                        
            print("end setting...")
            return True
        except Exception as e:
            print(e)
            return False
    
    def setAudioType(self, input_index):
        self.audio = pyaudio.PyAudio()
        try:
            self.stream = self.audio.open(format=self.FORMAT, 
                    channels=self.CHANNELS, 
                    rate=self.RATE, 
                    input=True, 
                    input_device_index=input_index,
                    frames_per_buffer=self.CHUNK)            
            return True
        except Exception as e:
            print(e)
            return False
        
    def recording(self):
        now = time.localtime()
        print("start recording...")
        frames = []
        count = 0
        self.data = None 
        try:
            while (True):

                self.data = self.stream.read(self.CHUNK)

                frames.append(self.data)

                vol = max(array('h', self.data))

                if vol <= self.lowerBound and count > 50:
                    break
                elif count <= 50 and vol <= self.lowerBound:
                    count += 1
                else:
                    count = 0

            self.WAVE_OUTPUT_FILENAME = "Voice" + str(now.tm_hour) + "_" + str(now.tm_min) + "_"+ str(now.tm_sec)+".wav"
            
            waveFile = wave.open(self.directory +  "/" +self.WAVE_OUTPUT_FILENAME, 'wb')
            waveFile.setnchannels(self.CHANNELS)
            waveFile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            waveFile.setframerate(self.RATE)
            waveFile.writeframes(b''.join(frames))
            waveFile.close()

            print("end recording...")
            return True
        except Exception as e:
            print(e)
            return False
        
    def stt(self):
        try:
            data = open(self.directory +  "/" +self.WAVE_OUTPUT_FILENAME, "rb")
            Lang = "Kor"
            URL = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang="+Lang

            ID = "your_client_id"
            Secret = "your_secret"

            headers = {
                "Content-Type": "###",
                "X-NCP-APIGW-API-KEY-ID": "###",
                "X-NCP-APIGW-API-KEY": "###",
            }

            response = requests.post(URL, data=data,headers=headers)
            rescode = response.status_code

            if(rescode == 200):
                self.sttResult = response.text
                print(response.text)
            else:
                print("Error : " + response.text)
        except Exception as e:
            print(e)
            
    def closeStt(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()