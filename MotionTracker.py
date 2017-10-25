import Tkinter as tk
import numpy as np
import tkFileDialog
import cv2
import pickle
import os

frameNumber = 0
roiPoints = []
corners = []

root = tk.Tk()
root.withdraw()
root.update()
file_path = tkFileDialog.askopenfilename(parent=root,title='Choose a H264 video file to process...')
cap = cv2.VideoCapture(file_path)
frame_title = os.path.split(file_path)[1]
cv2.namedWindow(frame_title)

def selectCorners(event,x,y,flags,param):
    global corners
    
    if event == cv2.EVENT_LBUTTONDOWN and len(corners)<2:
        corners.append((x,y))
    elif event == cv2.EVENT_LBUTTONUP and len(corners)<2:
        corners.append((x,y))
        cv2.rectangle(frame,corners[0],(x,y),(0,0,255),1)
        cv2.imshow(frame_title,frame)
        print "corners: " + str(corners)
    pass

while True:
	ret,frame = cap.read()
	if not ret:
		break

	key = cv2.waitKey(25) & 0xFF
	frameNumber+=1

	cv2.imshow(frame_title,frame)

	if key == ord("p"):
		while cap.isOpened():
			key = cv2.waitKey(0) & 0xFF

			if key == ord('p'):
				break
			elif key == ord('m'):
				cv2.setMouseCallback(frame_title, selectCorners)
			elif key == ord('s'):
				saved = {"corners":corners}
		 		pickle.dump(saved,open(file_path[:-5] + ".p","wb"))
		 		print('Done')
		 		cv2.destroyAllWindows()
		 		cap.release()
		 	elif key == ord('q') or key == 27:
		 		cv2.destroyAllWindows()
		 		cap.release()

	elif key == ord('q') or key == 27:
		cv2.destroyAllWindows()
		cap.release()


cap = cv2.VideoCapture(file_path)
frame_title = os.path.split(file_path)[1]
cv2.namedWindow(frame_title)
cap.set(cv2.CAP_PROP_POS_FRAMES, frameNumber)
firstFrame = None

while True:

	ret,frame = cap.read()
	text = "Unoccupied"

	if not ret:
		break;

	key = cv2.waitKey(25) & 0xFF
	frameNumber+=1
	cv2.rectangle(frame, corners[0], corners[1], (0, 255, 0), 2)

	roi = frame[corners[0][1]:corners[1][1], corners[0][0]:corners[1][0]]

	gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	if firstFrame is None:
		firstFrame = gray
		continue

	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 10, 255, cv2.THRESH_BINARY)[1]

	thresh = cv2.dilate(thresh, None, iterations=1)
	(_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < 10:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		text = "Occupied"

	# draw the text and timestamp on the frame
	cv2.putText(frame, "Chamber Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	
	cv2.imshow("Thresh", thresh)
	cv2.imshow("Frame Delta", frameDelta)

	cv2.imshow(frame_title,frame)
	#cv2.imshow('Crop', roi)
	
	if key == ord('q') or key == 27:
		cv2.destroyAllWindows()
		cap.release()







