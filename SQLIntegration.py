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
engine = create_engine("mssql+pyodbc://" + userName +":" + password +"@" + hostNamePort + "/" + dbName + "?driver=ODBC+Driver+17+for+SQL+Server", echo=True)
engine.connect()


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


""" with Session(engine) as session:
    testPerson = Person(
        pextID = "Puggyberra",
        firstNAME = "test",
        lastNAME = "ing",
        email = "test@testing.com"
    )
    session.add(testPerson)
    session.commit()

user = session.scalars(SQL_QUERY).one()
print(user)
for person in session.scalars(select(Person)):
    print(person) """
