
import wx
import wx.stc
from Theme import *
from MarkdownStreamingTokenizer import *

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
        self.GetSizer().Add(header)
       
        # Sizer for the header panel
        toolbarSizer = wx.BoxSizer()
        header.SetSizer(toolbarSizer)
        header.SetAutoLayout(True)

        # Add new button
        newBtn = wx.StaticBitmap(header, bitmap=Theme.getIcon('menu', 16), size=wx.Size(44, 44))
        newBtn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        newBtn.Bind(wx.EVT_LEFT_DOWN, lambda e: self.onMenuPressed())
        toolbarSizer.Add(newBtn)


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
            

    # Called by Scintilla when we have text which needs to be styled
    def onStyleNeeded(self, event):
        
        # Get range of text which needs to be styled
        startPos = self.text.GetEndStyled()
        lineNum = self.text.LineFromPosition(startPos)
        startPos = self.text.PositionFromLine(lineNum)
        endPos = event.GetPosition()

        # Style this line
        print("Style needed from " + str(startPos) + " to " + str(endPos))
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
