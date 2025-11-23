Football league management system with player performance tracker

Mainly created using python. User Interface made using tkinter and ttkbootstrap. Basic SQL statements used. SQLite used. 8 SQL tables used

Lets a league admin update log in league standings and match scores every week. Generates fixtures at the start of the season and ensures each team plays each other once. Can easily be modified to each team playing twice. Tracks each teams points, goals for, goals against, goal difference, games played, wins, losses and draws

The player performance tracker lets a team captain log in and update player stats and request player transfer. Lets them approve and deny incoming transfer requests. Lets them create a new player and each player is linked to that captains team when created. 


SQL tables
Login(UserID, Username, HashedPassword, Permissions)
LeagueTable(SeasonID)
Gameweek(GameweekID, SeasonID)
Fixture(FixtureID, GameweekID, TeamID(home), TeamID(away), HomeTeam goals, AwayTeam goals, processed)
Team(TeamID, TeamName, UserID, Points, GamesPlayed, Wins, Draws, Loses, GoalsFor, GoalsAgainst, GoalDifference, Transfers)
Players(PlayerID, TeamID, PlayerName, Position, GamesPlayed, Goals, Assists, CleanSheets, Tackles, FoulsCommitted, YellowCards, RedCards)
TransferRequests(TransferID, TeamID(Requested), TeamID(Current), PlayerID, processed)
