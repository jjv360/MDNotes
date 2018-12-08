
import os

# Private, tries to find a writable user folder.
def _getPath():

    # Find user's path. First try the app's directory, for portable apps
    try:

        # Get app-bound user folder
        p = os.path.abspath(os.path.join(__file__, "../user"))

        # Create user folder if needed
        os.makedirs(p, exist_ok=True)

        # Check if writable
        if not os.access(p, os.W_OK):
            raise

        # Success!
        return p

    except:
        pass

    # Ok, the app folder is not writable, use the system user folder instead
    p = os.path.abspath(os.path.expanduser("~/.mdnotes"))

    # Create if needed
    os.makedirs(p, exist_ok=True)

    # Done
    return p


# Get user path
path = _getPath()
del _getPath