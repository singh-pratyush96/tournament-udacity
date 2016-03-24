# Tournament
A database schema to store the game matches between players, implementation according to Swiss system.

### Features
* Swiss pairing of players for matchup. Ranked in order of `number of wins`, then `win to matches ratio` and finally `player ID` (if same values encountered).
* Gives `'bye'` to random player in case of odd players.
* Multiple tournament support.
* No consecutive rematch between players (if there are more than 2 players).
* A player gets highest `'bye'` streak of 1 (if there are more than 2 players).

### Usage

* __Initializing database__
    * In a terminal, type `sudo su - postgres` to switch to master user of psql.
    * Type `psql` to initiate psql session
    * If the user which wants to use database doesn't exists as a role, type  
    ```
    create user <username> with password <password>;
    ```.
    * Add database `tournament` and grant all permissions to the user :  
    ```
    create database tournament;
    grant all on database tournament to <username>;
    ```  
    * Initiate the tables from the file `tournament.sql` :  
    ```
    \i <path-to-tournament.sql
    ```
    * Close the session by typing `\q` followed by `exit`.
