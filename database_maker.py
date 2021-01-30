import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS players
             (discord VARCHAR PRIMARY KEY, 
             player VARCHAR NOT NULL, 
             character_name VARCHAR NOT NULL, 
             role VARCHAR NOT NULL, 
             faction VARCHAR NOT NULL, 
             favours INTEGER NOT NULL)''')

c.execute('''CREATE TABLE IF NOT EXISTS bugs
             (timeset VARCHAR PRIMARY KEY, 
             setter VARCHAR NOT NULL,
             settee VARCHAR NOT NULL)''')

c.execute('''CREATE TABLE IF NOT EXISTS transactions
             (timeset VARCHAR PRIMARY KEY, 
             payer VARCHAR NOT NULL,
             payee VARCHAR NOT NULL,
             favournum INTEGER NOT NULL)''')

c.execute('''CREATE TABLE IF NOT EXISTS playerIDs
             (identifier VARCHAR PRIMARY KEY, 
             userID VARCHAR NOT NULL)''')


