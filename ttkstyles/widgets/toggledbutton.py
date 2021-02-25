import tkinter as tk
from tkinter import ttk
from ttkwidgets.frames.balloon import Balloon

class ToggleButton(ttk.Widget):
    """VERY SIMPLE ToggleButton widget for Ttk"""

    def __init__(self, master=None, tooltip=None, **kwargs):
        
        ttk.Widget.__init__(self, master, "ttk::checkbutton", kwargs)
        # TODO: Replace the style support check with something like this:
        # self.tk.eval('info exists ttk::theme::azure::ttkstylesSupport')
        try:
            self.configure(style='ToggleButton')
        except:
            self.configure(style='Toolbutton')
            
        self._tooltip = Balloon(self, text=tooltip)

    def invoke(self):
        """Toggles between the selected and deselected states and
        invokes the associated command. If the widget is currently
        selected, sets the option variable to the offvalue option
        and deselects the widget; otherwise, sets the option variable
        to the option onvalue.

        Returns the result of the associated command."""
        return self.tk.call(self._w, "invoke")
        
if __name__ == '__main__':
    root = tk.Tk()
    
    style = ttk.Style(root)
    root.tk.call('source', 'E:/Azure theme/New azure/azure.tcl')
    style.theme_use('azure')
    
    toggle = ToggleButton(root, text='ToggleButton', tooltip='Help text')
    toggle.pack(pady=20)
    
    root.mainloop()

