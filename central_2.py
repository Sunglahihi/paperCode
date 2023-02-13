import cv2
from cv2 import putText
import numpy as np
import os
import serial
import statistics
import pymysql
import timeit
import time
import schedule
import threading
from multiprocessing import Process
from threading import Thread
import speech_recognition as sr


'''
본체 앞 usb 포트
- 왼쪽 검은선
- 오른쪽 회색선

본체 뒤 usb 포트
- 맨위 왼쪽 마이크선
- 랜선 옆 왼쪽 대화 카메라
- 랜선 옆 오른쪽 추적 카메라 (매끈한거)
'''


# save_user = pymysql.connect(
#     user='root', # user이름 : root
#     passwd='0000', # tjdals2316393! = 내거 컴퓨터에서 mysql root 계정 비밀번호
#     host='127.0.0.1', # localhost
#     db='camuser',  # db 이름
#     charset='utf8'
# )
save_user = pymysql.connect(
    user='root',
    passwd='tjdals2316393!',
    host='localhost', 
    db='camuser',  
    charset='utf8'
)
# 바닥 타일로 4칸 정도 거리에서 잡힘
# 2칸 반이 제일 잘잡힘
arduino = serial.Serial('COM4',9600) # 스캔 회색선
arduino2 = serial.Serial('COM3',9600) # 대화 검은선
 
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('.//trainer_4man.yml')
cascadePath = ".//haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)
font = cv2.FONT_HERSHEY_SIMPLEX

#iniciate id counter
id = 0

# names related to ids: example ==> loze: id=1,  etc
names = ['박성민','구다훈', '양아름', '박연수', '최연우', '송우석', '강성준', '최승욱', '김기오']
kornames = ['park', 'gu', 'yang', 'park2', 'choi', 'song', 'kang', 'choi2', 'kim']
median_re=[]
for name in names :
    median_re.append([])

central=[]
for name in names :
    central.append([])

result1 = [0 for i in range(len(names))]
result2 = [0 for i in range(len(names))]
result3 = [0 for i in range(len(names))]
result4 = [0 for i in range(len(names))]


# Initialize and start realtime video capture
cam = cv2.VideoCapture(0)
cam22 = cv2.VideoCapture(1)
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height

# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

#db에 저장되어 있는 이름이랑 각도 가져오기 
index = 0

cursor = save_user.cursor(pymysql.cursors.DictCursor)



def central_lo(id):
    arduino.write(b'1\n')
    a=arduino.readline()
    b = int(a.decode())
    central[id].append(b)
    id = names[id]
    print( str(id)+' 님의 '+'중앙 각도 '+str(b)+'도 가 저장되었습니다.')

def getCameraStream():
    while True:
        ret, mat = cam22.read()
        if not ret:
            break

        ret, jpgI = cv2.imencode('.jpg', mat)

        jpgB = bytearray(jpgI.tobytes())

        yield (b'--PNPframe\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            jpgB + b'\r\n')
                
def search_lo(id):
    arduino.write(b'1\n')
    a=arduino.readline()
    b = int(a.decode())
    median_re[id].append(b)
    id = names[id]
    print( str(id)+' 님의 '+'각도 '+str(b)+'도 가 저장되었습니다.')

def talkMain():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("발언자 이름을 말해주세요")
        audio = r.listen(source)
    Name = r.recognize_google(audio, language='ko')
    print(Name)
    
    if Name not in name:
        print("이름을 찾을 수가 없습니다.\n")
        
    else:
        print("이름을 찾았습니다.\n")
        print(angle[name.index(Name)])
        arduino2.write(angle[name.index(Name)].encode())
        a=arduino2.readline()
        b = int(a.decode())
        print(Name+"님이 있는 곳으로 카메라를 돌렸습니다.\n")

# def meassage_scan():
#     print("---------------------전체 스캔 완료------------------------------")
#     t = threading.Timer(8, meassage_scan)
#     t.start()


# # job1 = schedule.every(8).seconds.do(meassage_scan)
# meassage_scan()
prev = time.time()

while True:

        st = timeit.default_timer()
        ret, img =cam.read() # 스캔용 카메라
        ret2, frame = cam22.read() # 대화용 카메라


        # img = cv2.flip(img, -1) # Flip vertically
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
        )

        
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
            # Check if confidence is less them 100 ==> "0" is perfect match
            if (confidence < 100):
                pix = int(round(x+w/2))
                if ( 300 < pix < 340) :
                    central_lo(id)
                    

                search_lo(id)
            else:
                id = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))
                
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)

        te = timeit.default_timer()
        fps = int(1./(te - st))
        # print(fps)

            
            #cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1) 
        
        count = 0
        for i in median_re :
            if not i:
                continue

            else : 
                result1[count]=int(statistics.median(i))
                result2[count]=int(statistics.mean(i))
            count+=1
        count = 0

        for i in central :

            if not i:
                continue

            else : 
                result3[count]=int(statistics.median(i))
                result4[count]=int(statistics.mean(i))
            count+=1    

        save_sql = []

        for i in names:
            save_sql.append([])

        for i in range(0,len(save_sql)) :
            save_sql[i].append(names[i])
            save_sql[i].append(kornames[i])
            save_sql[i].append(result1[i])
            save_sql[i].append(result2[i])
            save_sql[i].append(result3[i])
            save_sql[i].append(result4[i])

        sql = "DELETE FROM camuser.user;" # 안바꿔도 될듯 테이블 이름이 user라서 camuser의 user테이블을 뜻함
        cursor.execute(sql)
        save_user.commit()

        sql = "INSERT INTO camuser.user(name, name_kor ,median, mean, central_median, central_mean) VALUES (%s, %s, %s, %s, %s, %s);"
        cursor.executemany(sql, save_sql)
        save_user.commit()
        
        sql = "SELECT * FROM camuser.user"
        cursor.execute(sql) # sql문 db서버로 보내기
        result = cursor.fetchall() # 데이터를 서버로부터 가져오는 거
        name = []
        angle = []

        for i in range(len(result)):
            a = list(result[i].values())
            name.append(a[0]) # 한글이름
            angle.append(a[2]) # 저장된 각도
        
    
        #putText(frame, fps, (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
        cv2.imshow('camera',img)
        cv2.imshow('frame',frame)
        
        key = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting vided
        if key == 27:
            break
            
        if key == ord('g'):
            talkMain()

print("사용자 위치정보를 MySQL에 저장하였습니다.")
cam.release()
cv2.destroyAllWindows()