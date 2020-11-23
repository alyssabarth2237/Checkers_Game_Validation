from gamePiece import GamePiece, King
from point import Point
from config import rows, cols

dummyColor = "na"

def pawnToKing(pt, pieceGrid):
    if pieceGrid[pt.x][pt.y].type == "pawn":
        samePColor = pieceGrid[pt.x][pt.y].pColor

        pieceGrid[pt.x][pt.y] = GamePiece(dummyColor, pt, "na")
        pieceGrid[pt.x][pt.y] = King(samePColor, pt, pieceGrid)

    else:
        print(" << ERROR: pawnToKing CALLED ON KING PIECE >>")
    return



def capture(blackPiecePt, endPt, pieceGrid):
    #print("  {{{  ERROR: MUST WRITE CAPTURE FUNCTION!!!  }}}")

    #find middle pt
    xinc = int(endPt.x - blackPiecePt.x)
    yinc = int(endPt.y - blackPiecePt.y)
    if (abs(xinc) != 2) or (abs(yinc) != 2):
        print("   {{{ ERROR: X OR Y INCREMENT TOO LARGE IN CAPTURE }}}")
        return
    xinc = xinc // 2
    yinc = yinc // 2
    middlePt = Point(blackPiecePt.x + xinc, blackPiecePt.y + yinc)
    if pieceGrid[middlePt.x][middlePt.y].type == "None":
        print("   {{{ ERROR: NO PIECE TO CAPTURE IN CAPTURE }}}")
        return
    currColor = pieceGrid[blackPiecePt.x][blackPiecePt.y].pColor
    if pieceGrid[middlePt.x][middlePt.y].pColor == currColor:
        print("   {{{ ERROR: CANNOT CAPTURE YOUR OWN (SAME COLORED) PIECE IN CAPTURE }}}")
        return
    pieceGrid[middlePt.x][middlePt.y] = GamePiece(dummyColor, middlePt, "na")

    return

def printBoard(pieceGrid):
    for y in range(rows - 1, -1, -1):
        #print("  -   -   -   -   -   -   -   -  ")
        print("  ---  ---  ---  ---  ---  ---  ---  ---  ")
        rowStr = ""
        for x in range(cols):
            #rowStr += "  "
            rowStr += "   "
            xMod = x % 2
            yMod = y % 2
            if xMod == yMod:
                if pieceGrid[x][y].type != "None":
                    if pieceGrid[x][y].pColor == "black":
                        if pieceGrid[x][y].type == "pawn":
                            rowStr += "X "
                        else:
                            rowStr += "x "
                    else:
                        if pieceGrid[x][y].type == "pawn":
                            rowStr += "0 "
                        else:
                            rowStr += "o "
                else:
                    rowStr += "  "
            else:
                rowStr += "\ "
        #rowStr += "|"
        rowStr += "   "
        print(rowStr)
    #print("  -   -   -   -   -   -   -   -  ")
    print("  ---  ---  ---  ---  ---  ---  ---  ---  ")

    return

def ptListPrintStr(listIn):
    str = "[ "
    for pt in listIn:
        str += f"({pt.x}, {pt.y})"
        if pt != listIn[-1]:
            str+= ", "
    str += " ]"
    return str

