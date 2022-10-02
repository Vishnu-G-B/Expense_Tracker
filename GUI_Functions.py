import mysql.connector,traceback,datetime,os
from datetime import date,timedelta
import pandas as pd
from tkinter import messagebox
from dateutil import relativedelta

def newtable(*args):
    db = mysql.connector.connect(
        host="localhost",
        user=args[0],
        passwd=args[1],
        database="ExpenseTracker"
    )
    mycursor = db.cursor()


    tblname = args[2]
    mycursor.execute("CREATE TABLE `{}`(ExpenseName varchar(50) DEFAULT 'No Description',Amount int UNSIGNED,`Expense made on` datetime default now(), ID int PRIMARY KEY NOT NULL AUTO_INCREMENT)".format(tblname))

def newmainrow(*args):
    db = mysql.connector.connect(
        host="localhost",
        user=args[0],
        passwd=args[1],
        database="ExpenseTracker"
    )
    mycursor = db.cursor()
    name = args[2]
    mycursor.execute("INSERT INTO main values(%s,0)",(name,))
    db.commit()
    newtable(args[0],args[1],name)
    print("new main row successfully created")

def insert(*args):
    db = mysql.connector.connect(
        host="localhost",
        user=args[0],
        passwd=args[1],
        database="ExpenseTracker"
        )
    mycursor = db.cursor()

    #inserting into the desired table
    temp = ""

    try:
        tblname = str(args[2])
        name = str(args[3])
        amount = int(args[4])
        if name in ("","Expense Name"," ",None,"Expense Description"):
            query = f"INSERT INTO `{tblname}`(Amount) Values(%s)"
            mycursor.execute(query, (amount,))

            db.commit()
            print("Record successfully added")

        else:
            query = f"INSERT INTO `{tblname}`(ExpenseName,Amount) VALUES(%s,%s)"

            mycursor.execute(query,(name,amount))
            db.commit()
            print("Record successfully added")

        # updating the main table
        query = "Select SUM(Amount) from `{}`".format(tblname)
        mycursor.execute(query)
        record = mycursor.fetchone()
        for x in record:
            temp = x

        query = "UPDATE main SET Amount = {} WHERE ExpenseName = '{}'".format(temp, tblname)
        mycursor.execute(query)
        db.commit()

        messagebox.showinfo("Success!","Item Successfully Added!")

    except ValueError:
        messagebox.showerror("Invalid Value","Please Enter A Valid Amount in Numbers")

    except mysql.connector.errors.ProgrammingError:
        messagebox.showerror("Invalid Value","Please Enter a Valid Table/Category Name")

    except Exception:
        traceback.print_exc()

def view(*args):
    df2 = pd.DataFrame(columns=["ExpenseName", "Amount"])

    db = mysql.connector.connect(
        host="localhost",
        user=args[0],
        passwd=args[1],
        database="ExpenseTracker"
    )
    mycursor = db.cursor(buffered=True)
    name = args[2]
    lenargs = len(args) - 2

    mainlst = []
    emptylst = []
    templst1 = []
    i, x = 0, 0

    if lenargs == 1 and name == "main":
        mycursor.execute("SELECT * FROM main")
        result = mycursor.fetchall()

        mycursor.execute("SELECT SUM(Amount) FROM main")
        temp2 = ["Total Amount:", mycursor.fetchone()[0]]
        result.append(temp2)
        df = pd.read_sql(f"SELECT ExpenseName,Amount FROM `{name}`", db)
        return result, df



    elif lenargs == 2 and name == "main":
        Ndays = int(args[3])
        days_before = str((date.today() - timedelta(days=Ndays)).isoformat())
        dateNtime = days_before + " 00:00:00"

        mycursor.execute("SHOW TABlES")
        lst1 = mycursor.fetchall()
        lst1.remove(('main',))
        lst1.remove(('startup',))

        for ele in lst1:
            tablename = ele[0]
            mycursor.execute(
                f"SELECT ExpenseName,Amount,`Expense made on` FROM `{tablename}` WHERE `Expense made on`>'{dateNtime}' ")
            result = mycursor.fetchall()

            if result != emptylst:
                for ele2 in result:
                    ele2 = list(ele2)
                    ele2.append(tablename)
                    templst1.append(ele2)

            mycursor.execute(f"SELECT SUM(Amount) FROM `{tablename}` WHERE `Expense made on`>'{dateNtime}' ")
            try:
                x += mycursor.fetchone()[0]
            except:
                x += 0

        mainlst.extend(templst1)
        temp2 = ["Total amount:", x, "-", "-"]
        mainlst.append(temp2)

        for ele3 in lst1:
            tablename = ele3[0]
            mycursor.execute(f"SELECT ExpenseName,Amount FROM `{tablename}` WHERE `Expense made on` > '{dateNtime}' ")
            data = mycursor.fetchall()
            for row in data:
                if row[0] == None:
                    tempdf = list(row)
                    tempdf[0] = "No Description"
                    df2.loc[i] = tempdf
                else:
                    df2.loc[i] = list(row)
                i += 1

        return mainlst, df2


    else:
        try:
            name = (args[2])
            Ndays = int((args[3]))

            days_before = str((date.today() - timedelta(days=Ndays)).isoformat())
            dateNtime = days_before + " 00:00:00"

            mycursor.execute(
                f"SELECT ID,ExpenseName,Amount,`Expense made on` FROM `{name}` WHERE `Expense made on`>'{dateNtime}' ")
            result = mycursor.fetchall()

            mycursor.execute(f"SELECT SUM(Amount) FROM `{name}` WHERE `Expense made on`>'{dateNtime}' ")
            temp2 = ["-", "Total amount:", mycursor.fetchone()[0], "-"]
            result.append(temp2)
            df = pd.read_sql(f"SELECT ExpenseName,Amount FROM `{name}` WHERE `Expense made on`>'{dateNtime}' ", db)
            return result, df

        except mysql.connector.errors.ProgrammingError:
            print("""Table Does Not Exist 
    PLease enter a Valid Table Name""")



        except:
            name = (args[2])
            if name == "Total Amount":
                messagebox.showwarning("Table Does Not Exist","Can't View This Item")

            else:
                mycursor.execute(f"Select ID,ExpenseName,Amount,`Expense made on` from `{name}` ")
                result = mycursor.fetchall()

                mycursor.execute(f"SELECT SUM(Amount) FROM `{name}`")
                temp2 = ["-", "Total Amount:", mycursor.fetchone()[0], "-"]
                result.append(temp2)
                df = pd.read_sql(f"SELECT ExpenseName,Amount FROM `{name}`", db)
                return result, df

def delete(*args):
    db = mysql.connector.connect(
        host="localhost",
        user=args[0],
        passwd=args[1],
        database="ExpenseTracker"
    )
    mycursor = db.cursor()

    tblname = args[2]
    sno = int(args[3])
    temp = ''

    mycursor.execute(f"DELETE FROM `{tblname}` WHERE ID = {sno}")
    db.commit()
    print("Record successfully deleted")


    query = f"Select SUM(Amount) from {tblname}"
    mycursor.execute(query)
    record = mycursor.fetchone()
    for x in record:
        temp = x

    query = """UPDATE main SET Amount = %s WHERE ExpenseName = %s"""
    mycursor.execute(query,(temp, tblname))
    db.commit()

def DeleteAll(*args):
    db = mysql.connector.connect(
        host="localhost",
        user=args[0],
        passwd=args[1],
        database="ExpenseTracker"
    )
    mycursor = db.cursor()

    mycursor.execute("SELECT ExpenseName FROM main ")
    lst1 = mycursor.fetchall()
    for x in lst1:
        temp = x[0]
        mycursor.execute(f"DELETE FROM {temp}")
        mycursor.execute(f"UPDATE main SET Amount = 0 WHERE ExpenseName = '{temp}' ")
        mycursor.execute(f"ALTER TABLE {temp} AUTO_INCREMENT = 1")
    db.commit()

def deletemain(*args):
    db = mysql.connector.connect(
        host= "localhost",
        user= args[0],
        passwd= args[1],
        database= "ExpenseTracker"
    )
    mycursor = db.cursor()

    name = args[2]
    mycursor.execute(f"DELETE FROM main WHERE ExpenseName = '{name}'")
    db.commit()

    try:
        mycursor.execute(f"DROP TABLE `{name}`")
        print("Row successfully deleted.")
        messagebox.showinfo("Successfully Excecuted", "Category Successfully Deleted")
    except:
        messagebox.showerror("Not Found","NO Such Category Exists!")

def recursive_insert(username,passwd,amt,interval,date,tablename,expensename = "No Description"):
    db = mysql.connector.connect(
        host= "localhost",
        user= username,
        passwd= passwd,
        database= "ExpenseTracker"
    )
    mycursor = db.cursor()

    if amt == 'Amount':
        messagebox.showerror("Incorrect Data","Please Enter a Valid Amount in Numbers")
        return

    templst = []
    templst.append(datetime.date.today())
    temp_date = datetime.datetime.strptime(date, '%m/%d/%y')
    nextmonth = temp_date + relativedelta.relativedelta(months=interval)
    templst.append([expensename, amt, date, nextmonth, 0])
    for i in range(1, 120):
        nextmonth = nextmonth + relativedelta.relativedelta(months=interval)
        templst.append([expensename, amt, date, nextmonth, 0])

    mycursor.execute(f'SELECT MAX(ID) FROM {tablename}')

    if os.path.isfile(r"information\recurring_expenses.csv"):
        df_recur = pd.read_csv(r"information\recurring_expenses.csv")
        templst.pop(0)
        try:
            df_recur[f"{tablename}, {mycursor.fetchone()[0] + 1}"] = templst
        except TypeError:
            df_recur[f"{tablename}, {1}"] = templst #FOR FIRST TIME INSERTING INTO A TABLE WITH NO OTHER VALUES
        df_recur.to_csv(r"information\recurring_expenses.csv",index=False)

    else:
        df_recur = pd.DataFrame()
        try:
            df_recur[f"{tablename}, {mycursor.fetchone()[0] + 1}"] = templst
        except TypeError:
            df_recur[f"{tablename}, {1}"] = templst #FOR FIRST TIME INSERTING INTO A TABLE WITH NO OTHER VALUES
        df_recur.drop([0], inplace=True)
        df_recur.to_csv(r"information\recurring_expenses.csv",index=False)


def recursive_read(username, passwd):
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=passwd,
        database="ExpenseTracker"
    )
    mycursor = db.cursor()
    temp = ""

    try:
        df2 = pd.read_csv(r"information\recurring_expenses.csv")

    except FileNotFoundError:
        print("Setup Complete")
        return

    for j in range(len(df2.columns)):
        column_names = df2.columns[j].split(",")

        headername = column_names[0]
        ID = int(column_names[1])

        for i in range(len(df2.index) - 1):
            check = df2.iloc[i,j].split(',')

            if check[6][1] == "0":

                # Converting the date from CSV to MySQL usable format
                temp_date = (str(check[3] + "," + check[4] + "," + check[5]).replace("datetime.date", "")).strip()
                date_list = temp_date.split("(")
                date_list = date_list[1].split(")")
                test_date = date_list[0].replace(" ", "")
                test_date = test_date.replace(",", "-")
                test_date = datetime.datetime.strptime(test_date, '%Y-%m-%d')

                if test_date < datetime.datetime.today():
                    tablename = ((list(df2.columns)[j]).split())[0].replace(",", "")
                    amount = check[1]

                    expensename = check[0].replace("'", "")
                    expensename = expensename.replace("[", "")

                    mycursor.execute(f"INSERT INTO {tablename}(expensename,amount,`expense made on`) VALUES('{expensename}', {amount}, '{test_date.date()}')")

                    query = "Select SUM(Amount) from `{}`".format(tablename)
                    mycursor.execute(query)
                    record = mycursor.fetchone()
                    for x in record:
                        temp = x

                    query = "UPDATE main SET Amount = {} WHERE ExpenseName = '{}'".format(temp, tablename)
                    mycursor.execute(query)

                    db.commit()

                    check[6] = check[6].replace("0","1")

                    df2.loc[i,f"{headername}, {ID}"] = check

                    df2[f"{headername}, {ID}"] = df2

                    df2.to_csv(r"information\recurring_expenses.csv",index=False)



    print("Setup Complete")