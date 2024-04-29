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
    character = {
        'name': "",
        'realm': "Zul'jin",
        'faction': "Horde",
        'race': "",
        'guild': "The Fire Heals You"
    }

    for i in range(len(parsedData)):
        if parsedData['charName'].iloc[i] not in uniqueCharNames:
            character['name'] = parsedData['charName'].iloc[i]
            character['race'] = parsedData['charRace'].iloc[i]
            uniqueCharNames.append(character)

    charsInDatabase = []
    for char in session.scalars(select(Character)):
        charsInDatabase.append(char.cNAME)

    if uniqueCharNames[0]['name'] not in charsInDatabase:
        newChar = Character(
            cNAME = uniqueCharNames[0]['name'],
            cREALM = uniqueCharNames[0]['realm'],
            cFACTION = uniqueCharNames[0]['faction'],
            cRACE = uniqueCharNames[0]['race'],
            cGUILD = uniqueCharNames[0]['guild']
        )

        user = session.scalars(select(Account).where(Account.wowACCOUNT == "DEATHKRON")).one()
        user.characters.append(newChar)
        session.commit()

    charsInDatabase = []
    for char in session.scalars(select(Character)):
        charsInDatabase.append(char.cNAME)

    print("unique char names: ",uniqueCharNames[0])
    print("Chars in database:", charsInDatabase)



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
