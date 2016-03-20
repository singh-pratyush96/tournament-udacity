-- Relation to store player information
create table if not exists players (
pid serial primary key,                               -- Player ID
pname varchar(50)                                      -- Player Name
);

-- Relation to store tournament information
create table if not exists tournaments (
tid serial primary key,                   -- Tournament ID
tname varchar(30)                         -- Tournament Name
)

-- Relation for players and tournaments
create table if not exists tournamentplayers (
tid integer references tournaments(tid) not null,     -- Tournament ID
pid integer references players(pid) not null,         -- Player ID
wins integer not null default 0,                      -- Number of wins in the tournament
matches integer not null default 0,                   -- Number of matches in the tournament
lastoppid integer references players(pid) default -1  -- Last opponent played with
);