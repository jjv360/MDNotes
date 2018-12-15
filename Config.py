
import os
import configparser

# Private, tries to find a writable user folder.
def _getPath():

    # Find user's path. First try the app's directory, for portable apps
    # try:

    #     # Get app-bound user folder
    #     p = os.path.abspath(os.path.join(__file__, "../user"))

    #     # Create user folder if needed
    #     os.makedirs(p, exist_ok=True)

    #     # Check if writable
    #     if not os.access(p, os.W_OK):
    #         raise

    #     # Success!
    #     return p

    # except:
    #     pass

    # Ok, the app folder is not writable, use the system user folder instead
    p = os.path.abspath(os.path.expanduser("~/.mdnotes"))

    # Create if needed
    os.makedirs(p, exist_ok=True)

    # Done
    return p


# Get user path
path = _getPath()
del _getPath


# Load current config
ini = configparser.ConfigParser()
ini.read(os.path.join(path, "settings.ini"))


# Get a setting
def get(section, option, fallback):
    return ini.get(section, option, fallback=fallback)


# Get a setting
def getboolean(section, option, fallback=False):
    return ini.getboolean(section, option, fallback=fallback)


# Get a setting
def getfloat(section, option, fallback):
    return ini.getfloat(section, option, fallback=fallback)


# Get a setting
def getint(section, option, fallback):
    return ini.getint(section, option, fallback=fallback)


# Set a setting
def set(section, option, value):

    # Create section if needed
    if not ini.has_section(section):
        ini.add_section(section)

    # Update config
    ini.set(section, option, value)

    # Write changes
    with open(os.path.join(path, "settings.ini"), 'w') as f:
        ini.write(f)