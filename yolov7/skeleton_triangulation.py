import cv2
import numpy as np

R = []

T = []

mtx1 = []

mtx2 = [] 

RT1 = np.concatenate([np.eye(3), [[0],[0],[0]]], axis = -1)
RT2 = np.concatenate([R, T], axis = -1)

#Cam_1_mtrx = mtx1 @ RT1  #TODO: to implement
#Cam_2_mtrx = mtx2 @ RT2 #TODO: to implement

def DLT(P1, P2, point1, point2):
 
    A = [point1[1]*P1[2,:] - P1[1,:],
         P1[0,:] - point1[0]*P1[2,:],
         point2[1]*P2[2,:] - P2[1,:],
         P2[0,:] - point2[0]*P2[2,:]
        ]
    A = np.array(A).reshape((4,4))
    #print('A: ')
    #print(A)
 
    B = A.transpose() @ A
    from scipy import linalg
    U, s, Vh = linalg.svd(B, full_matrices = False)
 
    print('Triangulated point: ')
    print(Vh[3,0:3]/Vh[3,3])
    return Vh[3,0:3]/Vh[3,3]


