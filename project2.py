from tkinter import *
from tkinter import ttk
import numpy as np
from scipy.linalg import svd
from tkinter import filedialog
from PIL import ImageTk, Image
import cv2

def img1ClickHandler(event):
    # if len(imgPoints1)<10:
    #     x,y = event.x,event.y
    #     print("first: ",x,y)
    #     imgPoints1.append([x,y])
    #     canvas1.create_oval(x-5,y-5,x+5,y+5,fill=dot_color, tags='dots')
    # print("img1:",imgPoints1)
    if len(imgPoints1) == 10 and len(imgPoints2) == 10:
        epiModeChk.state(['!disabled'])
    
    if epipolarMode.get():
        x,y = event.x,event.y
        canvas1.create_oval(x-5,y-5,x+5,y+5,fill=dot_color, tags='dots')
        drawEpipolarLine(x,y)
    
def img2ClickHandler(event):
    # if len(imgPoints2)<10:
    #     x,y = event.x,event.y
    #     print("second: ",x,y)
    #     imgPoints2.append([x,y])
    #     canvas2.create_oval(x-5,y-5,x+5,y+5,fill=dot_color, tags='dots')
    # print("img2:",imgPoints2)
    if len(imgPoints1) == 10 and len(imgPoints2) == 10:
        epiModeChk.state(['!disabled'])
    
def createInputMatrix():
    for i in range(len(imgPoints1)):
        p = imgPoints1[i]
        q = imgPoints2[i]
        matrixA.append([q[0]*p[0],q[0]*p[1],q[0],q[1]*p[0],q[1]*p[1],q[1],p[0],p[1],1])
def computeFundamentalMatrix():
    print("mode chck:",epipolarMode.get())
    # if len(imgPoints1) < 10 or len(imgPoints2) < 10:
    #     return
    if epipolarMode.get():
        canvas1.delete('dots')
        canvas2.delete('dots')
        print(imgPoints1)
        createInputMatrix()
        U, s, vt = svd(matrixA)
        minEigenValue = np.argmin(s)
        global matrixF
        matrixF = vt[minEigenValue].reshape(3,3)
        print(matrixF)
    

def computeEpipolarPoints(u,v):
    # print(matrixF)
    f1 = matrixF[0]
    f2 = matrixF[1]
    f3 = matrixF[2]
    u1 = -((0*(v*f2[0]+v*f2[1]+f2[2]))+u*f3[0]+v*f3[1]+f3[2])/(u*f1[0]+v*f1[1]+f1[2])
    u2 = -((1080*(v*f2[0]+v*f2[1]+f2[2]))+u*f3[0]+v*f3[1]+f3[2])/(u*f1[0]+v*f1[1]+f1[2])
    return int(u1),0,int(u2),1080

def computeAvg(img,u,v,n):
    sum = 0
    for i in range(-n,n+1):
        for j in range(-n,n+1):
            sum+=img[u+i][v+j]
    return sum/(2*n+1)**2

def computeStdDeviation(img,u,v,n):
    sum = 0
    avg = computeAvg(img,u,v,n)
    for i in range(-n,n+1):
        for j in range(-n,n+1):
            sum+= (img[u+i][v+j] - avg)**2
    return (sum**0.5)/(2*n+1)

def computeZNCC(img1,img2,u,v,u1,v1,n):
    std_deviation1 = computeStdDeviation(img1,u,v,n)
    std_deviation2 = computeStdDeviation(img2,u1,v1,n)
    avg1=computeAvg(img1,u,v,n)
    avg2=computeAvg(img2,u1,v1,n)
    sum=0
    for i in range(-n,n+1):
        for j in range(-n,n+1):
            sum+=(img1[u+i][v+j] - avg1)*(img2[u1+i][v1+j] - avg2)
    return sum/((2*n+1)**2 * std_deviation1*std_deviation2)

def drawEpipolarLine(u,v):
    u1,v1,u2,v2 = computeEpipolarPoints(u,v)
    canvas2.create_line(u1,v1,u2,v2,fill='green',width=5)
    p1 = np.array([u1,v1])
    p2 = np.array([u2,v2])
    # im1= Image.open(img1Url).resize((1920,1080))
    # im2= Image.open(img2Url).resize((1920,1080))
    # img1 = np.asarray(im1)
    # img2 = np.asarray(im2)
    # points = getLinePoints(u1,v1,u2,v2)
    # for p in points:
    #     print(computeZNCC(img1,img2,u,v,p[0],p[1],50))
    

def selectImg1():
    imgPoints1.clear()
    imgPoints2.clear()
    epipolarMode.set(False)
    # epiModeChk.state(['disabled'])
    global img1Url
    img1Url = filedialog.askopenfilename(initialdir=imageDir,title="Select 1st image",filetypes=(("jpg files","*.jpg"),("all files","*.*")))
    canvas1.img = ImageTk.PhotoImage(Image.open(img1Url).resize((1920,1080)))
    canvas1.create_image(0, 0, image=canvas1.img, anchor="nw")
def selectImg2():
    imgPoints1.clear()
    imgPoints2.clear()
    epipolarMode.set(False)
    # epiModeChk.state(['disabled'])
    global img2Url
    img2Url = filedialog.askopenfilename(initialdir=imageDir,title="Select 2nd image",filetypes=(("jpg files","*.jpg"),("all files","*.*")))
    canvas2.img = ImageTk.PhotoImage(Image.open(img2Url).resize((1920,1080)))
    canvas2.create_image(0, 0, image=canvas2.img, anchor="nw")
def getLinePoints(x1, y1, x2, y2):
    points = []
    issteep = abs(y2-y1) > abs(x2-x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2-y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if(x>0 and x<1921):
            if issteep:
                points.append((y, x))
            else:
                points.append((x, y))
            error -= deltay
            if error < 0:
                y += ystep
                error += deltax

        
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return points


if __name__ == "__main__":
    imageDir = "/home/burhan/Desktop/"
    imgPoints1 = []
    imgPoints2 = []
    matrixA = []
    # matrixF = []
    dot_color = "#FF0000"
    main_window = Tk()
    main_window.title("Project 2")

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
    epiModeChk = ttk.Checkbutton(frame3, text="Epiploar Mode", variable=epipolarMode)
    # epiModeChk.config(command = computeFundamentalMatrix)

    epiModeChk.pack() 
    # if len(imgPoints1) < 10 or len(imgPoints2) < 10:
    #     epiModeChk.state(['disabled'])
    # global matrixF
    frame4 = ttk.Frame(main_window)
    frame4.grid(row=2,column=1)
    frame4.config()

    pixelMode = BooleanVar()
    pixModeChk = ttk.Checkbutton(frame4, text="Pixel Matching Mode", variable=pixelMode)
    # pixModeChk.config(command = )
    pixModeChk.pack()
    matrixF = [[-2.78119151e-08, -6.59734003e-06,  5.16262124e-03],[ 2.58666671e-06,  2.74851330e-07, -1.46301729e-01],[-6.10334920e-03,  1.49293048e-01,  9.77877030e-01]]

    main_window.mainloop()
    # print("img1:",imgPoints1)
    # print("img2:",imgPoints2)


# [[-2.78119151e-08 -6.59734003e-06  5.16262124e-03]
#  [ 2.58666671e-06  2.74851330e-07 -1.46301729e-01]
#  [-6.10334920e-03  1.49293048e-01  9.77877030e-01]]