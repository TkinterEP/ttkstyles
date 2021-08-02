import tkinter as tk
from tkinter import ttk
from ttkstyles import Style

window = tk.Tk()
style = Style(window)
c = ttk.Checkbutton(window, text="Hello World")

for i, image in enumerate(c.image_names()):
    ttk.Label(window, image=image).grid(column=i, row=0)
    print(image)


ttk.Button(window, text="Destroy", command=window.destroy).grid(column=0, columnspan=i, row=1)

window.mainloop()
