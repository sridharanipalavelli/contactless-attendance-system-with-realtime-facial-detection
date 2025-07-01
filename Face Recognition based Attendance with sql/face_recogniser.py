##import face_recognition
import matplotlib.pyplot as plt
import os
import numpy as np
import cv2
import sqlite3
import tkinter as tk
import threading
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
import time
# from playsound import playsound


timekeeper = 0
mail = 0
siren = 0

sec = 60
fromaddr = "jkkalyani160@gmail.com"
toaddr = "kotthapallilakshmirekha843@gmail.com"
passwd = "derhgwbunliwumqg"

def sendmail():
    global timekeeper, mail, siren
    while True:
        # if siren == 1:
        #     for i in range(5):
        #         playsound('siren.wav')
        #     siren = 0
            
        if time.time()-timekeeper >= sec and mail == 1:
            timekeeper = time.time()
            # instance of MIMEMultipart 
            msg = MIMEMultipart() 
            
            # storing the senders email address   
            msg['From'] = fromaddr 
            
            # storing the receivers email address  
            msg['To'] = toaddr 
            
            # storing the subject  
            msg['Subject'] = "Subject of the Mail"
            
            # string to store the body of the mail 
            body = "Attendance Marked"
            
            # attach the body with the msg instance 
            msg.attach(MIMEText(body, 'plain')) 
            
            # open the file to be sent  
            filename = "image.png"
            attachment = open("detected.png", "rb") 
            
            # instance of MIMEBase and named as p 
            p = MIMEBase('application', 'octet-stream') 
            
            # To change the payload into encoded form 
            p.set_payload((attachment).read()) 
            
            # encode into base64 
            encoders.encode_base64(p) 
            
            p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
            
            # attach the instance 'p' to instance 'msg' 
            msg.attach(p) 
            
            # creates SMTP session 
            s = smtplib.SMTP('smtp.gmail.com', 587) 
            
            # start TLS for security 
            s.starttls() 
            
            # Authentication 
            s.login(fromaddr, passwd) 
            
            # Converts the Multipart msg into a string 
            text = msg.as_string() 
            
            # sending the mail 
            # s.sendmail(fromaddr, toaddr, text)
            mail = 0

        

def train_recogniser(face_recogniser,face_detector,train_dir_name):
    labels=os.listdir(train_dir_name)
    try:
        labels.remove(".DS_Store")
    except:
        pass
    print(labels)
    train_faces=[]
    train_labels=[]
       
    count=0
    for label in labels:
        if "." in label:
            continue
        label_path=train_dir_name+'/'+label
        print(label_path)
        for image_name in os.listdir(label_path):
            loc=label_path+'/'+image_name
            print('\t',image_name,end='')
            image=cv2.imread(loc)
            gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            train_faces.append(gray)
            train_labels.append(count)
            print("\tprocessed")
        count+=1
    print("Training model",end='')
    face_recogniser.train(train_faces,np.array(train_labels).reshape(-1,1))
    print("\t completed")
    return labels


def track_faces():
    def run():
        global mail, siren
        face_recogniser=cv2.face.LBPHFaceRecognizer_create()
        face_detector=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        labels=train_recogniser(face_recogniser,face_detector,"train_images")
        cam=cv2.VideoCapture(0)
        k=65
        c = 0
        print("Starting ")
        while(k not in (27,ord('q'),ord('Q'))):
            _,image=cam.read()
            gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            faces=face_detector.detectMultiScale(gray)
            for face in faces:
                left=face[0]
                top=face[1]
                width=face[2]
                height=face[3]
                image=cv2.rectangle(image,(left,top),(left+width,top+height),color=(0,255,0))
                label=face_recogniser.predict(gray[top:top+height,left:left+width])
                print('Label', label)
               
                if(label[1]<75):    #threshold for distance(label[1]) whose large value indicates that face doesn't match
                    na = str(labels[label[0]]).replace(" ","_")
                    sq = f"insert into {na} (name,attend,date) VALUES ('{na}',{1},'{str(datetime.datetime.now().date())}')"
                    conn = sqlite3.connect("atten.db")
                    conn.execute(sq)
                    conn.commit()
                    conn.close()
                    label=labels[label[0]]+"(%.2f)"%label[1]
                    image=cv2.putText(image,label,(left,top-5), cv2.FONT_HERSHEY_PLAIN,1.5,(0,255,0))
                    image=cv2.putText(image,"Attendance Marked",(0,100), cv2.FONT_HERSHEY_PLAIN,3,(0,0,255))
                    c = 0
                    print("Showing 1")
                    cv2.imshow('img',image)
                    k=cv2.waitKey(1)
                    print("Showed 1")
                    cv2.imwrite('detected.png', image)
                    mail = 1
                    siren = 1
                    
            image=cv2.putText(image,"press Esc/Q to exit",(0,30), cv2.FONT_HERSHEY_PLAIN,2,(255,255,0))
            print("Showing 2")
            cv2.imshow('img',image)
            k=cv2.waitKey(1)
            print("Showed 2")
        cv2.destroyAllWindows()
        
    thread = threading.Thread(target= run)
    thread.start()
    # thread_mail = threading.Thread(target= sendmail)
    # thread_mail.start()
    
    #run()
if __name__ == "__main__":
    track_faces()
