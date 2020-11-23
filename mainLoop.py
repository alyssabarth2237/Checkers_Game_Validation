from copy import deepcopy
from gc import collect
from sys import argv
from time import perf_counter
#******************************
from config import rows, cols, redMoveDir, blackMoveDir, moveLimit, moveRate
from point import Point
from gamePiece import GamePiece, Pawn
from referee import Referee
from minimaxSearch import Tree, minimax, alphaMin, betaMax, randomMove, TreeAdjustable
from capture import capture, pawnToKing, printBoard, ptListPrintStr
#******************************

# ***Important Notes***
# cols = x
# rows = y
# pieceGrid[x][y] = pieceGrid[col][row] = pieceGrid[j][i] (with j outer and i inner)
# for cols (for rows) = for x (for y)

def printHi():
    print("hi")
    print("wazzup")
    print("bye")
    return

def playGame(normalMode, valueBlack, valueRed):
    if valueRed == "na":
        valueRed = "E"

    totalRandTime = 0.0
    totalMinimaxTime = 0.0
    wasError = False
    winner = "na"
    numMoves = 0


    # first coordinate is x and second is y
    # 0,0 is the bottom left square
    dummyMove = (Point(-1, -1), [])
    endGame = False
    dummyColor = "na"
    pieceGrid = []  # for locs of pieces
    referee = Referee()
    turn = "None"
    moveCount = 0
    prevMoveA = dummyMove
    prevPrevMoveA = dummyMove
    prevMoveB = dummyMove
    prevPrevMoveB = dummyMove


    # *** initialize board ***

    for x in range(cols):
        currColPiece = [] #for dummys in pieceGrid
        for y in range(int(rows/2)):

            currColPiece.append(GamePiece(dummyColor, Point(x, (y * 2)), "na"))
            currColPiece.append(GamePiece(dummyColor, Point(x, (y * 2 + 1)), "na"))

        pieceGrid.append(currColPiece)


    #creating black pieces
    firstY = 0
    lastY = 0
    if blackMoveDir == 1:
        firstY = 0
        lastY = 2
    else:
        firstY = 5
        lastY = 7
    for y in range(firstY, lastY + 1):
        for x in range(int(cols/2)):
            pieceGrid[x * 2 + (y % 2)][y] = Pawn("black", Point(x * 2 + (y % 2), y), pieceGrid)
    #creating red pieces
    if redMoveDir == -1:
        firstY = 5
        lastY = 7
    else:
        firstY = 0
        lastY = 2
    for y in range(firstY, lastY + 1):
        for x in range(int(cols / 2)):
            pieceGrid[x * 2 + (y % 2)][y] = Pawn("red", Point(x * 2 + (y % 2), y), pieceGrid)

    print("Done creating pieces...")
    turn = "black"
    print(" { Black's Turn }")
    printBoard(pieceGrid)


    while not endGame:

        # first AI (A) (Black)
        # use command line arguments for mode? (normalMode)
        # random player

        # prevMoveStr = "[ "
        # for pt in prevMoveA[1]:
        #     prevMoveStr += pt.printStr()
        #     if pt != prevMoveA[1][-1]:
        #         prevMoveStr += ", "
        # prevMoveStr += " ]"
        # prevPrevMoveStr = "[ "
        # for pt in prevPrevMoveA[1]:
        #     prevPrevMoveStr += pt.printStr()
        #     if pt != prevPrevMoveA[1][-1]:
        #         prevPrevMoveStr += ", "
        # prevPrevMoveStr += " ]"
        # print(
        #     f'prevMove: {prevMoveA[0].printStr()}  {prevMoveStr}    prevPrevMove: {prevPrevMoveA[0].printStr()}  {prevPrevMoveStr}')

        # ** Timing
        randStart = perf_counter()

        bestTup = (0, 0, 0)  # garbage init
        tree = []
        if normalMode == True:
            tree = TreeAdjustable(pieceGrid, prevMoveA, prevPrevMoveA, prevMoveB, prevPrevMoveB, "black", valueBlack)
            alpha = alphaMin
            beta = betaMax
            print("   Calling Minimax...")
            bestTup = minimax(tree.rootInd, tree, alpha, beta)
        else:
            tree = Tree(pieceGrid, prevMoveA, prevPrevMoveA, prevMoveB, prevPrevMoveB, "black")
            alpha = alphaMin
            beta = betaMax
            print("   Calling Random...")
            bestTup = randomMove(tree)

        # tree = Tree(pieceGrid, prevMoveA, prevPrevMoveA, prevMoveB, prevPrevMoveB, "black")
        # alpha = alphaMin
        # beta = betaMax
        # bestTup = (0, 0, 0)  # garbage init
        # bestTup = randomMove(tree)

        # ** Timing
        randFinish = perf_counter()
        totalRandTime += randFinish - randStart

        # FIXME: SWITCH FUNCTION TO RANDOM OR OTHER THAN MINIMAX FOR COMMAND LINE ARGUMENTS
        # if normalMode == True:
        #     bestTup = minimax(tree.rootInd, tree, alpha, beta)
        # else:
        #     bestTup = randomMove(tree)
        # FIXME: DELETES
        del tree
        collect()
        blackPiecePt = bestTup[0]
        blackEndPts = bestTup[1]
        print(f"Black Move Value: {bestTup[2]}")
        if isinstance(blackEndPts[0], int):
            print(" ***********************************   Error WITH MINIMAX HERE")
            print(f"blackPiecePt: {blackPiecePt.printStr()}")
            print("blackEndPts:")
            print(blackEndPts)
            print(f"Black Move Value: {bestTup[2]}")
            wasError = True
            break
        if blackPiecePt != Point(-1, -1):
            print(f"Best Val: ( {blackPiecePt.printStr()}, {ptListPrintStr(blackEndPts)} )")

        # * moveAI Section *

        if blackPiecePt != Point(-1, -1):
            #FIXME: NEEDS FOR LOOP FOR EACH ENDPOINT
            # FIXME: NEED FUNCTION TO HANDLE CAPTURES AND REMOVE PIECES
            prevPrevMoveA = prevMoveA
            prevMoveA = (blackPiecePt, deepcopy(blackEndPts))

            for endPt in blackEndPts:
                # must capture piece if jumping
                if abs(endPt.x - blackPiecePt.x) > 1:
                    # jumping
                    capture(blackPiecePt, endPt, pieceGrid)

                # update loc of current piece to endPt
                pieceGrid[blackPiecePt.x][blackPiecePt.y].loc = endPt
                # set endPt in pieceGrid to blackPiecePt in pieceGrid
                pieceGrid[endPt.x][endPt.y] = pieceGrid[blackPiecePt.x][blackPiecePt.y]
                # set blackPiecePt in pieceGrid to blank piece
                pieceGrid[blackPiecePt.x][blackPiecePt.y] = GamePiece(dummyColor, Point(x, (y * 2)), "na")

                blackPiecePt = endPt
                if (blackPiecePt.y == pieceGrid[blackPiecePt.x][blackPiecePt.y].lastRow) and (
                        pieceGrid[blackPiecePt.x][blackPiecePt.y].type == "pawn"):
                    pawnToKing(blackPiecePt, pieceGrid)

        else:
            # executes if AI looses because it has no legal moves available
            print("   *** BLACK HAS NO LEGAL MOVES ***")
            print("   *** RED WON! ***")
            print("   *** GAME OVER ***")
            numMoves = moveCount
            if (numMoves % 2) == 0:
                numMoves = numMoves // 2
            else:
                numMoves = (numMoves + 1) // 2
            print(f"   *** MOVE COUNT: {numMoves}")
            printBoard(pieceGrid)
            winner = "minimax"
            break


        moveCount += 1
        # check for if red or black has won
        blackCount = 0
        redCount = 0
        for x in range(cols):
            for y in range(rows):
                if pieceGrid[x][y].pColor == "black":
                    blackCount += 1
                elif pieceGrid[x][y].pColor == "red":
                    redCount += 1

        if (redCount == 0) and (blackCount > 0):
            # black has won!
            print("   *** BLACK WON! ***")
            print("   *** GAME OVER ***")
            numMoves = moveCount
            if (numMoves % 2) == 0:
                numMoves = numMoves // 2
            else:
                numMoves = (numMoves + 1) // 2
            print(f"   *** MOVE COUNT: {numMoves}")
            printBoard(pieceGrid)
            winner = "random"
            break
        elif (blackCount == 0) and (redCount > 0):
            # red has won!
            print("   *** RED WON! ***")
            print("   *** GAME OVER ***")
            numMoves = moveCount
            if (numMoves % 2) == 0:
                numMoves = numMoves // 2
            else:
                numMoves = (numMoves + 1) // 2
            print(f"   *** MOVE COUNT: {numMoves}")
            printBoard(pieceGrid)
            winner = "minimax"
            break
        if moveCount == moveLimit:
            # no winner!
            print("   *** MOVE LIMIT EXCEEDED! ***")
            print("   *** GAME OVER ***")
            numMoves = moveCount
            if (numMoves % 2) == 0:
                numMoves = numMoves // 2
            else:
                numMoves = (numMoves + 1) // 2
            print(f"   *** MOVE COUNT: {numMoves}")
            printBoard(pieceGrid)
            winner = "none"
            break

        turn = "red"
        print(" { Red's Turn }")
        printBoard(pieceGrid)


        #***********************************************************************************************************
        #***********************************************************************************************************

        # second AI (B) (Red)
        # minimax search

        # prevMoveStr = "[ "
        # for pt in prevMoveB[1]:
        #     prevMoveStr += pt.printStr()
        #     if pt != prevMoveB[1][-1]:
        #         prevMoveStr += ", "
        # prevMoveStr += " ]"
        # prevPrevMoveStr = "[ "
        # for pt in prevPrevMoveB[1]:
        #     prevPrevMoveStr += pt.printStr()
        #     if pt != prevPrevMoveB[1][-1]:
        #         prevPrevMoveStr += ", "
        # prevPrevMoveStr += " ]"
        # print(
        #     f'prevMove: {prevMoveB[0].printStr()}  {prevMoveStr}    prevPrevMove: {prevPrevMoveB[0].printStr()}  {prevPrevMoveStr}')

        # ** Timing
        minimaxStart = perf_counter()

        bestTup = (0, 0, 0)  # garbage init
        tree = []
        tree = TreeAdjustable(pieceGrid, prevMoveB, prevPrevMoveB, prevMoveA, prevPrevMoveA, "red", valueRed)
        alpha = alphaMin
        beta = betaMax
        print("   Calling Minimax...")
        bestTup = minimax(tree.rootInd, tree, alpha, beta)
        # if normalMode == True:
        #     tree = TreeAdjustable(pieceGrid, prevMoveB, prevPrevMoveB, prevMoveA, prevPrevMoveA, "red", valueRed)
        #     alpha = alphaMin
        #     beta = betaMax
        #     print("   Calling Minimax...")
        #     bestTup = minimax(tree.rootInd, tree, alpha, beta)
        # else:
        #     tree = Tree(pieceGrid, prevMoveB, prevPrevMoveB, prevMoveA, prevPrevMoveA, "red")
        #     alpha = alphaMin
        #     beta = betaMax
        #     print("   Calling Minimax...")
        #     bestTup = minimax(tree.rootInd, tree, alpha, beta)

        # tree = Tree(pieceGrid, prevMoveB, prevPrevMoveB, prevMoveA, prevPrevMoveA, "red")
        # alpha = alphaMin
        # beta = betaMax
        # bestTup = (0, 0, 0)  # garbage init
        # # print("   Calling Minimax...")
        # bestTup = minimax(tree.rootInd, tree, alpha, beta)

        # ** Timing
        minimaxFinish = perf_counter()
        totalMinimaxTime += minimaxFinish - minimaxStart

        # FIXME: SWITCH FUNCTION TO RANDOM OR OTHER THAN MINIMAX FOR COMMAND LINE ARGUMENTS
        # if normalMode == True:
        #     bestTup = minimax(tree.rootInd, tree, alpha, beta)
        # else:
        #     bestTup = randomMove(tree)
        del tree
        collect()
        redPiecePt = bestTup[0]
        redEndPts = bestTup[1]
        print(f"Red Move Value: {bestTup[2]}")
        if isinstance(redEndPts[0], int):
            print(" ***********************************   Error WITH MINIMAX HERE")
            print(f"redPiecePt: {redPiecePt.printStr()}")
            print("redEndPts:")
            print(redEndPts)
            print(f"Red Move Value: {bestTup[2]}")
            wasError = True
            break
        if redPiecePt != Point(-1, -1):
            print(f"Best Val: ( {redPiecePt.printStr()}, {ptListPrintStr(redEndPts)} )")

        # * moveAI Section *

        if redPiecePt != Point(-1, -1):
            prevPrevMoveB = prevMoveB
            prevMoveB = (redPiecePt, deepcopy(redEndPts))

            for endPt in redEndPts:
                # must capture piece if jumping
                if abs(endPt.x - redPiecePt.x) > 1:
                    # jumping
                    capture(redPiecePt, endPt, pieceGrid)

                # update loc of current piece to endPt
                pieceGrid[redPiecePt.x][redPiecePt.y].loc = endPt
                # set endPt in pieceGrid to redPiecePt in pieceGrid
                pieceGrid[endPt.x][endPt.y] = pieceGrid[redPiecePt.x][redPiecePt.y]
                # set redPiecePt in pieceGrid to blank piece
                pieceGrid[redPiecePt.x][redPiecePt.y] = GamePiece(dummyColor, Point(x, (y * 2)), "na")

                redPiecePt = endPt
                if (redPiecePt.y == pieceGrid[redPiecePt.x][redPiecePt.y].lastRow) and (
                        pieceGrid[redPiecePt.x][redPiecePt.y].type == "pawn"):
                    pawnToKing(redPiecePt, pieceGrid)

        else:
            # executes if AI looses because it has no legal moves available
            print("   *** RED HAS NO LEGAL MOVES ***")
            print("   *** BLACK WON! ***")
            print("   *** GAME OVER ***")
            numMoves = moveCount
            if (numMoves % 2) == 0:
                numMoves = numMoves // 2
            else:
                numMoves = (numMoves + 1) // 2
            print(f"   *** MOVE COUNT: {numMoves}")
            printBoard(pieceGrid)
            winner = "random"
            break


        moveCount += 1
        # check for if red or black has won
        blackCount = 0
        redCount = 0
        for x in range(cols):
            for y in range(rows):
                if pieceGrid[x][y].pColor == "black":
                    blackCount += 1
                elif pieceGrid[x][y].pColor == "red":
                    redCount += 1

        if (redCount == 0) and (blackCount > 0):
            # black has won!
            print("   *** BLACK WON! ***")
            print("   *** GAME OVER ***")
            numMoves = moveCount
            if (numMoves % 2) == 0:
                numMoves = numMoves // 2
            else:
                numMoves = (numMoves + 1) // 2
            print(f"   *** MOVE COUNT: {numMoves}")
            printBoard(pieceGrid)
            winner = "random"
            break
        elif (blackCount == 0) and (redCount > 0):
            # red has won!
            print("   *** RED WON! ***")
            print("   *** GAME OVER ***")
            numMoves = moveCount
            if (numMoves % 2) == 0:
                numMoves = numMoves // 2
            else:
                numMoves = (numMoves + 1) // 2
            print(f"   *** MOVE COUNT: {numMoves}")
            printBoard(pieceGrid)
            winner = "minimax"
            break
        if moveCount == moveLimit:
            # no winner!
            print("   *** MOVE LIMIT EXCEEDED! ***")
            print("   *** GAME OVER ***")
            numMoves = moveCount
            if (numMoves % 2) == 0:
                numMoves = numMoves // 2
            else:
                numMoves = (numMoves + 1) // 2
            print(f"   *** MOVE COUNT: {numMoves}")
            printBoard(pieceGrid)
            winner = "none"
            break


        turn = "black"
        print(" { Black's Turn }")
        printBoard(pieceGrid)


    return (totalRandTime, totalMinimaxTime, winner, moveCount, wasError)


