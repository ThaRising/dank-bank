imports
from tkinter import *

#Main Screen
master = Tk()
master.title('Banking App')

def login_session():
    print("true")

def login():
    #Vars
    global temp_login_username
    global temp_login_accountID
    global temp_login_password
    global login_screen
    temp_login_username = StringVar()
    temp_login_accountID =IntVar()
    temp_login_password = StringVar()
    #Login Screen
    login_screen = Toplevel(master)
    login_screen.title('Login')
    #Labels
    Label(login_screen, text="Bitte Anmelden", font=('Calibri',12)).grid(row=0,sticky=N,pady=10)
    Label(login_screen, text="Username", font=('Calibri',12)).grid(row=1,sticky=W)
    Label(login_screen, text="AccountID", font=('Calibri',12)).grid(row=2,sticky=W)
    Label(login_screen, text="Passwort", font=('Calibri',12)).grid(row=3,sticky=W)

    #Entry
    Entry(login_screen, textvariable=temp_login_username).grid(row=1,column=1,padx=5)
    Entry(login_screen, textvariable=temp_login_accountID).grid(row=2,column=1,padx=5)
    Entry(login_screen, textvariable=temp_login_password,show="*").grid(row=3,column=1,padx=5)


    #Button
    Button(login_screen, text="Login", command=login_session, width=15,font=('Calibri',12)).grid(row=4,sticky=W,pady=5,padx=5)


#Labels
Label(master, text = "Wilkommen bei der Dank Bank", font=('Calibri',14)).grid(row=0,sticky=N,pady=10)
Label(master, text = "In dieser App können sie ihr Konto verwalten", font=('Calibri',12)).grid(row=1,sticky=N)

#Buttons
Button(master, text="Login", font=('Calibri',12),width=20,command=login).grid(row=4,sticky=N,pady=10)

master.mainloop()