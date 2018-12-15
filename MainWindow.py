
import wx
import os
import Config
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
        self.filePanel.onClose = lambda: self.Close()
        self.filePanel.onTrayEnable = lambda enabled: self.EnableTray() if enabled else self.DisableTray()
        
        # Create right panel
        self.editor = EditorPanel(self.split)
        self.editor.onMenuPressed = self.onMenuPressed
        self.editor.onFileRenamed = lambda newPath: self.filePanel.refreshFiles(then_select=newPath)
        self.editor.onFileDeleted = lambda: self.filePanel.refreshFiles()

        # Set panels into split view
        if Config.getboolean('ui', 'show_file_list', False):
            self.split.SplitVertically(self.filePanel, self.editor, sashPosition=320)
        else:
            self.split.Initialize(self.editor)

        # Enable or disable the tray
        if Config.getboolean('ui', 'close_to_tray'):
            self.EnableTray()
        else:
            self.DisableTray()

        # Listen for events
        self.Bind(wx.EVT_ACTIVATE, self.didActivate)


    # Called when the window becomes active
    def didActivate(self, e):

        # Stop if deactivated
        if not e.GetActive():
            return

        # Tell the file list to refresh
        self.filePanel.refreshFiles()


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


    # Enables the system tray icon
    def EnableTray(self):
        print('enable!')


    # Disables the system tray icon
    def DisableTray(self):
        print('disable!')