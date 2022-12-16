import cv2
import threading
from skeleton_extraction import extract_kpts
import skeleton_triangulation
import numpy as np
import matplotlib as plt

class camThread(threading.Thread):

    def __init__(self, previewName, camId):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camId = camId
        self.stream = cv2.VideoCapture(self.camId)
        #Reading first frame
        if self.stream.isOpened():
            self.ret, self.frame = self.stream.read()

    def run(self):
        cap = cv2.VideoCapture(self.camId)
        while cap.isOpened():
        
            (ret, frame) = cap.read()
            
            if ret == True:
                #Extracting keypoints 
                self.current_kpts = extract_kpts(frame)
                #cv2.imshow(frame)

class cameraThread:

    def __init__(self, previewName, camId) :
        self.stream = cv2.VideoCapture(camId)
        (self.grabbed, self.frame) = self.stream.read()
        self.current_kpts, self.frame = extract_kpts(self.frame)
        self.started = False
        self.read_lock = threading.Lock()

    def start(self) :
        if self.started :
            return None

        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self
    
    def update(self) :
        while self.started :
            (grabbed, frame) = self.stream.read()
            kpts, frame = extract_kpts(frame)
            self.read_lock.acquire()
            self.grabbed, self.frame = grabbed, frame
            self.current_kpts = kpts
            self.read_lock.release()

    def readKpts(self):
        self.read_lock.acquire()
        kpts = self.current_kpts.copy()
        print(kpts)
        self.read_lock.release()
        return kpts

    def read(self) :
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

    def stop(self) :
        self.started = False
        self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback) :
        self.stream.release()

thread1 = cameraThread("Camera1", 0)
thread2 = cameraThread("Camera2", 1)
thread1.start()
thread2.start()

while True :

    frame = thread1.read()
    kpts = thread1.readKpts()
    frame2 = thread2.read()
    kpts2 = thread2.readKpts()

    #if TODO: frame.timestamp == frame2.timestamp:
    
    #Projection camera matrices
    #P1, P2 = []

    #3d points
    p3ds = []

    #kpts iteration and triangulation (we don't consider the kpt index that is the first element uv[0])
    '''
    for uv1, uv2 in zip(kpts, kpts2):
        _p3d = DLT(P1, P2, uv1[1:], uv2[1:])
        p3ds.append(_p3d)
    p3ds = np.array(p3ds)
    '''    
    print(kpts)
    
    cv2.imshow('webcam', frame)
    cv2.imshow('webcam2', frame2)

    if cv2.waitKey(1) == 27 :
        break

thread1.stop()
thread2.stop()

'''
while True:
    try:
        print(thread1.current_ktps)

    except KeyboardInterrupt:
        thread1.killThread = True
        break
    
    #if(thread1.frame.count != 0):
        #cv2.imshow("PoseEst", thread1.frame)
'''
''' 
cap = cv2.VideoCapture(0)
#cap2 = cv2.VideoCapture(1)

#To change ==> while cap.isOpened() && cap2.isOpened()


while cap.isOpened():

    (ret, frame) = cap.read()
    #(ret2, frame2) = cap2.read()

    if ret == True:
        
        #Extracting keypoints from skeleton 1
        kpts_camera_1 = extract_kpts(frame)
        print(kpts_camera_1)

        #Extractingkeypoints from skeleton 2
        #kpts_camera_2 = extract_kpts(frame2)

        #TODO: Triangulate from 2D to 3D
        #skeleton_triangulation ....

        #TODO: send 3D data with ZMQ/Protobuff
'''
