# Parser for saved variable file from DungeonXPTracker addon
# to csv that can be used with excel
# v0.1 by PuggyBerra and Squealz
# 12 Feb 2024

import pandas as pd
import numpy as np
from datetime import date
from pathlib import Path

# delimiters
tableStartDelimiter = '{'
tableEndDelimiter = '}'
columnStartDelimiter = '['
columnEndDelimiter = ']'
dataStartDelimiter = '='
dataEndDelimiter = ','

delimeters = [tableStartDelimiter, tableEndDelimiter, columnStartDelimiter, columnEndDelimiter, dataStartDelimiter, dataEndDelimiter]


# parses a lua table for column and data values
def getTableData(tableData):
    tableStart  = tableData[:].find(delimeters[0])
    tableEnd    = tableData[:].find(delimeters[1])
    columnStart = tableData[:].find(delimeters[2])
    columnEnd   = tableData[:].find(delimeters[3])
    dataStart   = tableData[:].find(delimeters[4])
    dataEnd     = tableData[:].find(delimeters[5])

    debug = False
    def checkValidTable():

        # check if any delimiters are not found
        if  tableStart  < 0 or \
            tableEnd    < 0 or \
            columnStart < 0 or \
            columnEnd   < 0 or \
            dataStart   < 0 or \
            dataEnd     < 0:
                if debug:
                    print("delimiter not found")
                return False

        # check if the table end is found before any other delimiter
        if  tableEnd < tableStart or \
            tableEnd < columnStart or \
            tableEnd < columnEnd or \
            tableEnd < dataStart or \
            tableEnd < dataEnd:
                if debug:
                    print("table end error")
                return False

        # check if the data end delimiter is found before delimiters it must come after
        if  dataEnd < tableStart    or \
            dataEnd < columnStart   or \
            dataEnd < columnEnd     or \
            dataEnd < dataStart:
                if debug:
                    print("data end error")
                    print("dataStart:", dataStart)
                    print("dataEnd:", dataEnd)
                    print("data found:", tableData[dataStart:dataEnd])
                    print("tableData[:tableEnd + 1]", tableData[:tableEnd + 1])
                return False

        # check if the data start delimiter is found before delimiters it must come after
        if  dataStart < tableStart  or \
            dataStart < columnStart or \
            dataStart < columnEnd:
                if debug:
                    print("data start error")
                return False

        # check if the column end delimiter is found before delimiters it must come after
        if  columnEnd < tableStart  or \
            columnEnd < columnStart:
                if debug:
                    print("column end error")
                return False

        # check if the column start delimiters is found before the table start delimiter
        if columnStart < tableStart:
                if debug:
                    print("column start error")
                return False

        return True

    columns = list()
    data = list()
    inTable = checkValidTable()

    if not inTable:
        return {}, -1

    # find all the column values and the data values in the table
    while inTable:
        # add found column value to columns list
        columnValue = tableData[columnStart + 2:columnEnd - 1]
        columns.append(columnValue)

        dataValue = tableData[dataStart+2:dataEnd]
        if (len(dataValue) > 0):
            # remove " " from around data values
            if dataValue[0] == '\"':
                dataEnd = dataStart + tableData[dataStart + 3:].find('"') + 4
                dataValue = tableData[dataStart+3:dataEnd-1]

            # format time values to be parsed by power query
            if columnValue == "endingTime" or columnValue == "startTime":
                dataValue = formatDate(dataValue)

        # check if found value is default empty value
        if (dataValue == 'a'):
            dataValue = "No Data"

        data.append(dataValue)

        # find next column and data start/end points
        columnStart = tableData[dataEnd:].find(delimeters[2]) + dataEnd
        columnEnd   = tableData[dataEnd:].find(delimeters[3]) + dataEnd
        dataStart   = tableData[dataEnd:].find(delimeters[4]) + dataEnd
        dataEnd     = tableData[dataEnd + 1:].find(delimeters[5]) + dataEnd + 1

        inTable = checkValidTable()

    table = {}
    # fill dictionary with found values
    for i in range(len(columns)):
        table[columns[i]] = data[i]

    return table, tableEnd

# given a string of data, start point, and begin/end delimeters
# returns values between delimeters and delimeter locations
# returns -1 if end of file
def findNextVariable(searchData, start, delimeterOne, delimiterTwo):
    varStart = searchData[start:len(searchData)-1].find(delimeterOne)
    if varStart < 0:
        return -1, -1, ""

    varStart += start
    varEnd = searchData[varStart:len(searchData)-1].find(delimiterTwo) + varStart

    if varStart < start:
        print("error found at start:", start)
        print("varStart:", varStart)
        print("length data:", len(searchData))
        print("file state:", searchData[start-1:])
        input("press enter to continue")
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

        endOfTable = data[start:len(data)-1].find('}')
        #if endOfTable > 0:
        #print("endOfTable:", endOfTable)
        if endOfTable >= 0 and endOfTable < varStart:
            #print("found end of table")
            foundValue = -1
            return varStart, varEnd, foundValue

        foundValue = data[varStart + 2:varEnd - 1]
        return varStart, varEnd, foundValue

    #print("varStart < 0")
    return -2, -2, -2

# takes keys, data with keys and values and delimeters
# maps the data to it's key
# returns the mapped data as a DataFrame
def getDataOld(data, begginingDelimeter, endingDelimeter, categories):
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
        #print("varStart:", varStart, "varEnd:", varEnd, "foundCategory:",foundCategory)
        varStart, varEnd, foundCategory = getCategory(data, varEnd + 1, begginingDelimeter[0], endingDelimeter[0])
        #print("varStart:", varStart, "varEnd:", varEnd, "foundCategory:",foundCategory)
        #if (foundCategory == -1):
            #print("-1 before appending category data")
            #input("press enter to continue")
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


    #print("out of while loop")
    #print("varStart:", varStart, "varEnd:", varEnd, "foundData")
    #print("\ncompiledData:", compiledData, "\n")
    df = pd.DataFrame(compiledData)
    return df


# takes a file formatted as a lua table
# returns a data frame of the column headings and row values for all tables in file
def getData(data):

    tableData, endPoint = getTableData(data)
    newEndPoint = 0
    allColumns = {}
    compiledData = {}

    # find all the columns in the lua tables
    while newEndPoint >= 0:
        for column in tableData:
            if column not in allColumns:
                allColumns[column] = ""

        tableData, newEndPoint = getTableData(data[endPoint + 2:])
        endPoint += newEndPoint + 2

    # find all the data values and add them to lists under the columns
    newEndPoint = 0
    tableData, endPoint = getTableData(data)
    while newEndPoint >= 0:
        if len(compiledData) == 0:
            for column in allColumns:
                if column in tableData:
                    compiledData[column] = [tableData[column]]
                else:
                    compiledData[column] = ["No Data"]

        else:
            for column in allColumns:
                if column in tableData:
                    compiledData[column] += [tableData[column]]
                else:
                    compiledData[column] += ["No Data"]

        tableData, newEndPoint = getTableData(data[endPoint + 2:])
        endPoint += newEndPoint + 2

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
            outputBackupName = ""

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

                    # add custom name to output file name
                    outputName = pathsDoc[accountBegin : accountEnd]
                    outputBackupName = pathsDoc[accountBegin : accountEnd]
                    print("Custom File Name: ", outputName)


            # add second entry to accounts with date prefix
            if outputName != "":
                outputBackupName = date.today().strftime("%Y%m%d") + "_" + outputName
            elif accountPathName != "":
                outputBackupName = date.today().strftime("%Y%m%d") + "_" + accountPathName
            else:
                print("No accounts found")

            accounts.append([accountPathName,outputName])
            accounts.append([accountPathName,outputBackupName])

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

        # use key values to map data to keys and get DataFrame from them
        lvlingData = getData(dungeonData[dungeonData.find("\"dungeons\"") + 15:])

        # output DataFrame as csv
        accountDisplayName = 0
        if accounts[i][1] != "":
            accountDisplayName = 1

        exportPath = "./dungeon_runs/" + accounts[i][accountDisplayName] + "_dungeonData.csv"
        lvlingData.to_csv(exportPath)
        exportPath = "./dungeon_runs/+"
        print("exported:", accounts[i][accountDisplayName] + "_dungeonData.csv")

    print("Parsing Complete")

if __name__ == '__main__':
    main()
