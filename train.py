# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import Message ,Text
import cv2,os
import shutil
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk
import tkinter.font as font
import mysql.connector
import sqlite3
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import glob
from Adafruit_CharLCD import Adafruit_CharLCD


conn = sqlite3.connect('students.db')
cursor = conn.cursor()

window= tk.Tk()
#helv36 = tk.Font(family='Helvetica', size=36, weight='bold')
window.title("Face_Recogniser")

dialog_title = 'QUIT'
dialog_text = 'Are you sure?'
#answer = messagebox.askquestion(dialog_title, dialog_text)
 
window.geometry('1000x600')
window.configure(background='teal')

#window.attributes('-fullscreen', True)

window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)

#path = "profile.jpg"

#Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
#img = ImageTk.PhotoImage(Image.open(path))

#The Label widget is a standard Tkinter widget used to display a text or image on the screen.
#panel = tk.Label(window, image = img)


#panel.pack(side = "left", fill = "y", expand = "no")

#cv_img = cv2.imread("img541.jpg")
#x, y, no_channels = cv_img.shape
#canvas = tk.Canvas(window, width = x, height =y)
#canvas.pack(side="left")
#photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(cv_img)) 
# Add a PhotoImage to the Canvas
#canvas.create_image(0, 0, image=photo, anchor=tk.NW)

#msg = Message(window, text='Hello, world!')

# Font is a tuple of (font_family, size_in_points, style_modifier_string)

#y=top padding,x=left padding

message = tk.Label(window, text="Smart-Attendance-System-with-Face recognition and RFID" ,bg="lime"  ,fg="black"  ,width=50  ,height=3,font=('times', 25, 'italic bold underline')) 

message.place(x=23, y=20)

lbl = tk.Label(window, text="Enter ID",width=15  ,height=2  ,fg="black"  ,bg="yellow" ,font=('times', 15, ' bold ')) 
lbl.place(x=100, y=180)

txt = tk.Entry(window,width=20  ,bg="yellow" ,fg="black",font=('times', 15, ' bold '))
txt.place(x=320, y=195)

lbl2 = tk.Label(window, text="Enter Name",width=15  ,fg="black"  ,bg="yellow"    ,height=2 ,font=('times', 15, ' bold ')) 
lbl2.place(x=100, y=280)

txt2 = tk.Entry(window,width=20  ,bg="yellow"  ,fg="black",font=('times', 15, ' bold ')  )
txt2.place(x=320, y=295)

lbl3 = tk.Label(window, text="Notification : ",width=15  ,fg="black"  ,bg="yellow"  ,height=2 ,font=('times', 15, ' bold underline ')) 
lbl3.place(x=100, y=380)

message = tk.Label(window, text="" ,bg="yellow"  ,fg="black"  ,width=35 ,height=2, activebackground = "yellow" ,font=('times', 15, ' bold ')) 
message.place(x=320, y=380)

lbl3 = tk.Label(window, text="Attendance : ",width=15  ,fg="black"  ,bg="yellow"  ,height=2 ,font=('times', 15, ' bold  underline')) 
lbl3.place(x=100, y=540)

message2 = tk.Label(window, text="" ,fg="black"   ,bg="yellow",activeforeground = "green",width=36  ,height=2  ,font=('times', 15, ' bold ')) 
message2.place(x=315, y=540)



def clear():
    txt.delete(0, 'end')    
    res = ""
    message.configure(text= res)

def clear2():
    txt2.delete(0, 'end')    
    res = ""
    message.configure(text= res)    
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

Attendance=0

def TakeImages():        
    Id=(txt.get())
    name=(txt2.get())
    if(is_number(Id) and name.isalpha()):
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector=cv2.CascadeClassifier(harcascadePath)
        sampleNum=0
        while(True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)        
                #incrementing sample number 
                sampleNum=sampleNum+1
                #saving the captured face in the dataset folder TrainingImage
                cv2.imwrite("/home/pi/Smart-attendance-system-with-face-recognition-master(Raspberry)/TrainingImage/ "+name +"."+Id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
                #display the frame
                cv2.imshow('frame',img)
            #wait for 100 miliseconds 
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # break if the sample number is morethan 100
            elif sampleNum>30:
                break
        cam.release()
        cv2.destroyAllWindows() 
        res = "Images Saved for ID : " + Id +" Name : "+ name
        row = [Id , name]
        #sending the registered student data to the database
        cursor.execute("""INSERT INTO attendance VALUES (?,?,?)""", [(Id),(name),(Attendance)])
        conn.commit()
        print("Records inserted........")
        message.configure(text= res)
    else:
        if(is_number(Id)):
            res = "Enter Alphabetical Name"
            message.configure(text= res)
        if(name.isalpha()):
            res = "Enter Numeric Id"
            message.configure(text= res)
    
def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()#recognizer = cv2.face.LBPHFaceRecognizer_create()#$cv2.createLBPHFaceRecognizer()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector =cv2.CascadeClassifier(harcascadePath)
    faces,Id = getImagesAndLabels("TrainingImage")
    recognizer.train(faces, np.array(Id))
    recognizer.save("/home/pi/Smart-attendance-system-with-face-recognition-master(Raspberry)/TrainingImageLabel/Trainner.yml")
    res = "Image Trained"#+",".join(str(f) for f in Id)
    message.configure(text= res)
    directory='/home/pi/Smart-attendance-system-with-face-recognition-master(Raspberry)/TrainingImage'
    os.chdir(directory)
    files=glob.glob('*jpg')
    for filename in files:
        os.remove(filename)

def getImagesAndLabels(path):
    #get the path of all the files in the folder
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)] 
    #print(imagePaths)
    
    #create empth face list
    faces=[]
    #create empty ID list
    Ids=[]
    #now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        #loading the image and converting it to gray scale
        pilImage=Image.open(imagePath).convert('L')
        #Now we are converting the PIL image into numpy array
        imageNp=np.array(pilImage,'uint8')
        #getting the Id from the image
        Id=int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        Ids.append(Id)        
    return faces,Ids


# instantiate lcd and specify pins
lcd = Adafruit_CharLCD(rs=21, en=24, d4=23, d5=17, d6=18, d7=22, cols=16, lines=2)
lcd.clear()


def TrackImages():
    lcd.message("Scan your RFID")

    reader = SimpleMFRC522()
    id, text = reader.read()
    rfid=int(text)
    lcd.clear()
    text="Id {} Recognized".format(rfid)
    lcd.message(text)
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()#cv2.createLBPHFaceRecognizer()
    recognizer.read("/home/pi/Smart-attendance-system-with-face-recognition-master(Raspberry)/TrainingImageLabel/Trainner.yml")
    harcascadePath = "/home/pi/Smart-attendance-system-with-face-recognition-master(Raspberry)/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath);    
    Id="Unknown"
    tt=str(Id)
    z=0
    if(rfid>0):
        cam = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_SIMPLEX
        col_names =  ['Id','Name','Attendance']
        attendance = pd.DataFrame(columns = col_names)
        time.sleep(2)
        lcd.clear()
        lcd.message("Identifying")
        while True:
            #Detection
            ret, im =cam.read()
            gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
            faces=faceCascade.detectMultiScale(gray, 1.3,5)
            #Recognition
            for(x,y,w,h) in faces:
                cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
                Id, conf = recognizer.predict(gray[y:y+h,x:x+w])
                if(conf < 50):
                    ts = time.time()
                    aa=cursor.execute("SELECT [Name] FROM attendance WHERE Id = {}".format(Id))
                    aa=cursor.fetchone()
                    tt=str(Id)+"-"+aa[0]

                else:
                    Id='Unknown'
                    tt=str(Id)
                    
                

                if(conf > 75):
                    noOfFile=len(os.listdir("/home/pi/Smart-attendance-system-with-face-recognition-master(Raspberry)/ImagesUnknown"))+1
                    cv2.imwrite("/home/pi/Smart-attendance-system-with-face-recognition-master(Raspberry)/ImagesUnknown/Image"+str(noOfFile) + ".jpg", im[y:y+h,x:x+w])
                cv2.putText(im,str(tt),(x,y+h), font, 1,(255,255,255),2)
                attendance=attendance.drop_duplicates(subset=['Id'],keep='last')
            cv2.imshow('Recognizer',im)
            z=z+1
            if(z==100) or (Id==rfid):
                break

            cv2.waitKey(1) & 0xFF
        
        cam.release()
        cv2.destroyAllWindows()

        #Database
        if(rfid==Id):
            cursor.execute("""UPDATE attendance set Attendance=Attendance+1 where id={}""".format(Id))
            conn.commit()
            Attendance=cursor.execute("SELECT [Attendance] FROM attendance WHERE Id = {}".format(Id))
            Attendance=cursor.fetchone()
            attendance.loc[len(attendance)] = [Id,aa[0],Attendance[0]]
            res=attendance
            text=" Attendance Updated\n -{}".format(aa[0])
            
            message2.configure(text= res)
            
            lcd.clear()      
            lcd.message(text)
            for x in range(0,3):
                lcd.move_left()
                time.sleep(2)
            time.sleep(1)
            
            for x in range(0,2):
                lcd.move_right()
                time.sleep(1)
            time.sleep(2)
            lcd.clear()
            
        else:
            lcd.clear()
            res="Id Mismatch"
            lcd.message(res)
            message2.configure(text= res)
         #print(attendance)
            time.sleep(3)
        lcd.clear()
        

  
clearButton = tk.Button(window, text="Clear", command=clear  ,fg="black"  ,bg="yellow"  ,width=15  ,height=2 ,activebackground = "Red" ,font=('times', 15, ' bold '))
clearButton.place(x=550, y=180)
clearButton2 = tk.Button(window, text="Clear", command=clear2  ,fg="black"  ,bg="yellow"  ,width=15  ,height=2, activebackground = "Red" ,font=('times', 15, ' bold '))
clearButton2.place(x=550, y=280)    
takeImg = tk.Button(window, text="Take Images", command=TakeImages  ,fg="black"  ,bg="yellow"  ,width=15  ,height=2, activebackground = "Red" ,font=('times', 15, ' bold '))
takeImg.place(x=60,y=460)
trainImg = tk.Button(window, text="Train Images", command=TrainImages  ,fg="black"  ,bg="yellow"  ,width=15 ,height=2, activebackground = "Red" ,font=('times', 15, ' bold '))
trainImg.place(x=280, y=460)
trackImg = tk.Button(window, text="Track Images", command=TrackImages  ,fg="black"  ,bg="yellow"  ,width=15  ,height=2, activebackground = "Red" ,font=('times', 15, ' bold '))
trackImg.place(x=500, y=460)
quitWindow = tk.Button(window, text="Quit", command=window.destroy  ,fg="black"  ,bg="yellow"  ,width=15  ,height=2, activebackground = "Red" ,font=('times', 15, ' bold '))
quitWindow.place(x=730, y=460)
copyWrite = tk.Text(window, background=window.cget("background"), borderwidth=0,font=('times', 30, 'italic bold underline'),)
copyWrite.configure(state="disabled",fg="red"  )
copyWrite.place(x=800, y=750)


window.mainloop()