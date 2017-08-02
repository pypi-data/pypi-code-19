
import json

from .vlq import encode, decode


class Token:
    """
    Represents a token from a source map, which maps from the original source
    information (Javascript, coffee, etc.) to the location in the generated
    (compiled and minified) file.
    """
    def __init__(self, genLine=None, genCol=None,
                 srcFile=None, srcLine=None, srcCol=None, srcName=None):
        self.genLine = genLine  # The line number in the generated (JS) file
        self.genCol  = genCol   # The column number
        self.srcFile = srcFile  # The source file name
        self.srcLine = srcLine
        self.srcCol  = srcCol
        self.srcName = srcName  # The function/variable name

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return '{}:{}/{} {} @ {}:{}'.format(
            self.srcFile, self.srcLine, self.srcCol,
            self.srcName,
            self.genLine, self.genCol
        )


class SourceMap:
    """
    Holds parsed source map information, read from one or more source map files.

    To use, call read() one or more times, in the order the Javascript files will
    be concatenated, and call generate to generate the map file.
    """
    def __init__(self):
        self.sources = []
        self.names   = []

        self.tokens  = []
        # Stored in the order they are found in the generated file.

        self.genLines = 0
        # The number of lines in the generated file.  This is used to "bump" generated lines
        # when we are concatenating map files (which means we are concatenating the generated
        # files).

    def generate(self):
        """
        Generates a source file as a string and returns it.
        """
        srcIdx  = 0
        nameIdx = 0
        genLine = 1
        srcLine = 0
        srcCol  = 0
        genCol  = 0

        tokens = self.tokens[:]
        tokens.sort(key=lambda t: (t.genLine, t.genCol))

        mappings = []

        for token in tokens:
            if genLine < token.genLine:
                mappings.append(';' * (token.genLine - genLine))
                genLine = token.genLine
                genCol = 0
            elif genCol > 0:
                mappings.append(',')

            fields = [
                token.genCol - genCol
            ]
            genCol = token.genCol

            if token.srcFile:
                idx = self.sources.index(token.srcFile)
                fields.append(idx - srcIdx)
                srcIdx = idx

                fields.append(token.srcLine - srcLine)
                srcLine = token.srcLine

                fields.append(token.srcCol - srcCol)
                srcCol = token.srcCol

            if token.srcName:
                idx = self.names.index(token.srcName)
                fields.append(idx - nameIdx)
                nameIdx = idx

            mappings.append(encode(fields))

        return {
            'version': 3,
            'sources': self.sources,
            'names': self.names,
            'mappings': ''.join(mappings)
        }

    def read(self, content):
        """
        Reads a source map and stores its contents.

        To merge source maps for concatenating source files, read the source maps in the order
        the source files will be concatenated.  This is important since the line numbers in the
        concatenated file must be calculated.  This class simply starts the "generated line"
        count from the end of the previous source map.

        Note that the token's name index will be changed if previous source maps already have
        the same name.
        """

        if content.startswith(")]}'"):
            content = content.split('\n', 1)[1]

        s = json.loads(content)

        # Merge the sources and names into the master lists.

        originalSources = s['sources']
        for source in originalSources:
            if source not in self.sources:
                self.sources.append(source)

        originalNames = s['names']
        for name in originalNames:
            if name not in self.names:
                self.names.append(name)

        # These variables are cumulative.  Note that genCol (field 1 in the Source Map
        # specification) is different and is reset to zero on each line.  (I'm not sure why
        # they didn't do that for srcCol too.)

        srcIdx  = 0
        nameIdx = 0
        genLine = self.genLines
        srcLine = 0
        srcCol  = 0

        for line in s['mappings'].split(';'):
            genLine += 1
            genCol = 0

            for segment in line.split(','):
                if not segment:
                    continue

                fields = decode(segment)

                srcFile = None
                srcName = None

                genCol += fields[0]

                if len(fields) > 1:
                    srcIdx += fields[1]
                    srcFile = originalSources[srcIdx]
                    srcLine += fields[2]
                    srcCol  += fields[3]

                if len(fields) == 5:
                    nameIdx += fields[4]
                    srcName = originalNames[nameIdx]

                self.tokens.append(Token(
                    genLine=genLine,
                    genCol=genCol,
                    srcFile=srcFile,
                    srcLine=srcLine,
                    srcCol=srcCol,
                    srcName=srcName
                ))

        self.genLines = genLine
