
import re

class MarkdownTokens:

    # Constructor
    def __init__(self, content):

        # Store markdown content
        self.content = content

        # Store current index into the text
        self.currentIndex = 0

        # Stores queue of next tokens to deliver
        self.tokenQueue = []


    # Return iterator
    def __iter__(self):

        # Return a copy of this class, with indexes set back to 0
        return MarkdownTokens(self.content)


    # Get next token
    def __next__(self):

        # Check if there's a token in the queue
        if len(self.tokenQueue) > 0:
            return self.tokenQueue.pop(0)

        # Stop if no more content
        if self.currentIndex >= len(self.content):
            raise StopIteration

        # Try each regex until we get the closest match
        matcher = None
        match = None
        for m in TokenMatchers:

            # Get info
            regex = m['regex']

            # Check if regex matches
            pmatch = regex.search(self.content, self.currentIndex)
            if not pmatch:
                continue

            # Check if this match is closer than the previous one
            if not match or pmatch.start() < match.start():
                matcher = m
                match = pmatch

        # If no matches, this is the final part of the document
        if not match:

            # Nothing found, the rest of the document is plain text
            token = Token('plain', fromIndex=self.currentIndex, toIndex=len(self.content))
            self.currentIndex = len(self.content)
            return token

        # Match was found! Create array of tokens
        typeName = matcher['name']
        skip_start = matcher.get('skip_start', 0)
        skip_end = matcher.get('skip_end', 0)
        tokens = []

        # If match was not at the start of the string, add blank token
        if match.start() > self.currentIndex:
            tokens.append(Token('plain', fromIndex=self.currentIndex, toIndex=match.start()))

        # Get range of skippable chars
        if skip_start > 0:
            tokens.append(Token('unimportant', fromIndex=match.start(), toIndex=match.start() + skip_start))

        # Add main tokens
        tokens.append(Token(typeName, fromIndex=match.start() + skip_start, toIndex=match.end() - skip_end))

        # Get range of skippable chars
        if skip_end > 0:
            tokens.append(Token('unimportant', fromIndex=match.end() - skip_end, toIndex=match.end()))

        # Update current position
        self.currentIndex = match.end()

        # Add extra tokens to the queue
        for i in range(1, len(tokens)):
            self.tokenQueue.append(tokens[i])

        # Return first token
        return tokens[0]



# Represents a matched token
class Token:
    """ Represents a token. """

    def __init__(self, typeName, fromIndex, toIndex):
        self.typeName = typeName
        self.fromIndex = fromIndex
        self.toIndex = toIndex




# Create list of regex expressions to match against
TokenMatchers = [

    # Match: # Header Name
    { 'name': 'header1', 'regex': re.compile("#[^#].*($|\n)"), 'skip_start': 1 },
    { 'name': 'header2', 'regex': re.compile("##[^#].*($|\n)"), 'skip_start': 2 },
    { 'name': 'header3', 'regex': re.compile("###[^#].*($|\n)"), 'skip_start': 3 }

]