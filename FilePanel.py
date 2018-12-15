
import wx
import os
import sys
from Theme import *
import Config
import AppInfo


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
        self.onClose = None

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
        # openBtn = wx.StaticBitmap(self.header, bitmap=Theme.getIcon('open-file', 16), size=wx.Size(44, 44))
        # openBtn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        # openBtn.Bind(wx.EVT_LEFT_DOWN, lambda e: self.openNote())
        # toolbarSizer.Add(openBtn)

        # Add flex space
        toolbarSizer.AddStretchSpacer()

        # Add settings button
        self.settingsBtn = wx.StaticBitmap(self.header, bitmap=Theme.getIcon('settings', 16), size=wx.Size(44, 44))
        self.settingsBtn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.settingsBtn.Bind(wx.EVT_LEFT_DOWN, lambda e: self.openSettings())
        toolbarSizer.Add(self.settingsBtn)

        # Build menu
        self.menu = self.buildMenu()

        # Store first line of each file
        self.descriptionCache = {}

        # Refresh file list (in the next run loop)
        wx.CallAfter(lambda: self.refreshFiles())


    # Creates the settings menu
    def buildMenu(self):

        # Create menu
        menu = wx.Menu()

        # Create version info entry
        itm = menu.Append(-1, item=AppInfo.name + ' version ' + AppInfo.version)
        itm.Enable(False)
        menu.AppendSeparator()

        # Create folder list submenu
        smenu = self.buildFolderMenu(menu)
        menu.AppendSubMenu(smenu, text="Folders")

        # Create close to task tray option
        closeTrayItem = menu.Append(-1, item='Close to system tray', kind=wx.ITEM_CHECK)
        closeTrayItem.Check(Config.getboolean('ui', 'close_to_tray'))
        menu.Bind(wx.EVT_MENU, lambda e: self.toggleCloseToTray(closeTrayItem), id=closeTrayItem.GetId())

        # Add separator
        menu.AppendSeparator()

        # Create about list submenu
        smenu = self.buildAboutMenu(menu)
        menu.AppendSubMenu(smenu, text="About")

        # Exit button
        itm = menu.Append(-1, item="Quit")
        menu.Bind(wx.EVT_MENU, lambda e: self.onClose(), id=itm.GetId())

        # Done
        return menu


    # Creates the about menu
    def buildAboutMenu(self, mainMenu):

        # Create menu
        menu = wx.Menu()

        itm = menu.Append(-1, item='OS: ' + wx.GetOsDescription())
        itm.Enable(False)

        itm = menu.Append(-1, item='Python: ' + sys.version)
        itm.Enable(False)

        itm = menu.Append(-1, item='wxPython: ' + wx.version())
        mainMenu.Bind(wx.EVT_MENU, lambda e: wx.InfoMessageBox(self), id=itm.GetId())

        # Done
        return menu


    # Creates the search folder menu
    def buildFolderMenu(self, mainMenu):

        # Create menu
        menu = wx.Menu()

        # Add permanent config folder
        itm = menu.Append(-1, item='Remove ' + Config.path)
        itm.Enable(False)

        # Add other folders
        folders = Config.get(section='ui', option='folders', fallback='').split('*')
        for path in folders:

            # Skip blanks
            if not path:
                continue

            # Create option to remove it
            itm = menu.Append(-1, item='Remove ' + path)
            mainMenu.Bind(wx.EVT_MENU, lambda e: self.removeFolder(path), id=itm.GetId())
            

        # Separator
        menu.AppendSeparator()

        # Option to add a folder
        itm = menu.Append(-1, item='Add folder')
        mainMenu.Bind(wx.EVT_MENU, lambda e: self.addFolder(), id=itm.GetId())

        # Done
        return menu


    # Called to toggle the close to tray menu option
    def toggleCloseToTray(self, menuitem):

        # Toggle current value
        isSet = not Config.getboolean('ui', 'close_to_tray')

        # Update menu
        menuitem.Check(isSet)

        # Update config
        Config.set('ui', 'close_to_tray', 'yes' if isSet else 'no')

        # Notify main window
        self.onTrayEnable(isSet)


    # Called when the user presses the settings button
    def openSettings(self):

        # Get menu position, right under the settings button
        pos = self.settingsBtn.GetPosition()
        pos.y += self.settingsBtn.GetSize().height

        # Show menu
        self.PopupMenu(self.menu, pos)


    # Called to add a folder to the watch list
    def addFolder(self):

        # Ask to open a folder
        path = wx.DirSelector(message="Select note folder", style=wx.DD_DIR_MUST_EXIST).strip()
        if not path:
            return

        # Get absolute path
        path = os.path.abspath(path)

        # Check if it exists already
        existingFolders = Config.get(section='ui', option='folders', fallback='').split('*')
        if path in existingFolders:
            return

        # Add to list
        existingFolders.append(path)

        # Write to config
        Config.set(section='ui', option='folders', value='*'.join(existingFolders))

        # Rebuild menu
        self.menu = self.buildMenu()

        # TODO: Refresh file list
        self.refreshFiles()


    # Called to remove a folder from the watch list
    def removeFolder(self, path):

        # Confirm with the user
        response = wx.MessageBox("Are you sure you want to remove '" + path + "' from the folder list?", caption="Remove Folder", style=wx.OK | wx.CANCEL | wx.CENTER | wx.ICON_QUESTION, parent=self)
        if not response == wx.OK:
            return

        # Get existing items
        existingFolders = Config.get(section='ui', option='folders', fallback='').split('*')

        # Remove it
        existingFolders.remove(path)

        # Write to config
        Config.set(section='ui', option='folders', value='*'.join(existingFolders))

        # Rebuild menu
        self.menu = self.buildMenu()

        # TODO: Refresh file list
        self.refreshFiles()


    # Refresh the file list
    def refreshFiles(self, then_select=None):

        # Get list of folders
        folders = Config.get(section='ui', option='folders', fallback='').split('*')

        # Add the config folder to it
        folders.insert(0, Config.path)

        # Get currently selected file, if any
        idx = self.GetSelection()
        currentFile = None
        if idx != wx.NOT_FOUND and idx-1 >= 0 and idx-1 < len(self.files):
            currentFile = self.files[idx-1]

        # Load files
        self.files = []
        self.descriptionCache = {}
        for folder in folders:

            # Skip blank folders
            if not folder:
                continue

            # Go through contents of the folder
            for filename in os.listdir(folder):

                # Check if file is markdown
                if not filename.lower().endswith('.md'):
                    continue

                # Get absolute path to file
                path = os.path.abspath(os.path.join(folder, filename))

                # Add it
                self.files.append(path)

        # If there are no files, add the starter file now
        if len(self.files) == 0:

            # Create default note if not exists
            notePath = os.path.join(Config.path, "My Notes.md")
            if not os.path.exists(notePath):
                with open(notePath, 'w') as file:
                    file.write("# Welcome to MDNotes!\nThis area is entirely yours, go ahead and write stuff here.")

            # Add to file list
            self.files.append(notePath)

        # Update number of rows
        self.SetRowCount(len(self.files) + 1)

        # If we want to open a file, open it
        if then_select:

            # Find it
            i = self.files.index(then_select)

            # Select it
            self.SetSelection(i+1)

        # If nothing is selected, or the selected file has been removed, select the first file
        elif self.GetSelection() == wx.NOT_FOUND or currentFile not in self.files:

            # Select it
            self.SetSelection(1)

            # And open it
            self.onFileOpen(self.files[0])

        # Redraw UI
        self.RefreshAll()


    # Event: Called when the window is resized
    def OnSize(self, e):

        # Get available size
        fullSize = self.GetClientSize()

        # Resize the header
        self.header.SetPosition(wx.Point(0, 0))
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


    # Creates a new note
    def createNote(self):
        
        # TODO: Get default folder
        folder = Config.path

        # Create filename
        filename = 'Note.md'
        index = 0
        while os.path.exists(os.path.join(folder, filename)):
            index += 1
            filename = 'Note (' + str(index) + ').md'

        # Create new file
        path = os.path.join(folder, filename)
        with open(path, 'w') as f:
            f.write("")

        # Add to file list
        self.files.insert(0, path)
        self.SetRowCount(1 + len(self.files))

        # Select it
        self.SetSelection(1)

        # Refresh UI
        self.RefreshAll()

        # Open it
        self.onFileOpen(path)

        
