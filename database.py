import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="cinema"
)

cursor = conn.cursor()
print("Connected successfully!")