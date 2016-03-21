#!/usr/bin/env python
#
# Test cases for tournament.py
# These tests are not exhaustive, but they should cover the majority of cases.
#
# If you do add any of the extra credit options, be sure to add/modify these test cases
# as appropriate to account for your module's added functionality.

from tournament import *

if __name__ == '__main__':

    # Clear tournaments
    clearTournaments()

    # Clear players
    clearPlayers()

    # Register new tournaments
    tidCricket = addTournament("Cricket")
    tidFootball = addTournament("Football")

    # Check if two are added
    tcount = countTournaments()
    if tcount != 2:
        raise ValueError(
            'Added 2 tournaments but found {0}'.format(tcount)
        )
    else:
        print("Added two tournaments")

    # Check number of player in tournament
    status, pcountCricket = countTournamentPlayers(tidCricket)
    if pcountCricket != 0:
        raise ValueError(
            'Added 0 players but found {0}'.format(pcountCricket)
        )
    else:
        print("No players in Cricket currently")

    # Try to query player count of a non existing tournament
    status, pcount = countTournamentPlayers(123123123)
    if status == True:
        raise ValueError(
            'Querry possible for non existing tournament'
        )
    else:
        print("Robust against invalid tournament entry.")

    # Add five players
    player1 = registerPlayer("Eto\'o")
    player2 = registerPlayer("Cristiano")
    player3 = registerPlayer("Zidane")
    player4 = registerPlayer("Dhoni")
    player5 = registerPlayer("Gayle")

    countPlayer = playerCount()
    if countPlayer != 5:
        raise ValueError(
            'Added 5 players but got {0}.'.format(countPlayer)
        )
    else:
        print('Success in adding players')

    # Register players to tournaments
    status = addPlayerTournament(tidFootball, player1) \
             and addPlayerTournament(tidFootball, player2) \
             and addPlayerTournament(tidFootball, player3) \
             and addPlayerTournament(tidCricket, player4) \
             and addPlayerTournament(tidCricket, player5)
    if not status:
        raise ValueError(
            'Unable to register players for tournament'
        )
    else:
        print('Players added successfully')

    print(swissPairings(tidFootball))
