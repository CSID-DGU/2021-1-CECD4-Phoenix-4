import os
import time
import urllib.request
from playsound import playsound
from pathlib import Path
class TTSModule: 
    def __init__(self):
        now = time.localtime()
        
        self.audio = None
        self.data = None
        self.ttsResult = None
        
        self.directory = str(now.tm_year) + "_" + str(now.tm_mon) + "_" + str(now.tm_mday)
        self.WAVE_OUTPUT_FILENAME = "RETVoice" + str(now.tm_hour) + "_" + str(now.tm_min) + "_"+ str(now.tm_sec)+".mp3"
                    
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            
        print("Today's data directory: " + self.directory + "\n")
            
    def tts(self, quotation):
        # recieve text quotes from chatbot, get mp3 from outer API  
        try:
            client_id = ""
            client_secret = ""
            outFilename = self.WAVE_OUTPUT_FILENAME
            encText = urllib.parse.quote(quotation)
            
            
            data = "speaker=nara&volume=0&speed=0&pitch=0&format=mp3&text=" + encText;
            url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
            
            request = urllib.request.Request(url)
            request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
            request.add_header("X-NCP-APIGW-API-KEY",client_secret)
            response = urllib.request.urlopen(request, data=data.encode('utf-8'))
            rescode = response.getcode()
           
            if(rescode==200):
                print("TTS mp3 저장")
                response_body = response.read()
                with open(self.directory +  "/" +outFilename, 'wb') as f:
                    f.write(response_body)

            else:
                print("Error Code:" + rescode)

        except Exception as e:
            print(e)
            
    def resultPlay(self):         
        file_path = str(os.getcwd()) + "\\" + str(self.directory) +  "\\" + str(self.WAVE_OUTPUT_FILENAME)
        print(file_path)
        playsound(file_path)    