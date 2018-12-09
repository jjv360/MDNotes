
import wx
import os
from Theme import *
import Config

class FilePanel(wx.VListBox):

    # Constructor
    def __init__(self, parent):
        super().__init__(parent)
        
        # Setup panel
        self.SetBackgroundColour(Theme.getColor('root/file-list', 'background-color'))
        self.SetSelectionBackground(Theme.getColor('root/file-list/selected', 'background-color'))

        # Listen for events
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LISTBOX, self.OnItemSelected)

        # Custom events
        self.onFileOpen = None

        # Header bar panel
        self.header = wx.Panel(self)
        self.header.SetSize(100, 44)
       
        # Sizer for the header panel
        toolbarSizer = wx.BoxSizer()
        self.header.SetSizer(toolbarSizer)
        self.header.SetAutoLayout(True)

        # Add new button
        newBtn = wx.StaticBitmap(self.header, bitmap=Theme.getIcon('new-file', 16), size=wx.Size(44, 44))
        newBtn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        newBtn.Bind(wx.EVT_LEFT_DOWN, lambda e: self.createNote())
        toolbarSizer.Add(newBtn)

        # Add open button
        openBtn = wx.StaticBitmap(self.header, bitmap=Theme.getIcon('open-file', 16), size=wx.Size(44, 44))
        openBtn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        openBtn.Bind(wx.EVT_LEFT_DOWN, lambda e: self.openNote())
        toolbarSizer.Add(openBtn)

        # Add flex space
        toolbarSizer.AddStretchSpacer()

        # Add settings button
        settingsBtn = wx.StaticBitmap(self.header, bitmap=Theme.getIcon('settings', 16), size=wx.Size(44, 44))
        settingsBtn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        toolbarSizer.Add(settingsBtn)

        # Load history of files
        self.files = []
        paths = Config.get('history', 'file_paths', '')
        paths = paths.split('*')
        for path in paths:

            # Skip blanks
            if not path:
                continue

            # Make sure file exists
            path = os.path.abspath(path)
            if not os.path.exists(path):
                continue

            # Add it
            self.files.append(path)

        # Update row count
        self.SetRowCount(len(self.files) + 1)

        # Store first line of each file
        self.descriptionCache = {}
        
        # If no default files, load one
        if len(self.files) == 0:

            # Create default note if not exists
            notePath = os.path.join(Config.path, "My Notes.md")
            if not os.path.exists(notePath):
                with open(notePath, 'w') as file:
                    file.write("# Welcome to MDNotes!\nThis area is entirely yours, go ahead and write stuff here.")
    
            # Get config folder
            self.addFile(notePath)

        else:

            # We have some files. Open the first one. Select row
            self.SetSelection(0)

            # Open file
            wx.CallAfter(lambda: self.onFileOpen(self.files[0]))


    # Event: Called when the window is resized
    def OnSize(self, e):

        # Get available size
        fullSize = self.GetClientSize()

        # Resize the header
        self.header.SetSize(fullSize[0], 44)


    # Called to determine the height of each row
    def OnMeasureItem(self, n):

        # First item is the padding for the menu bar
        if n == 0:
            return 44

        # Open files
        return 56


    # Called to draw the specified row
    def OnDrawItem(self, dc, rect, n):
        
        # Do nothing if it's the first padding item
        if n == 0:
            return

        # Minus padding from index
        n -= 1

        # Get file name
        path = os.path.abspath(self.files[n])
        name = os.path.basename(path)

        # Remove .md from filename
        if name[-3:].lower() == '.md':
            name = name[:-3]

        # Get first line of file from the cache
        description = self.descriptionCache.get(path)
        if not description:

            # Open file
            with open(path) as file:

                # Read valid line
                description = "(none)"
                for line in file.readlines():
                
                    # Ignore blank lines
                    if not line.strip():
                        continue

                    # Ignore headings
                    if line[0] == '#':
                        continue

                    # Use this line
                    description = line.strip()
                    break

                # Store in cache
                self.descriptionCache[path] = description

        # Draw title
        dc.SetFont(Theme.getFont('root/file-list/title'))
        dc.SetTextForeground(Theme.getColor('root/file-list/title', 'foreground-color'))
        dc.DrawText(text=name, x=rect.x + 10, y=rect.y + 10)

        # Draw description
        dc.SetFont(Theme.getFont('root/file-list/subtitle'))
        dc.SetTextForeground(Theme.getColor('root/file-list/subtitle', 'foreground-color'))
        dc.DrawText(text=description, x=rect.x + 10, y=rect.y + 30)

    
    # Called when the user selects a row
    def OnItemSelected(self, e):
        
        # Ignore padding
        n = self.GetSelection()
        if n == 0 or n == wx.NOT_FOUND:
            return

        # Get actual index minus padding
        n -= 1

        # Get selected file
        file = self.files[n]
        
        # Open file
        self.onFileOpen(file)


    # Adds a file to the file list
    def addFile(self, path):
        
        # Get absolute path
        path = os.path.abspath(path)

        # Make sure it doesn't exist already
        for f in self.files:
            if f == path:
                return

        # Insert it at the top
        self.files.insert(0, path)

        # Update row count
        self.SetRowCount(1 + len(self.files))

        # Select row
        self.SetSelection(0)

        # Redraw
        self.RefreshAll()

        # Open file
        wx.CallAfter(lambda: self.onFileOpen(path))

        # Save history
        Config.set('history', 'file_paths', '*'.join(self.files))


    # Creates a new note
    def createNote(self):

        # Ask the user where to save it
        with wx.FileDialog(self, message="Create note", defaultDir=Config.path, defaultFile="Note.md", wildcard="Markdown files (*.md)|*.md", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:

            # Check if the user cancelled
            if dlg.ShowModal() == wx.ID_CANCEL:
                return

            # Create new file
            path = os.path.abspath(dlg.GetPath())
            with open(path, 'w') as f:
                f.write("")

            # Add this file to our list
            self.addFile(path)

    
    # Opens an existing markdown file
    def openNote(self):

        # Ask user to select the file
        with wx.FileDialog(self, message="Open note", defaultDir=Config.path, wildcard="Markdown files (*.md)|*.md", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:

            # Check if the user cancelled
            if dlg.ShowModal() == wx.ID_CANCEL:
                return

            # Add file to our list
            path = os.path.abspath(dlg.GetPath())
            self.addFile(path)
