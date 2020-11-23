#this file contains the Referee class

#******************************
from point import Point
from boardCheck import BoardCheck
from gamePiece import Pawn, King
#******************************

class Referee:
    def __init__(self):
        self.boardCheck = BoardCheck()

    def isOpnt(self, currPt, endPt, pieceGrid):
        if (pieceGrid[endPt.x][endPt.y].pColor == "None"):
            return False
        if (pieceGrid[currPt.x][currPt.y].pColor == pieceGrid[endPt.x][endPt.y].pColor):
            return False
        return True

    def canMove(self, currPt, endPt, pieceGrid):
        moveAllowed = False
        #FIXME: CHANGE TO ONLY PAWN AND NOT BOTH PAWN AND VIRTUAL LATER
        if (isinstance(pieceGrid[currPt.x][currPt.y], Pawn)) or (pieceGrid[currPt.x][currPt.y].type == "virtual"):
            #can only move forward

            #check if endPt is off the board (second check)
            #FIXME: Take Out Second isInvalid Check
            if (self.boardCheck.isInvalid(endPt) == True):
                return False
            #check if endPt is in front of current square according to move dir and that only off by on for x
            if (endPt.y != (currPt.y + pieceGrid[currPt.x][currPt.y].moveDir)) and (abs(currPt.x - endPt.y) != 1):
                return False
            #check if endPt is open
            if (self.boardCheck.isOpen(pieceGrid, endPt) == True):
                return True
            return False
        elif isinstance(pieceGrid[currPt.x][currPt.y], King):
            # can move forwards or backwards
            # check if endPt is off the board
            if (self.boardCheck.isInvalid(endPt) == True):
                return False
            # check if endPt is not touching currPt on diagonal
            if (abs(currPt.y - endPt.y) != 1) and (abs(currPt.x - endPt.y) != 1):
                return False
            # check if endPt is open
            if (self.boardCheck.isOpen(pieceGrid, endPt) == True):
                return True
            return False
        else:
            #TODO: throw error
            pass
        return moveAllowed

    def canJump(self, currPt, endPt, pieceGrid):
        #TODO: FULLY WRITE FUNCTION
        # check if endPt is occupied by same color
        if (self.isOpnt(currPt, endPt, pieceGrid) == False):
            return (False, currPt)
        #get jump direction
        xJumpDir = endPt.x - currPt.x
        yJumpDir = endPt.y - currPt.y
        #check if next square on diagonal is invalid
        jumpEndPt = Point(endPt.x + xJumpDir, endPt.y + yJumpDir)
        if (self.boardCheck.isInvalid(jumpEndPt) == True):
            return (False, currPt)
        #check if jumpEndPt is not open
        if self.boardCheck.isOpen(pieceGrid, jumpEndPt) == False:
            return (False, currPt)
        #can make first jump
        return(True, jumpEndPt)

# FIXME: MAKE SURE THAT CHANGES TO FIX FIRST JUMP ARE CORRECT
    def howCanMove(self, currPt, pieceGrid):
        # returns a list of possible moves (in pt form) for current piece at pt
        possibleEndPts = []
        endPts = []
        noJumpEndPts = []

        #check two "forward" squares on diag according to moveDir
        #to the left
        endPt = Point(currPt.x - 1, currPt.y + pieceGrid[currPt.x][currPt.y].moveDir)
        if self.boardCheck.isInvalid(endPt) == False:
            possibleEndPts.append(endPt)
        #to the right
        endPt = Point(currPt.x + 1, currPt.y + pieceGrid[currPt.x][currPt.y].moveDir)
        if self.boardCheck.isInvalid(endPt) == False:
            possibleEndPts.append(endPt)
        if pieceGrid[currPt.x][currPt.y].type == "king":
            # to the left
            endPt = Point(currPt.x - 1, currPt.y + pieceGrid[currPt.x][currPt.y].moveDir * (-1))
            if self.boardCheck.isInvalid(endPt) == False:
                possibleEndPts.append(endPt)
            # to the right
            endPt = Point(currPt.x + 1, currPt.y + pieceGrid[currPt.x][currPt.y].moveDir * (-1))
            if self.boardCheck.isInvalid(endPt) == False:
                possibleEndPts.append(endPt)

        # *******************************************************************
        #           ***** Changes Here *****
        #for each check if can move and check for first jump
        for pt in possibleEndPts:
            movePossible = self.canMove(currPt, pt, pieceGrid)
            if movePossible == True:
                # change here:
                noJumpEndPts.append(pt)
            else:
                #check for first jump
                #if can jump then add jump endPt to endPts
                jumpResult = self.canJump(currPt, pt, pieceGrid)
                if jumpResult[0] == True:
                    endPts.append(jumpResult[1])

        # must check if endPts (jump endpoints) is empty and if so then set endPts equal to noJumpEndPts
        # if it is not empty then just return endPts with the jump endPoints only (English Standard Version)
        # change here (this is new):
        jumpsFound = True
        if not endPts:
            # no possible jumps
            endPts = noJumpEndPts
            jumpsFound = False
        # *******************************************************************

        #endPts has list of all possible first moves/jumps
        return (endPts, jumpsFound)

    def nextJumps(self, currPt, pieceGrid):
        # returns only a list of possible jumps
        possibleEndPts = []
        endPts = []
        # check two "forward" squares on diag according to moveDir
        # to the left
        endPt = Point(currPt.x - 1, currPt.y + pieceGrid[currPt.x][currPt.y].moveDir)
        if self.boardCheck.isInvalid(endPt) == False:
            possibleEndPts.append(endPt)
        # to the right
        endPt = Point(currPt.x + 1, currPt.y + pieceGrid[currPt.x][currPt.y].moveDir)
        if self.boardCheck.isInvalid(endPt) == False:
            possibleEndPts.append(endPt)
        if pieceGrid[currPt.x][currPt.y].type == "king":
            # to the left
            endPt = Point(currPt.x - 1, currPt.y + pieceGrid[currPt.x][currPt.y].moveDir * (-1))
            if self.boardCheck.isInvalid(endPt) == False:
                possibleEndPts.append(endPt)
            # to the right
            endPt = Point(currPt.x + 1, currPt.y + pieceGrid[currPt.x][currPt.y].moveDir * (-1))
            if self.boardCheck.isInvalid(endPt) == False:
                possibleEndPts.append(endPt)
        # for each check if can move and check for first jump
        for pt in possibleEndPts:
            movePossible = self.canMove(currPt, pt, pieceGrid)
            if movePossible == False:
                # if can jump then add jump endPt to endPts
                jumpResult = self.canJump(currPt, pt, pieceGrid)
                if jumpResult[0] == True:
                    endPts.append(jumpResult[1])
        # endPts has list of all possible next jumps
        return endPts
