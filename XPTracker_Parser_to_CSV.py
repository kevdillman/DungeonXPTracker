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
        return -1, -1, -1
    foundValue = searchData[varStart+2:varEnd]

    if(len(foundValue) > 1):
        if foundValue[1] == '\"':
            foundValue = foundValue[1:len(foundValue) - 3]

    return varStart, varEnd, foundValue

# goes through entire saved variables file adding categories to the list
def getCategories(data, begginingDelimeter, endingDelimeter):
    # preload the varStart and varEnd variables
    varStart, varEnd, foundData = findNextVariable(data, 0, begginingDelimeter, endingDelimeter)
    csvVariables = list()

    while (varStart >= 0):
        foundValue = data[varStart + 2:varEnd - 1]

        # add value to list if it hasn't been found before
        if foundValue not in csvVariables:
            # categories must be strings, first char past [ will be "
            if data[varStart+1] == '\"':
                csvVariables.append(foundValue)

        varStart, varEnd, foundData = findNextVariable(data, varEnd + 1, begginingDelimeter, endingDelimeter)
    #print("the variables are: \n", csvVariables)
    return csvVariables

# returns the category of the data or -2 if no delimeter found
def getCategory(data, start, begginingDelimeter, endingDelimeter):
    varStart, varEnd, foundValue = findNextVariable(data, start, begginingDelimeter, endingDelimeter)

    # prevents referencing out of range
    if(varStart >= 0):

        # if at end of set of data move to next set
        if data[varStart+1] != '\"':
            foundValue = -1
            return varStart, varEnd, foundValue

        foundValue = data[varStart + 2:varEnd - 1]
        return varStart, varEnd, foundValue

    return -2, -2, -2


def getData(data, begginingDelimeter, endingDelimeter, categories):
    csvVariables = {}
    compiledData = {}
    for column in categories:
        csvVariables[column] = ["No Data"]

    # preload the varStart and varEnd variables
    varStart, varEnd, foundCategory = getCategory(data, 0, begginingDelimeter[0], endingDelimeter[0])
    varStart, varEnd, foundData = findNextVariable(data, varEnd + 1, begginingDelimeter[1], endingDelimeter[1])

    while (varStart >= 0):
        if foundData[0] == '\"':
            foundData = foundData[1:len(foundData) - 2]
        csvVariables[foundCategory] = foundData

        # if wowui returns "a" instead of value change to "No Data"
        if (foundData == 'a'):
            csvVariables[foundCategory] = ["No Data"]

        varStart, varEnd, foundCategory = getCategory(data, varEnd + 1, begginingDelimeter[0], endingDelimeter[0])

        # add all of the new found dungeon data to the dictionary
        if foundCategory == -1:
            # initialize compiledData
            if len(compiledData) == 0:
                for column in categories:
                    compiledData[column] = [csvVariables[column]]
                    csvVariables[column] = ["No Data"]

            else:
                for column in categories:
                    compiledData[column] += [csvVariables[column]]
                    csvVariables[column] = ["No Data"]

            varStart, varEnd, foundCategory = getCategory(data, varEnd + 1, begginingDelimeter[0], endingDelimeter[0])

        varStart, varEnd, foundData = findNextVariable(data, varEnd + 1, begginingDelimeter[1], endingDelimeter[1])

    df = pd.DataFrame(compiledData)
    return df

def main():
    dungeonData = Path('./dungeon_runs/XPTracker.lua').read_text()
    parsedDungeonData = dungeonData[dungeonData.find("\"dungeons\"") + 17:]
    begginingDelimeter = ['[', '=']
    endingDelimeter = [']', ',']

    catHeadings = getCategories(parsedDungeonData, begginingDelimeter[0], endingDelimeter[0])
    lvlingData = getData(parsedDungeonData, begginingDelimeter, endingDelimeter, catHeadings)

    lvlingData.to_csv("./dungeon_runs/dungeonData.csv")

if __name__ == '__main__':
    main()
