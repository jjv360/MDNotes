
import wx
import os
from Theme import *
from FilePanel import *
from EditorPanel import *

class MainWindow(wx.Frame):
    
    # Constructor
    def __init__(self):
        super().__init__(None, title="MDNotes", size=(1024,768))

        # Setup window
        self.SetBackgroundColour(Theme.getColor('root', 'background-color'))

        # Create split view
        split = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        
        # Create left panel
        left = FilePanel(split)
        left.onFileOpen = self.onFileOpen
        
        # Create right panel
        self.editor = EditorPanel(split)

        # Set panels into split view
        split.SplitVertically(left, self.editor, sashPosition=320)
        split.SetSashSize(1)


    # Called when the user opens a file from the file list
    def onFileOpen(self, path):

        # Set window title
        self.SetTitle("MDNotes - " + os.path.basename(path))

        # Inform editor
        self.editor.openFile(path)