# Parser to parse saved variable from XPTracker addon
# to csv that can be used with excel
# 12 Feb 2024

import pandas as pd
import numpy as np
from datetime import date
from pathlib import Path

# given a string of data, start point, and begin/end delimeters
# returns values between delimeters and delimeter locations
# returns -1 if end of file
def findNextVariable(searchData, start, delimeterOne, delimiterTwo):
    varStart = searchData[start:len(searchData)-1].find(delimeterOne) + start
    varEnd = searchData[varStart:len(searchData)-1].find(delimiterTwo) + varStart
    endOfSet = searchData[varEnd + 1:len(searchData)-1].find("--")

    # if -- does not appear anymore in the file we've reached the end
    if endOfSet == -1:
        return -1, -1, ""
    foundValue = searchData[varStart+2:varEnd]

    if(len(foundValue) > 1):
        if foundValue[1] == '\"':
            foundValue = foundValue[1:len(foundValue) - 3]

    return varStart, varEnd, foundValue

# finds all key values in passed data
# returns list of keys
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

# finds next key value in data
# returns key start/end location and key
# returns -2 if no key found
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

# takes keys, data with keys and values and delimeters
# maps the data to it's key
# returns the mapped data as a DataFrame
def getData(data, begginingDelimeter, endingDelimeter, categories):
    csvVariables = {}
    compiledData = {}
    for column in categories:
        csvVariables[column] = ["No Data"]

    # preload the varStart and varEnd variables
    varStart, varEnd, foundCategory = getCategory(data, 0, begginingDelimeter[0], endingDelimeter[0])
    varStart, varEnd, foundData = findNextVariable(data, varEnd + 1, begginingDelimeter[1], endingDelimeter[1])

    while (varStart >= 0):

        if (len(foundData) > 0):
            # remove " " from around data values
            if foundData[0] == '\"':
                foundData = foundData[1:len(foundData) - 1]

        if foundCategory == "endingTime" or foundCategory == "startTime":
            foundData = formatDate(foundData)

        csvVariables[foundCategory] = foundData

        # if data value initialized to "a" change to "No Data"
        if (foundData == 'a'):
            csvVariables[foundCategory] = ["No Data"]

        varStart, varEnd, foundCategory = getCategory(data, varEnd + 1, begginingDelimeter[0], endingDelimeter[0])

        # add all of the new found dungeon data to the dictionary
        if foundCategory == -1 or foundCategory == -2:
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

# takes a date time input
# reformats date time to be read by excel and returns it
def formatDate(rawDate):
    yearFromRaw = "20" + rawDate[6:8]
    monthFromRaw = rawDate[3:5]
    dayFromRaw = rawDate[0:2]

    formattedDate = monthFromRaw + "/" + dayFromRaw + "/" + yearFromRaw + rawDate[8:]

    return formattedDate

# gets the account name and path to account's saved variables
def getPaths(pathsDoc):
    accounts = []
    savedVarsPath = ""

    # extract the path to account and saved variables from path.txt
    if pathsDoc.find('WTF\\Account') != -1:
        savedVarsPath = pathsDoc[0 : pathsDoc.find("WTF\\Account")] + "WTF\\Account\\"
    else:
        print("No path found")

    # check if more than one account and extract them from path.txt
    if pathsDoc.find(',') != -1:

        accountBegin = pathsDoc.find(',') + 2
        accountEnd = pathsDoc.find(',', accountBegin)
        while accountEnd != -1:
            accountPathName = ""
            outputName = ""

            accountPathName = pathsDoc[accountBegin : accountEnd]
            print("Account Name: ", accountPathName)

            # check if display name for account
            if len(pathsDoc) >= (accountEnd + 1):
                if pathsDoc[accountEnd + 1] != '\n':
                    accountBegin = accountEnd + 2
                    accountEnd = pathsDoc.find(',', accountBegin)

                    # handles no , after last term
                    if accountEnd == -1:
                        if pathsDoc.find('\n', accountBegin) != -1:
                            accountEnd = pathsDoc.find('\n', accountBegin)
                        else:
                            accountEnd = len(pathsDoc) - 1

                    # add date to output file name
                    outputName = pathsDoc[accountBegin : accountEnd]
                    print("Custom File Name: ", outputName)
                    outputName = date.today().strftime("%Y%m%d") + "_" + pathsDoc[accountBegin : accountEnd] + "_"

            accounts.append([accountPathName,outputName])

            accountBegin = accountEnd + 2
            accountEnd = pathsDoc.find(',', accountBegin)

        # handles no ',' after last account
        if len(pathsDoc) > accountBegin + 3:
            if pathsDoc.find('\n', accountBegin) != -1:
                accountPathName = pathsDoc[accountBegin : pathsDoc.find('\n', accountBegin)]
            else:
                accountPathName = pathsDoc[accountBegin : ]

            print("Account Name: ", accountPathName)
            accounts.append([accountPathName, ""])

    else:
        print("No account found")

    return accounts, savedVarsPath

def main():
    fileData = Path('./path.txt').read_text()
    accounts, savedVarsPath = getPaths(fileData)
    accountCount = len(accounts)

    for i in range(0, accountCount):
        accountPath = savedVarsPath + accounts[i][0] + "\\SavedVariables\\DungeonXPTracker.lua"
        dungeonData = Path(accountPath).read_text()
        parsedDungeonData = dungeonData[dungeonData.find("\"dungeons\"") + 17:]
        begginingDelimeter = ['[', '=']
        endingDelimeter = [']', ',']

        # get key values
        catHeadings = getCategories(parsedDungeonData, begginingDelimeter[0], endingDelimeter[0])

        # use key values to map data to keys and get DataFrame from them
        lvlingData = getData(parsedDungeonData, begginingDelimeter, endingDelimeter, catHeadings)

        # output DataFrame as csv
        accountDisplayName = 0
        if accounts[i][1] != "":
            accountDisplayName = 1

        exportPath = "./dungeon_runs/" + accounts[i][accountDisplayName] + "dungeonData.csv"
        lvlingData.to_csv(exportPath)
        print("exported:", accounts[i][accountDisplayName] + "dungeonData.csv")

    print("Parsing Complete")

if __name__ == '__main__':
    main()
