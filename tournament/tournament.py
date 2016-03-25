#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from random import shuffle


def connect():
    """
    Connect to the PostgreSQL database.
    Returns a database connection and corresponding cursor.
    """
    connection = psycopg2.connect("dbname=tournament")
    cursor = connection.cursor()
    return connection, cursor


def existsPlayer(pid):
    """
    Check if a player exists
    Args:
        pid: Player ID

    Returns: Status

    """
    conn, cur = connect()

    sql = 'select count(*) from players where pid = %s;'
    cur.execute(sql, (pid,))
    result = cur.fetchall()[0][0] == 1

    conn.close()
    return result


def existsTournament(tournamentid):
    """
    Check if a tournament exists

    Args:
        tournamentid: Tournament ID

    Returns: Status

    """
    conn, cur = connect()

    sql = 'select count(*) from tournaments where tid = %s;'
    cur.execute(sql, (tournamentid,))
    result = cur.fetchall()[0][0] == 1

    conn.close()
    return result


def existsTournamentPlayer(tournamentid, pid):
    """
    Check if a player is registered for a tournament
    Args:
        tournamentid: Tournament ID
        pid: Player ID

    Returns: Status

    """
    conn, cur = connect()

    sql = 'select count(*) from tournamentplayers where tid = %s and pid = %s;'
    cur.execute(sql, (tournamentid, pid))
    result = cur.fetchall()[0][0] == 1

    conn.close()
    return result


def deleteMatches(tournamentid=-1):
    """
    Remove all the match records from the database for a tournament.
    If no argument is passed, delete all matches from all tournament.

    Args:
        tournamentid (int): ID of tournament of which matches are to be cleared
                        If no argument passed, reset all matches
    Returns: Status
    """
    conn, cur = connect()

    if tournamentid == -1:  # If no argument passed
        sql = 'update tournamentplayers set wins = DEFAULT,' \
              ' matches = DEFAULT, lastoppid = default;'
        cur.execute(sql)
    else:
        if not existsTournament(tournamentid):
            conn.close()
            return False
        sql = 'update tournamentplayers set wins = DEFAULT,' \
              ' matches = DEFAULT, lastoppid = default where tid = %s;'
        cur.execute(sql, (tournamentid,))

    conn.commit()
    conn.close()
    return True


def deleteTournamentPlayers(tournamentid=-1):
    """
    Remove all the player records from the database.

    Args:
        tournamentid (int): Tournament ID of which players are to be deleted.
                    If no argument passed, delete for all tournaments
    Returns: Status
    """
    conn, cur = connect()

    if tournamentid == -1:  # If no argument passed
        sql = 'delete from tournamentplayers;'
    else:
        if not existsTournament(tournamentid):
            conn.close()
            return False
        sql = 'delete from tournamentplayers where tid = {0};' \
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
    Returns: Status, count of players
    """
    conn, cur = connect()

    # Get count of rows in player relation
    if tournamentid == -1:
        sql = 'select count(distinct pid) from tournamentplayers;'
        cur.execute(sql)
    else:
        if not existsTournament(tournamentid):
            conn.close()
            return False, -1
        sql = 'select count(distinct pid) from tournamentplayers ' \
              'where tid = %s;'
        cur.execute(sql, (tournamentid,))

    player_count = cur.fetchall()[0][0]
    conn.close()
    return True, player_count


def playerCount():
    """
    Count all players, whether registered or not
    Returns: Number of players
    """

    conn, cur = connect()

    sql = 'select count(*) from players;'
    cur.execute(sql)

    count = cur.fetchall()[0][0]

    conn.close()
    return count


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    Returns: ID of registered player
    """
    conn, cur = connect()

    sql = 'insert into players (pname) values (%s) returning pid;'
    cur.execute(sql, (name,))
    pid = cur.fetchall()[0][0]

    conn.commit()
    conn.close()
    return pid


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
    Returns: Status, list of tuples
    """
    conn, cur = connect()

    if tournamentid == -1:
        sql = 'select pid, pname, cwins, cmatches from players natural join ' \
              '(select pid, sum(wins) as cwins, sum(matches) as cmatches' \
              ' from tournamentplayers  group by pid)' \
              ' as allinfo  where cmatches = 0 order by pid;'
        cur.execute(sql)
        list1 = cur.fetchall()

        sql = 'select pid, pname, cwins, cmatches from players natural join ' \
              '(select pid, sum(wins) as cwins, sum(matches) as cmatches' \
              ' from tournamentplayers  group by pid)' \
              ' as allinfo where cmatches > 0 order by cwins desc, cwins/cmatches desc, pid;'
        cur.execute(sql)
        list2 = cur.fetchall()
    else:
        if not existsTournament(tournamentid):
            conn.close()
            return False, []
        sql = 'select pid, pname, wins, matches from players natural join' \
              ' tournamentplayers where tid = %s and matches = 0 ' \
              'order by pid;'
        cur.execute(sql, (tournamentid,))
        list1 = cur.fetchall()

        sql = 'select pid, pname, wins, matches from players natural join' \
              ' tournamentplayers where tid = %s and matches > 0 ' \
              'order by wins desc, wins/matches desc, pid;'
        cur.execute(sql, (tournamentid,))
        list2 = cur.fetchall()

    conn.close()
    return True, list2 + list1


def clearPlayers():
    """
    Delete all players
    """
    conn, cur = connect()

    sql = 'delete from players; delete from tournamentplayers;'
    cur.execute(sql)

    conn.commit()
    conn.close()


def reportMatch(tournamentid, winner, loser):
    """
    Report result of match. winner and loser are same
    in case of a 'bye'
    Args:
        tournamentid: Tournament ID
        winner: Winner ID
        loser: Loser ID

    Returns: Status

    """
    conn, cur = connect()

    if not existsTournamentPlayer(tournamentid, winner) or \
            not existsTournamentPlayer(tournamentid, loser):
        conn.close()
        return False

    sql = 'update tournamentplayers set matches = matches + 1,' \
          ' wins = wins + 1, lastoppid = %s where tid = %s and pid = %s;'
    cur.execute(sql, (loser, tournamentid, winner))
    if winner != loser:  # If not a bye
        sql = 'update tournamentplayers set matches = matches + 1,' \
              ' lastoppid = %s where tid = %s and pid = %s;'
        cur.execute(sql, (winner, tournamentid, loser))

    conn.commit()
    conn.close()


def swissPairings(tournamentid):
    """
    Returns a list of pairs of players for the next round of a match.
  
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
    conn, cur = connect()

    sql = 'select pid, pname, lastoppid from players natural join' \
          ' tournamentplayers where tid = %s and matches = 0 ' \
          'order by pid;'
    cur.execute(sql, (tournamentid,))
    list1 = cur.fetchall()

    sql = 'select pid, pname, lastoppid from players natural join' \
          ' tournamentplayers where tid = %s and matches > 0 ' \
          'order by wins desc, wins/matches desc, pid;'
    cur.execute(sql, (tournamentid,))
    list2 = cur.fetchall()

    players = list2 + list1

    # Odd players, bye one who wasn't byed last time
    if len(players) % 2 == 1:
        tempList = list(players)
        shuffle(tempList)
        byed = False
        randomFirst = tempList[0]
        while not byed and len(tempList) > 0:
            if tempList[0][0] == tempList[0][2]:
                players.remove(tempList[0])
                reportMatch(tournamentid, tempList[0][0], tempList[0][0])
                byed = True
            tempList.remove(tempList[0])
        if not byed:
            reportMatch(tournamentid, randomFirst[0], randomFirst[0])
            players.remove(randomFirst)

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


def addTournament(name):
    """
    Register a new tournament
    Args:
        name: Name of tournament
    Returns:
        ID of tournament added
    """
    conn, cur = connect()

    sql = 'insert into tournaments (tname) values(%s) returning tid;'
    cur.execute(sql, (name,))
    tid = cur.fetchall()[0][0]

    conn.commit()
    conn.close()
    return tid


def addPlayerTournament(tid, pid):
    """
    Add a registered player to a tournament
    Args:
        tid: Tournament ID
        pid: Player ID

    Returns: Status
    """

    if not existsTournament(tid) or not existsPlayer(pid):
        return False

    conn, cur = connect()

    sql = 'insert into tournamentplayers (tid, pid) values (%s, %s);'
    cur.execute(sql, (tid, pid))

    conn.commit()
    conn.close()
    return True


def countTournaments():
    """
    Count number of tournaments
    Returns: Number of tournaments
    """
    conn, cur = connect()

    sql = 'select count(*) from tournaments;'
    cur.execute(sql)

    count = cur.fetchall()[0][0]

    conn.close()
    return count


def clearTournaments():
    """
    Delete all tournaments
    """
    conn, cur = connect()

    sql = 'delete from tournamentplayers; delete from tournaments;'
    cur.execute(sql)

    conn.commit()
    conn.close()