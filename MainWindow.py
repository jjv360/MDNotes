
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
        self.split = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        
        # Create left panel
        self.filePanel = FilePanel(self.split)
        self.filePanel.onFileOpen = self.onFileOpen
        
        # Create right panel
        self.editor = EditorPanel(self.split)
        self.editor.onMenuPressed = self.onMenuPressed

        # Set panels into split view
        if Config.getboolean('ui', 'show_file_list', False):
            self.split.SplitVertically(self.filePanel, self.editor, sashPosition=320)
        else:
            self.split.Initialize(self.editor)


    # Called when the user opens a file from the file list
    def onFileOpen(self, path):

        # Set window title
        self.SetTitle("MDNotes - " + os.path.basename(path))

        # Inform editor
        self.editor.openFile(path)


    # Called when the menu button is pressed in the editor window
    def onMenuPressed(self):

        # Toggle visibility of left panel
        if self.split.IsSplit():
            self.split.Unsplit(self.filePanel)
        else:
            self.split.SplitVertically(self.filePanel, self.editor, sashPosition=320)

        # Record current state
        Config.set('ui', 'show_file_list', 'yes' if self.split.IsSplit() else 'no')