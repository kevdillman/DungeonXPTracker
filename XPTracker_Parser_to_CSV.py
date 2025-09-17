# Parser for saved variable file from DungeonXPTracker addon
# to csv that can be used with excel
# v0.1 by PuggyBerra and Squealz
# 12 Feb 2024

import pandas as pd
import numpy as np
from datetime import date
from pathlib import Path
from savedVariableParser import getData
print("loading SQLIntegration")
from SQLIntegration import addData
print("SQLIntegration loaded")

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

if __name__ == '__main__':
    # read the path to the saved variables file and the account
    # folders to parse, as well as display names for the account if desired
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

        # add data to SQL Database
        if accounts[i][accountDisplayName] == "DEATHKRON":
            addData(accounts[i][accountDisplayName], lvlingData)

    print("Parsing Complete")
