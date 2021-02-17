import tkinter as tk
from tkinter import ttk
from ttkstyles import Style
from pdb import set_trace

window = tk.Tk()
style = Style(window)
style.load_theme("/home/jesse/Source/ttk-theme-yaru/yaru", "tcl")
c = ttk.Checkbutton(window, text="Hello World")

for i, image in enumerate(c.image_names()):
    ttk.Label(window, image=image).grid(column=i, row=0)
    print(image)

window.mainloop()
