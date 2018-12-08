#
# Entry point

import wx
from MainWindow import *

# Create app
app = wx.App()
frame = MainWindow()
frame.Show()

# Main app loop
app.MainLoop()