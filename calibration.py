import numpy as np
import math
from scipy.linalg import svd

def getPointsArray(inputFile):
    with open(inputFile, 'r') as f:
        rows = int(f.readline())
        locationMatrix = []
        for i in range(rows):
            # # print(line.split())
            # if line == None:
            #     continue
            locationMatrix.append([float(num) for num in f.readline().split()])
        return locationMatrix

def createInputMatrix(locations2D, locations3D):
    matrixA = []
    vectorM = []
    for i in range(len(locations2D)):
        p3D = locations3D[i]
        p2D  = locations2D[i]
        matrixA.append([-p3D[0],-p3D[1],-p3D[2],-1,0,0,0,0,p2D[0]*p3D[0],p2D[0]*p3D[1],p2D[0]*p3D[2],p2D[0]])
        matrixA.append([0,0,0,0,-p3D[0],-p3D[1],-p3D[2],-1,p2D[1]*p3D[0],p2D[1]*p3D[1],p2D[1]*p3D[2],p2D[1]])
        vectorM.append("m"+str(i))
    return (matrixA,vectorM)

def compute2Dpoints(calibrationMatrix,point3D):
    #calculate 2D points
    m0 = calibrationMatrix[0]
    m1 = calibrationMatrix[1]
    m2 = calibrationMatrix[2]
    u = (m0[0]*point3D[0]+m0[1]*point3D[1]+m0[2]*point3D[2]+m0[3])/(m2[0]*point3D[0]+m2[1]*point3D[1]+m2[2]*point3D[2]+m2[3])
    v = (m1[0]*point3D[0]+m1[1]*point3D[1]+m1[2]*point3D[2]+m1[3])/(m2[0]*point3D[0]+m2[1]*point3D[1]+m2[2]*point3D[2]+m2[3])
    return u,v

def computeError(origPoints,computedPoints):
    #compute euclidean distance
    return math.sqrt(((computedPoints[0]-origPoints[0])**2)+((computedPoints[1]-origPoints[1])**2))

if __name__ == "__main__":
    source_path = "/mnt/3A0F13EC43ACDB83/workspace/repos/comp8510/"
    datasets=["2D.txt","3D.txt"]
    # for dataset in datasets:
    #     print(getMatrices(source_path+dataset+".txt"))
    points2D = getPointsArray(source_path+datasets[0])
    points3D = getPointsArray(source_path+datasets[1])
    matrixA,vectorM = createInputMatrix(points2D,points3D)
    # print(matrixA)
    # print(vectorM)
    U, s, vt = svd(matrixA)
    # print(s)
    # print(vt)
    minEigenValue = np.argmin(s)
    # print(minEigenValue)
    # print(vt[minEigenValue])
    calibrationMatrix = vt[minEigenValue].reshape(3,4)
    print("calibration matrix: \n",calibrationMatrix)
    # print(eigenMatrix[0])
    # print(eigenMatrix[0][0])
    computed2Dpoints = []
    errorValues = []
    for i in range(len(points3D)):
        u,v = compute2Dpoints(calibrationMatrix,points3D[i])
        computed2Dpoints.append([u,v])
        errorValues.append(computeError(points2D[i],[u,v]))
    # print(computed2Dpoints)
    avgError = sum(errorValues)/len(points2D)
    print("Average error: \n",avgError)
