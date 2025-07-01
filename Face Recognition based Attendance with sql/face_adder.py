import numpy as np
# import pandas as pd
import os
# from skimage.measure import compare_ssim
from skimage.metrics import structural_similarity
# import imutils
import cv2
import sqlite3

conn = sqlite3.connect("atten.db")

def take_snap(save_as='img.png'):
    cam=cv2.VideoCapture(0)
    _,img=cam.read()
    cv2.imshow('img',img)
    k=cv2.waitKey(1)
    while(k not in (27,ord('q'))):
        _,img=cam.read()
        cv2.imshow('img',img)
        k=cv2.waitKey(1)
        if(k in (ord(' '),ord('s'),13)):
            print("saving image at ",save_as)
            cv2.imwrite(save_as,img)
            print("press any key to continue")
            cv2.waitKey(0)
            break

def find_similarity(img1,img2):
    gray_img1=cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
    gray_img2=cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
    score,diff=structural_similarity(gray_img1,gray_img2,full=True)
    return(score)

def add_face(label,folder='train_images',req_count=50,rewrite=True):
    cam=cv2.VideoCapture(0) #initialising camera
    path="%s/%s"%(folder,label)
    
    face_detector=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    try:
        os.mkdir(path)
    except FileExistsError:
        # print("The training images for this label seems to already exist")
        # choice=input("Do you want to rewrite them?(Y/N): ")
        # if(choice in 'nN'):
        #     return
        if(not rewrite):
            return
        for image_name in os.listdir(path):
            os.remove(os.path.join(path,image_name))
    
    status=''

    ret,img=cam.read() #taking image
    show_img=np.copy(img)

    nr,nc,_=img.shape #height and width of image
    midx,midy=nc//2,nr//2 #center of image
    face_win=((midx-200,midy-200),(midx+200,midy+200))  # rectangle coords around center
    

    count=0 #initialise counter for filename generation of multiple images
    saved_images=[]
    
    while(count<req_count):#k not in (27,ord('q'))):  #27 is for esc button 
        ret,img=cam.read() #taking next snap
        show_img=np.copy(img)


        cv2.rectangle(show_img,face_win[0],face_win[1],color=(0,255,0)) #draw the rectangle around center
        cv2.circle(show_img,(midx,midy),radius=2,color=(0,255,0),thickness=-1) #mark the center with filled circle

        face_box=img[face_win[0][1]:face_win[1][1],face_win[0][0]:face_win[1][0]]
        gray_face=cv2.cvtColor(face_box,cv2.COLOR_BGR2GRAY)
        faces=face_detector.detectMultiScale(gray_face)

        if(len(faces)!=1):
            # print("\rCan't locate your face\t\t\t\t",end='')
            # status="Can't locate your face"
            cv2.putText(show_img,"Can't locate your face",(0,30), cv2.FONT_HERSHEY_PLAIN,2,(255,0,0))
            cv2.putText(show_img,'Saved %d/%d images'%(count,req_count),(0,nr-30), cv2.FONT_HERSHEY_PLAIN,1.7,(255,255,0))
        
            cv2.imshow('img',show_img)   #show the resultant image
            k=cv2.waitKey(1) #wait for a secound and return key press , -1 if key is not pressed

            continue

        face=faces[0]
        left=face[0]+face_win[0][0]
        top=face[1]+face_win[0][1]
        width=face[2]
        height=face[3]
        cv2.rectangle(show_img,(left,top),(left+width,top+height),color=(255,0,0))
        cv2.putText(show_img,label,(left,top-5), cv2.FONT_HERSHEY_PLAIN,1.5,(255,0,0))
        
        # cv2.imshow('img',show_img)   #show the resultant image
        # print("\rpress spaceBar/enter/s/S to select pic",end='')
        # k=cv2.waitKey(1) #wait for a secound and return key press , -1 if key is not pressed
        # if(k in (ord(' '),ord('s'),ord('S'),13)):

        left=face[0]
        top=face[1]
        cropped_image=face_box[top:top+height,left:left+width]
        # img[face_win[0][1]:face_win[1][1],face_win[0][0]:face_win[1][0]] #cropping image around rectangle
        face_img=cv2.resize(cropped_image,(100,100),interpolation=cv2.INTER_AREA)

        similarities=[find_similarity(img1,face_img) for img1 in saved_images]
        thresh_cond=[0.2<sim<0.6 for sim in similarities]

        if(not all(thresh_cond)):
            # print("\rThreshold condition failed the values are:-")
            # print(similarities)
            # status='Try changing face angle or expression'
            cv2.putText(show_img,'Try changing lighting/pose/expression',(0,30), cv2.FONT_HERSHEY_PLAIN,1.7,(255,255,0))
            cv2.putText(show_img,'Saved %d/%d images'%(count,req_count),(0,nr-30), cv2.FONT_HERSHEY_PLAIN,1.7,(255,255,0))
            cv2.imshow('img',show_img)   #show the resultant image
            k=cv2.waitKey(1) #wait for a secound and return key press , -1 if key is not pressed
            continue

        file_name="%s/%s/img%d.png"%(folder,label,count) #generate file name
        # print("\rsaving frame at ",file_name)
        cv2.putText(show_img,'Saved %d/%d images'%(count,req_count),(0,nr-30), cv2.FONT_HERSHEY_PLAIN,1.7,(255,255,0))
        count+=1 #increase counter for next image file
        saved_images.append(face_img)

        cv2.imshow(file_name,face_img)
        cv2.imshow('img',show_img) 
        cv2.imwrite(file_name,face_img)
        # print("press any key to continue")
        k=cv2.waitKey(1)
    cv2.destroyAllWindows()
    sq = f"""create table if not exists {label.replace(" ","_")}
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                     name text not null,
                     attend int not null,
                     date text not null)"""
    conn.execute(sq)
    conn.close()
if __name__=="__main__":
    # take_snap()
    label=input("Enter person name:")
    add_face(label=label,req_count=10,rewrite=True)

    # for i1 in os.listdir("train_images/test"):
    #     img1=cv2.imread('train_images/test/'+i1)
    #     print(i1)
    #     for i2 in os.listdir("train_images/test"):
    #         img2=cv2.imread('train_images/test/'+i2)
    #         print('\t\t',i2,'-->',find_similarity(img1,img2))
