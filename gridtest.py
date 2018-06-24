import sys
import Tkinter as tk

roomlist = ["one", "tlistLabelo", "three", "four"]


mGui = tk.Tk()
mGui.title("Log-In")

mlabel = tk.Label(text= "my label").grid(row=0,column=0,sticky=tk.W)
mlabel2 = tk.Label(text= "my label").grid(row=1,column=0,sticky=tk.W)

input_login = tk.Entry(mGui).grid(row=0,column=1,sticky=tk.W)
input_password = tk.Entry(mGui).grid(row=1,column=1,sticky=tk.W)

mGui.mainloop()

