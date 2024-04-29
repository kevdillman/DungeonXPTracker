# Class to implement Azure SQL Database integration

from sqlalchemy.engine import URL
from sqlalchemy import create_engine, select
from sqlalchemy import text
from sqlalchemy.orm import Session
import pyodbc
from models import Base, Person, Account, Character, Dungeon, DungeonRun, LevelReference, CharacterLevelHistory

# load the database connection into the engine
userName = "pyClient"
password = "pythonClientPasswordStrong!!1133$$"
hostNamePort = "192.168.1.204,1337"
dbName = "dungeonxptrackerdb"

# returns current drivers for pyodbc on system
#driverNames = [x for x in pyodbc.drivers() if x.endswith(' for SQL Server')]
#print(pyodbc.drivers())

# create engine and connect to database
engine = create_engine("mssql+pyodbc://" + userName +":" + password +"@" + hostNamePort + "/" + dbName + "?driver=ODBC+Driver+17+for+SQL+Server", echo=False)
engine.connect()
session = Session(engine)

def addCharacters(account, parsedData):
    uniqueCharNames = []
    uniqueChars = []
    character = {
        'name': "",
        'realm': "Zul'jin",
        'faction': "Horde",
        'race': "",
        'guild': "The Fire Heals You"
    }
    #print("length parsed data:", len(parsedData))
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

    addAllChars = False
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

def printCharacters():
    counter = 0
    for char in session.scalars(select(Character)):
        if counter == 0:
            print("\n\n")
        counter += 1
        print(char)
    print("\n\n")


printCharacters()
# creates tables from models file in database
#Base.metadata.create_all(engine)

# creates connection to pyodbc database
#connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};ADDRESS={hostNamePort};UID={userName};PWD={password};DATABASE={dbName};TrustServerCertificate=YES'
#conn = pyodbc.connect(connectionString)

# storing sql query
SQL_QUERY = """
SELECT *
FROM INFORMATION_SCHEMA.COLUMNS
"""

#cursor = conn.cursor()
#cursor.execute(SQL_QUERY)

kevinCharacter = Character(
        cNAME = "Lilmortade",
        cREALM = "Zul'jin",
        cFACTION = "Horde",
        cRACE = "Goblin",
        cGUILD = "The Fire Heals You"
)

kevinAccounts = [
    Account(
        wowACCOUNT = "DEATHKRON",
        bnetNAME = "DEATHKRON"
    )
]

kevin = Person(
    firstNAME = "Kevin",
    lastNAME = "Dillman",
    email = "kevdillman@gmail.com",
    accounts = kevinAccounts
)

writeData = False
if writeData:
    # adds a Person and their account
    with Session(engine) as session:
        session.add(kevinCharacter)
        session.commit()

    # adds a character to an account
    user = session.scalars(select(Account).where(Account.wowACCOUNT == "DEATHKRON")).one()
    user.characters.append(kevinCharacter)
    session.commit()


#user = session.scalars(SQL_QUERY).one()
#print(user)
#select(Person).where(Account.wowACCOUNT == "DEATHKRON")
#for person in session.scalars(select(Character)):
    #print(person)


""" with engine.connect() as connection:
    records = connection.execute(text(SQL_QUERY))
    for r in records:
        print(r) """

#print("Select specific user\n")

#session = Session(engine)
#accounts = ["DEATHKRON"]
"""
SQL_QUERY = select(Person).where(Person.pextID == "DEATHKRON")
user = session.scalars(SQL_QUERY).one()
print("user:", user)
print("current middle name: ", user.middleNAME)
user.middleNAME = "C"
print("update name:", user.middleNAME)
session.commit() """
