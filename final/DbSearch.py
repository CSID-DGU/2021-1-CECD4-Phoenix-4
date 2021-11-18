#기존 통합 클래스 파일에 추가
import pymysql

class DbSearcher:
    def __init__(self):
        #db connect setting
        host = "###"
        port = "###"
        username = "###"
        database = "###"
        password ="###"

        self.conn = pymysql.connect(host = host, user = username, passwd = password, db= database, port = port)
        self.cur = self.conn.cursor()
    
    def searchCstm(self, TTS, STT):
        #상담을 위한 기본 정보 로드 함수
        TTS.tts("상담자 확인을 위해 학번을 말해주세요.")
        TTS.resultPlay()
        
        STT.noTalkingSetting()
        STT.recording()
        STT.stt()
        STT.sttResult = STT.sttResult.replace('\"', '')
        STT.sttResult = STT.sttResult.replace('text:', '')
        STT.sttResult = STT.sttResult.replace(' ', '')
        STT.sttResult = STT.sttResult.replace('{', '')
        STT.sttResult = STT.sttResult.replace('}', '')
        query = "SELECT * FROM STUDENTINFO WHERE studentID = " + STT.sttResult + ";"
        try:
            self.cur.execute(query)
            studentInfo = self.cur.fetchone()
            print(studentInfo)
            return self.cur.fetchone()
        except:
            return None
    
    def outBoundList(self, Slist):
        #아웃바운드 기능을 위한 대상 검색 함수
        result = []
        query = "SELECT tel FROM STUDENTINFO WHERE "
        
        #Slist 구조: 2차원 배열, ['검색 분야(특성)','검색 키워드', '검색 조건']을 하나의 원소로 가지는 배열임
        #Slist의 검색 조건: 0 - 일치 검색+and / 1 - 일치 검색+or / 2 - 포함 검색+and / 3 - 포함 검색+or
        for target in Slist:
            if target[2] // 2 == 0:
                query += target[0] + ' = "' + target[1] + '"'
            else:  
                query += target[0] + ' like "%' + target[1] + '%"'
            if target != Slist[-1]:
                if target[2] % 2 == 0:
                    query += " and "
                else:
                    query += " or "
            else:
                query += ";"
        try:
            self.cur.execute(query)
        
            while True:
                row = self.cur.fetchone()
                if row == None:
                    break
                result.append(row[0])
        except:
            return None
        return result