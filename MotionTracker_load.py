import Tkinter as tk
import tkFileDialog
import pickle
import os
import numpy as np
import matplotlib.pyplot as plt

def load_data():
    
    root = tk.Tk()
    root.withdraw()
    root.update()
    file_path = tkFileDialog.askopenfilename(parent=root,title='Choose a pickle file ...')
    
    with open(file_path) as f:  
        alldata = pickle.load(f)
        a = alldata['frames']

    return a


# Check data
frames = load_data()
#for a in range(len(frames[0])):
#    frames[0][a] = frames[0][a] + frames[1][a]

plt.plot(frames[0], 'b')
plt.plot(frames[1], 'r')
plt.ylim([-2,4])
plt.title('tracked in right and middle chambers')
plt.legend({'R', 'M'})
plt.show()
