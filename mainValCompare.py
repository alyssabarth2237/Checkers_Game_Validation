import csv
from time import perf_counter
# ***********************************
from mainLoop import playGame
# ***********************************

#test pair twice with each starting first once
valList = ["A", "B", "C", "D", "E"]

totalTestingTime = 0.0
avgGameTime = 0.0
avgNumMoves = 0
wasErrorAllTests = False
trialNum = 1
prevValPairs = []


# *****Command Line Arguments******
normalMode = True
# *********************************


# main test file (each individual entry)
with open("Val_Vs_Val_Test_Main.csv", "w") as mainFile:
    mainFileStream = csv.writer(mainFile)
    # writing the headers for each field
    fields = ["Trial #", "Black Val f(x)", "Red Val f(x)", "Winner", "# Black Left", "# Red Left", "# Moves", "Total Game Time", "Error"]
    mainFileStream.writerow(fields)


print("Starting Testing...")

testStartTime = perf_counter()

# FIXME: FIRST PLAY GAME WITH ONE ORDER AND THEN SWITCH

for valI in valList:
    for valJ in valList:
        if ((valI, valJ) not in prevValPairs) and (valI != valJ):
            prevValPairs.append((valI, valJ))
            valStrBlack = f"Val {valI}"
            valStrRed = f"Val {valJ}"

            # start game time
            gameStartTime = perf_counter()

            # (totalRandTime, totalMinimaxTime, winner, moveCount, wasError, numLeftBlack, numLeftRed)
            results = playGame(normalMode, valI, valJ)

            # end game time
            gameStopTime = perf_counter()

            gameTime = gameStopTime - gameStartTime

            winner = results[2]
            moveCount = results[3]
            wasError = results[4]
            numLeftBlack = results[5]
            numLeftRed = results[6]

            numMoves = moveCount
            if (numMoves % 2) == 0:
                numMoves = numMoves // 2
            else:
                numMoves = (numMoves + 1) // 2

            if wasError == True:
                wasErrorAllTests = True
                break
            if winner == "black":
                winner = valStrBlack
            elif winner == "red":
                winner = valStrRed
            avgGameTime += gameTime
            avgNumMoves += numMoves

            # write to main file trial results
            with open("Val_Vs_Val_Test_Main.csv", "a") as mainFile:
                mainFileStream = csv.writer(mainFile)
                # ["Trial #", "Black Val f(x)", "Red Val f(x)", "Winner", "# Black Left", "# Red Left", "# Moves", "Total Game Time", "Error"]
                resultRow = [str(trialNum), valStrBlack, valStrRed, winner, str(numLeftBlack), str(numLeftRed), str(numMoves), str(gameTime), str(wasError)]
                mainFileStream.writerow(resultRow)
            trialNum += 1

            # *********** Now Flip the Pair ****************

            valStrBlack = f"Val {valJ}"
            valStrRed = f"Val {valI}"

            # start game time
            gameStartTime = perf_counter()

            # (totalRandTime, totalMinimaxTime, winner, moveCount, wasError)
            results = playGame(normalMode, valJ, valI)

            # end game time
            gameStopTime = perf_counter()

            gameTime = gameStopTime - gameStartTime

            winner = results[2]
            moveCount = results[3]
            wasError = results[4]

            numMoves = moveCount
            if (numMoves % 2) == 0:
                numMoves = numMoves // 2
            else:
                numMoves = (numMoves + 1) // 2

            if wasError == True:
                wasErrorAllTests = True
                break
            if winner == "black":
                winner = valStrBlack
            elif winner == "red":
                winner = valStrRed
            avgGameTime += gameTime
            avgNumMoves += numMoves

            # write to main file trial results
            with open("Val_Vs_Val_Test_Main.csv", "a") as mainFile:
                mainFileStream = csv.writer(mainFile)
                # ["Trial #", "Black Val f(x)", "Red Val f(x)", "Winner", "# Moves", "Total Game Time", "Error"]
                resultRow = [str(trialNum), valStrBlack, valStrRed, winner, str(numMoves), str(gameTime), str(wasError)]
                mainFileStream.writerow(resultRow)
            trialNum += 1



testStopTime = perf_counter()


totalTestingTime = testStopTime - testStartTime
# must be averaged
numTrials = trialNum - 1
avgGameTime = avgGameTime / numTrials
avgNumMoves = avgNumMoves / numTrials

# overall test results file
with open("Val_Vs_Val_Test_Overall.csv", "a") as file:
    fileStream = csv.writer(file)
    fields = ["# Trials", "Average # Moves", "Average Game Time", "Total Testing Time", "Error"]
    fileStream.writerow(fields)
    resultRow = [str(numTrials), str(avgNumMoves), str(avgGameTime), str(totalTestingTime), str(wasErrorAllTests)]
    fileStream.writerow(resultRow)


print("Finished Testing. Exiting Script...")