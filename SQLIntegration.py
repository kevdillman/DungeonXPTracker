# Class to implement Azure SQL Database integration

from sqlalchemy.engine import URL
from sqlalchemy import create_engine, select
from sqlalchemy import text
from sqlalchemy.orm import Session
import pyodbc
from models import Person

# load the database connection into the engine
userName = "pyClient"
password = "pythonClientPasswordStrong!!1133$$"
hostNamePort = "127.0.0.1,1337"
dbName = "dungeonxptrackerdb"

# returns current drivers for pyodbc on system
#driverNames = [x for x in pyodbc.drivers() if x.endswith(' for SQL Server')]
#print(pyodbc.drivers())

# create engine and connect to database
engine = create_engine("mssql+pyodbc://" + userName +":" + password +"@" + hostNamePort + "/" + dbName + "?driver=ODBC+Driver+17+for+SQL+Server")
engine.connect()

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

print("Select specific user\n")

session = Session(engine)
accounts = ["DEATHKRON"]
SQL_QUERY = select(Person).where(Person.pextID.in_(accounts))
for person in session.scalars(SQL_QUERY):
    print(person)
