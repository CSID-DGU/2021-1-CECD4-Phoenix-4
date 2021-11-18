from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators import csrf
from django.views.decorators.csrf import csrf_exempt
from CallCenter import models
import STT_Module
import TTS_Module
import os
import ChatBot_Module
import DbSearch
import time
# Create your views here.

global otb
global user_name
user_name = ""
chat = []

global stt
global tts

stt = None
tts = None

def index(request):
    cursor = connection.cursor()
    strSql = "select * from AICALLCENTER.COUNSELEEINFO;"
    cursor.execute(strSql)
    counsel_list = cursor.fetchall()
    strSql = "select * from AICALLCENTER.RELEARNING;"
    cursor.execute(strSql)
    reLearning_list = cursor.fetchall()
    strSql = "select * from AICALLCENTER.CALLADMIN;"
    cursor.execute(strSql)
    call_list = cursor.fetchall()
    context={
        'username':user_name,
        'counsel_list':counsel_list,
        'reLearning_list':reLearning_list,
        'call_list':call_list,
    }
    return render(request, 'CallCenter/index.html', context)

def counselor(request):
    global stt

    cursor = connection.cursor()
    strSql = "select * from AICALLCENTER.COUNSELEEINFO WHERE a_id = '" + str(user_name) + "';"
    cursor.execute(strSql)
    admin_info = cursor.fetchall()
    context={
        'username':user_name,
        'admin_info' : admin_info,
    }

    if stt != None:
        stt.closeStt()

    if stt != None:
        stt.closeStt()

    return render(request, 'CallCenter/counselor.html', context)

def counseling(request, user_id):
    global tts
    cursor = connection.cursor()
    strSql = "select * from AICALLCENTER.STUDENTINFO WHERE studentID = '" + str(user_id) + "';"
    cursor.execute(strSql)
    user = cursor.fetchone()
    strSql = "select DATE_FORMAT(startTime, '%Y-%m-%d'), dataLocation from AICALLCENTER.COUNSELEEINFO WHERE studentID = '" + str(user_id) + "';"
    cursor.execute(strSql)
    counseling_list = cursor.fetchall()
    data = []
    absolutepath = os.path.abspath('.')
    print(absolutepath)
    for counseling in counseling_list:
        dataLocation = counseling[1]
        dataPath = str(absolutepath) + "\\" + str(dataLocation)
        f = open(dataPath, 'r', encoding='UTF-8')
        QnAList = []
        while True:
            qline = f.readline().replace("Q: ",'').replace("\n",'').replace('\t','')
            if not qline:
                break
            aline = f.readline().replace("A: ",'').replace("\n",'').replace('\t','')
            QnAList.append([qline, aline])
        f.close()   
        data.append([counseling, QnAList])   
    context={
        'username':user_name,
        'user' : user,
        'QnAList' : data,
    }

    chatStart(tts)

    return render(request, 'CallCenter/counseling.html', context)    

@csrf_exempt
def chat(request):
    global stt
    global tts
    question = ""
    try:
        stt.recording()
        stt.stt()
        chatBot = ChatBot_Module.Chatbot()
        chatBot.answering(stt.sttResult)
        chatBot.answer
        chatBot.question
        tts.tts(chatBot.answer)
        tts.resultPlay()
        question = stt.sttResult.split(":")[1].replace('"','').replace('}','')
        answer = chatBot.answer.replace('"','')
        context = {
            'question' : question,
            'answer': answer,
            'checker' : True
        }
        print(context)
    except:
        context = {
            'question' : question,
            'answer' : "죄송한데 잘 이해하지 못했어요",
            'checker' : False
        }
    return JsonResponse(context)

def chatStart(tts):
    tts.tts("상담 내용을 말해주세요")
    tts.resultPlay()

@csrf_exempt
def phonecall(request):
    global stt
    global tts
    stt = STT_Module.STTModule()
    stt.setAudioType(1)
    stt.noTalkingSetting()
    tts = TTS_Module.TTSModule()
    tts.tts("상담자 확인을 위해 학번을 말해주세요.")
    tts.resultPlay()
    stt.recording()
    stt.stt()
    stt.sttResult = stt.sttResult.replace('\"', '')
    stt.sttResult = stt.sttResult.replace('text:', '')
    stt.sttResult = stt.sttResult.replace(' ', '')
    stt.sttResult = stt.sttResult.replace('{', '')
    stt.sttResult = stt.sttResult.replace('}', '')
    studendID = stt.sttResult
    query = "SELECT * FROM STUDENTINFO WHERE studentID = " + studendID + ";"
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        studentInfo = cursor.fetchone()
        studentID = studentInfo[0]
        context={
        'username':user_name,
        'user_id' : studentID,
        }
        return JsonResponse(context)
    except:
        context={
        'username':user_name,
        'user_id' : '2016112099',
        }
        return JsonResponse(context)
    


def outbound(request):
    global otb
    if request.method == 'GET' and request.GET.get("dateSelect") != None:
        otb = models.outBoundClass()
        otb.date = request.GET.get("date")
        result = otb.searchDate()
        otb.point = 0
        otb.readPoint = -1
        context = {"otb": otb}
        return render(request, 'CallCenter/outbound.html', context)
    elif request.method == 'GET' and request.GET.get("selected") != None:
        otb.step = 3
        otb.point = int(request.GET.get("data"))
        otb.text = otb.result[int(request.GET.get("data"))]
        context = {"otb": otb}
        return render(request, 'CallCenter/outbound.html', context)
    elif request.method == 'GET' and (request.GET.get("listed") != None or request.GET.get("next") != None):
        otb.step = 2
        otb.point = -1
        result1, result2, sum, now = otb.getNextSendList(1)
        context = {"otb": otb, "tel": result1, "text" : result2, "sum": sum, "now": now}
        return render(request, 'CallCenter/outbound.html', context)
    elif request.method == 'GET' and request.GET.get("prev") != None:
        otb.step = 2
        otb.point = -1
        result1, result2, sum, now = otb.getNextSendList(-1)
        context = {"otb": otb, "tel": result1, "text" : result2, "sum": sum, "now": now}
        return render(request, 'CallCenter/outbound.html', context)
    elif request.method == 'GET' and request.GET.get("tagInfo") != None:
        if request.GET.get("add") != None:
            result = otb.addNewOutBound(request.GET.get("tag"), request.GET.get("tagInfo"), request.GET.get("text"))
        elif request.GET.get("delete") != None:
            result = otb.deleteOutBound()
        elif request.GET.get("update") != None:
            result = otb.updateOutBound(request.GET.get("text"))
        otb.step = 1
        return render(request, 'CallCenter/outbound.html', {})
    else:
        return render(request, 'CallCenter/outbound.html', {})

def system(request):
    csr = searchUser()
    csr.connectDB()

    if request.method == 'GET' and request.GET.get("NUM") != None:
        if request.GET.get("NUM") == "0":
            result = csr.addDB(request.GET.get("ID"), request.GET.get("PW"), request.GET.get("GRADE"))
            csr.connectDB()
            print(result)
        else:
            if request.GET.get("change") == None:
                print("delete")
                result = csr.changeDB(request.GET.get("NUM"), request.GET.get("ID"), request.GET.get("PW"), request.GET.get("GRADE"), True)
            else:
                result = csr.changeDB(request.GET.get("NUM"), request.GET.get("ID"), request.GET.get("PW"), request.GET.get("GRADE"), False)
            csr.connectDB()
            print(result)
    context = {'user' : csr, 'username':user_name}

    return render(request, 'CallCenter/system.html', context)

def user_info(request):
    cursor = connection.cursor()
    strSql = "select * from AICALLCENTER.STUDENTINFO"
    cursor.execute(strSql)
    user_list = cursor.fetchall()
    context={
        'username':user_name,
        'userlist':user_list,
    }
    return render(request, 'CallCenter/user_info.html', context)

def data(request):
    cursor = connection.cursor()
    strSql = "select * from AICALLCENTER.STUDENTINFO"
    cursor.execute(strSql)
    user_list = cursor.fetchall()
    context={
        'username':user_name,
        'userlist':user_list,
    }
    return render(request, 'CallCenter/data.html', context)

@csrf_exempt
def register(request):
    cursor = connection.cursor()
    if request.method == "POST" and request.POST.get('username') != None:
        userid = request.POST.get('username')
        userpw = request.POST.get('password')
        grade = request.POST.get('select')
        strSql = "insert into AICALLCENTER.ADMIN(a_id, a_pw, a_grade) VALUES('"+ str(userid) + "', '" + str(userpw) +"', " + str(grade) + ");"
        cursor.execute(strSql)
        return redirect('login');    
    return render(request, 'CallCenter/register.html');

class searchUser():
    def __init__(self):
        self.user = None
        self.count = None
        self.all = 10
    def connectDB(self):
        cursor = connection.cursor()
        strSql = "select a_uid, a_id, a_pw, a_grade from AICALLCENTER.ADMIN"
        result = cursor.execute(strSql)
        self.user = cursor.fetchall()
        self.count = len(self.user)
        self.all -= self.count
        return self.user
    def addDB(self, a_id, a_pw, a_grade):
        notAvail1 = "새 ID 입력"
        notAvail2 = "새 PW 입력"
        notAvail3 = "새 등급 입력"

        lastUid = 0

        for i in self.user:
            if i[0] >= lastUid:
                lastUid = i[0]

        cursor = connection.cursor()
        if a_id != notAvail1 and a_pw != notAvail2 and a_grade != notAvail3: 
            try:
                strSql = 'insert INTO AICALLCENTER.ADMIN values("' + str(lastUid+1) + '", "' + a_id + '", "' +  a_pw + '", "' +  a_grade + '")'
                result = cursor.execute(strSql)
                self.all = 10
                return True
            except Exception as e:
                print(e)
                return False
        else:
            return False

    def changeDB(self, a_uid, a_id, a_pw, a_grade, isDelete):
        cursor = connection.cursor()
        if isDelete:
            try:
                strSql = 'delete from AICALLCENTER.ADMIN where a_uid = "' + a_uid + '"'
                result = cursor.execute(strSql)
                self.all = 10
                return True
            except Exception as e:
                print(e)
                return False
        else:
            try:
                strSql = "UPDATE AICALLCENTER.ADMIN set a_id = '" + a_id + "', a_pw = '" + a_pw + "', a_grade = '" + a_grade + "' "
                strSql += "where a_uid = '" + a_uid + "'"
                result = cursor.execute(strSql)
                self.all = 10
                return True
            except Exception as e:
                print(e)
                return False



@csrf_exempt
def userLogin(request):
    cursor = connection.cursor()
    if request.method == "POST" and request.POST.get('username') != None:
        userid = request.POST.get('username')
        userpw = request.POST.get('password')
        strSql = "select a_uid, a_id, a_pw, a_grade from AICALLCENTER.ADMIN WHERE a_id = '" + userid + "'"
        cursor.execute(strSql)
        row_count = cursor.rowcount
        rows = cursor.fetchall()
        if row_count != 0 and rows[0][2] == userpw:
            print(userid)
            global user_name
            user_name = userid
            if rows[0][3] == 0:
                return redirect('index')
            else:
                return redirect('counselor')
        else:
            return render(request, 'CallCenter/login.html');    
    return render(request, 'CallCenter/login.html');
       
