import cv2
import threading

#This script generate frames from both cameras in cam1 e cam2 folders

class camThread(threading.Thread):
    def __init__(self, previewName, camID):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camID = camID
        self.lock = threading.Lock()
    def run(self):
        print ("Starting " + self.previewName)
        camPreview(self.previewName, self.camID)

def camPreview(previewName, camID):
    cv2.namedWindow(previewName)
    cam = cv2.VideoCapture(camID)
    if cam.isOpened():  # try to get the first frame
        rval, frame = cam.read()
    else:
        rval = False

    i = 0
    while rval:
        cv2.imshow(previewName, frame)
        #lock.acquire()
        cv2.imwrite('camera_calibration/'+'cam'+str(camID)+'/'+'frame0'+str(i)+'.jpg', frame)
        #lock.release()
        rval, frame = cam.read()
        key = cv2.waitKey(10)
        if key == 27:  # exit on ESC
            break
        i+=1
    cv2.destroyWindow(previewName)

thread1 = camThread("Camera 1", 1)
thread2 = camThread("Camera 2", 2)
thread1.start()
thread2.start()