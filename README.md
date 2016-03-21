# Tournament
A database schema to store the game matches between players, implementation according to Swiss system.

### Features
* Swiss pairing of players for matchup. Ranked in order of `number of wins`, then `win to matches ratio` and finally `player ID` (if same values encountered).
* Gives `'bye'` to random player in case of odd players.
* Multiple tournament support.
* No consecutive rematch between players (if there are more than two players).
* A player gets highest `'bye'` streak of 1 (if there are more than 2 players).