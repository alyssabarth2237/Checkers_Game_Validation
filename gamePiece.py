#this file contains the GamePiece, Pawn, and King classes

#*******************************************************
from config import redMoveDir, blackMoveDir
from boardCheck import BoardCheck
#*******************************************************

class GamePiece:
    def __init__(self, pColorIn, locIn, pieceGrid):
        self.type = "None"
        self.pColor = pColorIn
        self.loc = locIn
        self.lastRow = -2
        self.moveDir = -10
        self.boardCheck = BoardCheck()

    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, val):
        self._type = val
    @property
    def pColor(self):
        return self._pColor
    @pColor.setter
    def pColor(self, val):
        self._pColor = val
    @property
    def loc(self):
        return self._loc
    @loc.setter
    def loc(self, val):
        self._loc = val
    @property
    def lastRow(self):
        return self._lastRow
    @lastRow.setter
    def lastRow(self, val):
        self._lastRow = val
    @property
    def moveDir(self):
        return self._moveDir
    @moveDir.setter
    def moveDir(self, val):
        self._moveDir = val


class Pawn(GamePiece):
    def __init__(self, pColorIn, locIn, pieceGrid):
        super().__init__(pColorIn, locIn, pieceGrid)
        self.type = "pawn"
        if pColorIn == "red":
            if redMoveDir == -1:
                self.lastRow = 0
            else:
                self.lastRow = 7
            self.moveDir = redMoveDir
        elif pColorIn == "black":
            if blackMoveDir == 1:
                self.lastRow = 7
            else:
                self.lastRow = 0
            self.moveDir = blackMoveDir
        else:
            self.lastRow = -2
            self.moveDir = -10

        if (self.boardCheck.isOpen(pieceGrid, self.loc) == False) or (self.boardCheck.isInvalid(self.loc) == True):
            print('error')


class King(GamePiece):
    def __init__(self, pColorIn, locIn, pieceGrid):
        super().__init__(pColorIn, locIn, pieceGrid)
        self.moveDir = 1 #1 vs -1 doesn't matter but picked one to make life easier
        self.type = "king"
        if pColorIn == "red":
            if redMoveDir == -1:
                self.lastRow = 0
            else:
                self.lastRow = 7
        elif pColorIn == "black":
            if blackMoveDir == 1:
                self.lastRow = 7
            else:
                self.lastRow = 0
        else:
            self.lastRow = -2
            self.moveDir = -10

        if (self.boardCheck.isOpen(pieceGrid, self.loc) == False) or (self.boardCheck.isInvalid(self.loc) == True):
            # throw error
            print('error')


