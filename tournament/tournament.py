#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

from random import shuffle

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def existsTournament(tournamentid):
    conn = connect()
    cur = conn.cursor()

    sql = 'select count(*) from tournaments where tid = {0};' \
        .format(tournamentid)
    cur.execute(sql)
    result = cur.fetchall()[0][0] == 1

    conn.close()
    return result


def existsTournamentPlayer(tournamentid, pid):
    conn = connect()
    cur = conn.cursor()

    sql = 'select count(*) from tournamentplayer where tid = {0} and pid = {1};'.format(tournamentid, pid)
    cur.execute(sql)
    result = cur.fetchall()[0][0] == 0

    conn.close()
    return result


def deleteMatches(tournamentid=-1):
    """
    Remove all the match records from the database for a tournament.
    If no argument is passed, delete all matches from all tournament.

    Args:
        tournamentid (int): ID of tournament of which matches are to be cleared
                        If no argument passed, reset all matches
    """
    conn = connect()
    cur = conn.cursor()

    if tournamentid == -1:  # If no argument passed
        sql = 'update table tournamentplayer set wins = DEFAULT,' \
              ' matches = DEFAULT, lastoppid = default;'
    else:
        if not existsTournament(tournamentid):
            return False
        sql = 'update table tournamentplayer set wins = DEFAULT,' \
              ' matches = DEFAULT, lastoppid = default where tid = {0};' \
            .format(tournamentid)
    cur.execute(sql)

    conn.commit()
    conn.close()
    return True


def deleteTournamentPlayers(tournamentid=-1):
    """Remove all the player records from the database.

    Args:
        tournamentid (int): Tournament ID of which players are to be deleted.
                    If no argument passed, delete for all tournaments
    """
    conn = connect()
    cur = conn.cursor()

    if tournamentid == -1:  # If no argument passed
        sql = 'delete from tournamentplayer;'
    else:
        if not existsTournament(tournamentid):
            return False
        sql = 'delete from tournamentplayer where tid = {0};' \
            .format(tournamentid)
    cur.execute(sql)

    conn.commit()
    conn.close()
    return True


def countTournamentPlayers(tournamentid=-1):
    """Returns the number of players currently registered.

    Args:
        tournamentid (int): Tournament ID to count players.
                        If no argument, count players participated in any
                         tournament
    """
    conn = connect()
    cur = conn.cursor()

    # Get count of rows in player relation
    if tournamentid == -1:
        sql = 'select count(distinct pid) from tournamentplayer;'
    else:
        if not existsTournament(tournamentid):
            return False, -1
        sql = 'select count(distinct pid) from tournamentplayer' \
              'where tid = {0};'.format(tournamentid)
    cur.execute(sql)

    player_count = cur.fetchall()[0][0]
    conn.close()
    return True, player_count


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cur = conn.cursor()

    sql = 'insert into players (name) values ({0});', format(name)
    cur.execute(sql)

    conn.commit()
    conn.close()


def playerStandings(tournamentid=-1):
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

    if tournamentid == -1:
        sql = 'select pid, pname, cwins, cmatches from players natural join ' \
              '(select pid, count(wins) as cwins, count(matches) as cmatches' \
              ' from tournamentplayers where matches = 0 group by pid)' \
              ' as allinfo order by pid;'
        cur.execute(sql)
        list1 = cur.fetchall()

        sql = 'select pid, pname, cwins, cmatches from players natural join ' \
              '(select pid, count(wins) as cwins, count(matches) as cmatches' \
              ' from tournamentplayers where matches > 0 group by pid)' \
              ' as allinfo order by cwins desc, cwins/cmatches desc, pid;'
        cur.execute(sql)
        list2 = cur.fetchall()
    else:
        if not existsTournament(tournamentid):
            return False, []
        sql = 'select pid, pname, wins, matches from players natural join' \
              ' tournamentplayer where tid = {0} and matches = 0 ' \
              'order by pid;' \
            .format(tournamentid)
        cur.execute(sql)
        list1 = cur.fetchall()

        sql = 'select pid, pname, wins, matches from players natural join' \
              ' tournamentplayer where tid = {0} and matches > 0 ' \
              'order by wins desc, wins/matches desc, pid;' \
            .format(tournamentid)
        cur.execute(sql)
        list2 = cur.fetchall()

    conn.close()
    return True, list2 + list1


def reportMatch(tournamentid, winner, loser):
    conn = connect()
    cur = conn.cursor()

    if not existsTournamentPlayer(tournamentid, winner) or \
            not existsTournamentPlayer(tournamentid, loser):
        return False

    sql = 'update table tournamentplayer set matches = matches + 1,' \
          ' wins = wins + 1, lastopp = {0} where tid = {1} and pid = {2};' \
        .format(loser, tournamentid, winner)
    cur.execute(sql)
    if winner != loser:  # If not a bye
        sql = 'update table tournamentplayer set matches = matches + 1,' \
              ' lastopp = {0} where tid = {1} and pid = {2};' \
            .format(winner, tournamentid, loser)
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

    sql = 'select pid, pname, lastopp from players natural join' \
          ' tournamentplayer where tid = {0} and matches = 0 ' \
          'order by pid;' \
        .format(tournamentid)
    cur.execute(sql)
    list1 = cur.fetchall()

    sql = 'select pid, pname, lastopp from players natural join' \
          ' tournamentplayer where tid = {0} and matches > 0 ' \
          'order by wins desc, wins/matches desc, pid;' \
        .format(tournamentid)
    cur.execute(sql)
    list2 = cur.fetchall()

    players = list2 + list1

    # Odd players, bye one who wasn't byed last time
    if len(players) % 2 == 1:
        tempList = list(players)
        shuffle(tempList)
        byed = False
        while not byed:
            if tempList[0][0] == tempList[0][2]:
                byed = True
                players.remove(tempList[0])
                reportMatch(tournamentid, tempList[0][0], tempList[0][0])
            tempList.remove(tempList[0])

    # Arrange players, no rematch
    pairs = []
    while len(players) > 2:  # No. of players will always be odd
        player1 = players[0]
        player2 = players[1]
        if player1[2] == player2[0]:
            player2 = players[2]
        players.remove(player1)
        players.remove(player2)
        pairs.append((player1[0], player1[1], player2[0], player2[1]))

    # Add remaining two players
    pairs.append((players[0][0], players[0][1], players[1][0], players[1][1]))

    conn.close()
    return pairs