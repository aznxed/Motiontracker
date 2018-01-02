import Tkinter as tk
import numpy as np
import argparse
import tkFileDialog
import cv2
import pickle
import os
from progress.bar import Bar
from glob import glob

def getArg():
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--veteran_mode", action='store_true')
	args = vars(ap.parse_args())
	return args

def selectDirectory():
	root = tk.Tk()
	root.withdraw()
	root.update()
	directory = tkFileDialog.askdirectory()

	return directory

def selectCorners(event,x,y,flags,param):
    
    if event == cv2.EVENT_LBUTTONDOWN and len(corners)<8:
        corners.append((x,y))

    elif event == cv2.EVENT_LBUTTONUP and len(corners)<8:
        corners.append((x,y))
        #print "corners: " + str(corners)
    pass

def maxContour(cnts):
	maxSize = 0

	for c in cnts:
		if cv2.contourArea(c) < 25:
			continue
		elif cv2.contourArea(c) > maxSize:
			maxSize = cv2.contourArea(c)

	return maxSize
def setupReference(frame, corners):
	roi = frame[corners[0][1]:corners[1][1], corners[0][0]:corners[1][0]]
	roi2 = frame[corners[2][1]:corners[3][1], corners[2][0]:corners[3][0]]

	gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	gray2 = cv2.cvtColor(roi2, cv2.COLOR_BGR2GRAY)
	gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)

	return gray, gray2

def processImage(frame, corners, refFrame, refFrame2):
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

	return cnts, cnts2, thresh, thresh2, frameDelta, frameDelta2

def displayImageDif(frame, corners, thresh, thresh2, frameDelta, frameDelta2):
	cv2.rectangle(frame, corners[0], corners[1], (0, 255, 0), 2)
	cv2.rectangle(frame, corners[2], corners[3], (255, 0, 0), 2)

			# draw the text and timestamp on the frame
	cv2.putText(frame, "Chamber Status 1: {}".format(text), (10, 20),
	cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

	cv2.putText(frame, "Chamber Status 2: {}".format(text2), (10, 40),
	cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
			
	cv2.imshow("Thresh", thresh)
	cv2.imshow("Frame Delta", frameDelta)

	cv2.imshow("Thresh2", thresh2)
	cv2.imshow("Frame Delta2", frameDelta2)
	cv2.imshow(frame_title,frame)
	pass

def processText(cnts, cnts2, text, text2, frametracker, frametracker2):
	if text == 'Occupied' and text2 == 'Occupied':
			#Compare which contour is larger
		if maxContour(cnts) > maxContour(cnts2):
			frametracker.append( 1 )
			frametracker2.append( 0 )
		else:
			frametracker.append( 0 )
			frametracker2.append( 1 )

	elif text == 'Unoccupied' and text2 == 'Occupied':
		frametracker.append( 0 )
		frametracker2.append( 1 )
	elif text == 'Occupied' and text2 == 'Unoccupied':
		frametracker.append( 1 )
		frametracker2.append( 0 )
	elif text == 'Unoccupied' and text2 == 'Unoccupied':
		frametracker.append( 0 )
		frametracker2.append( 0 )

#Initialize Variables
global corners
corners = []
completeframes = []
stoppedframe = []

#Get Arguments and Set up Directory
args = getArg()
directory = selectDirectory()
videoName = str(directory) +"/vid*.mp4"
videoList = glob(videoName)
videoList.sort()

#Begin to select ROI
for i in range(len(videoList)):
	
	cap = cv2.VideoCapture(videoList[i])
	frame_title = os.path.split(videoList[i])[1]
	length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	cv2.namedWindow(frame_title)
	frameNumber = 0

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
			 	elif key == ord('q') or key == 27:
			 		stoppedframe.append(frameNumber)
			 		cv2.destroyAllWindows()
			 		cap.release()
			 		continue

		elif key == ord('q') or key == 27:
			cv2.destroyAllWindows()
			cap.release()
			break

#Beginning of video processing
for i in range(len(videoList)):
	file_path = videoList[i]
	cap = cv2.VideoCapture(file_path)

	if not args.get("veteran_mode", True):
		frame_title = os.path.split(file_path)[1]
		cv2.namedWindow(frame_title)

	cap.set(cv2.CAP_PROP_POS_FRAMES, stoppedframe[0])
	length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	del stoppedframe[0]

	#Set up reference frame
	ret,frame = cap.read()
	refFrame, refFrame2 = setupReference(frame, corners)

	#Start at the beginning
	cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
	bar = Bar('Processing', max=length)

	#Reset the frames tracked
	frametracker = []
	frametracker2 = []

	for a in range(length):

		ret,frame = cap.read()
		text = "Unoccupied"
		text2 = "Unoccupied"

		if not args.get("veteran_mode", True):
			key = cv2.waitKey(25) & 0xFF
		else:
			key = None

		cnts, cnts2, thresh, thresh2, frameDelta, frameDelta2 = processImage(frame, corners, refFrame, refFrame2)

		for c in cnts:
			# if the contour is too small, ignore it
			if cv2.contourArea(c) < 25:
				continue

			# compute the bounding box for the contour, draw it on the frame,
			# and update the text
			text = "Occupied"

		for c in cnts2:
			# if the contour is too small, ignore it
			if cv2.contourArea(c) < 25:
				continue

			# compute the bounding box for the contour, draw it on the frame,
			# and update the text
			text2 = "Occupied"

		
		processText(cnts, cnts2, text, text2, frametracker, frametracker2)
		bar.next()

		if not args.get("veteran_mode", True):
			displayImageDif(frame, corners, thresh, thresh2, frameDelta, frameDelta2)
		
		if key == ord('q') or key == 27:
			cv2.destroyAllWindows()
			cap.release()

	del corners[0]
	del corners[0]
	del corners[0]
	del corners[0]
	completeframes.append(frametracker)
	completeframes.append(frametracker2)

	bar.finish()
	saved = {"frames":completeframes}
	pickle.dump(saved,open(file_path[:-5] + ".p","wb"))
	del completeframes[0]
	del completeframes[0]
	
	print "Finished processing Video " + str(i+1) + " of " + str(len(videoList))


