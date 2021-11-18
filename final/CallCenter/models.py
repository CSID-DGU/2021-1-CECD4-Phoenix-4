from django.db import models
from django.db import connection
# Create your models here.

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
class outBoundClass():
    def __init__(self):
        self.date = None
        self.studentID = None
        self.text = None
        self.result = None
        self.point = None
        self.step = 1

    def searchDate(self):
        cur = connection.cursor()
        query = "SELECT * FROM AICALLCENTER.OUTBOUNDDB where date = '" + self.date + "'"
        cur.execute(query)
        self.result = cur.fetchall()
        self.step = 2
        return self.result

    def addNewOutBound(self, tag, tagInfo, text):
        cur = connection.cursor()
        if tag == "address":
            query = "SELECT * FROM AICALLCENTER.STUDENTINFO where " + tag + " like '%" + tagInfo + "%'"
        else: 
            query = "SELECT * FROM AICALLCENTER.STUDENTINFO where " + tag + " = '" + tagInfo + "'"
        cur.execute(query)
        result = cur.fetchall()

        for i in result:
            try:
                query = "insert into AICALLCENTER.OUTBOUNDDB values('"+self.date+"', "+str(i[0])+", '"+ text + "', '" + i[8]+ "')"
                cur.execute(query)
            except Exception as e:
                print(e)
    
    def deleteOutBound(self):
        cur = connection.cursor()
        try:
            query = "delete FROM AICALLCENTER.OUTBOUNDDB where date = '" + self.date + "' and studentID = '" + self.text[1] + "' and text = '" + self.text[2] + "' "
            cur.execute(query)
            return True
        except Exception as e:
            print(e)
            return False

    def updateOutBound(self, text):
        cur = connection.cursor()
        try:
            query = "update AICALLCENTER.OUTBOUNDDB set text = '"+ str(text) +"' where date = '" + self.date + "' and studentID = '" + self.text[1] + "' and text = '" + self.text[2] + "' "
            cur.execute(query)
            return True
        except Exception as e:
            print(e)
            return False