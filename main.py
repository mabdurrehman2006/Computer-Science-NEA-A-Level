import tkinter as tk
import ttkbootstrap as ttk
import tkinter.messagebox
import sqlite3
import sys


username_list=[] #list to store username of current user logged in
position_options=["GK", "RB", "CB", "LB", "RWB", "LWB", "CDM", "CM", "CAM", "RM", "LM", "RW", "LW", "CF", "ST"] #list of football position for creating a new player


class sqlconnection(): #class for managing connection to database
    def connect(): #function opens connection to database and creates cursor to be used in program 
        global FootballSystem #Declares FootballSystem as a global variable so it can be accessed and used throughout the program
        FootballSystem=sqlite3.connect('Footballsystem.db') #Opens a connection to the database.
        global cursor #Declares cursor as a global variable so it can be accessed and used throughout the program
        cursor=FootballSystem.cursor()#creates cursor to open connection to database


class ErrorMessages(): #Class with reusable error message boxes so it's cleaner while coding
    def wrong_username(): #Displays error if username is wrong
        tk.messagebox.showinfo("Error", "Username is not correct")
    def no_username_password(): #Displays error if username or password is missing
        tk.messagebox.showinfo("Error", "Please enter both username and password")
    def wrong_password(): #Displays error if password is wrong
        tk.messagebox.showinfo("Error", "Password is not correct")


class passwords: #class to validate and hash passwords
    def validate(password):
        number=any(char.isdigit() for char in password) #Check if password has a number
        upper=any(char.isupper() for char in password) #Check if password has an uppercase character
        special=any(char in '[$&+,:;=?@#|<>.^*()%!-]' for char in password) #Check if password has a special character from those specified
        if not 6<=len(password)<=20: #Check password length is between 6 and 20 characters
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


class generate_fixtures: #Generates fixtures for the league by scheduling home and away matches for each week
    def __init__(self):
        pass
    def work():
        #Connects to the database and fetches all team names from the Team table
        sqlconnection.connect()
        cursor.execute("SELECT TeamName From Team")
        Teams=[row[0] for row in cursor.fetchall()]

        #Checks if there are enough teams to generate fixtures(must be at least 2 teams)
        if len(Teams)<2:
            tk.messagebox.showinfo("Error", "Not enough teams to generate fixtures")
        
        #If odd number of teams, adds a "None" value to ensure even number of teams    
        else: 
            if len(Teams)%2!=0:
                Teams.append(None)

        #Generates fixtures for each week by pairing home and away teams
            matches_per_week=len(Teams)//2
            num_of_weeks=len(Teams)-1

            fixtures=[]
            teams=Teams.copy()
        
            for week in range(num_of_weeks):
                matches=[]
                for x in range(matches_per_week):
                    home=teams[x]
                    away=teams[-(x+1)]

                    if home is not None and away is not None:
                        matches.append((home, away))
                fixtures.append(matches)
                teams=[teams[0]]+[teams[-1]]+teams[1:-1]

            #Inserts a new season into the LeagueTable and creates gameweeks
            cursor.execute("INSERT INTO LeagueTable DEFAULT VALUES")
            seasonID=cursor.lastrowid

            for x in range(num_of_weeks):
                cursor.execute("INSERT INTO Gameweek (SeasonID) VALUES (?)", (seasonID, ))

            cursor.execute("SELECT GameweekID FROM Gameweek WHERE SeasonID=?", (seasonID,))
            gameweekID = [row[0] for row in cursor.fetchall()]

            #Inserts fixtures into the Fixture table with placeholders for scores
            for gw, games in zip(gameweekID, fixtures):
                for home, away in games:
                    cursor.execute("INSERT INTO Fixture (GameweekID, HomeTeam, AwayTeam, HomeTeamGoals, AwayTeamGoals) VALUES (?, ?, ?, ?, ?)", (gw, home, away, None, None))
            tk.messagebox.showinfo("Success", "Fixtures generated") #Displays success message when fixtures are generated

        #Commits changes to the database and closes the connection
        FootballSystem.commit()
        FootballSystem.close()


class viewtransferrequests: #Class for viewing and managing transfer requests
    def __init__(self, root):
        pass #Initializes the class with root
    def back(self, transferwindow): #Closes the current window and navigates back to the team admin home page
            transferwindow.withdraw() #Closes the current window
            choice=teamadmin_home_page(transferwindow) #Creates a new instance of teamadmin_home_page
            choice.work() #Calls work function of teamadmin_home_page
    def work(self):
        transferwindow=tk.Toplevel(login) #Creates a new window for viewing transfer requests
        transferwindow.title("Create New Team") #Sets the window title
        transferwindow.geometry('900x450') #Sets the window size
        transferwindow.protocol("WM_DELETE_WINDOW", closeAPP) #Handles window close event

        #header
        header_main=ttk.Label(master=transferwindow, text="Football League Table and Player Performance Report System", font="Calibri 10 bold")
        header_main.grid(row=0, column=0, columnspan=3)

        #Transfer requests text label
        transferrequests_label=ttk.Label(master=transferwindow, text="Transfer Requests", font="Calibri 20 bold")
        transferrequests_label.grid(row=1, column=0, columnspan=3)

        #Creates a Treeview to show the transfer requests
        tree=ttk.Treeview(transferwindow, columns=("Player", "From", "To"), show="headings")

        #Sets column headers
        tree.heading("Player", text="Player Name")
        tree.heading("From", text="Current Team")
        tree.heading("To", text="Requested Team")

        #Configures the width and alignment of each column in the Treeview
        tree.column("Player", width=200, anchor="center")
        tree.column("From", width=200, anchor="center")
        tree.column("To", width=200, anchor="center")


        tree.grid(row=2, column=0, columnspan=3, padx=10, pady=10) #Places the Treeview on the window

        self.load_requests(tree, transferwindow) #calls load_requests function to load transfer requests

        #Back Button to return to the previous screen
        def back(): #Function to go back to previous window
            self.back(transferwindow) #Calls back function
        back_button=ttk.Button(master=transferwindow, text="Back", command=back) #Button to go back to previous page
        back_button.grid(row=99, column=0, columnspan=999, sticky="ew") #Places button on window

    def load_requests(self, tree, transferwindow): #loads all transfer requests and inserts them into treeview
        try:
            sqlconnection.connect() #connects to database

            #Retrieves all unresolved transfer requests
            cursor.execute("SELECT TransferID, PlayerID, RequestedID, CurrentID FROM TransferRequests WHERE processed=0")
            requests=cursor.fetchall()

            #Clears existing rows in the treeview
            for row in tree.get_children():
                tree.delete(row)

            for request in requests:
                TransferID, PlayerID, RequestedID, CurrentID = request

                #Get player name
                cursor.execute("SELECT PlayerName FROM Players WHERE PlayerID=?", (PlayerID,))
                player_name=cursor.fetchone()[0]

                #Get current team name
                cursor.execute("SELECT TeamName FROM Team WHERE TeamID=?", (CurrentID,))
                current_team=cursor.fetchone()[0]
                
                #Get requested team name
                cursor.execute("SELECT TeamName FROM Team WHERE TeamID=?", (RequestedID,))
                requested_team=cursor.fetchone()[0]

                #Create buttons for each row 
                def approve_func(tid=TransferID):
                    self.process_request(tid, approve=True, window=transferwindow)

                def deny_func(tid=TransferID):
                    self.process_request(tid, approve=False, window=transferwindow)

                #Insert row into treeview
                tree.insert("", "end", values=(player_name, current_team, requested_team, "Approve", "Deny"))

                #Creates buttons underneath for the transfer request(easier to do outside of Treeview and it would be harder for me to do inside of treeview)
                row_num=len(tree.get_children())+2
                approve_btn=ttk.Button(master=transferwindow, text="Approve", command=approve_func) #approve button
                deny_btn=ttk.Button(master=transferwindow, text="Deny", command=deny_func) #deny button

                approve_btn.grid(row=row_num, column=1)
                deny_btn.grid(row=row_num, column=2)

            FootballSystem.close() #closes database connection

        except sqlite3.Error as error: #Handle any database errors
            tk.messagebox.showinfo("Error", f"Error loading transfer requests: {error}") #Display error message

    def process_request(self, TransferID, approve, window): #handles approving and denying transfer requests
        try:
            sqlconnection.connect() #connects to database

            if approve:
                #Move the player to the new team
                cursor.execute("SELECT PlayerID, RequestedID FROM TransferRequests WHERE TransferID=?", (TransferID,))
                result=cursor.fetchone()
                PlayerID=result[0]
                RequestedID=result[1]
                cursor.execute("UPDATE Players SET TeamID=? WHERE PlayerID=?", (RequestedID, PlayerID))

            #Mark the transfer as processed
            cursor.execute("UPDATE TransferRequests SET processed=1 WHERE TransferID=?", (TransferID,))

            #Commits changes to the database and closes the connection
            FootballSystem.commit()
            FootballSystem.close()

            #Refresh the window to update the list
            window.destroy()
            self.work()

        except sqlite3.Error as error: #Handle any database errors
            tk.messagebox.showinfo("Error", f"Error processing request: {error}") #Display error message


class requesttransfer: #Class to create and submit transfer requests for players
    def __init__(self, root):
        pass #Initializes the class with root
    def back(self, transferwindow): #Closes the current window and navigates back to the team admin home page
            transferwindow.withdraw() #Closes the current window
            choice=teamadmin_home_page(transferwindow) #Creates a new instance of teamadmin_home_page
            choice.work() #Calls work function of teamadmin_home_page
    def submit(self, PlayerID): #Function to submit a transfer request for a player
        sqlconnection.connect() #Connects to the database
        cursor.execute("SELECT processed FROM TransferRequests WHERE PlayerID=?", (PlayerID,))
        Processed=cursor.fetchone() #Fetches result

        cursor.execute("SELECT TeamID FROM Players WHERE PlayerID=?", (PlayerID,))
        result=cursor.fetchone()
        if not result:
            tk.messagebox.showinfo("Error", "Player not found")
            return
        Current=result[0]

        username=username_list[0] #Retrieves the current logged-in user's username
        cursor.execute("SELECT UserID FROM login WHERE Username=?", (username,))
        userID=cursor.fetchone()
        userID=userID[0] #Gets the user ID

        cursor.execute("SELECT TeamID FROM Team WHERE UserID=?", (userID,))
        Requested=cursor.fetchone()
        Requested=Requested[0] #Extracts the team ID for team requesting transfer

        #Check if player already has an unprocessed request
        cursor.execute("SELECT * FROM TransferRequests WHERE PlayerID=? AND processed=0", (PlayerID,))
        existing_request=cursor.fetchone()

        if existing_request:
            tk.messagebox.showinfo("Error", "This player already has a pending transfer request")
            FootballSystem.close() #Closes database connection
            return #Stops execution

        
        #If the requested transfer is on the captain's own team, it shows an error
        elif Requested==Current:
            tk.messagebox.showinfo("Error", "Cannot request transfer for a player that plays for your team")
            FootballSystem.close() #Closes database connection
            return #Stops execution
        
        #Checks if the transfer request can be created based on the processed state and whether the player is in the same team
        elif Processed is None or Processed=="" or Processed==1:
            
            cursor.execute("INSERT INTO TransferRequests (RequestedID, CurrentID, PlayerID) VALUES(?, ?, ?)", (Requested, Current, PlayerID)) #Creates the transfer request in the database
            #Commits changes to the database and closes the connection
            FootballSystem.commit() 
            FootballSystem.close()
            tk.messagebox.showinfo("Success", "Transfer Request Created Successfully") #Shows success message



    def work(self): #Function that creates the interface for submitting a transfer request
        transferwindow=tk.Toplevel(login) #Creates a new window for transfer requests
        transferwindow.title("Create New Team") #Sets the window title
        transferwindow.geometry('900x450') #Sets the window size
        transferwindow.protocol("WM_DELETE_WINDOW", closeAPP) #Handles window close event

        header_main=ttk.Label(master=transferwindow, text="Football League Table and Player Performance Report System", font="Calibri 10 bold") #Header label for the page
        header_main.grid(row=0, column=0, columnspan=3) #Places header label on window

        PlayerID_Text=ttk.Label(master=transferwindow, text="Player ID", font="Calibri 10 bold") #Label for text that says 'Player ID'
        PlayerID_Text.grid(row=1, column=0) #Places label on window

        PlayerID=tk.StringVar() #Creates a variable to store PlayerID input
        PlayerID_Entry=ttk.Entry(
            master=transferwindow,
            textvariable=PlayerID
        ) #Creates an entry field for Player ID
        PlayerID_Entry.grid(row=1, column=1) #Places Entry on window



        def submit_command(): #Function for handling the transfer request submission
            playerID=PlayerID.get()
            if not playerID.isdigit():
                tk.messagebox.showinfo("Error", "Player ID must be a number")
                return

            playerID=int(playerID)

            self.submit(playerID)
        #submit button
        submit_button=ttk.Button(master=transferwindow, 
                       text="Submit Transfer Request",
                       command=submit_command
                       )
        submit_button.grid(row=2, column=0, columnspan=999, sticky="ew")

        def back(): #Function to go back to the previous window
            self.back(transferwindow) #Calls back function to return to previous page
        back_button=ttk.Button(master=transferwindow, 
                       text="Back",
                       command=back
                       ) #Button to go back to the previous window
        back_button.grid(row=3, column=0, columnspan=999, sticky="ew") #Places the back button on the window
        

class editplayerstats: #Class for editing player statistics
    def __init__(self, root):
        pass
    def back(self, viewteam, player_name): #Closes the current window and navigates back to the team admin home page
            viewteam.withdraw() #Closes the current window
            choice=viewplayercaptain(viewteam) #Creates a new instance of viewplayercaptain
            choice.work(player_name) #Calls work function of viewplayercaptain
    def work(self, player_name):
        viewteam=tk.Toplevel(login) #Creates a new top-level window for viewing player stats
        viewteam.title("View Team") #Sets window title
        viewteam.geometry('1200x550') #Sets window size
        self.viewteam=viewteam 
        viewteam.protocol("WM_DELETE_WINDOW", closeAPP) #Handles window close event
        team_name=self.fetchteam(player_name) #Fetches team name associated with the player
        
        #Header label
        header_main=ttk.Label(master=viewteam, text="Football League Table and Player Performance Report System", font="Calibri 10 bold", anchor="center")
        header_main.grid(row=0, column=0, columnspan=999, sticky="ew") #Places label on window

        #Label for player name
        player_label=ttk.Label(master=viewteam, text=player_name, font="Calibri 20 bold", anchor="center")
        player_label.grid(row=1, column=0, columnspan=999, sticky="ew") #Places label on window


        sqlconnection.connect() #Connects to the database
        cursor.execute("SELECT PlayerID FROM Players WHERE PlayerName=?", (player_name,))
        PlayerID=cursor.fetchone() #Fetches player ID
        PlayerID=PlayerID[0] #Extracts PlayerID value
        cursor.execute("SELECT Position FROM Players WHERE PlayerName=?", (player_name,))
        Position=cursor.fetchone() #Fetches player's position
        Position=Position[0] #Extracts Position value
        team_label=ttk.Label(master=viewteam, text=f'PlayerID: {PlayerID}', font="Calibri 10 bold", anchor="center")
        team_label.grid(row=2, column=0, columnspan=999, sticky="ew") #Places label on window
        
        #Label for PlayerID
        PlayerID_label=ttk.Label(master=viewteam, text=f'Team: {team_name}', font="Calibri 10 bold", anchor="center")
        PlayerID_label.grid(row=3, column=0, columnspan=999, sticky="ew") #Places label on window

        #Label for Player Position
        Position_label=ttk.Label(master=viewteam, text=f'Position: {Position}', font="Calibri 10 bold", anchor="center")
        Position_label.grid(row=4, column=0, columnspan=999, sticky="ew") #Places label on window

        stats=self.fetch_data(player_name) #Fetching player stats
        stat_names=["Games Played", "Goals", "Assists", "Clean Sheets", "Tackles", "Fouls Committed", "Yellow Cards", "Red Cards"]
        stat_vars=[tk.StringVar(value=str(value)) for value in stats] #Creates StringVar for each stat to allow editing in entry fields
        
        for x in range(len(stat_names)):
            ttk.Label(viewteam, text=stat_names[x], font="Calibri 10").grid(row=5, column=x, padx=10, pady=5, sticky="w") #Label for stat names
            entry=ttk.Entry(viewteam, textvariable=stat_vars[x], width=15) #Creates entry field for stat input
            entry.grid(row=6, column=x, padx=10, pady=5) #Places entry fields on window

        def save_stats(): #Function to save updated stats to the database
            updated_stats=[var.get() for var in stat_vars] #Get updated values from stat variables
            #Checks if all inputs are valid integers
            for stat in updated_stats:
                if not stat.isdigit():
                    tk.messagebox.showinfo("Error", "Please enter valid integers for all stats.")
                    return
            try:
                #Update the database with the new values
                sqlconnection.connect() #Connects to the database
                cursor.execute("UPDATE Players SET GamesPlayed=?, Goals=?, Assists=?, CleanSheets=?, Tackles=?, FoulsCommitted=?, YellowCards=?, RedCards=? WHERE PlayerName=?", (*updated_stats, player_name))
                FootballSystem.commit() #Commit changes to the database
                tk.messagebox.showinfo("Success", "Player stats updated successfully.") #Display success message
                FootballSystem.close() #Close database connection
            except sqlite3.Error as error: #Handle any database errors
                tk.messagebox.showinfo("Error", f"Error updating Player: {error}") #Display error message
                

        save_button = ttk.Button(viewteam, text="Update Stats", command=save_stats) #Button to trigger save_stats function
        save_button.grid(row=7, column=0, columnspan=999, pady=10, sticky="ew") #Places button on window
        #Back Button
        def back(): #Function to go back to previous window
            self.back(viewteam, player_name) #Calls back function
        back_button=ttk.Button(master=viewteam, 
                       text="Back",
                       command=back
                       ) #Button to go back to previous page
        back_button.grid(row=8, column=0, columnspan=999, sticky="ew") #Places button on window
    def fetch_data(self, player_name): #Function to fetch player stats from the database
        try:
            sqlconnection.connect() #Connects to the database

            
            cursor.execute("SELECT GamesPlayed, Goals, Assists, CleanSheets, Tackles, FoulsCommitted, YellowCards, RedCards FROM Players WHERE PlayerName=?", (player_name,))
            player=cursor.fetchone() #Fetch player stats
            stats=player #Store player stats

            FootballSystem.close() #Close database connection
            return stats #Return stats
        
        except sqlite3.Error as error: #Handle any database errors
            tk.messagebox.showinfo("Error", f"Error fetching Player: {error}") #Display error message
    def fetchteam(self, player_name): #Function to fetch team name associated with the player
        try:
            sqlconnection.connect() #Connects to the database
            cursor.execute("SELECT TeamID FROM Players WHERE PlayerName=?", (player_name,))
            TeamID=cursor.fetchone() #Fetch TeamID associated with the player
            TeamID=TeamID[0] #Extract TeamID value
            cursor.execute("SELECT TeamName FROM Team WHERE TeamID=?", (TeamID,))
            team_name=cursor.fetchone() #Fetch team name using TeamID
            team_name=team_name[0] #Extract team name value
            FootballSystem.close() #Close database connection
            return team_name #Return team name
        except sqlite3.Error as error: #Handle any database errors
            tk.messagebox.showinfo("Error", f"Error fetching Team Name: {error}") #Display error message


class viewplayer(): #Class for viewing player details, including stats and team information
    def __init__(self, root):
        pass #Initializes the class with root
    def back(self, viewteam): #Closes the current window and navigates back to the view team sheet page
            viewteam.withdraw() #Closes the current window
            choice=viewteamsheet(viewteam) #Creates a new instance of viewteamsheet
            choice.work() #Calls work function of viewteamsheet
    def work(self, player_name): #Main function to display player details in a new window, fetches player stats and team info
        
        viewteam=tk.Toplevel(login) #Creates a new top-level window for viewing player details and stats
        viewteam.title("View Team") #Sets window title
        viewteam.geometry('1200x550') #Sets window size
        self.viewteam=viewteam
        viewteam.protocol("WM_DELETE_WINDOW", closeAPP) #Handles window close event
        team_name=self.fetchteam(player_name) #Fetches team name associated with the player
        
        #Header label
        header_main=ttk.Label(master=viewteam, text="Football League Table and Player Performance Report System", font="Calibri 10 bold", anchor="center")
        header_main.grid(row=0, column=0, columnspan=999, sticky="ew") #Places label on window

        #Label for player name
        name_label=ttk.Label(master=viewteam, text=player_name, font="Calibri 20 bold", anchor="center")
        name_label.grid(row=1, column=0, columnspan=999, sticky="ew") #Places label on window

        #Fetches player ID from the database
        sqlconnection.connect() #Connects to the database
        cursor.execute("SELECT PlayerID FROM Players WHERE PlayerName=?", (player_name,))
        PlayerID=cursor.fetchone()
        PlayerID=PlayerID[0] #Gets the player ID
        FootballSystem.close() #Close database connection

        #Player ID label
        playerID_label=ttk.Label(master=viewteam, text=f'PlayerID: {PlayerID}', font="Calibri 10 bold", anchor="center")
        playerID_label.grid(row=2, column=0, columnspan=999, sticky="ew") #Places label on window
        
        #Team Name label
        team_label=ttk.Label(master=viewteam, text=f'Team: {team_name}', font="Calibri 10 bold", anchor="center")
        team_label.grid(row=3, column=0, columnspan=999, sticky="ew") #Places label on window

        #Configures the Treeview widget to display player stats
        viewteam.grid_columnconfigure(0, weight=1)
        tree=ttk.Treeview(viewteam, columns=("Position","GamesPlayed","Goals","Assists","CleanSheets","Tackles","FoulsCommitted","YellowCards","RedCards"), show="headings")

        #Sets column headers
        tree.heading("Position", text="Position")
        tree.heading("GamesPlayed", text="Games Played")
        tree.heading("Goals", text="Goals")
        tree.heading("Assists", text="Assists")
        tree.heading("CleanSheets", text="Clean Sheets")
        tree.heading("Tackles", text="Tackles")
        tree.heading("FoulsCommitted", text="Fouls Committed")
        tree.heading("YellowCards", text="Yellow Cards")
        tree.heading("RedCards", text="Red Cards")

        #Configures the width and alignment of each column in the Treeview
        tree.column("Position", width=120, anchor="center")
        tree.column("GamesPlayed", width=120, anchor="center")
        tree.column("Goals", width=120, anchor="center")
        tree.column("Assists", width=120, anchor="center")
        tree.column("CleanSheets", width=120, anchor="center")
        tree.column("Tackles", width=120, anchor="center")
        tree.column("FoulsCommitted", width=120, anchor="center")
        tree.column("YellowCards", width=120, anchor="center")
        tree.column("RedCards", width=120, anchor="center")

        tree.grid(row=4, column=0, padx=10, pady=10, sticky="ew") #Places the Treeview on the window

        self.fetch_data(tree, player_name) #Fetches player data and populates the Treeview







        #Back button to return to the previous screen
        def back(): #Function to go back to previous window
            self.back(viewteam) #Calls back function
        back_button=ttk.Button(master=viewteam, 
                       text="Back",
                       command=back
                       ) #Button to go back to previous page
        back_button.grid(row=6, column=0, columnspan=999, sticky="ew") #Places button on window

    def fetch_data(self, tree, player_name): #Fetches player data from the database and displays it in the Treeview
        try:
            sqlconnection.connect() #Connects to the database

            #Retrieves all player details including stats
            cursor.execute("SELECT Position, GamesPlayed, Goals, Assists, CleanSheets, Tackles, FoulsCommitted, YellowCards, RedCards FROM Players WHERE PlayerName=?", (player_name,))
            player=cursor.fetchone()

            #Clears existing rows in the treeview before inserting new data
            for row in tree.get_children(): 
                tree.delete(row)

            tree.insert("", "end", values=player) #Inserts the player stats into the treeview

            FootballSystem.close() #Close database connection
        
        except sqlite3.Error as error: #Handle any database errors
            tk.messagebox.showinfo("Error", f"Error fetching Player: {error}") #Display error message
    def fetchteam(self, player_name): #Retrieves the team name the player belongs to by using the player's ID and returns it
        try:
            sqlconnection.connect() #Connects to the database
            cursor.execute("SELECT TeamID FROM Players WHERE PlayerName=?", (player_name,))
            TeamID=cursor.fetchone() #Extract TeamID value
            TeamID=TeamID[0] #Fetch TeamID associated with the player
            cursor.execute("SELECT TeamName FROM Team WHERE TeamID=?", (TeamID,))
            team_name=cursor.fetchone() #Fetch team name using TeamID
            team_name=team_name[0] #Extract team name value
            FootballSystem.close() #Close database connection
            return team_name
        except sqlite3.Error as error: #Handle any database errors
            tk.messagebox.showinfo("Error", f"Error fetching Team Name: {error}") #Display error message


class viewplayercaptain(viewplayer): #Inherits from the viewplayer class and overrides the back and next functions for captain's specific views
    def back(self, viewteam): #Closes the current window and navigates back to the view team sheet captain page
            viewteam.withdraw() #Closes the current window
            choice=viewteamsheetcaptain(viewteam) #Creates a new instance of viewteamsheetcaptain
            choice.work() #Calls work function of viewteamsheetcaptain
    def next(self, viewteam, player_name): #Handles the next button logic, hides the current window and opens the edit player stats page
            viewteam.withdraw() #Closes the current window
            choice=editplayerstats(viewteam) #Creates a new instance of editplayerstats
            choice.work(player_name) #Calls work function of editplayerstats
    def work(self, player_name): #Main function to display the player details window for captain, using the parent class' method and adding 'edit stats' button
        super().work(player_name) #Calls the 'work' function of the parent 'viewplayer' class to show player details
        viewteam=self.viewteam #Retrieves the reference to the current window
        
        #Next Button to navigate to the 'editplayerstats' window
        def next():
            self.next(viewteam, player_name) #Calls the next function to navigate to the edit player stats window
        next_button=ttk.Button(master=viewteam, 
                       text="Edit Stats",
                       command=next
                       ) # Creates the Edit Stats button
        next_button.grid(row=5, column=0, columnspan=999, sticky="ew") #Places button on window


class viewteamsheet(): #Manages the back navigation for the viewteamsheet, retrieves the team name based on teamID, and then opens the 'viewteam' window
    def __init__(self, root):
        pass #Initializes the class with root
    def back(self, viewtable, teamID): #Closes the current window and navigates back to the view team page
            viewtable.withdraw() #Closes the current window
            sqlconnection.connect() #Connects to the database
            cursor.execute("SELECT TeamName FROM Team WHERE TeamID=?", (teamID,)) #Retrieves the team name from the database
            team_name=cursor.fetchone() 
            team_name=team_name[0] #Extracts the team name
            FootballSystem.close() #Closes the database connection
            choice=viewteam(viewtable) 
            choice.work(team_name) #Calls the work function of the viewteam with the team name
    def next(self, viewtable, player_name): #Handles the next button logic, hides the current window and opens the view player stats page
        viewtable.withdraw() #Closes the current window
        choice=viewplayer(viewtable) #Creates an instance of the viewplayer
        choice.work(player_name) #Calls the work function of the viewplayer with the player name
    def work(self):
        
        viewtable=tk.Toplevel(login) #Creates a new top-level window for viewing player details and stats
        viewtable.title("View Table") #Sets window title
        viewtable.geometry('1300x450') #Sets window size
        viewtable.protocol("WM_DELETE_WINDOW", closeAPP) #Handles window close event
        self.viewtable=viewtable
    
        #Header label
        header_main=ttk.Label(master=viewtable, text="Football League Table and Player Performance Report System", font="Calibri 10 bold", anchor='center')
        header_main.grid(row=0, column=0, columnspan=999, sticky="ew")#Places label on window

        #Configures the Treeview widget to display players and their stats
        tree=ttk.Treeview(viewtable, columns=("PlayerName","Position","GamesPlayed","Goals","Assists","CleanSheets","Tackles","FoulsCommitted","YellowCards","RedCards"), show="headings")

        #Sets column headers
        tree.heading("PlayerName", text="Player Name")
        tree.heading("Position", text="Position")
        tree.heading("GamesPlayed", text="Games Played")
        tree.heading("Goals", text="Goals")
        tree.heading("Assists", text="Assists")
        tree.heading("CleanSheets", text="Clean Sheets")
        tree.heading("Tackles", text="Tackles")
        tree.heading("FoulsCommitted", text="Fouls Committed")
        tree.heading("YellowCards", text="Yellow Cards")
        tree.heading("RedCards", text="Red Cards")

        #Configures the width and alignment of each column in the Treeview
        tree.column("PlayerName", width=200, anchor="center")
        tree.column("Position", width=120, anchor="center")
        tree.column("GamesPlayed", width=120, anchor="center")
        tree.column("Goals", width=120, anchor="center")
        tree.column("Assists", width=120, anchor="center")
        tree.column("CleanSheets", width=120, anchor="center")
        tree.column("Tackles", width=120, anchor="center")
        tree.column("FoulsCommitted", width=120, anchor="center")
        tree.column("YellowCards", width=120, anchor="center")
        tree.column("RedCards", width=120, anchor="center")

        tree.grid(row=1, column=0, padx=10, pady=10, sticky="ew") #Places the Treeview on the window

        TeamID=self.fetch_data(tree) #Fetches Team ID
        self.teamID=TeamID


        #Defines behavior when a player is selected in the table
        def on_player_click(event):
            selected_player = tree.selection() #Gets the selected player from the table
            if selected_player: #If a player is selected
                item_values = tree.item(selected_player)["values"] #Retrieves the player values
                player_name = item_values[0] #Extracts the player name
                self.next(viewtable, player_name) #Calls the 'next' function to open the player's details

        tree.bind("<<TreeviewSelect>>", on_player_click) #Binds the click event to the function

        
        #Back button to return to the previous screen
        def back(): #Function to go back to previous window
            self.back(viewtable, TeamID) #Calls back function
        back_button=ttk.Button(master=viewtable, 
                       text="Back",
                       command=back
                       ) #Button to go back to previous page
        back_button.grid(row=2, column=0, columnspan=999, sticky="ew") #Places button on window

    #Fetches the data from the database for the team and fills the treeview with player stats
    def fetch_data(self, tree):
        try:
            sqlconnection.connect() #Connects to the database
            Captain_Username1=username_list[0] #Retrieves the current captain's username
            cursor.execute("SELECT UserID FROM Login WHERE Username=?", (Captain_Username1,))
            UserID=cursor.fetchone()
            UserID=UserID[0] #Extracts the user ID
            cursor.execute("SELECT TeamID FROM Team WHERE UserID=?", (UserID,))
            TeamID=cursor.fetchone()
            TeamID=TeamID[0] #Extracts the team ID
            #Retrieves player statistics for the selected team, ordered by games played
            cursor.execute("SELECT PlayerName, Position, GamesPlayed, Goals, Assists, CleanSheets, Tackles, FoulsCommitted, YellowCards, RedCards FROM Players WHERE TeamID=? ORDER BY GamesPlayed DESC", (TeamID,))
            players=cursor.fetchall()


            #Clears existing rows in the treeview
            for row in tree.get_children():
                tree.delete(row)

            #Inserts the player data into the treeview
            for player in players:
                tree.insert("", "end", values=player)

            FootballSystem.close() #Closes the database connection
            return TeamID #Returns the team ID
        except sqlite3.Error as error: #Handle any database errors
            tk.messagebox.showinfo("Error", f"Error fetching players: {error}") #Display error message


class viewteamsheetcaptain(viewteamsheet): #Inherits from the viewteamsheet class and overrides the back and next functions for captain's specific views
    def back(self, viewtable, teamID): #Closes the current window and navigates back to the team admin home page
            viewtable.withdraw() #Closes the current window
            #loginwindow=tk.Toplevel()
            choice=teamadmin_home_page(viewtable) #Creates an instance of the teamadmin_home_page
            choice.work() #Calls the work function of the viewplayer with the teamadmin_home_page
    def next(self, viewtable, player_name): #Handles the next button logic, hides the current window and opens the view player captain page
        viewtable.withdraw() #Closes the current window
        choice=viewplayercaptain(viewtable)#Creates an instance of the viewplayercaptain page
        choice.work(player_name) #Calls the work function of the viewplayer with the viewplayercaptain page
    def work(self): #Main function to display the team sheet for the captain, with functionality to select a player and view their details
        super().work() #Calls the 'work' function of the parent class 'viewteamsheet'
        viewtable=self.viewtable #Assigns the viewtable to an instance variable

        #Back button to return to the previous screen
        def back():
            teamID=self.teamID #Retrieves the team ID from the instance variable
            self.back(viewtable, teamID)  #Calls the 'back' function to go back to the previous view
        back_button=ttk.Button(master=viewtable, 
                       text="Back",
                       command=back
                       ) #Creates the Back button
        back_button.grid(row=2, column=0, columnspan=999, sticky="ew") #Places button on window


class createnewplayer: #class to create new player in logged in team captains team
    def __init__(self, root):
        pass #Initializes the class with root
    def work(self):
        createteam=tk.Toplevel(login) #Creates a new window for creating player
        createteam.title("Create New Team") #Sets the window title
        createteam.geometry('900x450') #Sets the window size
        createteam.protocol("WM_DELETE_WINDOW", closeAPP) #Handles window close event
        


        def back(): #Closes the current window and navigates back to the team admin home page
            createteam.withdraw() #Closes the current window
            choice=teamadmin_home_page(createteam) #Creates a new instance of teamadmin_home_page
            choice.work() #Calls work function of teamadmin_home_page
        def submit():
            PlayerName1=PlayerName.get().strip() #retrieves playername and removes spaces at beginning or end
            Position1=Position.get() #retrieves position 
            Captain_Username1=username_list[0]
            sqlconnection.connect() #connects to database
            cursor.execute("SELECT UserID FROM Login WHERE Username=?", (Captain_Username1,)) #executes command to retrieve userid where username is the captain username
            UserID=cursor.fetchone()
            UserID=UserID[0] #Gets the user ID
            cursor.execute("SELECT TeamID FROM Team WHERE UserID=?", (UserID,)) #executes command to retrieve TeamID where user id is the user id retrieved previously
            TeamID=cursor.fetchone()
            TeamID=TeamID[0] #Gets the team ID
            cursor.execute("INSERT INTO Players (PlayerName, TeamID, Position, GamesPlayed, Goals, Assists, CleanSheets, Tackles, FoulsCommitted, YellowCards, RedCards) VALUES(?, ?, ?, 0, 0, 0, 0, 0, 0, 0, 0)", (PlayerName1, TeamID, Position1)) #executes command to create player in the database using variables retrieved
            FootballSystem.commit() #commits changes
            FootballSystem.close() #closes database
            back()#exits to team admin home page

            tk.messagebox.showinfo("Success", "Player Created Successfully") #displays success message


        def validate_inputs(): #validates inputs and makes sure that user selected player name and position
            if PlayerName.get().strip()=="": #checks if user did not enter player name
                tk.messagebox.showinfo("Error", "Player Name cannot be blank.") #displays error message if not entered
            elif Position.get()=="Select Position": #checks if user did not select player position
                tk.messagebox.showinfo("Error", "Please select a position from the dropdown.") #displays error message if not selected
                
            else: #if both are valid then calls submit function
                submit()
            
        


        #Header
        header_main=ttk.Label(master=createteam, text="Football League Table and Player Performance Report System", font="Calibri 10 bold")
        header_main.grid(row=0, columnspan=2)


        frame=ttk.Frame(createteam)
        frame.grid(rowspan=10, columnspan=2)


        #Create New Team text
        createteamtitle_main=ttk.Label(master=createteam, text="Create New Player", font="Calibri 30 bold")
        createteamtitle_main.grid(row=1, columnspan=2)

        #Text for all required fields to create team
        Playername_Text=ttk.Label(master=createteam, text="Player Name", font="Calibri 10 bold")
        Playername_Text.grid(row=2, column=0)
        Position_text=ttk.Label(master=createteam, text="Position", font="Calibri 10 bold")
        Position_text.grid(row=3, column=0)


        #Text Entry's for all fields
        PlayerName=tk.StringVar()
        PlayerName_Entry=ttk.Entry(
            master=createteam,
            textvariable=PlayerName
        )
        PlayerName_Entry.grid(row=2, column=1)

        position_options=["GK", "RB", "CB", "LB", "RWB", "LWB", "CDM", "CM", "CAM", "RM", "LM", "RW", "LW", "CF", "ST"]

        Position=tk.StringVar()
        Position_dropdown=ttk.Combobox(
            master=createteam,
            textvariable=Position, 
            values=position_options, 
            state="readonly"
        )
        Position_dropdown.grid(row=3, column=1)
        Position_dropdown.set("Select Position") 




        #Submit Button
        submit_button=ttk.Button(master=createteam, 
                       text="Submit",
                       command=validate_inputs
                       )
        submit_button.grid(row=6, column=0, pady=10, columnspan=999, sticky='ew')

        #Back Button
        back_button=ttk.Button(master=createteam, 
                       text="Back",
                       command=back
                       )
        back_button.grid(row=10, column=0, pady=10, columnspan=999, sticky='ew')


class viewgameweek: #class to view fixtures in a gameweek
    def __init__(self, root):
        pass #Initializes the class with root
    def back(self, viewweeks): #Closes the current window and navigates back to the view fixtures page
            viewweeks.withdraw() #Closes the current window
            choice=viewfixtures(viewweeks) #Creates a new instance of teamadmin_home_page
            choice.work() #Calls work function of teamadmin_home_page
    def work(self, gameweekID): 
        self.viewweeks=tk.Toplevel(login) #Creates a new window for transfer requests
        self.viewweeks.title("View Fixtures") #Sets window title
        self.viewweeks.geometry('1200x450') #Sets window size
        viewweeks=self.viewweeks
        viewweeks.protocol("WM_DELETE_WINDOW", closeAPP) #Handles window close event

        #Header label
        header_main=ttk.Label(master=viewweeks, text="Football League Table and Player Performance Report System", font="Calibri 10 bold", anchor='center')
        header_main.grid(row=0, column=0, columnspan=999, sticky="ew")

        #Label for gameweek ID text
        GameweekID_Text=ttk.Label(master=viewweeks, text=f'Gameweek ID: {gameweekID}', font="Calibri 15 bold", anchor='center')
        GameweekID_Text.grid(row=1, column=0, columnspan=999, sticky="ew")

        #Warning telling user that each fixture can only have its score updated once. This is to prevent extra points being added to the table
        tk.messagebox.showinfo("Warning", "Each fixture can only have its score updated once, if you make a mistake while updating the scores, please contact Muhammad Abdur Rehman")

        #Configures the Treeview widget to display fixtures for this gameweek
        self.tree=ttk.Treeview(viewweeks, columns=("FixtureID", "HomeTeam", "HomeScore", "-",  "AwayScore", "AwayTeam"), show="headings")
        tree=self.tree

        #Sets column headers
        tree.heading("FixtureID", text="Fixture ID")
        tree.heading("HomeTeam", text="Home Team")
        tree.heading("HomeScore", text="Home Score")
        tree.heading("-", text="-")
        tree.heading("AwayScore", text="Away Score")
        tree.heading("AwayTeam", text="Away Team")

        #Configures the width and alignment of each column in the Treeview
        tree.column("FixtureID", width=150, anchor="center")
        tree.column("HomeTeam", width=150, anchor="center")
        tree.column("HomeScore", width=150, anchor="center")
        tree.column("-", width=150, anchor="center")
        tree.column("AwayScore", width=150, anchor="center")
        tree.column("AwayTeam", width=150, anchor="center")

        tree.grid(row=2, column=0, columnspan=6, padx=10, pady=10, sticky="ew") #Places the Treeview on the window

        sqlconnection.connect()
        cursor.execute("""SELECT FixtureID, HomeTeam, HomeTeamGoals, AwayTeamGoals, AwayTeam FROM Fixture WHERE GameweekID=?""", (gameweekID,))
        self.fixtures=cursor.fetchall()
        fixtures=self.fixtures

        self.score_entries = {}

        for fixture in fixtures:
            fixtureID, home_team, home_score, away_score, away_team=fixture
            
            
            tree.insert("", "end", values=(fixtureID, home_team, home_score, "-", away_score, away_team))

            if home_score is not None:
                home_var = tk.StringVar(value=str(home_score))
            else:
                home_var = tk.StringVar(value="")
            if away_score is not None:
                away_var = tk.StringVar(value=str(away_score))
            else:
                away_var = tk.StringVar(value="")
            
            self.away_var=away_var
            self.home_var=home_var
            self.score_entries[fixtureID] = (home_var, away_var, home_team, away_team)


        
        

        #Back Button
        def back():
            self.back(viewweeks)
            FootballSystem.close()
        back_button=ttk.Button(master=viewweeks, 
                       text="Back",
                       command=back
                       )
        back_button.grid(row=1000, column=0, columnspan=999, sticky="ew", pady=5)


class viewgameweekadmin(viewgameweek): #Inherits from the viewgameweek class and overrides the back function for admin specific views. Adds ability to edit scores for admins
    def back(self, viewweeks): #Closes the current window and navigates back to the view fixtures admin page
            viewweeks.withdraw() #Closes the current window
            choice=viewfixturesadmin(viewweeks) #Creates a new instance of viewfixturesadmin
            choice.work() #Calls work function of viewfixturesadmin
    def work(self, gameweekID): #Function that adds score editing for admins
        super().work(gameweekID) #Calls the 'work' function of the parent 'viewgameweek' class to show fixtures
        viewweeks=self.viewweeks #Retrieves the reference to the current window
        entryFrame = ttk.Frame(viewweeks) #adds frame where score entries will go
        
        #These are used to keep track of score variables for each fixture
        home_var=self.home_var #Retrieves the reference to home var
        away_var=self.away_var #Retrieves the reference to away var
        fixtures=self.fixtures #Retrieves the reference to 'fixtures' list

        #This loop creates editable entry fields for each fixture
        for fixture in fixtures:
            fixtureID, home_team, home_score, away_score, away_team=fixture

            #If the scores already exist, they’re filled in the entries
            if home_score is not None:
                home_var=tk.StringVar(value=str(home_score))
            else:
                home_var=tk.StringVar(value="")
            if away_score is not None:
                away_var=tk.StringVar(value=str(away_score))
            else:
                away_var=tk.StringVar(value="")
            
            #Stores the values in the score_entries dictionary so they can be accessed later
            self.score_entries[fixtureID]=(home_var, away_var, home_team, away_team)

            #Creates label and entry boxes for each fixture
            entryFrame=ttk.Frame(viewweeks)
            ttk.Label(entryFrame, text=f"{home_team} vs {away_team}").pack(side="left")
            ttk.Entry(entryFrame, textvariable=home_var, width=5).pack(side="left")
            ttk.Label(entryFrame, text=":").pack(side="left")
            ttk.Entry(entryFrame, textvariable=away_var, width=5).pack(side="left")

            #Places the frame in the window
            entryFrame.grid(row=3+fixtureID, column=0, columnspan=6, pady=2)
        score_entries=self.score_entries #Gets access to the dictionary of entry fields
        def submit_scores(): #function runs when the submit button is pressed
            for fixtureID in score_entries:
                    home_var=score_entries[fixtureID][0] #Gets the home team's score entry field for this fixture
                    away_var=score_entries[fixtureID][1] #Gets the away team's score entry field for this fixture
                    home_team=score_entries[fixtureID][2] #Gets the name of the home team for this fixture
                    away_team=score_entries[fixtureID][3] #Gets the name of the away team for this fixture

                    #Gets the scores from the entry fields
                    home_score1 = home_var.get().strip()
                    away_score1 = away_var.get().strip()
                    
                    #Validates scores. If they are missing or invalid it stops
                    if not home_score1 or not away_score1:
                        tk.messagebox.showinfo("Error", f"Score input for fixture {fixtureID} cannot be empty.")
                        return
        
                    if not home_score1.isdigit() or not away_score1.isdigit():
                        tk.messagebox.showinfo("Error", f"Invalid score input for fixture {fixtureID}. Please enter valid integers.")
                        return
                    
                    #Converts the score strings to integers
                    home_score=int(home_score1)
                    away_score=int(away_score1)

                    win=3
                    draw=1
                    #Checks if the fixture has already been processed
                    cursor.execute("SELECT processed FROM Fixture WHERE FixtureID=?", (fixtureID,))
                    processed = cursor.fetchone()[0]

                    if processed: #Stops duplicate updates if the fixture was already done to prevent extra points being added
                        tk.messagebox.showinfo("Error", f"Fixture {fixtureID} has already been processed")
                        continue

                    #Updates the scores in the fixture table
                    cursor.execute("UPDATE Fixture SET HomeTeamGoals=?, AwayTeamGoals=? WHERE FixtureID=?", 
                           (home_score, away_score, fixtureID))
                    
                    #Updates stats for both teams
                    cursor.execute("UPDATE Team SET GamesPlayed=GamesPlayed+1, GoalsFor=GoalsFor+?, GoalsAgainst=GoalsAgainst+? WHERE TeamName=?", (home_score, away_score, home_team))
                    cursor.execute("UPDATE Team SET GamesPlayed=GamesPlayed+1, GoalsFor=GoalsFor+?, GoalsAgainst=GoalsAgainst+? WHERE TeamName=?", (away_score, home_score, away_team))

                    #Gets the updated stats for goal difference calculation
                    cursor.execute("SELECT GoalsFor, GoalsAgainst, GoalDifference FROM Team WHERE TeamName=?", (home_team,))
                    home_stats=cursor.fetchone()
                    cursor.execute("SELECT GoalsFor, GoalsAgainst, GoalDifference FROM Team WHERE TeamName=?", (away_team,))
                    away_stats=cursor.fetchone()

                    #Recalculates goal difference for both teams
                    homeGF=home_stats[0]+home_score
                    homeGA=home_stats[1]+away_score
                    homeGD=homeGF-homeGA
        
                    awayGF=away_stats[0]+away_score
                    awayGA=away_stats[1]+home_score
                    awayGD=awayGF-awayGA
                    
                    cursor.execute("UPDATE Team SET GoalDifference=? WHERE TeamName=?", (homeGD, home_team))
                    cursor.execute("UPDATE Team SET GoalDifference=? WHERE TeamName=?", (awayGD, away_team))

                    #Adds points depending on result
                    if home_score>away_score:
                        cursor.execute("UPDATE Team SET Points=Points+?, Wins=Wins+1 WHERE TeamName=?", (win, home_team))
                        cursor.execute("UPDATE Team SET Losses=Losses+1 WHERE TeamName=?", (away_team, ))
                    elif home_score<away_score:
                        cursor.execute("UPDATE Team SET Points=Points+? WHERE TeamName=?", (win, away_team))
                        cursor.execute("UPDATE Team SET Losses=Losses+1 WHERE TeamName=?", (home_team, ))
                    else:
                        cursor.execute("UPDATE Team SET Points=Points+?, Draws=Draws+1 WHERE TeamName=?", (draw, home_team))
                        cursor.execute("UPDATE Team SET Points=Points+?, Draws=Draws+1 WHERE TeamName=?", (draw, away_team))
                    #Marks the fixture as processed to prevent repeat updates
                    cursor.execute("UPDATE Fixture SET processed=1 WHERE FixtureID=?", (fixtureID,))
                

    
            FootballSystem.commit() #Commmits changes to the database
            tk.messagebox.showinfo("Success", "Scores have been updated") #Success message pops up

        
        #Button that calls the submit_scores function when clicked
        submit_button=ttk.Button(master=viewweeks, 
                       text="Submit",
                       command=submit_scores
                       )
        submit_button.grid(row=999, column=0, columnspan=999, sticky="ew", pady=5)


class viewfixtures: #class to view gameweeks in a season
    def __init__(self, root):
        pass #Initializes the class with root
    def back(self, viewfixtures): #Closes the current window and navigates back to the login page
            viewfixtures.withdraw() #Closes the current window
            loginwindow=tk.Toplevel() #Creates a new top-level window
            choice=loginpage() #Creates a new instance of loginpage
            choice.work(loginwindow) #Calls work function of loginpage
    def work(self):
        self.viewfixtures=tk.Toplevel(login) #Creates a new top-level window for viewing gameweeks
        viewfixtures=self.viewfixtures
        viewfixtures.title("View Gameweek") #Sets window title
        viewfixtures.geometry('1200x450') #Sets window size
        viewfixtures.protocol("WM_DELETE_WINDOW", closeAPP) #Handles window close event
        def generate(): #function to generate fixtures
            generate_fixtures.work() #calls the 'work' function of the 'generate_fixtures' class

        #Header
        header_main=ttk.Label(master=viewfixtures, text="Football League Table and Player Performance Report System", font="Calibri 10 bold", anchor='center')
        header_main.grid(row=0, column=0, columnspan=999, sticky="ew")


        sqlconnection.connect() #Connects to the database
        cursor.execute("SELECT FixtureID FROM Fixture") #fetches FixtureIDs from database
        fixtures=cursor.fetchall()#stores FixtureIDs in list
        if not fixtures: #If list is empty, displays text saying there are no fixtures and tells guest user to contact admin
            No_fixtures_Text=ttk.Label(master=viewfixtures, text="There are no fixtures currently, please contact League Admin", font="Calibri 20 bold", anchor='center')
            No_fixtures_Text.grid(row=1, column=0, columnspan=999, sticky="ew")


        else: #Displays list of gameweeks
            cursor.execute("SELECT MAX(SeasonID) FROM LeagueTable") #Gets the most recent season ID from the LeagueTable
            seasonID=cursor.fetchone()
            seasonID=seasonID[0] #Extracts the season ID

            #Season ID label
            SeasonID_Text=ttk.Label(master=viewfixtures, text=f'Season ID: {seasonID}', font="Calibri 15 bold", anchor='center')
            SeasonID_Text.grid(row=1, column=0, columnspan=999, sticky="ew")
            
            self.tree=ttk.Treeview(viewfixtures, columns=("Gameweek", "Gameweek_ID"), show="headings") #Initialises the treeview to show gameweeks
            tree=self.tree 
            tree.heading("Gameweek", text="Gameweek") #Sets heading for the gameweek number
            tree.heading("Gameweek_ID", text="Gameweek ID") #Sets heading for the actual GameweekID in the database
            tree.column("Gameweek_ID", width=200, anchor="center") #Configures width/alignment
            tree.column("Gameweek", width=200, anchor="center") #Configures width/alignment
            tree.grid(row=2, column=0, padx=10, pady=10, sticky="ew") #Places the tree on the window

            self.fetch_data(tree, seasonID) #Calls a function to fetch and display the actual data in the treeview

            def on_gameweek_click(event): #Runs when a gameweek row is clicked
                selected_week = tree.selection()
                if selected_week:
                    item_values = tree.item(selected_week)["values"]
                    gameweekID = item_values[1] #Gets the gameweek ID from the selected row
                    viewfixtures.withdraw() #Closes this window
                    choice=viewgameweek(viewfixtures) #Creates a new instance of viewgameweek
                    choice.work(gameweekID) #Calls work function of viewgameweek

            tree.bind("<<TreeviewSelect>>", on_gameweek_click) #Links the above function to the click event





        #Back button to return to the previous screen
        def back(): #Function to go back to previous window
            self.back(viewfixtures) #Calls back function
        back_button=ttk.Button(master=viewfixtures, 
                       text="Back",
                       command=back
                       ) #Button to go back to previous page
        back_button.grid(row=3, column=0, columnspan=999, sticky="ew", pady=5) #Places button on window
        
    def fetch_data(self, tree, seasonID): #This function fetches gameweek data for a given season
        try:
            sqlconnection.connect() #Connects to database


            cursor.execute("SELECT GameweekID FROM Gameweek WHERE SeasonID=? ORDER BY GameweekID ASC", (seasonID,))
            Gameweeks=[row[0] for row in cursor.fetchall()] #Stores a list of all gameweek IDs

            #Clears existing rows in the tree
            for row in tree.get_children():
                tree.delete(row)

            #Loops through gameweeks and adds them to the tree
            for x, gameweekID in enumerate(Gameweeks, start=1): 
                tree.insert("", "end", values=(x, gameweekID))


            FootballSystem.close() #Closes the database connection
        
        except sqlite3.Error as error: #Handle any database errors
            tk.messagebox.showinfo("Error", f"Error fetching gameweeks: {error}") #Display error message


class viewfixturesadmin(viewfixtures): #Class inherits from 'viewfixtures' and is used by admins to view gameweeks
    def back(self, viewfixtures): #Closes the current window and navigates back to the view admin league table(admin home page)
            viewfixtures.withdraw() #Closes the current window
            choice=admin_home_page(viewfixtures) #Creates a new instance of admin league table(admin home page)
            choice.work() #Calls work function of admin league table(admin home page)
    def work(self):
        super().work() #Calls the original viewfixtures work() to reuse the same layout and logic
        def generate(): #Function for generating fixtures
            generate_fixtures.work() #Calls the generate fixtures class's work function
        viewfixtures=self.viewfixtures
        
        #Header
        header_main=ttk.Label(master=viewfixtures, text="Football League Table and Player Performance Report System", font="Calibri 10 bold", anchor='center')
        header_main.grid(row=0, column=0, columnspan=999, sticky="ew")
        
        sqlconnection.connect() #Connects to the database
        cursor.execute("SELECT FixtureID FROM Fixture") #fetches FixtureIDs from database
        fixtures=cursor.fetchall() #stores FixtureIDs in list
        if not fixtures:  #If list is empty(there are no fixtures), displays text saying there are no fixtures and tells guest user to contact admin
            No_fixtures_Text=ttk.Label(master=viewfixtures, text="There are no fixtures currently, would you like to generate them? \nONLY DO THIS ONCE ALL TEAMS HAVE BEEN CREATED", font="Calibri 20 bold", anchor='center')
            No_fixtures_Text.grid(row=1, column=0, columnspan=999, sticky="ew") #Displays warning for admins
            Generate_fixtures_button=ttk.Button(master=viewfixtures, text="Generate", command=generate) #Button to generate fixtures
            Generate_fixtures_button.grid(row=2, column=0, columnspan=999, sticky="ew", pady=5) #Places the button
        else:
            tree=self.tree #Gets the treeview that was created by the parent class
            def on_gameweek1_click(event): #Runs when a gameweek row is clicked
                selected_week = tree.selection()
                if selected_week:
                    item_values = tree.item(selected_week)["values"]
                    gameweekID = item_values[1]
                    viewfixtures.withdraw() #Closes current window
                    choice=viewgameweekadmin(viewfixtures) #Creates a new instance of viewgameweekadmin
                    choice.work(gameweekID) #Calls work function of viewgameweekadmin
            tree.bind("<<TreeviewSelect>>", on_gameweek1_click) #Links the above function to the click event


class viewteamadmin(): #This class allows the admin to view a specific team’s stats and fixtures
    def __init__(self, root): 
        pass #Initializes the class with root
    def back(self, viewteam): #Function to go back to the viewtableadmin page
        viewteam.withdraw() #Closes the current window
        choice=viewtableadmin(viewteam) #Creates a new instance of viewtableadmin
        choice.work() #Calls work function of viewtableadmin
    def work(self, team_name):
        
        viewteam=tk.Toplevel(login) #Creates a new top-level window for viewing teams
        viewteam.title("View Team") #Sets window title
        viewteam.geometry('1200x550') #Sets window size
        self.viewteam=viewteam
        viewteam.protocol("WM_DELETE_WINDOW", closeAPP) #Handles window close even

        #Header
        header_main=ttk.Label(master=viewteam, text="Football League Table and Player Performance Report System", font="Calibri 10 bold", anchor="center")
        header_main.grid(row=0, column=0, columnspan=999, sticky="ew")

        #Team name label
        team_label=ttk.Label(master=viewteam, text=team_name, font="Calibri 20 bold", anchor="center")
        team_label.grid(row=1, column=0, columnspan=999, sticky="ew")

        #Gets the captain name for the team           
        captain_name=self.fetchcaptain(team_name)

        #Captain name label
        team_label=ttk.Label(master=viewteam, text=f'Captain: {captain_name}', font="Calibri 10 bold", anchor="center")
        team_label.grid(row=2, column=0, columnspan=999, sticky="ew")

        #Sets up treeview for team stats
        viewteam.grid_columnconfigure(0, weight=1)
        tree=ttk.Treeview(viewteam, columns=("Points","GamesPlayed","Wins","Draws","Losses","GoalsFor","GoalsAgainst","GoalDifference"), show="headings")

        #Adds headings 
        tree.heading("Points", text="Points")
        tree.heading("GamesPlayed", text="Games Played")
        tree.heading("Wins", text="Wins")
        tree.heading("Draws", text="Draws")
        tree.heading("Losses", text="Losses")
        tree.heading("GoalsFor", text="Goals For")
        tree.heading("GoalsAgainst", text="Goals Against")
        tree.heading("GoalDifference", text="Goal Difference")

        #Configures column width and alignment
        tree.column("Points", width=120, anchor="center")
        tree.column("GamesPlayed", width=120, anchor="center")
        tree.column("Wins", width=120, anchor="center")
        tree.column("Draws", width=120, anchor="center")
        tree.column("Losses", width=120, anchor="center")
        tree.column("GoalsFor", width=120, anchor="center")
        tree.column("GoalsAgainst", width=120, anchor="center")
        tree.column("GoalDifference", width=120, anchor="center")

        tree.grid(row=3, column=0, padx=10, pady=10, sticky="ew") #places tree on window

        self.fetch_data(tree, team_name) #Gets the actual team stats and displays them

        #Creates a second treeview for fixtures the team has played
        tree=ttk.Treeview(viewteam, columns=("GameweekID", "FixtureID", "HomeTeam", "HomeScore", "-",  "AwayScore", "AwayTeam"), show="headings")

        #Adds headings
        tree.heading("GameweekID", text="Gameweek ID")
        tree.heading("FixtureID", text="Fixture ID")
        tree.heading("HomeTeam", text="Home Team")
        tree.heading("HomeScore", text="Home Score")
        tree.heading("-", text="-")
        tree.heading("AwayScore", text="Away Score")
        tree.heading("AwayTeam", text="Away Team")

        #Configures column width and alignment
        tree.column("GameweekID", width=150, anchor="center")
        tree.column("FixtureID", width=150, anchor="center")
        tree.column("HomeTeam", width=150, anchor="center")
        tree.column("HomeScore", width=150, anchor="center")
        tree.column("-", width=150, anchor="center")
        tree.column("AwayScore", width=150, anchor="center")
        tree.column("AwayTeam", width=150, anchor="center")

        tree.grid(row=4, column=0, columnspan=6, padx=10, pady=10, sticky="ew") #places tree on window

        #Gets all fixtures where this team was the home or away team
        sqlconnection.connect() #connects to database
        cursor.execute("""SELECT GameweekID, FixtureID, HomeTeam, HomeTeamGoals, AwayTeamGoals, AwayTeam FROM Fixture WHERE HomeTeam=?""", (team_name,))
        homefixtures=cursor.fetchall()
        cursor.execute("""SELECT GameweekID, FixtureID, HomeTeam, HomeTeamGoals, AwayTeamGoals, AwayTeam FROM Fixture WHERE AwayTeam=?""", (team_name,))
        awayfixtures=cursor.fetchall()
        fixtures=homefixtures+awayfixtures #Combines homefixtures and awayfixtures lists

        #Inserts all fixtures into the table
        for fixture in fixtures:
            GameweekID, fixtureID, home_team, home_score, away_score, away_team  = fixture
            
            
            tree.insert("", "end", values=(GameweekID, fixtureID, home_team, home_score, "-", away_score, away_team))

            #These are used if score inputs are needed (but not used in this class)
            if home_score is not None:
                home_var=tk.StringVar(value=str(home_score))
            else:
                home_var=tk.StringVar(value="")
            if away_score is not None:
                away_var=tk.StringVar(value=str(away_score))
            else:
                away_var=tk.StringVar(value="")






        #Back button to return to the previous screen
        def back(): #Function to go back to previous window
            self.back(viewteam) #Calls back function
        back_button=ttk.Button(master=viewteam, 
                       text="Back",
                       command=back
                       ) #Button to go back to previous page
        back_button.grid(row=6, column=0, columnspan=999, sticky="ew") #Places button on window

    def fetch_data(self, tree, team_name): #Fetches team stats from the database
        try:
            sqlconnection.connect() #connects to database

            #Retrieves all teams in order of points
            cursor.execute("SELECT Points, GamesPlayed, Wins, Draws, Losses, GoalsFor, GoalsAgainst, GoalDifference FROM Team WHERE TeamName=?", (team_name,))
            teams=cursor.fetchone()

            #Clears any existing entries and adds new data
            for row in tree.get_children():
                tree.delete(row)

            tree.insert("", "end", values=teams)

            FootballSystem.close() #closes database connection
        
        except sqlite3.Error as error: #Handle any database errors
            tk.messagebox.showinfo("Error", f"Error fetching league table: {error}") #Display error message
    def fetchcaptain(self, team_name): #Gets the captain's username for a team
        try:
            sqlconnection.connect() #connects to database

            #retrieves captain id from Team table where TeamName is same as current team
            cursor.execute("SELECT UserID FROM Team WHERE TeamName=?", (team_name,))
            captainid=cursor.fetchone()
            captainid=captainid[0] 
            
            #Retrieves Username from Login table where UserID is same as captainid
            cursor.execute("SELECT Username FROM Login WHERE UserID=?", (captainid,))
            captain_name=cursor.fetchone()
            captain_name=captain_name[0]
            FootballSystem.close() #closes database connection
            return captain_name #returns captain name
        except sqlite3.Error as error: #Handle any database errors
            tk.messagebox.showinfo("Error", f"Error fetching captain name: {error}") #Display error message


class viewteam(viewteamadmin):  #This class is for the guest user to view team info, it inherits from the admin version but is more limited
    def __init__(self, root):
        pass
    def back(self, viewteam): #Overrides the back button so the user goes to the normal league table, not the admin one
        viewteam.withdraw() #Closes the current window
        choice=viewtable(viewteam) #Creates a new instance of the viewtable
        choice.work() #Calls work function of viewtable
    def next(self, viewteam): #This is used when the user wants to view a specific team's team sheet
        viewteam.withdraw() #Closes the current window
        viewteamsheet2=viewteamsheet(viewteam) #Creates a new instance of the viewteamsheet
        viewteamsheet2.work() #Calls work function of viewteamsheet
    def work(self, team_name):
        super().work(team_name) #Calls the admin version of work to reuse that code(sets up all the fixtures and stats)
        viewteam=self.viewteam
        sqlconnection.connect() #Connects to the database

        #Gets the user ID(captain id) for the team
        cursor.execute("SELECT UserID FROM Team WHERE TeamName=?", (team_name,))
        UserID=cursor.fetchone()
        UserID=UserID[0]

        #Gets the actual username from the user ID
        cursor.execute("SELECT Username FROM login WHERE UserID=?", (UserID,))
        username1=cursor.fetchone()
        username1=username1[0]
        username_list.clear() #Clears any old usernames in the list
        username_list.append(username1) #Stores the username for use in the next screen
        def view_teamsheet(): #Function for when the button is clicked
            self.next(viewteam) #Calls next function
        back_button=ttk.Button(master=viewteam, 
                       text="View Team Sheet",
                       command=view_teamsheet
                       ) #Creates the button for viewing the team sheet
        back_button.grid(row=5, column=0, columnspan=999, sticky="ew") #Places the button on the window
        

class viewtable(): #class to view league table
    def __init__(self, root):
        pass #Initializes the class with root
    def back(self, viewtable): #Closes the current window and navigates back to the login page
            viewtable.withdraw() #Closes the current window
            loginwindow=tk.Toplevel() #Creates a new top-level window
            choice=loginpage() #Creates a new instance of loginpage
            choice.work(loginwindow) #Calls work function of loginpage
    def next(self, viewtable, team_name): #closes current window and opens viewteam page
        viewtable.withdraw() #Closes the current window
        choice=viewteam(viewtable) #Creates a new instance of viewteam
        choice.work(team_name) #Calls work function of viewteam
    def work(self):
        
        viewtable=tk.Toplevel(login)
        viewtable.title("View Table")
        viewtable.geometry('1200x450')
        viewtable.protocol("WM_DELETE_WINDOW", closeAPP)


        #Header
        header_main=ttk.Label(master=viewtable, text="Football League Table and Player Performance Report System", font="Calibri 10 bold", anchor='center')
        header_main.grid(row=0, column=0, columnspan=999, sticky="ew")

        #Treeview for leaguetable
        tree=ttk.Treeview(viewtable, columns=("TeamName","Points","GamesPlayed","Wins","Draws","Losses","GoalsFor","GoalsAgainst","GoalDifference"), show="headings")

        #Sets up column headers
        tree.heading("TeamName", text="Team Name")
        tree.heading("Points", text="Points")
        tree.heading("GamesPlayed", text="Games Played")
        tree.heading("Wins", text="Wins")
        tree.heading("Draws", text="Draws")
        tree.heading("Losses", text="Losses")
        tree.heading("GoalsFor", text="Goals For")
        tree.heading("GoalsAgainst", text="Goals Against")
        tree.heading("GoalDifference", text="Goal Difference")

        #Configures width and alignment of columns
        tree.column("TeamName", width=200, anchor="center")
        tree.column("Points", width=120, anchor="center")
        tree.column("GamesPlayed", width=120, anchor="center")
        tree.column("Wins", width=120, anchor="center")
        tree.column("Draws", width=120, anchor="center")
        tree.column("Losses", width=120, anchor="center")
        tree.column("GoalsFor", width=120, anchor="center")
        tree.column("GoalsAgainst", width=120, anchor="center")
        tree.column("GoalDifference", width=120, anchor="center")

        tree.grid(row=1, column=0, padx=10, pady=10, sticky="ew") #places tree on grid

        self.fetch_data(tree) #fetches data

        def on_team_click(event):
            selected_team = tree.selection()
            if selected_team:
                item_values=tree.item(selected_team)["values"]
                team_name=item_values[0]
                self.next(viewtable, team_name)

        tree.bind("<<TreeviewSelect>>", on_team_click) #binds clicking tree to on_team_click function

        #Back Button
        def back():
            self.back(viewtable)
        back_button=ttk.Button(master=viewtable, 
                       text="Back",
                       command=back
                       )
        back_button.grid(row=2, column=0, columnspan=999, sticky="ew")

    
    def fetch_data(self, tree):
        try:
            sqlconnection.connect() #connects to database

            #Retrieves all teams in order of points
            cursor.execute("SELECT TeamName, Points, GamesPlayed, Wins, Draws, Losses, GoalsFor, GoalsAgainst, GoalDifference FROM Team ORDER BY Points DESC,  GoalDifference DESC, GoalsAgainst ASC")
            teams=cursor.fetchall()

            #deletes all rows in tree
            for row in tree.get_children():
                tree.delete(row)

            #inserts all teams into tree
            for team in teams:
                tree.insert("", "end", values=team)

            FootballSystem.close() #closes database connection
        
        except sqlite3.Error as error: #displays error message
            tk.messagebox.showinfo("Error", f"Error fetching league table: {error}")


class viewtableadmin(viewtable): #this class only exists so that admins go back to their home page or the 'next' function leads to viewteamadmin. Otherwise it is that exact same
    def __init__(self, root):
        pass
    def back(self, viewteam): #leads to admin home page instead of back to login screen
        viewteam.withdraw()
        choice=admin_home_page(viewteam)
        choice.work()
    def next(self, viewtable, team_name): #goes to viewteamadmin instead of viewteam
        viewtable.withdraw()
        choice=viewteamadmin(viewtable)
        choice.work(team_name)
    def work(self): #inherits work function from parent class
        super().work() #Calls the original viewtable work() to reuse the same layout and logic


class createnewteam: #class to create new team
    def __init__(self, root):
        pass
    def work(self):
        createteam=tk.Toplevel(login)
        createteam.title("Create New Team")
        createteam.geometry('900x450')
        createteam.protocol("WM_DELETE_WINDOW", closeAPP)
        


        def back(): #returns to team admin home page
            createteam.withdraw()
            choice=admin_home_page(createteam)
            choice.work()
        def submit(): #submit function to create new team
            TeamName1=TeamName.get() #retrieves team name from entry
            Captain_Username1=Captain_Username.get() #retrieves captain username from entry
            Captain_Password1=Captain_Password.get() #retrieves captain password from entry
            Captain_Password2=passwords.hash(Captain_Password1) #hashes captain password
            sqlconnection.connect()#connects to database
            cursor.execute("INSERT INTO Login (Username, HashedPassword, Permissions) VALUES(?, ?, 2)", (Captain_Username1, Captain_Password2))
            FootballSystem.commit() #commits changes to create new user with captain priveleges
            cursor.execute("SELECT UserID FROM Login WHERE Username=?", (Captain_Username1,))
            UserID=cursor.fetchone()
            UserID=UserID[0] #retrieves created captains user id
            cursor.execute("INSERT INTO Team (TeamName, UserID, Points, GamesPlayed, Wins, Draws, Losses, GoalsFor, GoalsAgainst, GoalDifference ) VALUES(?, ?, 0, 0, 0, 0, 0, 0, 0, 0)", (TeamName1, UserID))
            FootballSystem.commit() #commits changed to create new team
            FootballSystem.close() #closes database connection
            back() #returns to team captain home page

            tk.messagebox.showinfo("Success", "Team Created Successfully") #displays success message


        def validate_inputs(): #validates inputs
            sqlconnection.connect() #connects to database
            cursor.execute("SELECT * FROM Team WHERE TeamName=?", (TeamName.get(),))
            Team_Name=cursor.fetchone() #retrieves all teams
            cursor.execute("SELECT * FROM Login WHERE Username=?", (Captain_Username.get(),))
            CaptainUsername=cursor.fetchone() #retrieves captain username if there is the same as the one entered
            if TeamName.get().strip()=="": #Team name cannot be blank
                tk.messagebox.showinfo("Error", "Team Name cannot be blank.")

            elif Captain_Username.get().strip()=="": #Captain Username cannot be blank
                tk.messagebox.showinfo("Error", "Captain Username cannot be blank.")

            elif Captain_Password.get().strip()=="": #Password cannot be blank
                tk.messagebox.showinfo("Error", "Password cannot be blank.")

            elif Confirm_Password.get().strip()=="": #Confirm Password cannot be blank
                tk.messagebox.showinfo("Error", "Confirm Password cannot be blank.")

            elif Captain_Password.get()!=Confirm_Password.get(): #Passwords do not match
                tk.messagebox.showinfo("Error", "Passwords do not match.")

            elif Team_Name: #Team Name already exists
                tk.messagebox.showinfo("Error", "Team Name already exists.")
                
            elif CaptainUsername: #Captain Username already exists
                tk.messagebox.showinfo("Error", "Captain Username already exists.")
            elif not passwords.validate(Captain_Password.get()): #then validates passwords by using the function
                return
            else:
                FootballSystem.close() #closes connection
                submit() #calls submit function
            
        


        #Header
        header_main=ttk.Label(master=createteam, text="Football League Table and Player Performance Report System", font="Calibri 10 bold")
        header_main.grid(row=0, columnspan=2)


        frame=ttk.Frame(createteam)
        frame.grid(rowspan=10, columnspan=2)


        #Create New Team text
        createteamtitle_main=ttk.Label(master=createteam, text="Create New Team", font="Calibri 30 bold")
        createteamtitle_main.grid(row=1, columnspan=2)

        #Text for all required fields to create team
        Teamname_Text=ttk.Label(master=createteam, text="Team Name", font="Calibri 10 bold")
        Teamname_Text.grid(row=2, column=0)
        CaptainUsername_Text=ttk.Label(master=createteam, text="Captain Username", font="Calibri 10 bold")
        CaptainUsername_Text.grid(row=3, column=0)
        CaptainPassword_Text=ttk.Label(master=createteam, text="Captain Password", font="Calibri 10 bold")
        CaptainPassword_Text.grid(row=4, column=0)
        ConfirmPassword_Text=ttk.Label(master=createteam, text="Confirm Password", font="Calibri 10 bold")
        ConfirmPassword_Text.grid(row=5, column=0)


        #Text Entry's for all fields
        TeamName=tk.StringVar()
        TeamName_Entry=ttk.Entry(
            master=createteam,
            textvariable=TeamName
        )
        TeamName_Entry.grid(row=2, column=1)
        
        #captain username entry and stringvar
        Captain_Username=tk.StringVar()
        CaptainUsername_Entry=ttk.Entry(
            master=createteam,
            textvariable=Captain_Username
        )
        CaptainUsername_Entry.grid(row=3, column=1)

        #captain password entry and stringvar
        Captain_Password=tk.StringVar()
        CaptainPassword_Entry=ttk.Entry(
            master=createteam,
            textvariable=Captain_Password
        )
        CaptainPassword_Entry.config(show="*")
        CaptainPassword_Entry.grid(row=4, column=1)

        #confirm username entry and stringvar
        Confirm_Password=tk.StringVar()
        ConfirmPassword_Entry=ttk.Entry(
            master=createteam,
            textvariable=Confirm_Password
        )
        ConfirmPassword_Entry.config(show="*")
        ConfirmPassword_Entry.grid(row=5, column=1)


        #Submit Button
        submit_button=ttk.Button(master=createteam, 
                       text="Submit",
                       command=validate_inputs
                       )
        submit_button.grid(row=6, column=0, pady=10, columnspan=999, sticky='ew')

        #Back Button
        back_button=ttk.Button(master=createteam, 
                       text="Back",
                       command=back
                       )
        back_button.grid(row=10, column=0, pady=10, columnspan=999, sticky='ew')


class teamadmin_home_page: #team captain home page
    def __init__(self, root):
        pass
    
    def work(self):
        choice=tk.Toplevel(login)
        choice.title("Football League Table and Player Performance Report System")
        choice.geometry('650x200')
        choice.protocol("WM_DELETE_WINDOW", closeAPP)

        frame=ttk.Frame(choice) 
        frame.grid(rowspan=5, columnspan=2)

        username1=username_list[0] #retrieves captain username

        #header
        header_main=ttk.Label(master=frame, text="Football League Table and Player Performance Report System", font="Calibri 10 bold")
        header_main.grid(row=0, column=0, columnspan=3)

        def newplayer(): #calls createnewplayer class' work function
                choice.withdraw() 
                createnewplayer1=createnewplayer(choice)
                createnewplayer1.work()
        def viewteamsheet1(): #calls viewteamsheetcaptain class' work function
                choice.withdraw()
                viewteamsheet2=viewteamsheetcaptain(choice)
                viewteamsheet2.work()
        def viewtransfers(): #calls viewtransferrequests class' work function
                choice.withdraw()
                viewtransfers1=viewtransferrequests(choice)
                viewtransfers1.work()
        def maketransfers(): #calls requesttransfer class' work function
                choice.withdraw()
                viewtransfers1=requesttransfer(choice)
                viewtransfers1.work()
        def logout(): #returns to login page
            choice.withdraw()
            loginwindow=tk.Toplevel()
            login1=loginpage()
            login1.work(loginwindow)

        #Header
        header_main=ttk.Label(master=frame, text=f"Welcome {username1}", font="Calibri 20 bold")
        header_main.grid(row=1, column=0, columnspan=3)

        #Creates buttons for all functions above
        CreateTeam=ttk.Button(master=frame, width=20, text="Create Player", command=newplayer)
        CreateTeam.grid(row=2, column=0)
        ViewTable=ttk.Button(master=frame, width=20, text="View Team Sheet", command=viewteamsheet1)
        ViewTable.grid(row=2,  column=1, padx=10)
        ViewFixture=ttk.Button(master=frame, width=20, text="View Transfers", command=viewtransfers)
        ViewFixture.grid(row=2,  column=2, padx=10)
        ViewFixture=ttk.Button(master=frame, width=20, text="Request Transfer", command=maketransfers)
        ViewFixture.grid(row=2,  column=3, padx=10)
        logoutButton=ttk.Button(master=frame, width=20, text="Logout", command=logout)
        logoutButton.grid(row=3,  column=0, columnspan=4, sticky="ew", pady="5")


class admin_home_page: #admin home page
    def __init__(self, root):
        pass
    
    def work(self):
        choice=tk.Toplevel(login)
        choice.title("Football League Table and Player Performance Report System")
        choice.geometry('500x200')
        choice.protocol("WM_DELETE_WINDOW", closeAPP)

        frame=ttk.Frame(choice)
        frame.grid(rowspan=5, columnspan=2)

        header_main=ttk.Label(master=frame, text="Football League Table and Player Performance Report System", font="Calibri 10 bold")
        header_main.grid(row=0, column=0, columnspan=3)
        def newteam(): #calls createnewteam class' work function
                choice.withdraw()
                createnewteam1=createnewteam(choice)
                createnewteam1.work()
        def viewtableadmin1(): #calls viewtableadmin class' work function
                choice.withdraw()
                viewadmintable=viewtableadmin(choice)
                viewadmintable.work()
        def viewfixturelist(): #calls viewfixturesadmin class' work function
                choice.withdraw()
                viewfixturelist=viewfixturesadmin(choice)
                viewfixturelist.work()
        def logout(): #returns to login page
            choice.withdraw()
            loginwindow=tk.Toplevel()
            login1=loginpage()
            login1.work(loginwindow)

        
        #Creates buttons for all functions above
        CreateTeam=ttk.Button(master=frame, width=20, text="Create Team", command=newteam)
        CreateTeam.grid(row=2, column=0) #Create Team button
        ViewTable=ttk.Button(master=frame, width=20, text="View Table", command=viewtableadmin1)
        ViewTable.grid(row=2,  column=1, padx=10) #View Table button
        ViewFixture=ttk.Button(master=frame, width=20, text="View Fixtures", command=viewfixturelist)
        ViewFixture.grid(row=2,  column=2, padx=10) #View Fixtures button
        logoutButton=ttk.Button(master=frame, width=20, text="Logout", command=logout) 
        logoutButton.grid(row=3,  column=0, columnspan=3, sticky="ew", pady="5") #Logout button
        

        
class loginpage: #class for the login page
    def __init__(self):
        pass
    def work(self, login):
        login.title('Login')
        login.geometry('350x450')
        login.grid_columnconfigure(0, weight=1)
        login.protocol("WM_DELETE_WINDOW", closeAPP)

        #verifies that username exists and that password is correct and then checks user priveleges 
        def verifypassword():
            #connects to database
            FootballSystem=sqlite3.connect('Footballsystem.db')
            cursor=FootballSystem.cursor()
            password1=password.get()
            username1=username.get()
            #attempts to find username in database
            cursor.execute("SELECT HashedPassword FROM Login WHERE Username=?", (username1,))
            dbpassword=cursor.fetchone()
            if dbpassword is None: #if it does not find any username
                tk.messagebox.showinfo("Error", "Incorrect Username")
            dbpassword=dbpassword[0]
            cursor.execute("SELECT Permissions FROM Login WHERE Username=?", (username1,))
            userpriveleges=cursor.fetchone()
            userpriveleges=userpriveleges[0] #retrieves user privelege level
            FootballSystem.close()
            password2=str(passwords.hash(password1))
            if password2==dbpassword: #if password entered is same as database
                    if userpriveleges==1: #if user privelege level is admin
                        tk.messagebox.showinfo("Login Successful", "Admin Login Success")
                        login.withdraw()
                        #choice=tk.Tk()
                        leaguetable1=admin_home_page(login)
                        leaguetable1.work()
                    else: #if user privelege level is captain
                        tk.messagebox.showinfo("Login Successful", "Team Captain Login Success")
                        login.withdraw()
                        username_list.clear()
                        username_list.append(username1)
                        print(username_list)
                        leaguetable1=teamadmin_home_page(login)
                        leaguetable1.work()
            else: #show error message
                    tk.messagebox.showinfo("Error", "Incorrect Password")
        
        #login process
        def user_login():
            global password, username
            if password.get()=="" and username.get() =="": #if nothing is entered
                ErrorMessages.no_username_password()
            elif password.get()=="": #if password is blank
                ErrorMessages.wrong_password()
            elif username.get()=="": #if username is blank
                ErrorMessages.wrong_username()
            else:
                verifypassword() #calls verifypassword function
                return
        

        #Creates header
        header_main=ttk.Label(master=login, text="Football League Table and Player Performance Report System", font="Calibri 10 bold")
        header_main.grid(row=0, column=1, columnspan=2, pady=10)

        #Login text
        logintitle_main=ttk.Label(master=login, text="Login", font="Calibri 30 bold")
        logintitle_main.grid(row=1, column=1, columnspan=2, pady=10)


        #creates username text
        username_text=ttk.Label(master=login, text="Username", font="Calibri 10 bold")
        username_text.grid(row=2, column=1, pady=10)

        #creates username text entry
        global username
        username=tk.StringVar()
        username_textbox=ttk.Entry(master=login, 
                       textvariable=username
                       )
        username_textbox.grid(row=2, column=2, pady=10)



        #creates password text
        password_text=ttk.Label(master=login, text="Password", font="Calibri 10 bold")
        password_text.grid(row=3, column=1, pady=10)


        #creates password text entry
        global password
        password=tk.StringVar()
        password_textbox=ttk.Entry(master=login, 
                       textvariable=password
                       )
        password_textbox.config(show="*")
        password_textbox.grid(row=3, column=2, pady=10)



        #creates login/submit button
        login_button=ttk.Button(master=login, 
                       text="Login",
                       command=user_login
                       )
        login_button.grid(row=4, column=1, columnspan=2, pady=10, sticky="ew")


        def View_table(): #view table button
            login.withdraw()
            viewtable1=viewtable(login)
            viewtable1.work()
        View_Table=ttk.Button(master=login, 
                       text="View Table",
                       command=View_table
                       )
        View_Table.grid(row=6, column=1, columnspan=1, pady=10, sticky="ew")
        def View_gameweek(): #view gameweek button
            login.withdraw()
            viewgameweek1=viewfixtures(login)
            viewgameweek1.work()
        View_Gameweek=ttk.Button(master=login, 
                       text="View Fixtures",
                       command=View_gameweek
                       )
        View_Gameweek.grid(row=6, column=2, columnspan=1, padx=5, pady=10, sticky="ew")

        def Exit(): #exit function
            login.destroy()
            sys.exit()
        Exit_button=ttk.Button(master=login, 
                       text="Exit",
                       command=Exit
                       ) #exit button
        Exit_button.grid(row=7, column=1, columnspan=2, pady=10, sticky="ew")


def closeAPP(): #function for command when user closes app by clicking the 'x'
    sys.exit() #stops program


#Starts tkinter mainloop
login=tk.Tk()
login.protocol("WM_DELETE_WINDOW", closeAPP)
login_instance=loginpage()
login_instance.work(login)
login.mainloop()