-- Relation to store player information
create table if not exists players (
pid serial primary key not null,                               -- Player ID
pname varchar(50) not null                                     -- Player Name
);

-- Relation to store tournament information
create table if not exists tournaments (
tid serial primary key not null,                   -- Tournament ID
tname varchar(30) not null                         -- Tournament Name
);

-- Relation for players and tournaments
create table if not exists tournamentplayers (
tid integer references tournaments(tid) not null,     -- Tournament ID
pid integer references players(pid) not null,         -- Player ID
wins integer not null default 0,                      -- Number of wins in the tournament
matches integer not null default 0,                   -- Number of matches in the tournament
lastoppid integer default -1  -- Last opponent played with
);

-- View for getting details for all tournaments
create view if not exists all_tournament_player_stats as
(
(
select pid, pname, cwins, cmatches from
 players
   natural join
 (select pid, sum(wins) as cwins, sum(matches) as cmatches from
   tournamentplayers  group by pid)
where cmatches > 0 order by cwins desc, cwins/cmatches desc, pid
)
union all
(
select pid, pname, cwins, cmatches from
  players
    natural join
  (select pid, sum(wins) as cwins, sum(matches) as cmatches from
    tournamentplayers  group by pid)
where cmatches = 0 order by pid
)
);

-- View for getting tournament wise details
create view if not exists tournament_players_stats as
(
(
select tid, pid, pname, wins, matches from
  players
    natural join
  tournamentplayers
where matches > 0 order by wins desc, wins/matches desc, pid
)
union all
(
select tid, pid, pname, wins, matches from
  players
    natural join
  tournamentplayers
where matches = 0 order by pid
)
);