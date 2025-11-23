import sqlite3
import tkinter as tk
from tkinter import *
import ttkbootstrap as ttk
import  tkinter.messagebox


#connects to database
FootballSystem = sqlite3.connect('Footballsystem.db')
cursor = FootballSystem.cursor()
print("Connected to the database")


#Command that creates Login table
login="""CREATE TABLE IF NOT EXISTS Login(
UserID INTEGER PRIMARY KEY AUTOINCREMENT,
Username VARCHAR(50) NOT NULL,
HashedPassword VARCHAR(255) NOT NULL,
Permissions INT NOT NULL
);"""

#Command that creates LeagueTable table
table="""CREATE TABLE IF NOT EXISTS LeagueTable(
SeasonID INTEGER PRIMARY KEY AUTOINCREMENT
);"""

#Command that creates Gameweek table
Gameweek="""CREATE TABLE IF NOT EXISTS Gameweek(
GameweekID INTEGER PRIMARY KEY AUTOINCREMENT,
SeasonID INT,
FOREIGN KEY(SeasonID) REFERENCES LeagueTable(SeasonID)
);"""

#Command that creates Team table
Team="""CREATE TABLE IF NOT EXISTS Team(
TeamID INTEGER PRIMARY KEY AUTOINCREMENT,
TeamName VARCHAR(50) NOT NULL,
UserID INT,
Points INT,
GamesPlayed INT,
Wins INT,
Draws INT,
Losses INT,
GoalsFor INT,
GoalsAgainst INT,
GoalDifference INT,
Transfers INT,
FOREIGN KEY(UserID) REFERENCES Login(UserID)
);"""

#Command that creates Fixture table
Fixture="""CREATE TABLE IF NOT EXISTS Fixture(
FixtureID INTEGER PRIMARY KEY AUTOINCREMENT,
GameweekID INT NOT NULL,
HomeTeam NOT NULL,
AwayTeam NOT NULL, 
HomeTeamGoals INT,
AwayTeamGoals INT,
processed BOOLEAN DEFAULT 0,
FOREIGN KEY(GameweekID) REFERENCES Gameweek(GameweekID)
);"""

#Command that creates Players table
Players="""CREATE TABLE IF NOT EXISTS Players(
PlayerID INTEGER PRIMARY KEY AUTOINCREMENT,
TeamID INT, 
PlayerName VARCHAR(50) NOT NULL,
Position VARCHAR(3) NOT NULL,
GamesPlayed INT VARCHAR(3),
Goals INT VARCHAR(3),
Assists INT VARCHAR(3),
CleanSheets INT VARCHAR(3),
Tackles INT VARCHAR(3),
FoulsCommitted INT VARCHAR(3),
YellowCards INT VARCHAR(3),
RedCards INT VARCHAR(3),
FOREIGN KEY(TeamID) REFERENCES Team(TeamID)
);"""

#Command that creates TransferRequests table
TransferRequests="""CREATE TABLE IF NOT EXISTS TransferRequests(
TransferID INTEGER PRIMARY KEY AUTOINCREMENT,
RequestedID INT VARCHAR(4) NOT NULL,
CurrentID INT VARCHAR(4) NOT NULL,
PlayerID INT VARCHAR(4) NOT NULL,
processed BOOLEAN DEFAULT 0
);"""



#Executes all commands above to create tables
cursor.execute(login)
cursor.execute(table)
cursor.execute(Gameweek)
cursor.execute(Team)
cursor.execute(Fixture)
cursor.execute(Players)
cursor.execute(TransferRequests)

print("Success")

#imports admin create account page
import admincreation


