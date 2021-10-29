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

                if count > 100:
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
                "Content-Type": "application/octet-stream",
                "X-NCP-APIGW-API-KEY-ID": ****,
                "X-NCP-APIGW-API-KEY": ****,
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

class Relearn:
    def __init__(self):
        self.intent = ""
        self.question = ""
        self.answer = ""
        
        #Entity data load         
        file_list = os.listdir("AI-Call-Center/entities")
        file_name = None
        self.entities_dict = {}
        for i in file_list:
            if "entries" not in i:
                file_name = i
                self.entities_dict[i] = None
            else:
                with open("AI-Call-Center/entities/"+i, "r", encoding="utf8") as f: 
                    contents = f.read() # string 타입 
                    json_data = json.loads(contents) 
                    self.entities_dict[file_name] = json_data
    
    def entityCheck(self):
        self.intent_replase = {}
        result = False
        for i in self.entities_dict:
            for j in self.entities_dict[i]:
                for k in j["synonyms"]:
                    if k in self.question: 
                        self.intent_replase[k] = ('", "userDefined": false }, { '+
                                              '"text": "' + k +'"'+
                                              ', "meta": "@' + i.replace(".json", "")+'"'+
                                              ', "alias": "' +i.replace(".json", "")+'"'+
                                              ', "userDefined": false'+
                                              '}, { "text": "')
                        result = True
        return result
    
    def makeJson(self):
        
        if self.entityCheck() is True:
            for i in self.intent_replase:
                self.question = self.question.replace(i, self.intent_replase[i])
        
        f = open(self.intent + '.json', 'w', encoding='UTF-8')
        f.write('{ "id": "10d3155d-4468-4118-8f5d-15009af446d0", "name": "' + self.intent 
                + '", "auto": true, "contexts": [], "responses": [ { "resetContexts": false, '
                + '"affectedContexts": [], "parameters": [], "messages": [ { "type": 0, "lang": "ko", "speech": "' 
                + self.answer + '" } ], "defaultResponsePlatforms": {}, "speech": [] } ], '
                + '"priority": 500000, "webhookUsed": false, "webhookForSlotFilling": false, "fallbackIntent": false, "events": [] }')
        f.close()

        f = open(self.intent + '_usersays_ko.json', 'w', encoding='UTF-8')
        f.write("[")
        f.write('{ "id": "3330d5a3-f38e-48fd-a3e6-000000000001", "data": [ { "text": "' 
                + self.question + '", "userDefined": false } ], "isTemplate": false, "count": 0 }')
        f.write("]")
        f.close()
        
    def setFileContext(self, intent, question, answer):
        if(intent != ''):
            self.intent = intent
        
        if(self.question == ""):
            self.question = question
        else:
            self.question = self.question + " " + question
            
        if(self.answer == ""):
            self.answer = answer
        else:
            self.answer = self.answer + " " + answer                        
                    
    def moveJsonFile(self):
        localPosition = 'AI-Call-Center/intents/'
        shutil.move(self.intent + '.json',  localPosition + self.intent + '.json')
        shutil.move(self.intent + '_usersays_ko.json',  localPosition + self.intent + '_usersays_ko.json')
        
    def deleteTempJson(self):
        if(os.path.isfile(self.intent + '.json')):
            os.remove(self.intent + '.json')
        if(os.path.isfile(self.intent + '_usersays_ko.json')):
            os.remove(self.intent + '_usersays_ko.json')
            
        self.intent = ""
        self.question = ""
        self.answer = ""
 
class Chatbot:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ai-call-center-psmu-e586e119ee5c.json"
    
    def __init__(self):
        self.DIALOGFLOW_PROJECT_ID = 'ai-call-center-psmu'
        self.DIALOGFLOW_LANGUAGE_CODE = 'ko'
        self.text_to_be_analyzed = None
        self.SESSION_ID = "123456789"
        
    def answering(self, question):
        self.text_to_be_analyzed = question
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(self.DIALOGFLOW_PROJECT_ID, self.SESSION_ID)
        text_input = dialogflow.types.TextInput(text=self.text_to_be_analyzed, 
        language_code=self.DIALOGFLOW_LANGUAGE_CODE)
        query_input = dialogflow.types.QueryInput(text=text_input)

        try:
            response = session_client.detect_intent(session=session, query_input=query_input)
            self.question = response.query_result.query_text.replace('{"text":"', '').replace('\"}', '')
            self.answer = response.query_result.fulfillment_text
            
        except InvalidArgument:
            raise   