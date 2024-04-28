# Class to implement Azure SQL Database integration

from sqlalchemy.engine import URL
import pyodbc
import models

# load the database connection into the engine
userName = "pyClient"
password = "pythonClientPasswordStrong!!1133$$"
hostNamePort = "127.0.0.1,1337"
dbName = "dungeonxptrackerdb"

# returns current drivers for pyodbc on system
#driverNames = [x for x in pyodbc.drivers() if x.endswith(' for SQL Server')]
#print(pyodbc.drivers())

# non-working code to create SQLAlchemy engine
#engine = create_engine("mssql+pyodbc://" + userName +":" + password + hostNamePort + "/" + dbName + "?driver=ODBC+Driver+17+for+SQL+Server")

# creates connection to pyodbc database 
connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};ADDRESS={hostNamePort};UID={userName};PWD={password};DATABASE={dbName};TrustServerCertificate=YES'
conn = pyodbc.connect(connectionString)


# storing sql query
SQL_QUERY = """
SELECT *
FROM INFORMATION_SCHEMA.COLUMNS
"""

cursor = conn.cursor()
cursor.execute(SQL_QUERY)

records = cursor.fetchall()
#for r in records:
    #print(r)
