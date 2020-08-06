from tkinter import *
from tkinter import ttk
import numpy as np
from scipy.linalg import svd
from tkinter import filedialog
from PIL import ImageTk, Image
import cv2


def img1ClickHandler(event):
    if len(imgPoints1)<10:
        x,y = event.x,event.y
        imgPoints1.append((x,y))
        print("first: ",x,y,len(imgPoints1))
        canvas1.create_oval(x-5,y-5,x+5,y+5,fill=dot_color, tags='dots')
    # print("img1:",imgPoints1)
    if len(imgPoints1) == 10 and len(imgPoints2) == 10:
        modeChk.state(['!disabled'])
    if epipolarMode.get():
        drawEpipolarLine(event.x,event.y)
    
def img2ClickHandler(event):
    if len(imgPoints2)<10:
        x,y = event.x,event.y
        imgPoints2.append((x,y))
        print("second: ",x,y,len(imgPoints2))
        canvas2.create_oval(x-5,y-5,x+5,y+5,fill=dot_color, tags='dots')
    # print("img2:",imgPoints2)
    if len(imgPoints1) == 10 and len(imgPoints2) == 10:
        modeChk.state(['!disabled'])
    
def computeFundamentalMatrix():
    print("mode chck:",epipolarMode.get())
    if epipolarMode.get():
        canvas1.delete('dots')
        canvas2.delete('dots')
        print(imgPoints1)
        pts1 = np.int32(imgPoints1)
        pts2 = np.int32(imgPoints2)
        global matrixF
        matrixF, mask = cv2.findFundamentalMat(pts1,pts2,cv2.FM_LMEDS)
        print(matrixF)
        print(matrixF[0][0])

def computeEpipolarPoints(u,v,fMatrix):
    print(matrixF)
    f1 = fMatrix[0]
    f2 = fMatrix[1]
    f3 = fMatrix[2]
    u1 = -(0*(v*f2[0]+v*f2[1]+f2[2])+u*f3[0]+v*f3[1]+f3[2])/(u*f1[0]+v*f1[1]+f1[2])
    u2 = -(1080*(v*f2[0]+v*f2[1]+f2[2])+u*f3[0]+v*f3[1]+f3[2])/(u*f1[0]+v*f1[1]+f1[2])
    return u1,0,u2,1080

def drawEpipolarLine(u,v):
    u1,v1,u2,v2 = computeEpipolarPoints(u,v,matrixF)
    canvas2.create_line(u1,v1,u2,v2,fill='red',width=5)

def selectImg1():
    imgPoints1.clear()
    imgPoints2.clear()
    epipolarMode.set(False)
    modeChk.state(['disabled'])
    # global img1Url
    img1Url = filedialog.askopenfilename(initialdir=imageDir,title="Select 1st image",filetypes=(("jpg files","*.jpg"),("all files","*.*")))
    canvas1.img = ImageTk.PhotoImage(Image.open(img1Url).resize((1920,1080)))
    canvas1.create_image(0, 0, image=canvas1.img, anchor="nw")
def selectImg2():
    imgPoints1.clear()
    imgPoints2.clear()
    epipolarMode.set(False)
    modeChk.state(['disabled'])
    # global img2Url
    img2Url = filedialog.askopenfilename(initialdir=imageDir,title="Select 2nd image",filetypes=(("jpg files","*.jpg"),("all files","*.*")))
    canvas2.img = ImageTk.PhotoImage(Image.open(img2Url).resize((1920,1080)))
    canvas2.create_image(0, 0, image=canvas2.img, anchor="nw")

def computeFundamentalMatCV():
    img1 = cv2.imread('/home/burhan/Desktop/20200714_170554.jpg',0)  #queryimage # left image
    img2 = cv2.imread('/home/burhan/Desktop/20200714_170558.jpg',0) #trainimage # right image
    sift = cv2.xfeatures2d.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)

    # FLANN parameters
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params,search_params)
    matches = flann.knnMatch(des1,des2,k=2)
    good = []
    pts1 = []
    pts2 = []
    # ratio test as per Lowe's paper
    for i,(m,n) in enumerate(matches):
        if m.distance < 0.8*n.distance:
            good.append(m)
            pts2.append(kp2[m.trainIdx].pt)
            pts1.append(kp1[m.queryIdx].pt)
    pts1 = np.int32(pts1)
    pts2 = np.int32(pts2)
    global F 
    F, mask = cv2.findFundamentalMat(pts1,pts2,cv2.FM_LMEDS)
    print(F)

if __name__ == "__main__":
    imageDir = "/home/burhan/Desktop/"
    imgPoints1 = []
    imgPoints2 = []
    # matrixA = []
    # matrixF = []
    # computeFundamentalMatCV()
    dot_color = "#476042"
    main_window = Tk()
    main_window.title("Project 2 with OpenCV")

    button1 = ttk.Button(main_window,text="Select 1st image",command=selectImg1)
    button2 = ttk.Button(main_window,text="Select 2nd image",command=selectImg2)
    button1.grid(row=0,column=0)
    button2.grid(row=0,column=1)


    frame1 = ttk.Frame(main_window)
    frame1.grid(row=1,column=0)
    frame1.config(relief=SOLID)
    frame2 = ttk.Frame(main_window)
    frame2.grid(row=1,column=1)
    frame2.config(relief=SOLID)

    canvas1 = Canvas(frame1,width=1920,height=1080)
    canvas1.bind('<Button-1>',img1ClickHandler)
    canvas1.pack()
    canvas2 = Canvas(frame2,width=1920,height=1080)
    canvas2.bind('<Button-1>',img2ClickHandler)
    canvas2.pack()

    frame3 = ttk.Frame(main_window)
    frame3.grid(row=2,column=0)
    frame3.config()

    epipolarMode = BooleanVar()
    modeChk = ttk.Checkbutton(frame3, text="Epiploar Mode", variable=epipolarMode)
    modeChk.config(command = computeFundamentalMatrix)

    modeChk.pack() 
    if len(imgPoints1) < 10 or len(imgPoints2) < 10:
        modeChk.state(['disabled'])


    main_window.mainloop()
    # print("img1:",imgPoints1)
    # print("img2:",imgPoints2)





# [[ 1.95962208e-06 -8.19836584e-05  2.64289856e-01]
#  [ 8.08639085e-05 -3.96141339e-07 -7.67321249e-02]
#  [-2.68911957e-01  7.96023215e-02  1.00000000e+00]]

# [[ 2.00517156e-08  6.46929244e-06 -1.72202368e-02]
#  [-5.87467013e-06  2.92222259e-07  1.41722732e-01]
#  [ 1.52138984e-02 -1.43034621e-01  1.00000000e+00]]