
import wx 
import configparser
import glob
import os
import ctypes

class ThemeManager:

    # Constructor
    def __init__(self, name):
        """ Loads a named theme. Themes reside in the <installdir>/themes/<themename> directory. """

        # Load theme info
        self.config = configparser.ConfigParser()
        self.config.read("themes/" + name + "/manifest.ini")

        # Store information
        self.cache = {}
        self.fontCache = wx.FontList()
        self.pluginRoot = os.path.abspath(os.path.join(__file__, "../themes", name))
        self.id = self.config.get(section='plugin', option='id')
        self.name = self.config.get(section='plugin', option='name')
        self.author = self.config.get(section='plugin', option='author')
        self.description = self.config.get(section='plugin', option='description')

        # Get list of custom font files
        fontGlob = os.path.abspath(os.path.join(self.pluginRoot, self.config.get(section='plugin', option='install-fonts')))
        fontFiles = glob.glob(fontGlob)
        for font in fontFiles:

            # Check OS
            if os.name == 'nt':

                # Install font
                ctypes.windll.gdi32.AddFontResourceExW(font, 0x10, 0)   # FR_PRIVATE = 0x10 - No other apps can find this font reference, and remove it when this app shuts down

            else:

                # Unknown OS
                print('Cannot install font for unknown os ' + os.name + ': ' + font)


        # Done
        print('Theme: Loaded theme ' + self.name + ' by ' + self.author)


    # Get a style element string
    def getStyle(self, selector, name):
        """ Returns a style string from the theme. """

        # TODO: Load default base style
        value = None

        # Get generic section color
        v = self.config.get(section='style', option=name, fallback=None)
        if v:
            value = v

        # Get specific section color
        v = self.config.get(section='style/' + selector, option=name, fallback=None)
        if v:
            value = v

        # Done
        return value


    # Gets a color from the theme config.
    def getColor(self, selector, name):
        """ Returns a wx.Colour from the theme config. """

        # Check cache
        cacheID = 'color:' + selector + name
        cacheValue = self.cache.get(cacheID)
        if cacheValue:
            return cacheValue

        # Parse HEX color code
        value = self.getStyle(selector, name)
        components = value.split(",")
        r = int(components[0])
        g = int(components[1])
        b = int(components[2])
        a = 255
        if len(components) >= 4: a = int(components[3])
        value = wx.Colour(r, g, b, a)

        # Store in cache
        self.cache[cacheID] = value
        return value


    # Returns a wx.Font from the theme config.
    def getFont(self, selector):
        """ Returns a wx.Font from the theme config. """

        # Check cache
        cacheID = 'font:' + selector
        cacheValue = self.cache.get(cacheID)
        if cacheValue:
            return cacheValue

        # Get font params
        fontSize = self.getStyle(selector, 'font-size')
        fontFamily = self.getStyle(selector, 'font-family')
        fontStyles = self.getStyle(selector, 'font-styles')
        isBold = "bold" in fontStyles

        # Build font description
        value = self.fontCache.FindOrCreateFont(point_size=int(fontSize), family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_BOLD if isBold else wx.FONTWEIGHT_NORMAL, underline=False, facename=fontFamily)
        
        # Store in cache
        self.cache[cacheID] = value
        return value


    # Returns a bitmap image for the specified named icon.
    # Adapted from https://cyberxml.wordpress.com/2015/02/17/wxpython-wx-bitmap-icons-from-svg-xml/
    def getIcon(self, name, height):
        """ Returns a bitmap image for the specified named icon. """

        # Check cache
        cacheID = 'bitmap:' + name + str(height)
        cacheValue = self.cache.get(cacheID)
        if cacheValue:
            return cacheValue

        # Get icon path
        path = self.config.get(section='icons', option=name)
        path = os.path.join(self.pluginRoot, path)

        # Read PNG file data
        with open(path, 'rb') as file:

            # Load as wx image
            img = wx.Image(file)
            img = img.Scale(height, height)

            # Return bitmap
            bmp = wx.Bitmap(img)

            # Store in cache
            self.cache[cacheID] = bmp
            return bmp


# Load default theme
Theme = ThemeManager("Sunlight")