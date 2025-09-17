# saved variables parser

import pandas as pd

# takes a file formatted as a lua table
# returns a data frame of the column headings and row values for all tables in file
def getData(data):

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

    # takes a date time input
    # reformats date time to be read by excel and returns it
    def formatDate(rawDate):
        yearFromRaw = "20" + rawDate[6:8]
        monthFromRaw = rawDate[3:5]
        dayFromRaw = rawDate[0:2]

        formattedDate = monthFromRaw + "/" + dayFromRaw + "/" + yearFromRaw + rawDate[8:]

        return formattedDate

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
