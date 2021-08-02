import tkinter as tk
from tkinter import ttk
from ttkstyles import Style

window = tk.Tk()
style = Style(window)
c = ttk.Checkbutton(window, text="Hello World")

for i, image in enumerate(c.image_names()):
    ttk.Label(window, image=image).grid(column=i, row=0)

label = ttk.Label(window, text="Heading", style="Heading.TLabel")
label.grid(column=0, columnspan=i, row=1)
ttk.Button(window, text="Destroy", command=window.destroy).grid(column=0, columnspan=i, row=2)
print(style.layout("Heading.TLabel"))
print(style.element_options("Heading.TLabel"))
print(label.cget("style"))

window.mainloop()
