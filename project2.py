from tkinter import *
from tkinter import ttk
import numpy as np
from scipy.linalg import svd

def img1ClickHandler(event):
    if len(imgPoints1)<10:
        x,y = event.x,event.y
        imgPoints1.append([x,y])
        canvas1.create_oval(x-5,y-5,x+5,y+5,fill=dot_color)
    # print("img1:",imgPoints1)
    if len(imgPoints1) == 10 and len(imgPoints2) == 10:
        epipolarMode.state(['!disabled'])
    
def img2ClickHandler(event):
    if len(imgPoints2)<10:
        x,y = event.x,event.y
        imgPoints2.append([x,y])
        canvas2.create_oval(x-5,y-5,x+5,y+5,fill=dot_color)
    # print("img2:",imgPoints2)
    if len(imgPoints1) == 10 and len(imgPoints2) == 10:
        epipolarMode.state(['!disabled'])
    
def createInputMatrix():
    for i in range(len(imgPoints1)):
        p = imgPoints1[i]
        q = imgPoints2[i]
        matrixA.append([q[0]*p[0],q[0]*p[1],q[0],q[1]*p[0],q[1]*p[1],q[1],p[0],p[1],1])
def computeFundamentalMatrix():
    if len(imgPoints1) < 10 or len(imgPoints2) < 10:
        return
    canvas1.delete('all')
    canvas2.delete('all')
    createInputMatrix()
    U, s, vt = svd(matrixA)
    minEigenValue = np.argmin(s)
    matrixF = vt[minEigenValue].reshape(3,3)
    print(matrixF)
    

if __name__ == "__main__":
    imgPoints1 = []
    imgPoints2 = []
    matrixA = []
    matrixF = []
    dot_color = "#476042"
    main_window = Tk()
    main_window.title("Project 2")
    frame1 = ttk.Frame(main_window)
    frame1.grid(row=0,column=0)
    frame1.config(relief=SOLID)
    frame2 = ttk.Frame(main_window)
    frame2.grid(row=0,column=1)
    frame2.config(relief=SOLID)

    canvas1 = Canvas(frame1,width=1280,height=720,background="blue")
    canvas1.bind('<Button-1>',img1ClickHandler)
    canvas1.pack()
    canvas2 = Canvas(frame2,width=1280,height=720,background="black")
    canvas2.bind('<Button-1>',img2ClickHandler)
    canvas2.pack()

    frame3 = ttk.Frame(main_window)
    frame3.grid(row=1,column=0)
    frame3.config()

    epipolarMode = ttk.Checkbutton(frame3, text="Epiploar Mode")
    epipolarMode.config(command = computeFundamentalMatrix)
    epipolarMode.pack() 
    if len(imgPoints1) < 10 or len(imgPoints2) < 10:
        epipolarMode.state(['disabled'])


    main_window.mainloop()
    # print("img1:",imgPoints1)
    # print("img2:",imgPoints2)
