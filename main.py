import csv
from time import perf_counter
from sys import argv
# ***********************************
from mainLoop import playGame
# ***********************************

#test 20 times to start (later 50?)
numTrials = 50

totalTestingTime = 0.0
numMMWins = 0
numRandWins = 0
numDraws = 0
avgGameTime = 0.0
avgAvgRandTime = 0.0
avgAvgMMTime = 0.0
avgNumMoves = 0
wasErrorAllTests = False


# *****Command Line Arguments******
normalMode = False
valueBlack = "na"
valueRed = "na"
if len(argv) == 3:
    normalMode = True
    if str(argv[1]).upper() == "A":
        valueBlack = "A"
    elif str(argv[1]).upper() == "B":
        valueBlack = "B"
    elif str(argv[1]).upper() == "C":
        valueBlack = "C"
    elif str(argv[1]).upper() == "D":
        valueBlack = "D"
    else:
        # E
        valueBlack = "E"

    if str(argv[2]).upper() == "A":
        valueRed = "A"
    elif str(argv[2]).upper() == "B":
        valueRed = "B"
    elif str(argv[2]).upper() == "C":
        valueRed = "C"
    elif str(argv[2]).upper() == "D":
        valueRed = "D"
    else:
        # E
        valueRed = "E"
if len(argv) == 2:
    if str(argv[1]).upper() == "A":
        valueRed = "A"
    elif str(argv[1]).upper() == "B":
        valueRed = "B"
    elif str(argv[1]).upper() == "C":
        valueRed = "C"
    elif str(argv[1]).upper() == "D":
        valueRed = "D"
    else:
        # E
        valueRed = "E"


# *********************************

if normalMode == True:
    print("*** Using Normal AI ***")
    print(f"*** Black: Value Function {valueBlack} ***")
    print(f"*** Red: Value Function {valueRed} ***")
else:
    print("*** Using Random AI ***")





# main test file (each individual entry)
# with open("Rand_VS_Minimax_Test_Main.csv", "w") as mainFile:
with open("Rand_VS_ValA_Test_Main.csv", "w") as mainFile:
    mainFileStream = csv.writer(mainFile)
    # writing the headers for each field
    fields = ["Trial #", "Winner", "# Moves", "Average Random Move Time", "Average Minimax Move Time", "Total Game Time", "Error"]
    mainFileStream.writerow(fields)


print("Starting Testing...")

testStartTime = perf_counter()

for i in range(1, numTrials + 1):
    # start game time
    gameStartTime = perf_counter()

    # (totalRandTime, totalMinimaxTime, winner, moveCount, wasError)
    results = playGame(normalMode, valueBlack, valueRed)

    # end game time
    gameStopTime = perf_counter()

    gameTime = gameStopTime - gameStartTime

    avgRandTime = results[0]
    avgMMTime = results[1]
    winner = results[2]
    moveCount = results[3]
    wasError = results[4]

    numRandMoves = 0
    numMMMoves = 0
    numMoves = moveCount
    if (numMoves % 2) == 0:
        numMoves = numMoves // 2
        numRandMoves = numMoves
        numMMMoves = numMoves
    else:
        numMoves = (numMoves + 1) // 2
        # black went first so it got the extra move
        numRandMoves = numMoves
        numMMMoves = numMoves - 1

    # average rand time
    avgRandTime = avgRandTime / numRandMoves
    # average minimax time
    avgMMTime = avgMMTime / numMMMoves

    if wasError == True:
        wasErrorAllTests = True
        break
    if winner == "red":
        winner = "minimax"
        numMMWins += 1
    elif winner == "black":
        winner = "random"
        numRandWins += 1
    else:
        # draw
        numDraws += 1
    avgGameTime += gameTime
    avgAvgRandTime += avgRandTime
    avgAvgMMTime += avgMMTime
    avgNumMoves += numMoves

    # write to main file trial results
    # with open("Rand_VS_Minimax_Test_Main.csv", "a") as mainFile:
    with open("Rand_VS_ValA_Test_Main.csv", "a") as mainFile:
        mainFileStream = csv.writer(mainFile)
        # ["Trial #", "Winner", "# Moves", "Average Random Move Time", "Average Minimax Move Time", "Total Game Time", "Error"]
        resultRow = [str(i), winner, str(numMoves), str(avgRandTime), str(avgMMTime), str(gameTime), str(wasError)]
        mainFileStream.writerow(resultRow)





testStopTime = perf_counter()


totalTestingTime = testStopTime - testStartTime
# must be averaged
avgGameTime = avgGameTime / numTrials
avgAvgRandTime = avgAvgRandTime / numTrials
avgAvgMMTime = avgAvgMMTime / numTrials
avgNumMoves = avgNumMoves / numTrials

# overall test results file
# with open("Rand_VS_Minimax_Test_Overall.csv", "a") as file:
with open("Rand_VS_ValA_Test_Overall.csv", "a") as file:
    fileStream = csv.writer(file)
    fields = ["# Trials", "# Minimax Wins", "# Random Wins", "# Draws", "Average # Moves",
              "Average Average Random Move Time", "Average Average Minimax Move Time", "Average Game Time",
              "Total Testing Time", "Error"]
    fileStream.writerow(fields)
    resultRow = [str(numTrials), str(numMMWins), str(numRandWins), str(numDraws), str(avgNumMoves), str(avgAvgRandTime),
                 str(avgAvgMMTime), str(avgGameTime), str(totalTestingTime), str(wasErrorAllTests)]
    fileStream.writerow(resultRow)


print("Finished Testing. Exiting Script...")

