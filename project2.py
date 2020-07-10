from tkinter import *
from tkinter import ttk
import numpy as np
from scipy.linalg import svd
from tkinter import filedialog
from PIL import ImageTk, Image

def img1ClickHandler(event):
    if len(imgPoints1)<10:
        x,y = event.x,event.y
        imgPoints1.append([x,y])
        canvas1.create_oval(x-5,y-5,x+5,y+5,fill=dot_color, tags='dots')
    # print("img1:",imgPoints1)
    if len(imgPoints1) == 10 and len(imgPoints2) == 10:
        modeChk.state(['!disabled'])
    if epipolarMode.get():
        drawEpipolarLine(event.x,event.y)
    
def img2ClickHandler(event):
    if len(imgPoints2)<10:
        x,y = event.x,event.y
        imgPoints2.append([x,y])
        canvas2.create_oval(x-5,y-5,x+5,y+5,fill=dot_color, tags='dots')
    # print("img2:",imgPoints2)
    if len(imgPoints1) == 10 and len(imgPoints2) == 10:
        modeChk.state(['!disabled'])
    
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
        createInputMatrix()
        U, s, vt = svd(matrixA)
        minEigenValue = np.argmin(s)
        global matrixF
        matrixF = vt[minEigenValue].reshape(3,3)
        print(matrixF)
    

def computeEpipolarPoints(u,v):
    print(matrixF)
    f1 = matrixF[0]
    f2 = matrixF[1]
    f3 = matrixF[2]
    u1 = -(0*(v*f2[0]+v*f2[1]+f2[2])+u*f3[0]+v*f3[1]+f3[2])/(u*f1[0]+v*f1[1]+f1[2])
    u2 = -(1080*(v*f2[0]+v*f2[1]+f2[2])+u*f3[0]+v*f3[1]+f3[2])/(u*f1[0]+v*f1[1]+f1[2])
    return u1,0,u2,1080
def drawEpipolarLine(u,v):
    u1,v1,u2,v2 = computeEpipolarPoints(u,v)
    canvas2.create_line(u1,v1,u2,v2,fill='green',width=5)
def selectImg1():
    imgPoints1.clear()
    imgPoints2.clear()
    epipolarMode.set(False)
    modeChk.state(['disabled'])
    # global img1Url
    img1Url = filedialog.askopenfilename(initialdir="/home/burhan/",title="Select 1st image",filetypes=(("jpg files","*.jpg"),("all files","*.*")))
    canvas1.img = ImageTk.PhotoImage(Image.open(img1Url).resize((1920,1080)))
    canvas1.create_image(0, 0, image=canvas1.img, anchor="nw")
def selectImg2():
    imgPoints1.clear()
    imgPoints2.clear()
    epipolarMode.set(False)
    modeChk.state(['disabled'])
    # global img2Url
    img2Url = filedialog.askopenfilename(initialdir="/home/burhan/",title="Select 2nd image",filetypes=(("jpg files","*.jpg"),("all files","*.*")))
    canvas2.img = ImageTk.PhotoImage(Image.open(img2Url).resize((1920,1080)))
    canvas2.create_image(0, 0, image=canvas2.img, anchor="nw")

if __name__ == "__main__":
    imgPoints1 = []
    imgPoints2 = []
    matrixA = []
    # matrixF = []
    dot_color = "#476042"
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
    modeChk = ttk.Checkbutton(frame3, text="Epiploar Mode", variable=epipolarMode)
    modeChk.config(command = computeFundamentalMatrix)

    modeChk.pack() 
    if len(imgPoints1) < 10 or len(imgPoints2) < 10:
        modeChk.state(['disabled'])


    main_window.mainloop()
    # print("img1:",imgPoints1)
    # print("img2:",imgPoints2)
