import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
f = open('init_db.txt', 'r')

conn = psycopg2.connect(database="schedule_bot",
                        user="dbadmin",
                        password="pass",
                        host="localhost",
                        port="5434")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

comm = f.readline()[:-1]

while comm != '':
    cursor.execute(comm)
    comm = f.readline()[:-1]

cursor.close()
conn.close()
