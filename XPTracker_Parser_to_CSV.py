# Parser to parse saved variable from XPTracker addon
# to csv that can be used with excel
# 12 Feb 2024

import pandas as pd
import numpy as np
from pathlib import Path

# given a string of data and a start point returns index of [ and ]
def findNextVariable(searchData, start, delimeterOne, delimiterTwo):
    varStart = searchData[start:len(searchData)-1].find(delimeterOne) + start
    varEnd = searchData[varStart:len(searchData)-1].find(delimiterTwo) + varStart
    endOfSet = searchData[varEnd + 1:len(searchData)-1].find("--")

    # if -- does not appear anymore in the file we've reached the end
    if endOfSet == -1:
        return -1, -1

    return varStart, varEnd

# goes through entire saved variables file adding categories to the list
def getCategories(data, begginingDelimeter, endingDelimeter):
    # preload the varStart and varEnd variables
    varStart, varEnd = findNextVariable(data, 0, begginingDelimeter, endingDelimeter)
    csvVariables = list()

    while (varStart > 0):
        foundValue = data[varStart+2:varEnd-1]

        # add value to list if it hasn't been found before
        if foundValue not in csvVariables:
            # categories must be strings, first char past [ will be "
            if data[varStart+1] == '\"':
                csvVariables.append(foundValue)

        varStart, varEnd = findNextVariable(data, varEnd + 1, begginingDelimeter, endingDelimeter)
    #print("the variables are: \n", csvVariables)
    return csvVariables



def getData(data, begginingDelimeter, endingDelimeter, categories):
    # preload the varStart and varEnd variables
    varStart, varEnd = findNextVariable(data, 0, begginingDelimeter, endingDelimeter)
    csvVariables = list()
    #print("varStart is: ", varStart, "varEnd is: ", varEnd)
    counter = 0
    while (varStart >= 0) and counter < 20:
        foundValue = data[varStart+2:varEnd]

        csvVariables.append(foundValue)
        counter += 1
        varStart, varEnd = findNextVariable(data, varEnd + 1, begginingDelimeter, endingDelimeter)

    return csvVariables

# work in progress
# creates a DataFrame from the categorie headings filling each category with every value found
def createDataFrame(columns, rows):

    index = 0
    combineData = {}
    for columnTitle in columns:
        combineData[columnTitle] = rows
        index += 1

   # print("the combinded data is: \n", combineData)
    df = pd.DataFrame(combineData)
    print("The dataframe is: \n", df)
    return 0

def main():
    dungeonData = Path('./dungeon_runs/XPTracker.lua').read_text()
    parsedDungeonData = dungeonData[dungeonData.find("\"dungeons\"") + 12:]
    begginingDelimeter = '['
    endingDelimeter = ']'

    catHeadings = getCategories(parsedDungeonData, begginingDelimeter, endingDelimeter)

    begginingDelimeter = '='
    endingDelimeter = ','
    lvlingData = getData(parsedDungeonData[5:len(parsedDungeonData)-1], begginingDelimeter, endingDelimeter, catHeadings)

    createDataFrame(catHeadings, lvlingData)

if __name__ == '__main__':
    main()
