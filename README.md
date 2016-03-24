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
    
* __Using the functions__
    * Import the `tournament.py` file in the file you wish to work on
    * Adding new tournaments :  
    ```python
    added_tournament_id = addTournament(name_of_tournament)
    ```  
    * Adding new players :  
    ```python
    added_player_id = registerPlayer(name_of_player)
    ```  
    * Adding players to tournaments :  
    ```python
    status = addPlayerTournament(tournament_id, player_id)
    ```  
    * Get the `swiss pairing` for a tournament :  
    ```python
    pairs_list = swissPairings(tournament_id)
    ```  
    * Reporting a match for a tournament between two players :  
    ```python
    status = reportMatch(tournament_id, winner_id, loser_id)
    ```  
    *Note* : Pass same value for `winner_id` and `loser_id` to indicate a bye.  
    * Getting player standings :  
    ```python
    status, player_details_list = playerStandings(tournament_id)
    ```  
    *Note* : To get overall ranking (not for just a tournament) do not pass any argument.  
    * Clearing players, matches and tournaments :  
    ```python
    clearPlayers()
    status = deleteMatches(tournament_id)
    clearTournaments()
    ```  
    *Note* : Pass no argument in `deleteMatches()` to delete matches for all tournaments.