import sqlite3
import tkinter as tk
from tkinter import *
import ttkbootstrap as ttk
import  tkinter.messagebox


#Connects to the database
FootballSystem = sqlite3.connect('Footballsystem.db')
cursor = FootballSystem.cursor()


class passwords: #class to validate and hash passwords
    def validate(password):
        number=any(char.isdigit() for char in password) #Check if password has a number
        upper=any(char.isupper() for char in password) #Check if password has an uppercase character
        special=any(char in '[$&+,:;=?@#|<>.^*()%!-]' for char in password) #Check if password has a special character from those specified
        if not 6 <= len(password) <= 20: #Check password length is between 6 and 20 characters
            tk.messagebox.showinfo("Error", "Password be greater than 6 characters and less than 20")
            return False #displays error message and returns false if condition not met
        elif not number: #Checks if there is at least one number
            tk.messagebox.showinfo("Error", "Password must have number")
            return False #displays error message and returns false if condition not met
        elif not upper: #Checks if there is at least one uppercase letter
            tk.messagebox.showinfo("Error", "Password must have uppercase letter") 
            return False #displays error message and returns false if condition not met
        elif not special: #Checks if there is at least special character from those specified
            tk.messagebox.showinfo("Error", "Password must have special character from [$&+,:;=?@#|<>.^*()%!-]")
            return False #displays error message and returns false if condition not met
        else:
            return True #returns true if security requirements are met
    def hash(password):
        result=1
        for x in range(len(password)):
            result=result+ord(password[x])*(x+2) #Add ASCII value times position+2
            result=result^3  #XOR to make it more unique
            result=result%997 #Uses modulus to keep result in range
        return result 


def user_login(): #function that creates admin account if all conditions are met
    global password, username, confirm_password, confirm_username

    #retrieves all entries and stores them as variables
    username1=username.get()
    password1=password.get()
    confirm_password1=confirm_password.get()
    confirm_username1=confirm_username.get()

    #confirms that password and confirm password are same and that username and confirm username are same
    if password1==confirm_password1 and username1==confirm_username1:
        if passwords.validate(password1): #only runs if password meets security requirements
            tk.messagebox.showinfo("Success", "Account Created")
            password2=passwords.hash(password1)
            cursor.execute("INSERT INTO Login (Username, HashedPassword, Permissions) VALUES(?, ?, 1)", (username1, password2)) #executes command to create admin account
            FootballSystem.commit() #commits chagne
            FootballSystem.close() #closes database connection
            setup.destroy() 
    else: #displays error message if passwords or usernames do not match
        tk.messagebox.showinfo("Error", "Please make sure Username and Confirm Username are identical and Password and Confirm Password are identical")


#Creates tk instance called setup
setup=tk.Tk()
setup.title('Setup')
setup.geometry('900x450')

#Header
header_main=ttk.Label(master=setup, text="Football League Table and Player Performance Report System", font="Calibri 10 bold")
header_main.pack(pady=10)

#Setup text
setuptitle_main=ttk.Label(master=setup, text="Setup(Account Creation)", font="Calibri 30 bold")
setuptitle_main.pack(pady=20)


row1=tk.Frame(setup)
row1.pack(pady=5, anchor="w", padx=350)


#creates username text and text entry
lUsername=Label(row1, text='Username')
username=Entry(row1)
lUsername.pack(side="left")
username.pack(side="left")



row2=tk.Frame(setup)
row2.pack(pady=5, anchor="w", padx=303)

#creates confirm username text and text entry
lConfirm_Username=Label(row2, text='Confirm Username')
confirm_username=Entry(row2)
lConfirm_Username.pack(side="left")
confirm_username.pack(side="left")


row3=tk.Frame(setup)
row3.pack(pady=5, anchor="w", padx=352)

#creates password text and text entry
lPassword=Label(row3, text='Password')
password=Entry(row3)
password.config(show="*")
lPassword.pack(side="left")
password.pack(side="left")


row4=tk.Frame(setup)
row4.pack(pady=5, anchor="w", padx=303)


#creates confirm password text and text entry
lConfirm_Password=Label(row4, text='Confirm Password')
confirm_password=Entry(row4)
confirm_password.config(show="*")
lConfirm_Password.pack(side="left")
confirm_password.pack(side="left")




row5=tk.Frame(setup)
row5.pack(pady=5, anchor="s")


#creates submit button to create account
setup_button=ttk.Button(master=row5, 
                       text="Create account",
                       command=user_login
                       )
setup_button.pack()




#tkinter mainloop
setup.mainloop()