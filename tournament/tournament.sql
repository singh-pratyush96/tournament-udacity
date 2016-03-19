-- Relation to store player information
create table if not exists player (
pid serial primary key,               -- Player ID
name varchar(50),                     -- Player Name
wins integer default 0,               -- Number of matches won
matches integer default 0,            -- Number of matches played
tid integer                           -- Tournament ID
);

-- Relation to keep track of last opponent of each player
create table if not exists lastopp (
pid integer primary key not null references player(pid),     -- Player ID
lastoppid integer default -1,         -- Last opponent faced
tid integer                           -- Tournament ID
);