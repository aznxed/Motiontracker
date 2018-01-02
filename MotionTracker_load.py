import Tkinter as tk
import tkFileDialog
import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
import argparse

def load_data():
    
    root = tk.Tk()
    root.withdraw()
    root.update()
    file_path = tkFileDialog.askopenfilename(parent=root,title='Choose a pickle file ...')
    
    with open(file_path) as f:  
        alldata = pickle.load(f)
        a = alldata['frames']

    return a

def getArg():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verify_data", action='store_true')
    args = vars(ap.parse_args())
    return args

# Check data

frames = load_data()
args = getArg()

if args.get("verify_data", True):
    for a in range(len(frames[0])):
        frames[0][a] = frames[0][a] + frames[1][a]
    plt.plot(frames[0], 'b')

else:
    plt.plot(frames[0], 'b')
    plt.plot(frames[1], 'r')

plt.ylim([-2,4])
plt.title('Tracked in right and middle chambers')
plt.legend({'R', 'M'})
plt.show()


frames3 = []
for a in range(len(frames[0])):
    if frames[0][a] == 0 and frames[1][a] == 0:
        frames3.append(1)

#Frames[0] = Middle Chamber
#Frames[1] = Right Chamber
#Frames3 = Left Chamber
print 'Total number of frames ' + str(len(frames[1]))
print 'Frames spent in middle chamber ' + str(frames[0].count(1))
print 'Frames spent in right chamber ' + str(frames[1].count(1))
print 'Frames spent in left chamber ' + str(frames3.count(1))

