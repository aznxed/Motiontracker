import Tkinter as tk
import numpy as np
import tkFileDialog
import cv2
import pickle
import os
from progress.bar import Bar

frameNumber = 0
roiPoints = []
global corners
corners = []
frametracker = []
frametracker2 = []

root = tk.Tk()
root.withdraw()
root.update()
file_path = tkFileDialog.askopenfilename(parent=root,title='Choose a H264 video file to process...')
cap = cv2.VideoCapture(file_path)
frame_title = os.path.split(file_path)[1]
cv2.namedWindow(frame_title)

def selectCorners(event,x,y,flags,param):
    
    if event == cv2.EVENT_LBUTTONDOWN and len(corners)<4:
        corners.append((x,y))

    elif event == cv2.EVENT_LBUTTONUP and len(corners)<4:
        corners.append((x,y))
        print "corners: " + str(corners)
    pass

length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print length

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
				print("Corner Selection ")
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
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#print length
ret,frame = cap.read()

roi = frame[corners[0][1]:corners[1][1], corners[0][0]:corners[1][0]]
roi2 = frame[corners[2][1]:corners[3][1], corners[2][0]:corners[3][0]]

gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (21, 21), 0)

gray2 = cv2.cvtColor(roi2, cv2.COLOR_BGR2GRAY)
gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)

refFrame = gray
refFrame2 = gray2

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
bar = Bar('Processing', max=length)

for a in range(length):

	ret,frame = cap.read()
	text = "Unoccupied"
	text2 = "Unoccupied"

	#key = cv2.waitKey(25) & 0xFF
	frameNumber+=1
	cv2.rectangle(frame, corners[0], corners[1], (0, 255, 0), 2)
	cv2.rectangle(frame, corners[2], corners[3], (255, 0, 0), 2)

	roi = frame[corners[0][1]:corners[1][1], corners[0][0]:corners[1][0]]
	roi2 = frame[corners[2][1]:corners[3][1], corners[2][0]:corners[3][0]]

	gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	gray2 = cv2.cvtColor(roi2, cv2.COLOR_BGR2GRAY)
	gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)


	frameDelta = cv2.absdiff(refFrame, gray)
	thresh = cv2.threshold(frameDelta, 10, 255, cv2.THRESH_BINARY)[1]

	thresh = cv2.dilate(thresh, None, iterations=1)
	(_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

	frameDelta2 = cv2.absdiff(refFrame2, gray2)
	thresh2 = cv2.threshold(frameDelta2, 10, 255, cv2.THRESH_BINARY)[1]

	thresh2 = cv2.dilate(thresh2, None, iterations=1)
	(_, cnts2, _) = cv2.findContours(thresh2.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < 25:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		text = "Occupied"

	for c in cnts2:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < 5:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		text2 = "Occupied"

	if text == 'Occupied':
		frametracker.append( 1 )
	elif text == 'Unoccupied':
		frametracker.append( 0 )

	if text2 == 'Occupied':
		frametracker2.append( 1 )
	elif text2 == 'Unoccupied':
		frametracker2.append( 0 )

	bar.next()

	# draw the text and timestamp on the frame
	#cv2.putText(frame, "Chamber Status 1: {}".format(text), (10, 20),
	#	cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

	#cv2.putText(frame, "Chamber Status 2: {}".format(text2), (10, 40),
	#	cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	
	#cv2.imshow("Thresh", thresh)
	#cv2.imshow("Frame Delta", frameDelta)

	#cv2.imshow("Thresh2", thresh2)
	#cv2.imshow("Frame Delta2", frameDelta2)
	#cv2.imshow(frame_title,frame)

	
	#if key == ord('q') or key == 27:
	#	cv2.destroyAllWindows()
	#	cap.release()
bar.finish()
print len(frametracker)
print len(frametracker2)
print 'Done'

