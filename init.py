import mysql.connector,os
from tkinter import messagebox
import pickle

def createmain(username,password):
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password,
        database="ExpenseTracker"
    )

    mycursor = db.cursor()

    mycursor.execute("SHOW TABLES")
    data = mycursor.fetchall()
    if ('startup',) not in data:
        mycursor.execute("CREATE TABLE IF NOT EXISTS main(ExpenseName varchar(50), Amount int UNSIGNED)")
        mycursor.execute("CREATE TABLE IF NOT EXISTS startup(ID int PRIMARY KEY NOT NULL AUTO_INCREMENT)")
        with open("details.dat",'wb') as file:
            data = (username,password)
            pickle.dump(data,file)
        os.makedirs(r"information")
    else:
        pass


def databaseconn(username,password):

    try:
        db = mysql.connector.connect(
            host="localhost",
            user=username,
            passwd=password
        )
        mycursor = db.cursor()
        mycursor.execute("CREATE DATABASE IF NOT EXISTS ExpenseTracker")
        createmain(username, password)
        print("Successfully Initialized")
        return True


    except :
        messagebox.showerror("Access Denied","Incorrect UserName or Password")

