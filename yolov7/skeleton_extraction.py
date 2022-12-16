import torch
from torchvision import transforms

from utils.datasets import letterbox
from utils.general import non_max_suppression_kpt
from utils.plots import output_to_keypoint, plot_skeleton_kpts

import matplotlib.pyplot as plt
import cv2
import numpy as np


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

if torch.cuda.is_available:
    print('Cuda Available')
    print(torch.cuda.get_device_name(0))


def load_model():
    model = torch.load('yolov7/yolov7-w6-pose.pt', map_location=device)['model']
    # Put in inference mode
    model.float().eval()

    if torch.cuda.is_available():
        # half() turns predictions into float16 tensors
        # which significantly lowers inference time
        model.half().to(device)
    return model

model = load_model()

def run_inference(image):
    # Resize and pad image
    image = letterbox(image, 960, stride=64, auto=True)[0] # shape: (567, 960, 3)
    # Apply transforms
    image = transforms.ToTensor()(image) # torch.Size([3, 567, 960])
    if torch.cuda.is_available():
      image = image.half().to(device)
    # Turn image into batch
    image = image.unsqueeze(0) # torch.Size([1, 3, 567, 960])
    with torch.no_grad():
      output, _ = model(image)
    return output, image

def draw_keypoints(output, image):
  output = non_max_suppression_kpt(output, 
                                     0.25, # Confidence Threshold
                                     0.65, # IoU Threshold
                                     nc=model.yaml['nc'], # Number of Classes
                                     nkpt=model.yaml['nkpt'], # Number of Keypoints
                                     kpt_label=True)
  with torch.no_grad():
        output = output_to_keypoint(output)
        
  nimg = image[0].permute(1, 2, 0) * 255
  nimg = nimg.cpu().numpy().astype(np.uint8)
  nimg = cv2.cvtColor(nimg, cv2.COLOR_RGB2BGR)

  for idx in range(output.shape[0]):
      plot_skeleton_kpts(nimg, output[idx, 7:].T, 3)

  return nimg

def extract_kpts(frame):

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    output, frame = run_inference(frame)

    nimg = frame[0].permute(1, 2, 0) * 255
    nimg = nimg.cpu().numpy().astype(np.uint8)
    nimg = cv2.cvtColor(nimg, cv2.COLOR_RGB2BGR)

    output = non_max_suppression_kpt(output, 
                             0.25, # Confidence Threshold
                             0.65, # IoU Threshold
                             nc=model.yaml['nc'], # Number of Classes
                             nkpt=model.yaml['nkpt'], # Number of Keypoints
                             kpt_label=True)

    with torch.no_grad():
        output = output_to_keypoint(output)

    frame = nimg

    kpts = output[0, 7:].T
    steps = 3
    num_kpts = len(kpts) // steps
    keypoints = []
    for kid in range(num_kpts):
        x_coord, y_coord = kpts[steps * kid], kpts[steps * kid + 1]
        cv2.circle(frame, (int(x_coord), int(y_coord)), 2, (int(255), int(0), int(0)), -1)
        cv2.putText(frame, str(kid), (int(x_coord), int(y_coord)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        keypoints.append((kid, x_coord, y_coord))

    return keypoints, frame

        

def pose_estimation_video(filename):

    if filename == '0':
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(filename)

    # VideoWriter for saving the video
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter('VideoEsempio1.mp4', fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():

        (ret, frame) = cap.read()

        if ret == True:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            output, frame = run_inference(frame)

            frame = draw_keypoints(output, frame)

            frame = cv2.resize(frame, (int(cap.get(3)), int(cap.get(4))))
            out.write(frame)
            cv2.imshow('Pose estimation', frame)
        else:
            break

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

