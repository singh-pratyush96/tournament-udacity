#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from random import randint


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches(tournamentid):
    """Remove all the match records from the database."""
    conn = connect()
    cur = conn.cursor()

    # Reset player scores
    sql = 'update player set wins=0, matches=0 where tid = {0};'.format(tournamentid)
    cur.execute(sql)

    # Reset last opponent id
    sql = 'update lastopp set lastoppid = DEFAULT where tid = {0};'.format(tournamentid)
    cur.execute(sql)

    conn.commit()
    conn.close()


def deletePlayers(tournamentid):
    """Remove all the player records from the database."""
    conn = connect()
    cur = conn.cursor()

    # Delete user from table
    sql = 'delete from player where tid = {0};'.format(tournamentid)
    cur.execute(sql)

    # No user, no matches
    sql = 'delete from lastopp where tid = {0};'.format(tournamentid)
    cur.execute(sql)
    conn.commit()
    conn.close()


def countPlayers(tournamentid):
    """Returns the number of players currently registered."""
    conn = connect()
    cur = conn.cursor()

    # Get count of rows in player relation
    sql = 'select count(*) from player where tid = {0};'.format(tournamentid)
    cur.execute(sql)

    # get result
    player_count = cur.fetchall()[0][0]
    conn.close()
    return player_count


def registerPlayer(tournamentid, name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cur = conn.cursor()

    # Insert new player and get pid
    sql = 'insert into player (name, tid) values(\'{0}\', {1}) returning pid;'.format(name.replace('\'', '\\'''),
                                                                                      tournamentid)
    cur.execute(sql)

    # Insert this pid in last opponent table and set last opponent to default
    newid = cur.fetchall()[0][0]
    sql = 'insert into lastopp (pid, tid) values({0}, {1});'.format(newid, tournamentid)
    cur.execute(sql)

    conn.commit()
    conn.close()


def playerStandings(tournamentid):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cur = conn.cursor()

    # Get standings in order of pid for players who have played no matches
    sql = 'select * from player where matches = 0 and tid = {0} order by pid'.format(tournamentid)
    cur.execute(sql)
    list1 = cur.fetchall()

    # Get standings in order of wins THEN win/matches THEN by pid for others
    sql = 'select * from player where matches > 0 and tid = {0} order by wins desc, wins/matches desc, pid;'.format(
        tournamentid)
    cur.execute(sql)
    list2 = cur.fetchall()

    conn.close()
    return list2 + list1


def reportMatch(tournamentid, winner, loser):
    conn = connect()
    cur = conn.cursor()

    # Update player table with new data
    sql = 'update player set wins = wins + 1, matches = matches + 1 where pid = {0} and tid = {1};'.format(winner,
                                                                                                           tournamentid)
    cur.execute(sql)
    if winner != loser:
        sql = 'update player set matches = matches + 1 where pid = {0} and tid = {1};'.format(loser, tournamentid)
        cur.execute(sql)

    # Update lastopp table with new data
    sql = 'update lastopp set lastoppid = {0} where pid = {1} and tid = {2};'.format(loser, winner, tournamentid)
    cur.execute(sql)
    if winner != loser:
        sql = 'update lastopp set lastoppid = {0} where pid = {1} and tid = {2};'.format(winner, loser, tournamentid)
        cur.execute(sql)

    conn.commit()
    conn.close()


def swissPairings(tournamentid):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect()
    cur = conn.cursor()

    # Get all players with last opponents in order
    sql = 'select pid, name, lastoppid from player natural join lastopp where tid = {0} and matches = 0 order by pid ;'.format(
        tournamentid)
    cur.execute(sql)
    list1 = cur.fetchall()

    sql = 'select pid, name, lastoppid from player natural join lastopp where tid = {0} and matches > 0 order by wins desc, wins/matches desc, pid;'.format(
        tournamentid)
    cur.execute(sql)
    list2 = cur.fetchall()

    players = list2 + list1
    conn.close()

    # If odd players, give one of them a bye
    templist = list(players)
    if len(players) % 2 == 1:
        loop = True
        while loop:
            position = randint(0, len(templist) - 1)
            temp = templist[position]
            if temp[0] != temp[2]:
                players.remove(temp)
                reportMatch(tournamentid, temp[0], temp[0])
                loop = False
            templist.remove(temp)

    # Generate pairings
    pairs = []
    while len(players) > 2:
        player1 = players[0]
        if players[0][2] == players[1][0]:  # If next player in order was previous
            player2 = players[2]
        else:
            player2 = players[1]
        players.remove(player1)
        players.remove(player2)
        pairs.append((player1[0], player1[1], player2[0], player2[1]))

    pairs.append((players[0][0], players[0][1], players[1][0], players[1][1]))
    return pairs
