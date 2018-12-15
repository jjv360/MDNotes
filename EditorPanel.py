
import wx
import wx.stc
import Config
from Theme import *
from MarkdownStreamingTokenizer import *
from send2trash import send2trash

# Define scintilla built-in style codes TODO: Shouldn't this be defined somewhere in wx.stc?
STYLE_DEFAULT               = 32
STYLE_LINENUMBER            = 33
STYLE_BRACELIGHT            = 34
STYLE_BRACEBAD              = 35
STYLE_CONTROLCHAR           = 36
STYLE_INDENTGUIDE           = 37
STYLE_CALLTIP               = 38
STYLE_FOLDDISPLAYTEXT       = 39
STYLE_LASTPREDEFINED        = 39
STYLE_MAX                   = 255

# Define our own style codes
# TODO: Move this to a lexer class?
CUSTOMSTYLE_HEADER1         = 1
CUSTOMSTYLE_HEADER2         = 2
CUSTOMSTYLE_HEADER3         = 3
CUSTOMSTYLE_UNIMPORTANT     = 4


class EditorPanel(wx.Panel):

    # Constructor
    def __init__(self, parent):
        super().__init__(parent)

        # Events the instance owner must listen to
        self.onMenuPressed = None
        self.onFileRenamed = None
        self.onFileDeleted = None

        # Setup panel
        self.SetBackgroundColour(Theme.getColor('root/editor', 'background-color'))

        # Setup sizer
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        # Setup components
        self.setupHeaderBar()
        self.setupTextBox()

        # Currently opened file
        self.currentFile = None

        # Save timer
        self.saveTimer = wx.CallLater(1000, self.save)
        self.saveTimer.Stop()


    # Sets up the header
    def setupHeaderBar(self):

        # Header bar panel
        header = wx.Panel(self)
        self.GetSizer().Add(header, flag=wx.EXPAND)
       
        # Sizer for the header panel
        toolbarSizer = wx.BoxSizer()
        header.SetSizer(toolbarSizer)
        header.SetAutoLayout(True)

        # Add menu button
        menuBtn = wx.StaticBitmap(header, bitmap=Theme.getIcon('menu', 16), size=wx.Size(44, 44))
        menuBtn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        menuBtn.Bind(wx.EVT_LEFT_DOWN, lambda e: self.onMenuPressed())
        toolbarSizer.Add(menuBtn)

        # Add file name label
        self.nameLbl = wx.StaticText(header, label="...")
        self.nameLbl.SetFont(Theme.getFont('root/editor/filename'))
        self.nameLbl.SetForegroundColour(Theme.getColor('root/editor/filename', 'foreground-color'))
        toolbarSizer.Add(self.nameLbl, proportion=1, flag=wx.ALIGN_CENTER_VERTICAL)

        # Add rename button
        renameBtn = wx.StaticBitmap(header, bitmap=Theme.getIcon('rename', 16), size=wx.Size(44, 44))
        renameBtn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        renameBtn.Bind(wx.EVT_LEFT_DOWN, lambda e: self.onRenamePressed())
        toolbarSizer.Add(renameBtn)

        # Add change folder button
        self.folderBtn = wx.StaticBitmap(header, bitmap=Theme.getIcon('folder', 16), size=wx.Size(44, 44))
        self.folderBtn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.folderBtn.Bind(wx.EVT_LEFT_DOWN, lambda e: self.onFolderPressed())
        toolbarSizer.Add(self.folderBtn)

        # Add delete button
        deleteBtn = wx.StaticBitmap(header, bitmap=Theme.getIcon('delete', 16), size=wx.Size(44, 44))
        deleteBtn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        deleteBtn.Bind(wx.EVT_LEFT_DOWN, lambda e: self.onDeletePressed())
        toolbarSizer.Add(deleteBtn)


    # Sets up the text editor component
    def setupTextBox(self):

        # Create text editor component
        self.text = wx.stc.StyledTextCtrl(self)
        self.text.SetWrapMode(1)
        self.text.SetWrapIndentMode(1)
        self.GetSizer().Add(self.text, proportion=1, flag=wx.EXPAND)

        # Bind events
        self.text.Bind(wx.stc.EVT_STC_CHANGE, self.onTextChange)
        self.text.Bind(wx.stc.EVT_STC_STYLENEEDED, self.onStyleNeeded)

        # Apply style to text control
        self.applyTheme()


    # Applies the current theme to the text control
    def applyTheme(self):

        # Set up the base text theme
        self.text.StyleResetDefault()
        Theme.applySciStyle(self.text, 'root/editor', code=STYLE_DEFAULT)

        # Copy base text theme to all styles
        self.text.StyleClearAll()

        # Apply other styles
        Theme.applySciStyle(self.text, 'root/editor/header1', code=CUSTOMSTYLE_HEADER1)
        Theme.applySciStyle(self.text, 'root/editor/header2', code=CUSTOMSTYLE_HEADER2)
        Theme.applySciStyle(self.text, 'root/editor/header3', code=CUSTOMSTYLE_HEADER3)
        Theme.applySciStyle(self.text, 'root/editor/unimportant', code=CUSTOMSTYLE_UNIMPORTANT)
        
    
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

        # Remove .md extension from filename
        filename = os.path.basename(path)
        if filename.lower().endswith('.md'):
            filename = filename[:-3]

        # Set filename label
        self.nameLbl.SetLabelText(filename)


    # Called when the contexts of the text area changes
    def onTextChange(self, e):

        # Schedule a save
        self.saveTimer.Start(1000)


    # Saves the document.
    def save(self):

        # Stop if no active document
        if not self.currentFile:
            return

        # Stop save timer
        if self.saveTimer.IsRunning():
            self.saveTimer.Stop()

        # Open the file for writing
        with open(self.currentFile, 'w') as file:

            # Write the content
            text = self.text.GetText()
            file.write(text)
            

    # Called by Scintilla when we have text which needs to be styled
    def onStyleNeeded(self, event):
        
        # Get range of text which needs to be styled
        startPos = self.text.GetEndStyled()
        lineNum = self.text.LineFromPosition(startPos)
        startPos = self.text.PositionFromLine(lineNum)
        endPos = event.GetPosition()

        # Style this line
        stylePos = startPos
        self.text.StartStyling(stylePos, 31)

        # Go through entire document until we get to where we need to be
        for token in MarkdownTokens(self.text.GetText()):

            # Stop if current token is before our requested region
            if token.toIndex <= stylePos:
                continue

            # Stop if we've gone past the end of our requested style region
            if token.fromIndex >= endPos:
                break

            # Get length of this token
            length = token.toIndex - stylePos

            # Get style code
            code = STYLE_DEFAULT
            if token.typeName == 'header1': code = CUSTOMSTYLE_HEADER1
            if token.typeName == 'header2': code = CUSTOMSTYLE_HEADER2
            if token.typeName == 'header3': code = CUSTOMSTYLE_HEADER3
            if token.typeName == 'unimportant': code = CUSTOMSTYLE_UNIMPORTANT

            # Apply style
            stylePos += length
            self.text.SetStyling(length, code)


    # Called when the use presses the rename button
    def onRenamePressed(self):

        # Get current name
        filename = os.path.basename(self.currentFile)

        # Remove .md extension
        if filename.lower().endswith('.md'):
            filename = filename[:-3]

        # Ask for new name
        newFilename = wx.GetTextFromUser(message="Enter the new name for this note.", caption="Rename note", default_value=filename, parent=self)

        # Check if cancelled or unchanged
        if not newFilename or newFilename == filename:
            return

        # Add extension if needed
        if not newFilename.lower().endswith('.md'):
            newFilename += '.md'

        # Get path to new file
        oldPath = self.currentFile
        newPath = os.path.abspath(os.path.join(oldPath, '..', newFilename))

        # Save now, just in case
        self.save()

        # Move file
        os.rename(oldPath, newPath)

        # Inform file list to reload.
        self.onFileRenamed(newPath)

        # Open it again
        self.openFile(newPath)


    # Called when the user wants to change the folder this note is in
    # TODO: Make folders which appear only contain the most relevate paths, ie. remove path prefixes which match all stored paths
    def onFolderPressed(self):

        # Get current folder list
        folders = Config.get(section='ui', option='folders', fallback='').split('*')
        folders = filter(None, folders)

        # Create menu
        menu = wx.Menu()

        # Create info entry
        itm = menu.Append(-1, item='Note location')
        itm.Enable(False)

        menu.AppendSeparator()

        # Add local folder
        itm = menu.Append(-1, item='Local', kind=wx.ITEM_CHECK)
        menu.Bind(wx.EVT_MENU, lambda e: self.moveCurrentFileTo(Config.path), id=itm.GetId())
        if self.currentFile.lower().startswith(Config.path.lower()):
            itm.Check(True)

        # Add other folders
        for path in folders:

            # Skip blanks
            if not path:
                continue

            # Add menu option
            itm = menu.Append(-1, item=path, kind=wx.ITEM_CHECK)
            menu.Bind(wx.EVT_MENU, lambda e: self.moveCurrentFileTo(path), id=itm.GetId())
            if self.currentFile.lower().startswith(path.lower()):
                itm.Check(True)

        # Calculate menu position (just under the folder button)
        pos = self.folderBtn.GetPosition()
        pos.y += self.folderBtn.GetSize().height

        # Show menu
        self.PopupMenu(menu, pos)


    # Moves the current file to the specified folder
    def moveCurrentFileTo(self, folder):

        # Create paths
        oldPath = self.currentFile
        newPath = os.path.abspath(os.path.join(folder, os.path.basename(self.currentFile)))

        # Save now, just in case
        self.save()

        # Move file
        os.rename(oldPath, newPath)

        # Inform file list to reload
        self.onFileRenamed(newPath)

        # Open it again
        self.openFile(newPath)


    # Called when the user presses the delete button
    def onDeletePressed(self):

        # Confirm with the user
        response = wx.MessageBox("Are you sure you want to delete this note?", caption="Delete Note", style=wx.OK | wx.CANCEL | wx.CENTER | wx.ICON_QUESTION, parent=self)
        if not response == wx.OK:
            return

        # Cancel save timer if any
        if self.saveTimer.IsRunning():
            self.saveTimer.Stop()

        # Delete it!
        send2trash(self.currentFile)

        # Get file list to refresh and open us another file
        self.onFileDeleted()