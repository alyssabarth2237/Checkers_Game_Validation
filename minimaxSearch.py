from random import randint, seed
#******************************
from referee import Referee
from gamePiece import GamePiece
from point import Point
from config import rows, cols, redMoveDir, blackMoveDir
from boardCheck import BoardCheck
#******************************

alphaMin = -2147483647
betaMax = 2147483647
dummyVal = -2147483648
maxDepth = 6
ref = Referee()
dummyMove = (Point(-1, -1), [])
arrayStartingSize = 3000
boardCheck = BoardCheck()


class Array:
    def __init__(self):
        self.startingSize = arrayStartingSize
        self.size = self.startingSize
        self.array = []
        for i in range(self.size):
            #parentIndIn, indIn, depthIn, typeIn, currPtIn, endPtsIn, boardIn, prevMove, prevPrevMove, repeatingMoves):
            self.array.append(Node(-1, -1, -1, "max", -1, [-1], [], dummyMove, dummyMove, dummyMove, dummyMove, False, False, "None"))

    def add(self, ind, node):
        if ind < self.size:
            #array currently large enough
            self.array[ind] = node
        else:
            #must grow array
            # print("Growing Array...")
            for i in range(self.size):
                self.array.append(Node(-1, -1, -1, "max", -1, [-1], [], dummyMove, dummyMove, dummyMove, dummyMove, False, False, "None"))
            self.size = self.size * 2
            self.array[ind] = node
        return

    def index(self, ind):
        return self.array[ind]

    def __del__(self):
        del self.startingSize
        del self.size
        del self.array
        return



def copyBoard(boardIn):
    newBoard = []
    for x in range(cols):
        currCol = []
        for y in range(rows):
            currCol.append(boardIn[x][y])
        newBoard.append(currCol)
    return newBoard

class Node:
    def __init__(self, parentIndIn, indIn, depthIn, typeIn, currPtIn, endPtsIn, boardIn, prevMoveMax, prevPrevMoveMax, prevMoveMin, prevPrevMoveMin, repeatingMovesMax, repeatingMovesMin, maxColorIn):
        #boardIn is the already updated board with the result of this node's move
        self.parentInd = parentIndIn
        self.ind = indIn
        self.depth = depthIn
        self.type = typeIn
        self.currPt = currPtIn
        self.endPts = endPtsIn
        self.children = []
        self.val = 0
        self.boardRslt = []
        self.visited = False
        self.prevMoveMax = prevMoveMax
        self.prevPrevMoveMax = prevPrevMoveMax
        self.prevMoveMin = prevMoveMin
        self.prevPrevMoveMin = prevPrevMoveMin
        self.repeatingMovesMax = repeatingMovesMax
        self.repeatingMovesMin = repeatingMovesMin
        self.maxColor = maxColorIn
        if self.type == "max":
            self.val = alphaMin
        else:
            self.val = betaMax

        if self.depth >= 0:
            self.boardRslt = copyBoard(boardIn)

        return

    def mostAttackablePiece(self, currColor, otherColor, myPts, oppntPts):
        # score for each of oppnt's pts
        #most to least important factors:
        # distance away from edges
        # surrounding square for blocking (how many openings)
        # distance from my pts
        # FIXME: CHANGE FOR KING?
        # whether or not it's a king? (possibly add later)
        distEdgeW = 100
        ssOpenW = 50
        distMyPtsW = -1

        mAPt = Point(-1, -1)
        mAPtVal = 0
        for oppntPt in oppntPts:
            currVal = 0

            # *** distance away from edges

            closestDist = 100
            leftDist = oppntPt.x
            closestDist = min(closestDist, leftDist)
            rightDist = 7 - oppntPt.x
            closestDist = min(closestDist, rightDist)
            topDist = 7 - oppntPt.y
            closestDist = min(closestDist, topDist)
            bottomDist = oppntPt.y
            closestDist = min(closestDist, bottomDist)
            # FIXME: PENALTY OR WAY TO ACCOUNT FOR CORNER PIECES (more than one dist is 0)
            currVal += distEdgeW * closestDist

            # *** surrounding square for blocking (how many openings)

            # hardcode 4 corner pieces to check
            numSqrsOpen = 0
            ssQueue = []

            # upper left diag
            ssPt = Point(oppntPt.x - 1, oppntPt.y + 1)
            ssQueue.append(ssPt)
            # bottom left diag
            ssPt = Point(oppntPt.x - 1, oppntPt.y - 1)
            ssQueue.append(ssPt)
            # upper right diag
            ssPt = Point(oppntPt.x + 1, oppntPt.y + 1)
            ssQueue.append(ssPt)
            # bottom right diag
            ssPt = Point(oppntPt.x + 1, oppntPt.y - 1)
            ssQueue.append(ssPt)

            for ssPt in ssQueue:
                if (boardCheck.isInvalid(ssPt) == False):
                    if self.boardRslt[ssPt.x][ssPt.y].pColor != otherColor:
                        # square is either open or has my colored piece
                        numSqrsOpen += 1
            currVal += ssOpenW * numSqrsOpen

            # *** distance from my pts

            totDist = 0
            for myPt in myPts:
                # -1 because dist should be zero when they are next to other piece
                xDist = abs(myPt.x - oppntPt.x) - 1
                yDist = abs(myPt.y - oppntPt.y) - 1
                dist = min(xDist, yDist)
                totDist += dist
            currVal += distMyPtsW * totDist

            #now check for larger value
            if currVal > mAPtVal:
                mAPtVal = currVal
                mAPt = oppntPt

        return mAPt


    def canReachKingSqr(self, pt, kingPt, lastRow):
        allKingSqrs = []
        moveDir = 0
        if lastRow == 7:
            allKingSqrs = [Point(1, lastRow), Point(3, lastRow), Point(5, lastRow), Point(7, lastRow)]
            moveDir = 1
        else:
            allKingSqrs = [Point(0, lastRow), Point(2, lastRow), Point(4, lastRow), Point(6, lastRow)]
            moveDir = -1
        stepsLeft = abs(lastRow - pt.y)
        leftKingSqr = max(allKingSqrs[0].x, pt.x - stepsLeft)
        rightKingSqr = min(allKingSqrs[-1].x, pt.x + stepsLeft)
        if (kingPt.x >= leftKingSqr) and (kingPt.x <= rightKingSqr):
            return True
        return False


    def bestKingSqr(self, lastRow, currColor, otherColor):
        # self.boardRslt[x][y].pColor
        # get left and right most king sqrs
        allKingSqrs = []
        moveDir = 0
        if lastRow == 7:
            allKingSqrs = [Point(7, lastRow), Point(5, lastRow), Point(3, lastRow), Point(1, lastRow)]
            moveDir = 1
        else:
            allKingSqrs = [Point(0, lastRow), Point(2, lastRow), Point(4, lastRow), Point(6, lastRow)]
            moveDir = -1
        # changed:
        kingSqrs = allKingSqrs
        # stepsLeft = abs(lastRow - pt.y)
        # leftKingSqr = max(allKingSqrs[0], pt.x - stepsLeft)
        # rightKingSqr = min(allKingSqrs[-1], pt.x + stepsLeft)
        # kingSqrs = []
        # for sqr in allKingSqrs:
        #     if (sqr >= leftKingSqr) and (sqr <= rightKingSqr):
        #         kingSqrs.append(sqr)
        leftSlope = 0
        rightSlope = 0
        leftIntercept = 0
        rightIntercept = 0
        #switched if and else

        # pick best king sqr
        bestKingSqr = (Point(-1, -1), -1)
        for sqr in kingSqrs:
            if moveDir == 1:
                leftSlope = 1
                rightSlope = -1
                leftIntercept = sqr.y - sqr.x
                rightIntercept = sqr.x + sqr.y
            else:
                leftSlope = -1
                rightSlope = 1
                leftIntercept = sqr.x + sqr.y
                rightIntercept = sqr.y - sqr.x

            numOpenSqrs = 0
            frontTriag = []
            #figure out frontTriag
            tempQueue = []
            tempQueue.append((sqr, 0))
            prevSqrs = []
            prevSqrs.append(tempQueue[0][0])
            while tempQueue:
                possibleSqr = tempQueue.pop(0)
                if (possibleSqr[0].x >= 0) and (possibleSqr[0].x <= 7):
                    if moveDir == 1:
                        #previously >=
                        if possibleSqr[0].y <= (leftSlope * possibleSqr[0].x + leftIntercept):
                            if possibleSqr[0].y <= (rightSlope * possibleSqr[0].x + rightIntercept):
                                frontTriag.append(possibleSqr[0])
                    else:
                        if possibleSqr[0].y >= (leftSlope * possibleSqr[0].x + leftIntercept):
                            if possibleSqr[0].y >= (rightSlope * possibleSqr[0].x + rightIntercept):
                                frontTriag.append(possibleSqr[0])
                if possibleSqr[1] < 3:
                    nextSqr = (Point(possibleSqr[0].x - 1, possibleSqr[0].y - moveDir * 1), possibleSqr[1] + 1)
                    if not (nextSqr[0] in prevSqrs):
                        prevSqrs.append(nextSqr[0])
                        tempQueue.append(nextSqr)
                    nextSqr = (Point(possibleSqr[0].x + 1, possibleSqr[0].y - moveDir * 1), possibleSqr[1] + 1)
                    if not (nextSqr[0] in prevSqrs):
                        prevSqrs.append(nextSqr[0])
                        tempQueue.append(nextSqr)
            # now count how many squares are open in frontTriag
            for pSqr in frontTriag:
                if self.boardRslt[pSqr.x][pSqr.y].pColor != otherColor:
                    numOpenSqrs += 1
            if numOpenSqrs > bestKingSqr[1]:
                bestKingSqr = (sqr, numOpenSqrs)
        # now we have the best king sqr
        # return the point for the king sqr
        return bestKingSqr[0]

    def valFunction(self):
        # FIXME: FIX FIRST ROW, LAST ROW, AND EDGE PIECES, SO CORNER PIECES AREN'T COUNTED TWICE
        # FIXME: CHANGING FUNCTION SO IS DIFFERENT WHEN THERE ARE FEWER PIECES ON THE BOARD
        # Both (Same Weights):


        # Normal (Many Pieces):
        # number of pieces in first row
        # number of pieces in last row
        # number of edge pieces (More Weight)
        # full first row

        # Less than X Pieces Total or Less than Y Pieces of the Color Whose Turn it Is:
        # X = minTotPts and Y = minColorPts
        # number of edge pieces (Less Weight)
        # (Average ?) distance of pieces from current color's opponent's pieces

        minTotPts = 10
        minColorPts = 5

        val = 0
        currColor = ""
        otherColor = ""
        myPts = []
        oppntPts = []
        firstRow = -1
        lastRow = -1
        goalSign = 0
        repeatBaseVal = 0
        numMyPts = 0
        numOppntPts = 0
        numTotPts = 0
        myRepeatingMoves = False

        if self.type == "min":
            currColor = "red"
            otherColor = "black"
            goalSign = 1
            repeatBaseVal = alphaMin + 1
            myRepeatingMoves = self.repeatingMovesMax
            if redMoveDir == -1:
                firstRow = 7
                lastRow = 0
            else:
                firstRow = 0
                lastRow = 7
        else:
            currColor = "black"
            otherColor = "red"
            goalSign = -1
            repeatBaseVal = betaMax - 1
            myRepeatingMoves = self.repeatingMovesMin
            if blackMoveDir == 1:
                firstRow = 0
                lastRow = 7
            else:
                firstRow = 7
                lastRow = 0

        # handles repeating moves here
        if myRepeatingMoves == True:
            val = repeatBaseVal
            return val

        for x in range(rows):
            for y in range(cols):
                if self.boardRslt[x][y].pColor == currColor:
                    myPts.append(Point(x, y))
                elif self.boardRslt[x][y].pColor == otherColor:
                    oppntPts.append(Point(x, y))
        numMyPts = len(myPts)
        numOppntPts = len(oppntPts)
        numTotPts = numMyPts + numOppntPts


        # Both Numbers of Pieces With Same Weights:

        # Both) number of pieces

        # shared and not reset
        kingW = 4000  #2000
        # stepsToKingW = -100  # ??
        numReachBestKingW = 100


        # not shared and set in if statement
        stepsToKingW = 0  #-100
        myEdgePtW = 0  #100
        myFstRowW = 0  #200
        myLstRowW = 0  #100
        myFullFstRowW = 0 #500
        distToOppntPtsW = 0 #?? ./
        oppntEdgePtW = 0  # 100
        oppntFstRowW = 0  # 200
        oppntLstRowW = 0  # 100
        oppntFullFstRowW = 0  # 500
        numMyPtsW = 0  #1000
        numOppntPtsW = 0  #1300


        if (numMyPts > minColorPts) and (numOppntPts > minColorPts):
            # both normal
            # Both) number of pieces in first row
            # Both) number of pieces in last row
            # Both) number of edge pieces (More Weight)
            # Both) full first row
            stepsToKingW = -100
            myEdgePtW = 100
            myFstRowW = 200
            myLstRowW = 100
            myFullFstRowW = 500
            distToOppntPtsW = 0 #0 because it doesn't matter for this case
            oppntEdgePtW = myEdgePtW
            oppntFstRowW = myFstRowW
            oppntLstRowW = myLstRowW
            oppntFullFstRowW = myFullFstRowW
            numMyPtsW = 1000
            numOppntPtsW = 1300


        else:
            # both colors haw few points and behave the same
            # Both) number of edge pieces (Less Weight)
            # Both) (Average ?) distance of pieces from current color's opponent's pieces
            # FIXME: CHANGED WEIGHT
            stepsToKingW = -160  # ??
            myEdgePtW = 10
            myFstRowW = 0  # not needed
            myLstRowW = 0  # not needed
            myFullFstRowW = 0  # not needed
            # FIXME: CHANGED WEIGHT
            distToOppntPtsW = -30  #-40
            oppntEdgePtW = myEdgePtW
            oppntFstRowW = myFstRowW
            oppntLstRowW = myLstRowW
            oppntFullFstRowW = myFullFstRowW
            numMyPtsW = 3000
            numOppntPtsW = 3000


        distToOppntPts = 0
        lsDistToOppntPt = 0
        firstRowCt = 0
        stepsToKing = 0
        numReachBestKing = 0

        # Prev: 10, 13
        val += (numMyPtsW * numMyPts - numOppntPtsW * numOppntPts) * goalSign

        # bestKingSqr(lastRow, currColor, otherColor)
        kingSqr = self.bestKingSqr(lastRow, currColor, otherColor)

        for pt in myPts:
            # edge pieces
            if (pt.x == 0) or (pt.x == 7):
                val += myEdgePtW * goalSign
            # first row
            if pt.y == firstRow:
                val += myFstRowW * goalSign
                firstRowCt += 1
            # last row
            if pt.y == lastRow:
                val += myLstRowW * goalSign
            if self.boardRslt[pt.x][pt.y].type == "king":
                val += kingW * goalSign
                numReachBestKing += 1
            else:
                stepsToKing += (lastRow - pt.y)
                reachable = self.canReachKingSqr(pt, kingSqr, lastRow)
                if reachable:
                    numReachBestKing += 1
            # if distToOppntPtsW > 0:
            #     # find shortest distance for this piece to one of oppnts pieces
            #     shortestDist = 1000
            #     for oppntPt in oppntPts:
            #         # get x and y distances
            #         xDiff = abs(oppntPt.x - pt.x)
            #         if xDiff > 0:
            #             xDiff = xDiff - 1
            #         yDiff = abs(oppntPt.y - pt.y)
            #         if yDiff > 0:
            #             yDiff = yDiff - 1
            #
            #         dist = max(xDiff, yDiff)
            #         shortestDist = min(shortestDist, dist)
            #     if self.boardRslt[pt.x][pt.y].type != "king":
            #         distToOppntPts += shortestDist
            #     else:
            #         distToOppntPts += 2 * shortestDist
            #     lsDistToOppntPt = max(lsDistToOppntPt, shortestDist)

            # *******************************
            # mostAttackablePiece(self, currColor, otherColor, myPts, oppntPts)

            if distToOppntPtsW > 0:
                # find shortest distance for this piece to most attackable piece
                mAPt = self.mostAttackablePiece(currColor, otherColor, myPts, oppntPts)
                shortestDist = 1000
                xDiff = abs(mAPt.x - pt.x) - 1
                yDiff = abs(mAPt.y - pt.y) - 1
                dist = max(xDiff, yDiff)
                shortestDist = min(shortestDist, dist)
                distToOppntPts += shortestDist
                # if self.boardRslt[pt.x][pt.y].type != "king":
                #     distToOppntPts += shortestDist
                # else:
                #     distToOppntPts += 2 * shortestDist
                lsDistToOppntPt = max(lsDistToOppntPt, shortestDist)
            # ********************************

        if numOppntPts > 3:
            val += distToOppntPtsW * distToOppntPts
        else:
            val += distToOppntPtsW *lsDistToOppntPt * numMyPts

        val += stepsToKing * stepsToKingW * goalSign
        val += numReachBestKing * numReachBestKingW * goalSign
        if firstRowCt == 4:
            # full first row
            val += myFullFstRowW * goalSign

        distToOppntPts = 0
        lsDistToOppntPt = 0
        firstRowCt = 0
        stepsToKing = 0
        numReachBestKing = 0

        # bestKingSqr(lastRow, currColor, otherColor)
        kingSqr = self.bestKingSqr(firstRow, otherColor, currColor)

        for pt in oppntPts:
            # edge pieces
            if (pt.x == 0) or (pt.x == 7):
                val += (-1) * oppntEdgePtW * goalSign
            # first row
            if pt.y == lastRow:
                val += (-1) * oppntLstRowW * goalSign
                firstRowCt += 1
            # last row
            if pt.y == firstRow:
                val += (-1) * oppntFstRowW * goalSign
            if self.boardRslt[pt.x][pt.y].type == "king":
                val += (-1) * kingW * goalSign
                numReachBestKing += 1
            else:
                stepsToKing += (firstRow - pt.y)
                reachable = self.canReachKingSqr(pt, kingSqr, firstRow)
                if reachable:
                    numReachBestKing += 1
            if distToOppntPtsW > 0:
                # find shortest distance for this piece to one of oppnts pieces
                shortestDist = 1000
                for myPt in myPts:
                    # get x and y distances
                    xDiff = abs(myPt.x - pt.x)
                    if xDiff > 0:
                        xDiff = xDiff - 1
                    yDiff = abs(myPt.y - pt.y)
                    if yDiff > 0:
                        yDiff = yDiff - 1

                    dist = max(xDiff, yDiff)
                    shortestDist = min(shortestDist, dist)
                if self.boardRslt[pt.x][pt.y].type != "king":
                    distToOppntPts += shortestDist
                else:
                    distToOppntPts += 2 * shortestDist
                lsDistToOppntPt = max(lsDistToOppntPt, shortestDist)
        if numOppntPts > 3:
            val += (-1) * distToOppntPtsW * distToOppntPts
        else:
            val += (-1) * distToOppntPtsW *lsDistToOppntPt * numMyPts

        val += stepsToKing * (-1) * stepsToKingW * goalSign
        val += numReachBestKing * numReachBestKingW * goalSign
        if firstRowCt == 4:
            # full first row
            val += (-1) * oppntFullFstRowW * goalSign


        return val


    def nextBoard(self, currPtIn, endPtIn, prevBoard):
        currPt = currPtIn
        endPt = endPtIn
        if abs(endPt.x - currPt.x) <= 1:
            #no capture
            prevBoard[currPt.x][currPt.y].loc = endPt
            prevBoard[endPt.x][endPt.y] = prevBoard[currPt.x][currPt.y]
            #GamePiece(pColorIn, locIn, canvasIn, pieceNumIn, pieceGrid, gameGrid)
            prevBoard[currPt.x][currPt.y] = GamePiece("na", currPt, "na")
        else:
            #capture
            xMoveDir = 0
            yMoveDir = 0
            if currPt.x < endPt.x:
                xMoveDir = 1
            else:
                xMoveDir = -1
            if currPt.y < endPt.y:
                yMoveDir = 1
            else:
                yMoveDir = -1
            capturePt = Point(currPt.x + xMoveDir, currPt.y + yMoveDir)
            prevBoard[capturePt.x][capturePt.y] = GamePiece("na", currPt, "na")

            prevBoard[currPt.x][currPt.y].loc = endPt
            prevBoard[endPt.x][endPt.y] = prevBoard[currPt.x][currPt.y]
            prevBoard[currPt.x][currPt.y] = GamePiece("na", currPt, "na")
        return  #should have modified prevBoard in function that called nextBoard but if not change to line below
        #return prevBoard

    def makeChildren(self, treeInst):
        #find all red pieces on self.boardRslt
        #for each of them find howCanMove and then check for second jumps, etc.
        coloredPieces = [] #pts of the red pieces
        moves = [] #piece endPts lists pairs (all move options including all pieces)
        queue = []

        # *******
        # if not self.boardRslt:
        #     print(f'Depth: {self.depth}')
        #     print("howdy")
        # *******

        maxColor = self.maxColor
        minColor = ""
        if maxColor == "red":
            minColor = "black"
        else:
            minColor = "red"
        newType = ""
        currColor = ""
        prevMove = dummyMove
        prevPrevMove = dummyMove
        prevRepeatingMoves = False
        if self.type == "max":
            currColor = maxColor
            newType = "min"
            prevMove = self.prevMoveMax
            prevPrevMove = self.prevPrevMoveMax
            prevRepeatingMoves = self.repeatingMovesMax
        else:
            currColor = minColor
            newType = "max"
            prevMove = self.prevMoveMin
            prevPrevMove = self.prevPrevMoveMin
            prevRepeatingMoves = self.repeatingMovesMin
            otherPrevMove = self.prevMoveMax
            otherPrevPrevMove = self.prevPrevMoveMax
            otherPrevRepeatingMoves = self.prevPrevMoveMax
        newDepth = self.depth + 1
        # find red or black pieces

        for x in range(rows):
            for y in range(cols):
                if self.boardRslt[x][y].pColor == currColor:
                    coloredPieces.append(Point(x, y))


        #fill queue initially for each colored piece and put non jumping moves in moves
        noJumpEndPts = []
        jumpsFound = False
        for piece in coloredPieces:
            newCurrPt = piece
            howCanMoveRslt = ref.howCanMove(newCurrPt, self.boardRslt)
            possibleEndPts = howCanMoveRslt[0]
            jumpsFoundRslt = howCanMoveRslt[1]
            if jumpsFoundRslt == True:
                jumpsFound = True

            #now must check for double+ jumps
            for endPt in possibleEndPts:
                newBoard = copyBoard(self.boardRslt)
                self.nextBoard(newCurrPt, endPt, newBoard)
                newEndPts = [endPt]
                if abs(endPt.x - newCurrPt.x) <= 1:
                    #no jumps so add to moves
                    noJumpEndPts.append((newCurrPt, newEndPts, newBoard))
                else:
                    # jumps after so add to queue
                    queue.append((newCurrPt, newEndPts, newBoard))
        # now deal with appending noJumpEndPts to moves if no jumps (also check that queue is empty)
        if jumpsFound == False:
            for pt in noJumpEndPts:
                moves.append(pt)

        #now handle queue for all jumping combos
        #while the queue is not empty
        while queue:
            # if can jump further add to queue and if not add to moves
            tempMove = queue.pop(0)
            tempStartPt = tempMove[0]
            tempCurrPt = tempMove[1][-1]
            tempBoard = tempMove[2]
            possibleEndPts = ref.nextJumps(tempCurrPt, tempBoard)
            if not possibleEndPts:
                # no further jumps so add to moves
                moves.append(tempMove)
            else:
                # still jumping so add back to queue
                for endPt in possibleEndPts:
                    newBoard = tempBoard[:]
                    self.nextBoard(tempCurrPt, endPt, newBoard)
                    newEndPts = tempMove[1][:]
                    newEndPts.append(endPt)
                    queue.append((tempStartPt, newEndPts, newBoard))

        #now add all moves to tree
        nextPrevMove = dummyMove
        nextPrevPrevMove = dummyMove
        # if self.depth > 0:
        #     nextPrevMove = (self.currPt, self.endPts)
        #     nextPrevPrevMove = prevMove
        # else:
        #     nextPrevMove = prevMove
        #     nextPrevPrevMove = prevPrevMove
        for move in moves:
            # we need to keep but discourage repeating moves
            repeatingMoves = False
            if prevRepeatingMoves == True:
                repeatingMoves = True
            if (move[0] == prevMove[0]) and (move[1] == prevMove[1]):
                repeatingMoves = True
            if (move[0] == prevPrevMove[0]) and (move[1] == prevPrevMove[1]):
                repeatingMoves = True
            # if repeatingMoves == True:
            #     print("** repeating moves **")
            #     print("howdy")
            newInd = treeInst.nextAvailInd
            treeInst.nextAvailInd += 1
            self.children.append(newInd)
            #parentIndIn, indIn, depthIn, typeIn, currPtIn, endPtsIn, boardIn, treeIn
            # FIXME: CHANGE NODE INIT TO INCLUDE FLAG FOR REPEATING MOVES
            #def __init__(self, parentIndIn, indIn, depthIn, typeIn, currPtIn, endPtsIn, boardIn, prevMove, prevPrevMove, repeatingMoves):
            nextPrevMove = (move[0], move[1])
            nextPrevPrevMove = prevMove

            prevMoveMax = dummyMove
            prevPrevMoveMax = dummyMove
            prevMoveMin = dummyMove
            prevPrevMoveMin = dummyMove
            repeatingMovesMax = False
            repeatingMovesMin = False
            if self.type == "max":
                prevMoveMax = nextPrevMove
                prevPrevMoveMax = nextPrevPrevMove
                prevMoveMin = self.prevMoveMin
                prevPrevMoveMin = self.prevPrevMoveMin
                repeatingMovesMax = repeatingMoves
                repeatingMovesMin = self.repeatingMovesMin
            else:
                prevMoveMax = self.prevMoveMax
                prevPrevMoveMax = self.prevPrevMoveMax
                prevMoveMin = nextPrevMove
                prevPrevMoveMin = nextPrevPrevMove
                repeatingMovesMax = self.repeatingMovesMax
                repeatingMovesMin = repeatingMoves

            treeInst.tree.add(newInd, Node(self.ind, newInd, newDepth, newType, move[0], move[1], move[2], prevMoveMax, prevPrevMoveMax, prevMoveMin, prevPrevMoveMin, repeatingMovesMax, repeatingMovesMin, maxColor))
        return
    def printNode(self):
        print(f"({self.ind}, {self.depth}, {self.type}, {self.val})")
        return

    def __del__(self):
        del self.parentInd
        del self.ind
        del self.depth
        del self.type
        del self.currPt
        del self.endPts
        del self.children
        del self.val
        del self.boardRslt
        del self.visited
        del self.prevMoveMax
        del self.prevMoveMin
        del self.prevPrevMoveMax
        del self.prevPrevMoveMin
        del self.repeatingMovesMax
        del self.repeatingMovesMin
        return


class Tree:
    # def __init__(self, boardIn, prevMove, prevPrevMove):
    def __init__(self, boardIn, prevMoveMax, prevPrevMoveMax, prevMoveMin, prevPrevMoveMin, maxColor):
        self.tree = Array()
        self.rootInd = 0
        self.nextAvailInd = 1
        #make tree here
        dummyPt = Point(-1, -1)
        #parentIndIn, indIn, depthIn, typeIn, currPtIn, endPtsIn, boardIn, treeIn
        self.tree.add(0, Node(-1, 0, 0, "max", dummyPt, [dummyPt], boardIn, prevMoveMax, prevPrevMoveMax, prevMoveMin, prevPrevMoveMin, False, False, maxColor))
        #self.tree.reverse()
        self.currInd = 0
        self.currNode = self.tree.index(0)

    def visit(self, ind):
        #function for indexing node


        #set currInd
        self.currInd = ind
        #make children if not visited before
        self.currNode = self.tree.index(self.currInd)
        if self.currNode.visited == False:
            #FIXME: MAKE CHILDREN HERE

            #*****************
            if self.currNode.depth < maxDepth:
                # ***********
                if self.currNode.depth == -1:
                    print("self.currNode.depth is -1")
                    print("howdy")
                # ***********
                self.currNode.makeChildren(self)
                if not self.currNode.children:
                    self.currNode.val = self.currNode.valFunction()
            else:
                # FIXME: write function
                self.currNode.val = self.currNode.valFunction()
            # *****************
            #must make children and set currNode again after children have been made
            self.currNode = self.tree.index(self.currInd)
            self.currNode.visited = True

        #returns nothing (not needed)
        return

    #FIXME: CHECK IF CORRECT (FIXED)
    def levelOrderPrint(self):
        queue = []
        currLevel = -1
        queue.append(self.rootInd)
        while queue:
            currNode = queue.pop(0)
            self.visit(currNode)
            if self.currNode.depth > currLevel:
                print(f"*** Level {self.currNode.depth}:")
                currLevel = self.currNode.depth
            self.currNode.printNode()
            for childInd in self.currNode.children:
                queue.append(childInd)
        print("Finished Level Order Print...")
        return

    def __del__(self):
        del self.rootInd
        del self.nextAvailInd
        del self.currInd
        del self.currNode
        del self.tree
        return



# Minimax algorithm with alpha-beta pruning code borrowed from geeksforgeeks.org
#changed to match my game tree
# code on website written by Rituraj Jain
# link: https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
#FIXME: CHECK IF CORRECT (FIXED)
#FIXME: MUST CHANGE SO USES VISIT AND NODE INFORMATION IS ACCESSED FROM WITHIN THE TREE CLASS
#FIXME: CONVERT TREE ARRAY TO TREE CLASS
#FIXME: PASS IN NODE INDEX INSTEAD OF FULL NODE
def minimax(nodeInd, tree, alpha, beta):
    # **********
    tree.visit(nodeInd)
    node = tree.currNode
    # **********
    best = dummyVal
    bestCurrPt = Point(dummyVal, dummyVal)
    bestEndPts = [dummyVal]
    # Terminating condition. i.e
    # leaf node is reached
    if not node.children:
        return (node.currPt, node.endPts, node.val)

    if node.type == "max":
        best = alphaMin
        #call on each child
        for childInd in node.children:
            tup = minimax(childInd, tree, alpha, beta)
            val = tup[2]
            currPt = tup[0]
            endPts = tup[1]
            #select the max(best, val)
            if val > best:
                # best changes to val
                best = val
                bestCurrPt = currPt
                bestEndPts = endPts
            alpha = max(alpha, best)

            # Alpha Beta Pruning
            if beta <= alpha:
                break

    else:
        best = betaMax
        #call on each child
        for childInd in node.children:
            tup = minimax(childInd, tree, alpha, beta)
            val = tup[2]
            currPt = tup[0]
            endPts = tup[1]
            # select the min(best, val)
            if val < best:
                # best changes to val
                best = val
                bestCurrPt = currPt
                bestEndPts = endPts
            beta = min(beta, best)

            # Alpha Beta Pruning
            if beta <= alpha:
                break

    returnTup = (Point(dummyVal, dummyVal), [dummyVal], dummyVal)
    if node.depth > 0:
        # flip repeating moves values
        if best == alphaMin + 1:
            best = betaMax - 1
        elif best == betaMax - 1:
            best = alphaMin + 1
        returnTup = (node.currPt, node.endPts, best)
    else:
        returnTup = (bestCurrPt, bestEndPts, best)
    return returnTup


# *Here*
# Random Player Function
#def minimax(nodeInd, tree, alpha, beta):
def randomMove(tree):
    tree.visit(tree.rootInd)
    ind = -1
    if tree.nextAvailInd > 1:
        ind = randint(1, (tree.nextAvailInd - 1))
        tree.visit(ind)
    else:
        ind = 0
    node = tree.currNode
    return (node.currPt, node.endPts, 0)