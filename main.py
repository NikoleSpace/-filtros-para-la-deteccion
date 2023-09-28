import cv2
import pickle
import cvzone
import numpy as np
import time

# video feed
cap = cv2.VideoCapture('people.mp4')

with open('ChairPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 80, 150

space_timers = {i: None for i in range(len(posList))}


def checkChairSpace(imgPro):
    spaceCounter = 0
    current_time = time.time()

    for i, pos in enumerate(posList):
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)
        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1, thickness=2, offset=0)

        if count < 2200:
            color = (0, 255, 0)
            thickness = 5

            if space_timers[i] is not None:
                elapsed_time = int(current_time - space_timers[i])
                cvzone.putTextRect(img, f"Libre por {elapsed_time} s", (x, y - 30), scale=1, thickness=2, offset=0)


        else:
            color = (0, 0, 255)
            thickness = 2
            cvzone.putTextRect(img, "Ocupado", (x, y - 30), scale=1, thickness=2, offset=0)
            space_timers[i] = None
            if space_timers[i] is None:
                space_timers[i] = current_time
            spaceCounter += 1

        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)

    cvzone.putTextRect(img, f'Sitios ocupados: {spaceCounter}/{len(pos) + 4}', (100, 50), scale=3, thickness=3,
                       offset=10, colorR=(0, 0, 255))
    cvzone.putTextRect(img, f'Sitios libres: {(len(pos) + 4) - spaceCounter}/{len(pos) + 4}', (200, 100), scale=3,
                       thickness=3, offset=10, colorR=(0, 255, 0))


while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)

    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    checkChairSpace(imgDilate)

    # for pos in posList:
    # cv2.rectangle(img,pos,(pos[0]+width,pos[1]+height),(255,0,255),2)
    cv2.imshow("Image", img)
    # cv2.imshow("ImageBlur",imgBlur)
    # cv2.imshow("ImageThres",imgMedian)
    cv2.waitKey(10)