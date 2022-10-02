from tkinter import *
from ttkbootstrap import Style
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from GUI_Functions import *
from tkinter import messagebox
from ctypes import windll
from PIL import Image, ImageTk
import init,os,pickle
import tkinter as tk
from tkcalendar import *


style = Style(theme="darkly")
root = style.master
root.geometry("")
windll.shcore.SetProcessDpiAwareness(1)


def DeleteAllCommand():
    answer = messagebox.askyesno(
        "WARNING!", "This will delete ALL entries in EVERY category, do you wish to proceed?")
    if answer == 1:
        DeleteAll(Username, Password)
        messagebox.showinfo("Successful", "All data successfully deleted")


def AutoAddItem(kintercall):
    row_str = ""
    rowselection = listbox2.curselection()
    for i in rowselection:
        row_str = row_str + listbox2.get(i)
    row_list = row_str.split()
    item_no = row_list[0]

    expense_no_entry.delete(0, END)
    expense_no_entry.insert(0, item_no)
    DelteCommand()


def DeleteView(kintercall):  # Accounting for tkinter bind function argument
    global listbox2
    i = 1

    # Getting the table name from main listbox
    row_str = ""
    rowselection = listbox1.curselection()
    for i in rowselection:
        row_str = row_str + listbox1.get(i)
    row_list = row_str.split(':')
    table_name = row_list[0].strip()
    if table_name == "Total Amount":
        messagebox.showwarning("Table Does Not Exist", "Can't View This Item")
    else:
        table_list_items, df = view(Username, Password, table_name)

        listbox1.delete(0, END)
        listbox1.grid_forget()

        listbox2 = Listbox(delete_window, width=89, font=("Garamond bold", 15))
        for id, expensename, amount, date in table_list_items:
            list_items = f"{id}  :  {expensename}  :  ₹{amount}  :  {date}"
            listbox2.insert(i, list_items)
            i += 1

        listbox2.bind('<Double-1>', AutoAddItem)
        listbox2.grid(row=3, column=0, columnspan=2)

        table_name_entry.delete(0, END)
        table_name_entry.insert(0, f"{table_name}")

        home_button["state"] = NORMAL


def DeleteHome():
    updateListBoxes()
    listbox2.grid_forget()
    listbox1.grid(row=3, column=0, columnspan=2)
    table_name_entry.delete(0, END)
    expense_no_entry.delete(0, END)
    home_button["state"] = DISABLED


def DelteCommand():
    if expense_no_entry.get() == "-":
        messagebox.showerror("CANNOT DELETE", "Cannot Delete this Item")
    else:
        answer = messagebox.askyesno(
            "Confirmation", "Are you Sure you wish to delete this item??")
        if answer == 1:
            i = 1
            delete(Username, Password, table_name_entry.get(), expense_no_entry.get())
            listbox2.delete(0, END)
            table_list_items, df = view(Username, Password, table_name_entry.get())
            for id, expensename, amount, date in table_list_items:
                list_items = f"{id}  :  {expensename}  :  ₹{amount}  :  {date}"
                listbox2.insert(i, list_items)
                i += 1
            listbox2.grid(row=3, column=0, columnspan=2)
            updateListBoxes()


def MainDelete():
    i = 1
    global listbox1, view_button, home_button, table_name_entry, expense_no_entry, delete_window
    delete_window = Toplevel()
    table_name = Label(delete_window, text="Enter the Table Name  :", font=("Garamond bold", 20))
    expense_no = Label(delete_window, text="Enter the Expense No. :", font=("Garamond bold", 20))
    table_name_entry = Entry(delete_window, width=55)
    expense_no_entry = Entry(delete_window, width=55)
    ok_button = Button(delete_window, text="OK", command=DelteCommand,height=2, width=32, font=("Garamond bold", 15))
    cancel_button = Button(delete_window, text="CANCEL", command=delete_window.destroy,height=2, width=32, font=("Garamond bold", 15))
    delall_button = Button(delete_window, text="DELETE ALL",command=DeleteAllCommand, height=2, width=32, font=("Garamond bold", 15))
    home_button = Button(delete_window, text="HOME", command=DeleteHome,height=2, width=32, font=("Garamond bold", 15), state=DISABLED)
    listbox1 = Listbox(delete_window, width=89, font=("Garamond bold", 15))

    updateListBoxes()

    listbox1.bind('<Double-1>', DeleteView)

    table_name.grid(row=0, column=0, padx=10)
    expense_no.grid(row=1, column=0, padx=10)
    table_name_entry.grid(row=0, column=1, padx=10)
    expense_no_entry.grid(row=1, column=1, padx=10)
    ok_button.grid(row=2, column=0, padx=10, pady=10)
    cancel_button.grid(row=2, column=1, padx=10, pady=10)
    listbox1.grid(row=3, column=0, columnspan=2)
    delall_button.grid(row=4, column=0, padx=10, pady=10)
    home_button.grid(row=4, column=1, padx=10, pady=10)


def updateListBoxes():
    global mainTableName
    # UPDATE Listboxes:
    # MAIN Listbox:
    k = 1
    Mainlistbox.delete(0, END)
    main_list_items, df = view(Username, Password, "main")
    for tblname, amount in main_list_items:
        list_items = (f"{tblname} :  ₹{amount}")
        Mainlistbox.insert(k, list_items)
        k += 1
    SetMainGraph(df)

    # ListBox1:
    try:
        listbox1.delete(0, END)
        i = 1
        listbox1_items, df = view(Username, Password, "main")
        for tblname, amount in listbox1_items:
            list_items = f"{tblname} :  ₹{amount}"
            listbox1.insert(i, list_items)
            i += 1
    except:
        pass
    mainTableName = "main"


def updateDropMenus():
    global clicked,no_cat

    clicked.set("")
    table_name_drop['menu'].delete(0, 'end')  # THIS WILL OCCASIONALLY THROW AN ERROR DON'T BOTHER WITH IT.

    db = mysql.connector.connect(
        host="localhost",
        user=Username,
        passwd=Password,
        database="Expensetracker"
    )

    mycursor = db.cursor()

    options = []
    mycursor.execute("SELECT Expensename from main")
    data = mycursor.fetchall()
    for i in data:
        options.append(i[0])

    for opt in options:
        table_name_drop['menu'].add_command(label=opt, command=tk._setit(clicked, opt))
    try:
        clicked.set(options[0])
        no_cat = False
    except IndexError:
        messagebox.showwarning("NO CATEGORY","There are no categories of expenses present, please create a category first by clicking on the plus icon above the table on the main screen")
        no_cat = True

def insert_repeat(state):
    global clicked_recur,cal

    options = ["Monthly", "Every 3 Months", "Every 6 Months", "Annually"]
    clicked_recur = StringVar()
    repeat_times = OptionMenu(topframe, clicked_recur, *options)
    clicked_recur.set(options[0])
    repeat_times.config(font=("Garamond bold", 13), width=35)

    now = datetime.datetime.now()
    cal_frame = LabelFrame(topframe, width=450,height=250, borderwidth=0, highlightthickness=0)

    if state:
        ok_button = Button(topframe, text="OK", command=lambda: insertOk(False), height=2, width=30,font=("Garamond bold", 15))
        ok_button.grid(row=5, column=0, padx=10, pady=10)
        cancel_button.grid(row=5, column=1, padx=10, pady=10)
        repeat_times.grid(row=4, column=0, padx=10, pady=10)

        cal_frame.grid(row=4, column=1, padx=10, pady=10)

        cal = Calendar(cal_frame, selectmode="day",year=now.year, month=now.month, day=now.day)
        cal.pack(fill="both", expand=True)

        cal_frame.pack_propagate(False)

    else:
        topframe.pack_forget()
        topframe.destroy()
        MainInsert(False)

def insertOk(recur_check):
    if recur_check:
        insert(Username, Password, clicked.get(), expense_name_entry.get(), expense_amount_entry.get())
        updateListBoxes()

    else:
        if expense_name_entry.get():

            if clicked_recur.get() == "Monthly":
                recursive_insert(Username,Password,expense_amount_entry.get(),1, cal.get_date(),clicked.get(),expensename=expense_name_entry.get())
                messagebox.showinfo("Transaction Complete","Expense Registered")

            elif clicked_recur.get() == "Every 3 Months":
                recursive_insert(Username,Password,expense_amount_entry.get(),3, cal.get_date(),clicked.get(),expensename=expense_name_entry.get())
                messagebox.showinfo("Transaction Complete","Expense Registered")

            elif clicked_recur.get() == "Every 6 Months":
                recursive_insert(Username,Password,expense_amount_entry.get(),6, cal.get_date(),clicked.get(),expensename=expense_name_entry.get())
                messagebox.showinfo("Transaction Complete","Expense Registered")

            elif clicked_recur.get() == "Annually":
                recursive_insert(Username,Password,expense_amount_entry.get(),12, cal.get_date(),clicked.get(),expensename=expense_name_entry.get())
                messagebox.showinfo("Transaction Complete","Expense Registered")

        else:
            if clicked_recur.get() == "Monthly":
                recursive_insert(Username,Password,expense_amount_entry.get(),1, cal.get_date(),clicked.get())
                messagebox.showinfo("Transaction Complete","Expense Registered")

            elif clicked_recur.get() == "Every 3 Months":
                recursive_insert(Username,Password,expense_amount_entry.get(),3, cal.get_date(),clicked.get())
                messagebox.showinfo("Transaction Complete","Expense Registered")

            elif clicked_recur.get() == "Every 6 Months":
                recursive_insert(Username,Password,expense_amount_entry.get(),6, cal.get_date(),clicked.get())
                messagebox.showinfo("Transaction Complete","Expense Registered")

            elif clicked_recur.get() == "Annually":
                recursive_insert(Username,Password,expense_amount_entry.get(),12, cal.get_date(),clicked.get())
                messagebox.showinfo("Transaction Complete","Expense Registered")
        updateListBoxes()


def MainInsert(testvar):
    global clicked, options, table_name_drop, insert_window, ok_button, cancel_button,topframe, expense_name_entry, expense_amount_entry
    options = ['NULL']
    clicked = StringVar()
    check = IntVar()

    if testvar == True:
        insert_window = Toplevel()
        topframe = LabelFrame(insert_window)
        table_name = Label(topframe, text="Enter the Category Name :", font=("Garamond bold", 20))
        expense_name = Label(topframe, text="Enter Expense Description :", font=("Garamond bold", 20))
        expense_amount = Label(topframe, text="Enter the Expense Amount :", font=("Garamond bold", 20))
        table_name_drop = OptionMenu(topframe, clicked, *options)
        expense_name_entry = Entry(topframe, width=55, font=("Garamond bold", 13))
        expense_amount_entry = Entry(topframe, width=55, font=("Garamond bold", 13))
        expense_name_entry.insert(0, "Expense Description")
        expense_amount_entry.insert(0, "Amount")
        ok_button = Button(topframe, text="OK", command=lambda: insertOk(True), height=2, width=30, font=("Garamond bold", 15))
        cancel_button = Button(topframe, text="CANCEL", command=insert_window.destroy,height=2, width=38, font=("Garamond bold", 15))
        recursive_check = Checkbutton(topframe, text="Repeat Transaction", variable=check, font=("Garamond bold", 23), command=lambda: insert_repeat(check.get()))

        table_name_drop.config(font=("Garamond bold", 13), width=50)
        updateDropMenus()

        if no_cat == True:
            pass
        else:
            table_name.grid(row=0, column=0, padx=10, pady=10)
            expense_name.grid(row=1, column=0, padx=10)
            expense_amount.grid(row=2, column=0, padx=10)
            table_name_drop.grid(row=0, column=1, padx=10, pady=10)
            expense_name_entry.grid(row=1, column=1, padx=10)
            expense_amount_entry.grid(row=2, column=1, padx=10)
            ok_button.grid(row=4, column=0, padx=10, pady=10)
            cancel_button.grid(row=4, column=1, padx=10, pady=10)
            recursive_check.grid(row=3, column=0)

            topframe.pack()
            # print("hello")
        # messagebox.showwarning("NO CATEGORY","There are no categories of expenses present, please create a category first by clicking on the plus icon above the table on the main screen")


    else:
        topframe = LabelFrame(insert_window)
        table_name = Label(topframe, text="Enter the Category Name :", font=("Garamond bold", 20))
        expense_name = Label(topframe, text="Enter Expense Description :", font=("Garamond bold", 20))
        expense_amount = Label(topframe, text="Enter the Expense Amount :", font=("Garamond bold", 20))
        table_name_drop = OptionMenu(topframe, clicked, *options)
        expense_name_entry = Entry(topframe, width=55, font=("Garamond bold", 13))
        expense_amount_entry = Entry(topframe, width=55, font=("Garamond bold", 13))
        expense_name_entry.insert(0, "Expense Description")
        expense_amount_entry.insert(0, "Amount")
        ok_button = Button(topframe, text="OK", command=lambda: [insert(Username, Password, clicked.get(), expense_name_entry.get(), expense_amount_entry.get()),updateListBoxes()], height=2, width=30, font=("Garamond bold", 15))
        cancel_button = Button(topframe, text="CANCEL", command=insert_window.destroy, height=2, width=38,font=("Garamond bold", 15))
        recursive_check = Checkbutton(topframe, text="Repeat Transaction", variable=check, font=("Garamond bold", 23),command=lambda: insert_repeat(check.get()))

        table_name_drop.config(font=("Garamond bold", 13), width=50)
        updateDropMenus()

        if no_cat == True:
            pass
        else:
            table_name.grid(row=0, column=0, padx=10, pady=10)
            expense_name.grid(row=1, column=0, padx=10)
            expense_amount.grid(row=2, column=0, padx=10)
            table_name_drop.grid(row=0, column=1, padx=10, pady=10)
            expense_name_entry.grid(row=1, column=1, padx=10)
            expense_amount_entry.grid(row=2, column=1, padx=10)
            ok_button.grid(row=4, column=0, padx=10, pady=10)
            cancel_button.grid(row=4, column=1, padx=10, pady=10)
            recursive_check.grid(row=3, column=0)

            topframe.pack()


def nmrOK(tablename):
    newmainrow(Username, Password, tablename)
    updateListBoxes()

    messagebox.showinfo("Command Successful","New Category Successfully Created")


def delOK(tablename):
    deletemain(Username, Password, tablename)
    updateListBoxes()
    updateDropMenus()


def NewMainRow():

    top = Toplevel()
    new_row_name = Label(top, text="""Enter the Category Of Expense to ADD:""", font=("Garamond bold", 20))
    new_row_name_entry = Entry(top, width=40, borderwidth=2, font=("Garamond bold", 15))
    add_button = Button(top, text="ADD", command=lambda: nmrOK(new_row_name_entry.get()), height=2, width=30, font=("Garamond bold", 15))
    cancel_button = Button(top, text="CANCEL", command=top.destroy,height=2, width=40, font=("Garamond bold", 15))

    new_row_name.grid(row=0, column=0, padx=10)
    new_row_name_entry.grid(row=0, column=1, padx=10, columnspan=2)
    add_button.grid(row=2, column=1, padx=10, pady=10)
    cancel_button.grid(row=2, column=0, padx=10, pady=10)


def delrow():
    global clicked, options, table_name_drop
    options = ['NULL']
    clicked = StringVar()

    top = Toplevel()
    delete_row_name = Label(
        top, text="Choose the Category to DELETE: ", font=("Garamond bold", 20))
    table_name_drop = OptionMenu(top, clicked, *options)
    delete_button = Button(top, text="DELETE", command=lambda: delOK(
        clicked.get()), height=2, width=30, font=("Garamond bold", 15))
    cancel_button = Button(top, text="CANCEL", command=top.destroy,
                           height=2, width=35, font=("Garamond bold", 15))

    table_name_drop.config(font=("Garamond bold", 13), width=40)
    updateDropMenus()

    delete_row_name.grid(row=1, column=0, padx=10)
    table_name_drop.grid(row=1, column=1, padx=10, columnspan=2)
    delete_button.grid(row=2, column=2, padx=10, pady=10)
    cancel_button.grid(row=2, column=0, padx=10, pady=10)


def viewConfirm(option):
    global mainTableName
    try:
        if mainTableName == "main":
            if option == "All Time":
                i = 1
                main_list_items, df = view(Username, Password, "main")
                Mainlistbox.delete(0, END)
                for tblname, amount in main_list_items:
                    list_items = (f"{tblname} :  ₹{amount}")
                    Mainlistbox.insert(i, list_items)
                    i += 1
                SetMainGraph(df)

            elif option == "Past 15 Days":
                k = 1
                main_list_items, df = view(
                    Username, Password, mainTableName, 15)
                Mainlistbox.delete(0, END)
                for expensename, amount, dateNtime, category in main_list_items:
                    list_items = (
                        f"{k}  :  {expensename}  :  {amount}  :  {dateNtime}  :  {category}")
                    Mainlistbox.insert(k, list_items)
                    k += 1
                SetMainGraph(df)

            elif option == "Past 30 Days":
                l = 1
                main_list_items, df = view(
                    Username, Password, mainTableName, 30)
                Mainlistbox.delete(0, END)
                for expensename, amount, dateNtime, category in main_list_items:
                    list_items = (
                        f"{l}  :  {expensename}  :  {amount}  :  {dateNtime}  :  {category}")
                    Mainlistbox.insert(l, list_items)
                    l += 1
                SetMainGraph(df)

        else:
            if option == "All Time":
                m = 1
                main_list_items, df = view(Username, Password, mainTableName)
                Mainlistbox.delete(0, END)
                for id, expensename, amount, date in main_list_items:
                    list_items = f"{id}  :  {expensename}  :  ₹{amount}  :  {date}"
                    Mainlistbox.insert(m, list_items)
                    m += 1
                SetMainGraph(df)

            elif option == "Past 15 Days":
                n = 1
                main_list_items, df = view(
                    Username, Password, mainTableName, 15)
                Mainlistbox.delete(0, END)
                for id, expensename, amount, date in main_list_items:
                    list_items = f"{id}  :  {expensename}  :  ₹{amount}  :  {date}"
                    Mainlistbox.insert(n, list_items)
                    n += 1
                SetMainGraph(df)

            elif option == "Past 30 Days":
                o = 1
                main_list_items, df = view(
                    Username, Password, mainTableName, 30)
                Mainlistbox.delete(0, END)
                for id, expensename, amount, date in main_list_items:
                    list_items = f"{id}  :  {expensename}  :  ₹{amount}  :  {date}"
                    Mainlistbox.insert(o, list_items)
                    o += 1
                SetMainGraph(df)
    except:
        messagebox.showerror("ERROR", "CANNOT VIEW FURTHER")


def ViewTable(kintercall):
    global mainTableName
    row_str = ""
    rowselection = Mainlistbox.curselection()
    for i in rowselection:
        row_str = row_str + Mainlistbox.get(i)
    row_list = row_str.split(':')
    mainTableName = row_list[0].strip()
    viewConfirm("All Time")


def SetMainList():
    global Mainlistbox, mainTableName
    mainTableName = "main"
    i = 1
    clicked_main = StringVar()
    options = ["All Time", "Past 15 Days", "Past 30 Days"]
    clicked_main.set(options[0])

    ListFrame_parent = LabelFrame(root, borderwidth=0, highlightthickness=0)
    ListFrame_child1 = LabelFrame(
    ListFrame_parent, borderwidth=0, highlightthickness=0)
    ListFrame_child2 = LabelFrame(
    ListFrame_parent, borderwidth=0, highlightthickness=0)
    ListFrame_parent.grid(row=1, column=0, columnspan=4)
    ListFrame_child1.grid(row=0, column=4, sticky=E)
    ListFrame_child2.grid(row=0, column=0, sticky=W)

    Mainlistbox = Listbox(ListFrame_parent, width=76,font=('Garamond bold', 14))

    image = Image.open(r"Images\home.png")
    resize_home_img = image.resize((30, 30))
    home_img = ImageTk.PhotoImage(resize_home_img)
    Home_Button = Button(ListFrame_child2, image=home_img,borderwidth=0, command=updateListBoxes, bg='#222222')
    Home_Button.image = home_img

    image = Image.open(r"Images\checkbox.png")
    resize_check_img = image.resize((30, 30))
    check_img = ImageTk.PhotoImage(resize_check_img)
    confirm_button = Button(ListFrame_child1, image=check_img, borderwidth=0,command=lambda: viewConfirm(clicked_main.get()), bg="#222222")
    confirm_button.image = check_img

    image = Image.open(r"Images\plus1.png")
    resize_nmr_img = image.resize((30, 30))
    nmr_img = ImageTk.PhotoImage(resize_nmr_img)
    btn_newMrow = Button(ListFrame_child2, image=nmr_img,borderwidth=0, command=NewMainRow, bg="#222222")
    btn_newMrow.image = nmr_img

    image = Image.open(r"Images\delete.png")
    resize_delnmr_img = image.resize((30, 30))
    delnmr_img = ImageTk.PhotoImage(resize_delnmr_img)
    btn_delnmr = Button(ListFrame_child2, image=delnmr_img,borderwidth=0, command=delrow, bg="#222222")
    btn_delnmr.image = delnmr_img

    view_drop = OptionMenu(ListFrame_child1, clicked_main, *options)
    view_drop.config(bg="#1f77b4")

    main_list_items, df = view(Username, Password, mainTableName)
    for tblname, amount in main_list_items:
        list_items = (f"{tblname} :  ₹{amount}")
        Mainlistbox.insert(i, list_items)
        i += 1

    view_drop.config(font=("Garamond bold", 14), width=30)

    Mainlistbox.grid(row=1, column=0, columnspan=5)
    Home_Button.pack(side=LEFT, expand=True, fill=BOTH, padx=5)
    btn_newMrow.pack(side=LEFT, expand=True, fill=BOTH, padx=5)
    btn_delnmr.pack(side=LEFT, expand=True, fill=BOTH, padx=5)
    confirm_button.pack(side=LEFT, expand=True, fill=BOTH, padx=10)
    view_drop.pack(side=LEFT, expand=True, fill=BOTH)

    updateListBoxes()

def CreateMainButtons():
    image = Image.open(r"Images\plus.png")
    resize_insert_img = image.resize((50, 50))
    insert_img = ImageTk.PhotoImage(resize_insert_img)
    btn_insert = Button(root, image=insert_img,command=lambda: MainInsert(True), borderwidth=0, bg="#222222")
    btn_insert.image = insert_img

    image = Image.open(r"Images\delete.png")
    resize_del_img = image.resize((50, 50))
    del_img = ImageTk.PhotoImage(resize_del_img)
    btn_del = Button(root, image=del_img, command=MainDelete,borderwidth=0, bg="#222222")
    btn_del.image = del_img

    Mainlistbox.bind('<Double-1>', ViewTable)

    btn_insert.grid(row=2, column=3,pady=10)
    btn_del.grid(row=2, column=0,pady=10)


def SetMainGraph(df):
    try:
        main_graph_frame = LabelFrame(
            root, borderwidth=0, highlightthickness=0)
        main_graph_frame.grid(row=0, column=0, padx=10, columnspan=4, pady=10)

        fig = Figure(figsize=(6.85, 4), dpi=100)
        fig.patch.set_facecolor("#adb5bd")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#adb5bd")
        ax.set_ylabel("Amount(₹)")
        df.plot(x="ExpenseName", y="Amount", kind="bar", ax=ax)
        fig.subplots_adjust(left=0.125, bottom=0.41, right=0.9,
                            top=0.993, wspace=0.2, hspace=0.2)
        canvas = FigureCanvasTkAgg(fig, master=main_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    except NameError:
        main_graph_frame = LabelFrame(
            root, borderwidth=0, highlightthickness=0)
        main_graph_frame.grid(row=0, column=0, padx=10, columnspan=4, pady=10)

        fig = Figure(figsize=(6.85, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_facecolor("#adb5bd")
        ax.set_ylabel("Amount(₹)")
        temp, df = view(Username, Password, "main")
        df.plot(x="ExpenseName", y="Amount", kind="bar", ax=ax)
        fig.subplots_adjust(left=0.125, bottom=0.41, right=0.9,
                            top=0.993, wspace=0.2, hspace=0.2)
        canvas = FigureCanvasTkAgg(fig, master=main_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    except TypeError:
        main_graph_frame = LabelFrame(
            root, borderwidth=0, highlightthickness=0)
        main_graph_frame.grid(row=0, column=0, padx=10, columnspan=4, pady=10)
        fig = Figure(figsize=(6.85, 4), dpi=100)
        fig.subplots_adjust(left=0.125, bottom=0.41, right=0.9,
                            top=0.993, wspace=0.2, hspace=0.2)
        canvas = FigureCanvasTkAgg(fig, master=main_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()


def SetupMainUI():
    global Username, Password
    if init.databaseconn(username_entry.get(), password_entry.get()):
        Username = username_entry.get()
        Password = password_entry.get()
        login_frame.place_forget()
        temp, df = view(Username, Password, "main")
        SetMainGraph(df)
        SetMainList()
        CreateMainButtons()


login_frame = LabelFrame(root, text="Login", font=("Garamond bold", 20))
Username = ""
Password = ""
if not os.path.isfile("details.dat"):
    username_label = Label(login_frame, text="Username: ",font=("Garamond bold", 40))
    password_label = Label(login_frame, text="Password: ",font=("Garamond bold", 40))
    username_entry = Entry(login_frame, width=30, font=("Garamond bold", 15))
    password_entry = Entry(login_frame, width=30, font=("Garamond bold", 15))
    ok_button = Button(login_frame, text="OK", font=("Garamond bold", 20), command=SetupMainUI)
    cancel_button = Button(login_frame, text="CANCEL", font=("Garamond bold", 20), command=lambda: exit())

    login_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
    username_label.grid(row=0, column=0, padx=10, pady=10)
    username_entry.grid(row=0, column=1, padx=10, pady=10, ipady=4)
    password_label.grid(row=1, column=0, padx=10, pady=10)
    password_entry.grid(row=1, column=1, padx=10, pady=10, ipady=4)
    ok_button.grid(row=2, column=0, ipadx=100, ipady=25, padx=10, pady=10)
    cancel_button.grid(row=2, column=1, ipadx=100, ipady=25, padx=10, pady=10)

else:
    login_frame.place_forget()
    with open("details.dat", "rb") as file:
        data = pickle.load(file)
        Username = data[0]
        Password = data[1]
    temp, df = view(Username, Password, "main")
    recursive_read(Username,Password)
    SetMainGraph(df)
    SetMainList()
    CreateMainButtons()

root.mainloop()