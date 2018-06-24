import sys
import Tkinter as tk

roomlist = ["one", "tlistLabelo", "three", "four"]


mGui = tk.Tk()
mGui.title("Project")

mlabel = tk.Label(text= "my label").grid(row=0,column=0,sticky=tk.W)
mlabel2 = tk.Label(text= "my label").grid(row=1,column=0,sticky=tk.W)
mlabel3 = tk.Label(text= "my label").grid(row=0,column=1)

lb = tk.Listbox(mGui)
lb.pack()

mGui.mainloop()

