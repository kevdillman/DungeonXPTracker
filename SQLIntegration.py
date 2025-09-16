# Class to implement Azure SQL Database integration

from pathlib import Path
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, select, func
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
import pyodbc
from models import Base, Person, Account, Character, Dungeon, DungeonRun, LevelReference, CharacterLevelHistory

# returns current drivers for pyodbc on system
#driverNames = [x for x in pyodbc.drivers() if x.endswith(' for SQL Server')]
#print(pyodbc.drivers())

def getServerInfo(fileData = Path('./sqlServerInfo.txt').read_text()):
    # reads the SQL server connection information from sqlServerInfo.txt file

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
    person = linkAccountToPerson(accountName, session)

    if not person:
        print("No Person linked to account")
        return
    else:
        print("Account linked to Person: ", person)

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

def linkAccountToPerson(accountName, session: Session):
    # finds the person record associated with the given accountName
    person = session.scalars(select(Person).where(Person.accounts.any(Account.wowACCOUNT == accountName))).all()

    # if there is no matching person record allow one to be created
    if not person:
        print(f"no person associated with account \"{accountName}\" found")
        linkUser = input("Would you like to link a person to this account, Y/N: ")
        if linkUser != "Y":
            return False

        maxPID = printAllPersons(session)
        searchUserID = input("ID of user you want to associate account with or enter 'C' to create a new user: ")
        if searchUserID == 'C':
            manualAddPerson(session)
        elif (searchUserID.isdecimal()) and (int(searchUserID) >= 0 and int(searchUserID) <= maxPID):
            person = session.scalars(select(Person).where(Person.pID == searchUserID)).first()
            #for user in person:
            print("linking to: ", person)

            return person

        if not person:
            print("No user found with given ID")
            return False
    else:
        return person

def addCharacters(account, parsedData, session: Session):
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

def manualAddPerson(session: Session):
    #session = connectDatabase()
    fName = input("Person first name: ")
    lName = input("Person last name: ")
    emailAddress = input("Person email: ")

    person = Person(
        firstNAME=fName,
        lastNAME=lName,
        email=emailAddress
    )
    session.add(person)
    session.flush()

def manualAddAccount():
    session = connectDatabase()
    accountName = input("Account name: ")
    bName = input("bnet name: ")

    SQL_QUERY = select(Person)
    user = session.scalars(SQL_QUERY)
    for users in user:
        print(users)

    personNum = input("Which pID should be associated to this account: ")

    person = session.scalars(select(Person).where(Person.pID == personNum)).one()

    account = Account(
        wowACCOUNT=accountName,
        bnetNAME=bName,
        personID=person.pID
    )
    session.add(account)
    session.commit()

def searchUsers(session: Session):
    searchFirstName = input("First name of user you want to search for: ")
    searchLastName = input("Last name of the user you want to search for: ")
    users = session.scalars(select(Person).where(Person.firstNAME == searchFirstName).where(Person.lastNAME == searchLastName)).all()

    if not users:
        print("no results found")
    else:
        for i, user in enumerate(users, start=1):
            print(f"{i}. {user.firstNAME} {user.lastNAME} (id={user.pID})")
            print("user:", user)

def printAllPersons(session: Session):
    SQL_QUERY = select(Person)
    users = session.scalars(SQL_QUERY)
    print("\nAll users:")
    counter = 0
    for user in users:
        print(user)
        counter += 1

    #print("Number of users: ", counter)
    return counter

def printAllAccounts(session: Session):
    SQL_QUERY = select(Account)
    accounts = session.scalars(SQL_QUERY)
    print("\nAll accounts:")
    counter = 0
    for account in accounts:
        print(account)
        counter += 1

    #print("Number of accounts: ", counter)

def printCharacters(session: Session):
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
    session = connectDatabase()
    person = linkAccountToPerson("testAccount", session)
    printAllPersons(session)
    printAllAccounts(session)
    session.close()
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
