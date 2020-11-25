#this file contains the BoardCheck class

class BoardCheck:
    def __init__(self):
        self.dummyVar = "na"

    def isInvalid(self, pt):
        invalidPt = True
        #check x
        if (pt.x < 0) or (pt.x >= 8):
            return invalidPt
        #check y
        if (pt.y < 0) or (pt.y >= 8):
            return invalidPt
        #check if it's a light square (means diff even and odd x y) (only black squares used)
        if (pt.x % 2) != (pt.y % 2):
            return invalidPt
        invalidPt = False
        return invalidPt

    def isOpen(self, pieceGrid, endPt):
        if (pieceGrid[endPt.x][endPt.y].type == "None"):
            return True
        return False
