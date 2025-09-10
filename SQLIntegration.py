# Class to implement Azure SQL Database integration

from pathlib import Path
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, select
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
import pyodbc
from models import Base, Person, Account, Character, Dungeon, DungeonRun, LevelReference, CharacterLevelHistory

# returns current drivers for pyodbc on system
#driverNames = [x for x in pyodbc.drivers() if x.endswith(' for SQL Server')]
#print(pyodbc.drivers())

# gets the account name and path to account's saved variables
def getServerInfo(fileData = Path('./sqlServerInfo.txt').read_text()):
    userName = "username"
    password = "userpassword"
    hostName = "serverIP"
    hostPort = "port"
    dbName = "databaseName"

    # make sure required fields are in credential file
    fields = {"userName": "user",
              "password": "pass",
              "hostName": "host",
              "hostPort": "port",
              "dbName": "db",
              ",": ""}

    for field in fields:
        if fileData.find(field) == -1:
            print(field, " missing in sqlServerInfo.txt")
            return 1

    for field in fields:
        # end loop after last field is filled
        if field != ",":
            # find field label
            fieldBegin = fileData.find(field) + 2
            fieldEnd = fileData.find(',', fieldBegin)

            # get field data
            fieldBegin = fieldEnd + 2
            fieldEnd = fileData.find(',', fieldBegin)
            nextComma = fileData.find(',', fieldBegin)
            nextNewLine = fileData.find('\n', fieldBegin)

            # check if field data line ends in , or newline
            if len(fileData[fieldBegin:nextNewLine]) < len(fileData[fieldBegin:nextComma]):
                fieldEnd = fileData.find('\n', fieldBegin)

            if fieldEnd == -1:
                fieldEnd = fileData.find('\n', fieldBegin)
            if fieldEnd == -1:
                print("invalid format for data field:", field)
                return 1

            # add field data to credential dictionary
            fields[field] = fileData[fieldBegin:fieldEnd]

    return fields

def connectDatabase():
    # load the database connection info
    serverCredentials = getServerInfo()
    userName = serverCredentials["userName"]
    password = serverCredentials["password"]
    hostName = serverCredentials["hostName"]
    hostPort = serverCredentials["hostPort"]
    dbName =   serverCredentials["dbName"]

    # create engine and connect to database
    print("creating engine")
    engine = create_engine("mssql+pyodbc://" + userName +":" + password +"@" + hostName + "," + hostPort + "/" + dbName + "?driver=ODBC+Driver+17+for+SQL+Server", echo=False)
    print("connecting to db server")
    engine.connect()
    print("creating session")
    session = Session(engine)
    print("session created")
    return session

def addData(accountName: str, parsedData):
    """
    Ensure account exists, then add any new characters
    (and later dungeon runs, levels, etc.).

    Args:
        accountName (str): Account name used to link characters.
        parsedData (pd.DataFrame): Parsed data from CSV with headings like:
            ['endingTime','endingMoney','startLVL','startRest','endingXP',
             'startMoney','dungeon','charRace','startXP','charName',
             'endingRest','startTime','charRole','endingLVL']
    """
    session = connectDatabase()

    # Step 1: find person
    try:
        person = session.scalars(
            select(Person).where(Person.firstNAME == "Kevin")  # adjust lookup!
        ).one()
    except NoResultFound:
        person = Person(
            # fill person table
                firstNAME="",
                lastNAME="",
                email=""
        )
        session.add(person)
        session.flush()  # assigns person.pID

    # Step 2: find or create account
    try:
        account = session.scalars(
            select(Account).where(Account.wowACCOUNT == accountName)
        ).one()
    except NoResultFound:
        account = Account(
            wowACCOUNT=accountName,
            bnetNAME=accountName,
            personID=person.pID
        )
        session.add(account)
        session.flush()

    # --- 3. Add any new characters for this account ---
    addCharacters(account, parsedData, session)

    # --- 4. TODO: Add dungeon run or level history handling here ---
    # This is where you’ll later expand `addData`

def addCharacters(account, parsedData, session):
    uniqueCharNames = []
    uniqueChars = []
    character = {
        'name': "",
        'realm': "Zul'jin",
        'faction': "Horde",
        'race': "",
        'guild': "The Fire Heals You"
    }
    print("length parsed data:", len(parsedData))
    for i in range(len(parsedData)):
        if parsedData['charName'].iloc[i] not in uniqueCharNames:

            uniqueCharNames.append(parsedData['charName'].iloc[i])

            character['name'] = parsedData['charName'].iloc[i]
            character['race'] = parsedData['charRace'].iloc[i]
            uniqueChars.append(character)

            character = {
                'name': "",
                'realm': "Zul'jin",
                'faction': "Horde",
                'race': "",
                'guild': "The Fire Heals You"
            }

    charsInDatabase = []
    for char in session.scalars(select(Character)):
        charsInDatabase.append(char.cNAME)

    addAllChars = True
    if addAllChars:
        for i in range(len(uniqueChars)):
            if uniqueChars[i]['name'] not in charsInDatabase:
                newChar = Character(
                    cNAME = uniqueChars[i]['name'],
                    cREALM = uniqueChars[i]['realm'],
                    cFACTION = uniqueChars[i]['faction'],
                    cRACE = uniqueChars[i]['race'],
                    cGUILD = uniqueChars[i]['guild']
                )

                user = session.scalars(select(Account).where(Account.wowACCOUNT == "DEATHKRON")).one()
                user.characters.append(newChar)
                session.commit()

    charsInDatabase = []
    for char in session.scalars(select(Character)):
        charsInDatabase.append(char.cNAME)

    print("num unique chars found:", len(uniqueChars))
    print("Chars in database:", charsInDatabase)

def printCharacters(session):
    counter = 0
    for char in session.scalars(select(Character)):
        if counter == 0:
            print("\n\n")
        counter += 1
        print(char)
    print("\n\n")

if __name__ == "__main__":
    # Only runs if you call python SQLIntegration.py directly
    #seedKevin()
    print(getServerInfo())
    pass

#printCharacters()

# creates connection to pyodbc database
#connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};ADDRESS={hostNamePort};UID={userName};PWD={password};DATABASE={dbName};TrustServerCertificate=YES'
#conn = pyodbc.connect(connectionString)

#cursor = conn.cursor()
#cursor.execute(SQL_QUERY)

"""
SQL_QUERY = select(Person).where(Person.pextID == "DEATHKRON")
user = session.scalars(SQL_QUERY).one()
print("user:", user)
print("current middle name: ", user.middleNAME)
user.middleNAME = "C"
print("update name:", user.middleNAME)
session.commit() """
