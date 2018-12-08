
import wx
import wx.stc
from Theme import *

class EditorPanel(wx.Panel):

    # Constructor
    def __init__(self, parent):
        super().__init__(parent)

        # Setup panel
        self.SetBackgroundColour(Theme.getColor('root/editor', 'background-color'))

        # Create text editor component
        self.text = wx.stc.StyledTextCtrl(self)
        self.text.Bind(wx.stc.EVT_STC_CHANGE, self.onTextChange)

        # Set it to fill the panel space
        sizer = wx.BoxSizer()
        sizer.Add(self.text, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)

        # Currently opened file
        self.currentFile = None

        # Save timer
        self.saveTimer = wx.CallLater(1000, self.save)
        self.saveTimer.Stop()

    
    # Opens a file for editing
    def openFile(self, path):

        # Check if save timer was running
        if self.saveTimer.IsRunning():

            # Cancel save timer
            self.saveTimer.Stop()

            # Save now
            self.save()

        # Store file path
        self.currentFile = path

        # Open file
        with open(self.currentFile) as file:

            # Read file contents
            content = file.read()

            # Set editor content
            self.text.SetText(content)


    # Called when the contexts of the text area changes
    def onTextChange(self, e):

        # Schedule a save
        self.saveTimer.Start(1000)


    # Saves the document.
    def save(self):

        # Stop if no active document
        if not self.currentFile:
            return

        # Open the file for writing
        with open(self.currentFile, 'w') as file:

            # Write the content
            text = self.text.GetText()
            file.write(text)