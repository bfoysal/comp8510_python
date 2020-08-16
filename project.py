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
    # # print("img1:",imgPoints1)
    # if len(imgPoints1) == 10 and len(imgPoints2) == 10:
    #     epiModeChk.state(['!disabled'])
    
    if epipolarMode.get():
        x,y = event.x,event.y
        canvas1.create_oval(x-5,y-5,x+5,y+5,fill=dot_color, tags='dots')
        drawEpipolarLine(x,y)
    
def img2ClickHandler(event):
    # if len(imgPoints2)<10:
    #     x,y = event.x,event.y
    #     # print("second: ",x,y)
    #     imgPoints2.append([x,y])
    #     canvas2.create_oval(x-5,y-5,x+5,y+5,fill=dot_color, tags='dots')
    # # print("img2:",imgPoints2)
    if len(imgPoints1) == 10 and len(imgPoints2) == 10:
        epiModeChk.state(['!disabled'])
    
def createInputMatrix():
    for i in range(len(imgPoints1)):
        p = imgPoints1[i]
        q = imgPoints2[i]
        matrixA.append([q[0]*p[0],q[0]*p[1],q[0],q[1]*p[0],q[1]*p[1],q[1],p[0],p[1],1])
def computeFundamentalMatrix():
    # print("mode chck:",epipolarMode.get())
    # if len(imgPoints1) < 10 or len(imgPoints2) < 10:
    #     return
    if epipolarMode.get():
        canvas1.delete('dots')
        canvas2.delete('dots')
        # print(imgPoints1)
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
    v1 = -(0*(u*f1[0]+v*f1[1]+f1[2])+u*f3[0]+v*f3[1]+f3[2])/(u*f2[0]+v*f2[1]+f2[2])
    v2 = -(1080*(u*f1[0]+v*f1[1]+f1[2])+u*f3[0]+v*f3[1]+f3[2])/(u*f2[0]+v*f2[1]+f2[2])
    # u1 = -(0*(u*f2[0]+v*f2[1]+f2[2])+u*f3[0]+v*f3[1]+f3[2])/(u*f1[0]+v*f1[1]+f1[2])
    # u2 = -(1080*(u*f2[0]+v*f2[1]+f2[2])+u*f3[0]+v*f3[1]+f3[2])/(u*f1[0]+v*f1[1]+f1[2])
    # return int(u1),0,int(u2),1080
    return 0,v1,1080,v2
def getSearchRange(u,v,n):
    # print(matrixF)
    f1 = matrixF[0]
    f2 = matrixF[1]
    f3 = matrixF[2]
    v1 = -((u-n)*(u*f1[0]+v*f1[1]+f1[2])+u*f3[0]+v*f3[1]+f3[2])/(u*f2[0]+v*f2[1]+f2[2])
    v2 = -((u+n)*(u*f1[0]+v*f1[1]+f1[2])+u*f3[0]+v*f3[1]+f3[2])/(u*f2[0]+v*f2[1]+f2[2])
    return u-n,v1,u+n,v2

def computeAvg(img,u,v,n):
    sum = 0
    for i in range(-n,n+1):
        for j in range(-n,n+1):
            if((u+i)<frameWidth and (v+j)<frameHeight):
                # print((u+i),(v+j))
                sum+=img[u+i][v+j]
    return sum/(2*n+1)**2

def computeStdDeviation(img,u,v,n):
    sum = 0
    avg = computeAvg(img,u,v,n)
    for i in range(-n,n+1):
        for j in range(-n,n+1):
            if((u+i)<frameWidth and (v+j)<frameHeight):
                sum+= (img[u+i][v+j] - avg)**2
    return (sum**0.5)/(2*n+1)

def computeZNCC(img1,img2,u,v,u1,v1,n):
    std_deviation1 = computeStdDeviation(img1,u,v,n)
    std_deviation2 = computeStdDeviation(img2,u1,v1,n)
    avg1=computeAvg(img1,u,v,n)
    avg2=computeAvg(img2,u1,v1,n)
    # print(std_deviation1,std_deviation2)
    sum=0
    for i in range(-n,n+1):
        for j in range(-n,n+1):
            if((u+i)<frameWidth and (v+j)<frameHeight and (u1+i)<frameWidth and (v1+j)<frameHeight):
                sum+=(img1[u+i][v+j] - avg1)*(img2[u1+i][v1+j] - avg2)
            
    return sum/((2*n+1)**2 * std_deviation1*std_deviation2)

def drawEpipolarLine(u,v):
    u1,v1,u2,v2 = computeEpipolarPoints(u,v)
    # print(u1,v1,u2,v2)
    canvas2.create_line(u1,v1,u2,v2,fill='green',width=5)
    x1,y1,x2,y2 = getSearchRange(u,v,50)
    # print(x1,y1,x2,y2)
    # canvas2.create_line(x1,y1,x2,y2,fill='red',width=5)
    # p1 = np.array([u1,v1])
    # p2 = np.array([u2,v2])
    im1= Image.open(img1Url).resize((1080,1080))
    im2= Image.open(img2Url).resize((1080,1080))
    img1 = np.asarray(im1)
    img2 = np.asarray(im2)
    points = getLinePoints(x1,y1,x2,y2)
    maxZNCC = 0
    matchedPixel = (0,0)
    for p in points:
        # print(p)
        # print(computeZNCC(img1,img2,int(u),int(v),int(p[0]),int(p[1]),50))
        # canvas2.create_text(p[0],p[1],fill='red',font="Times 12",text="X")
        zncc = computeZNCC(img1,img2,int(u),int(v),int(p[0]),int(p[1]),4)
        if(maxZNCC<zncc[0]):
            maxZNCC = zncc[0]
            matchedPixel = p
    canvas2.create_text(matchedPixel[0],matchedPixel[1],fill='red',font="Times 8",text="X")


    

def selectImg1():
    imgPoints1.clear()
    imgPoints2.clear()
    # epipolarMode.set(False)
    # epiModeChk.state(['disabled'])
    global img1Url
    img1Url = filedialog.askopenfilename(initialdir=imageDir,title="Select 1st image",filetypes=(("jpg files","*.jpg"),("all files","*.*")))
    canvas1.img = ImageTk.PhotoImage(Image.open(img1Url).resize((1080,1080)))
    canvas1.create_image(0, 0, image=canvas1.img, anchor="nw")
def selectImg2():
    imgPoints1.clear()
    imgPoints2.clear()
    # epipolarMode.set(False)
    # epiModeChk.state(['disabled'])
    global img2Url
    img2Url = filedialog.askopenfilename(initialdir=imageDir,title="Select 2nd image",filetypes=(("jpg files","*.jpg"),("all files","*.*")))
    canvas2.img = ImageTk.PhotoImage(Image.open(img2Url).resize((1080,1080)))
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
    for x in np.arange(x1, x2 + 1,1):
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
    frameHeight = 1080
    frameWidth = 1080
    imgPoints1 = []
    imgPoints2 = []
    matrixA = []
    # matrixF = []
    dot_color = "#FF0000"
    main_window = Tk()
    main_window.title("Project 3")

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

    canvas1 = Canvas(frame1,width=1080,height=1080)
    canvas1.bind('<Button-1>',img1ClickHandler)
    canvas1.pack()
    canvas2 = Canvas(frame2,width=1080,height=1080)
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
    # # global matrixF
    frame4 = ttk.Frame(main_window)
    frame4.grid(row=2,column=1)
    frame4.config()

    pixelMode = BooleanVar()
    pixModeChk = ttk.Checkbutton(frame4, text="Pixel Matching Mode", variable=pixelMode)
    # pixModeChk.config(command = )
    # pixModeChk.pack()
    # matrixF = [[ 1.58406946e-07,  4.51762381e-07,  6.22376948e-03], [-2.69211010e-06, -2.24845556e-07, -6.57431845e-02], [-7.95642642e-03,  6.66038165e-02,  9.95560006e-01]]
    matrixF = [[ 1.60230126e-06, -1.20558896e-05,  1.70701100e-02], [ 8.78526657e-06, -6.92767089e-07, -7.79206768e-02], [-1.98507659e-02,  7.98544041e-02,  9.93411395e-01]]
    # matrixF = [[-1.25032772e-06,  1.87239054e-04, -1.61803424e-02], [-4.03134512e-04, -3.86798195e-06, -2.97906313e+00], [ 1.55964152e-02,  3.08254827e+00,  1.00000000e+00]]
    

    main_window.mainloop()
    # print("img1:",imgPoints1)
    # print("img2:",imgPoints2)
    

