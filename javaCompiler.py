"""
Python driver file for developing java parser that will integrate into
XPTracker_Parser_to_CSV.py to replace python file parser
"""

import sys
import subprocess
from pathlib import Path
from XPTracker_Parser_to_CSV import getPaths

if __name__ == '__main__':
    javac = "C:\\Users\\kevdi\\Documents\\Java\\jdk-21.0.9\\bin\\javac.exe"
    fileData = Path('./path.txt').read_text()
    accounts, savedVarsPath = getPaths(fileData)

    accountPath = savedVarsPath + accounts[0][0] + "\\SavedVariables\\DungeonXPTracker.lua"

    if sys.argv[1]:
        fName = sys.argv[1]
        className = fName[: len(fName) - 5]

        print(f"provided filename: {fName}")
        cmd = [javac, fName]

        print("compiling java file")
        subprocess.run(cmd, check=True)
        print(f"compiling {fName} complete")

        java  = "C:\\Users\\kevdi\\Documents\\Java\\jdk-21.0.9\\bin\\java.exe"
        cmd = [java, className, accountPath]

        print(f"running java class {className}")
        subprocess.run(cmd, check=True)

        #result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        #print(f"result from java file:\n{result.stdout}")

        print("java file execution complete")
    else:
        print("No filename provided")
