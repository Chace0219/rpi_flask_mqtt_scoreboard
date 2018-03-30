# coding=utf-8
import os, sys
import logging
import time
import json

class Team:
    def __init__(self, name, teamID, backColor=0x00FF00, foreColor=0xFFFFFF):
        self.name = name
        self.foreColor = foreColor
        self.backColor = backColor
        self.score = 0
        #
        self.active = False
        #
        self.teamID = teamID
        #
        self.position = 0
        ###
        self.players = []
        self.lead = False

    def sortByBadge(self):
        activePlayers = filter(lambda player: player.active == True, self.players)
        try:
            sortedPlayers = sorted(activePlayers, key=lambda k: k.badge)
            while(len(self.players)):
                self.players.pop()
            for player in sortedPlayers:
                print(player.name + ' badge is ' + str(player.badge))
                self.insertNewPlayer(player)
        except:
            print('sorting error')

    def insertNewPlayer(self, newplayer):
        self.players.append(newplayer)

    def setInfo(self, name='', score=1000, position=0, active=False, backColor=0xFF0000):
        try:
            if name != '':
                self.name = name
            self.backColor = backColor
            self.score = score
            self.position = position
            self.active = bool(active)
        except:
            pass

    def findPlayer(self, playerID):
        for player in self.players:
            if player.playerID == playerID:
                return player
        return None

    def setPlayerInfo(self, playerID, playerName, score, active, flags):
        try:
            # check whether player is in specified team
            player = self.findPlayer(playerID)
            print(player)
            if player == None:
                # there is no player with this id
                newPlayer = Player(playerID, playerName)
                newPlayer.setInfo(playerName, score, active, flags)
                self.insertNewPlayer(newPlayer)
            else:
                # when remove player from team, send reload command
                player.setInfo(playerName, score, active, flags)
            return True
        except:
            return False

class Player:
    def __init__(self, playerID, name):
        self.playerID = playerID
        self.name = name
        self.score = 0
        self.badge = 0xFF
        self.active = False

    def setInfo(self, name, score, active, flags):
        self.name = name
        self.score = score
        self.active = active
        self.badge = flags

# game status definitions
NOTSTARTED = 0
SETUP = 1
GAMECOUNTDOWN = 2
PLAYING = 3
ENDOFGAME = 4

class Game:
    def __init__(self, name, time):
        ###
        self.feedback = []
        self.name = name
        self.time = time
        ###
        self.teams = []
        self.gameStatus = NOTSTARTED

    def setGameStatus(self, status, name, remaining):
        self.gameStatus = status
        self.name = name
        self.time = remaining

    def appendFeed(self, feedString):
        try:
            if len(self.feedback) >= 25:
                self.feedback.pop(0)
                self.feedback.append(feedString)
            else:
                self.feedback.append(feedString)
        except:
            print('fatal error in append feed')
            pass
    def clearFeed(self):
        del(self.feedback[:])

    def info(self):
        result = dict()
        result['name'] = self.name
        result['remaintime'] = str(self.time)

        feeds = []
        for item in self.feedback:
            feeds.append(item)
        result['feeds'] = feeds
        result['feedcount'] = len(feeds)

        teams = []
        activeTeams = filter(lambda team: team.active == True, self.teams)

        for team in activeTeams:
            # check active players
            activePlayers = filter(lambda player: player.active == True, team.players)
            # remove all players
            while(len(team.players)):
                team.players.pop()
            # append again
            for player in activePlayers:
                team.players.append(player)


        teamCount = len(activeTeams)
        result['teamcount'] = teamCount
        if teamCount == 1:
            for team in activeTeams:
                teamInfo = dict()
                teamInfo['name'] = team.name
                teamInfo['score'] = team.score
                teamInfo['forecolor'] = '{0:06x}'.format(team.foreColor)
                teamInfo['backcolor'] = '{0:06x}'.format(team.backColor)
                teamInfo['lead'] = team.lead
                players = []
                playerCnt = len(team.players)
                teamInfo['twicecolumn'] = True
                teamInfo['playercount'] = playerCnt
                try:
                    sortedPlayers = sorted(team.players, key=lambda k: k.playerID)
                    for player in sortedPlayers:
                        if player.active == True:
                            playerInfo = dict()
                            playerInfo['name'] = player.name
                            playerInfo['number'] = player.playerID
                            playerInfo['score'] = player.score
                            playerInfo['badge'] = player.badge
                            players.append(playerInfo)
                except:
                    print('sorting error')
                teamInfo['players'] = players
                teams.append(teamInfo)
        if teamCount == 2:
            for team in activeTeams:
                teamInfo = dict()
                teamInfo['name'] = team.name
                teamInfo['score'] = team.score
                teamInfo['forecolor'] = '{0:06x}'.format(team.foreColor)
                teamInfo['backcolor'] = '{0:06x}'.format(team.backColor)
                teamInfo['lead'] = team.lead
                players = []
                playerCnt = len(team.players)
                if playerCnt > 20:
                    teamInfo['twicecolumn'] = True
                else:
                    teamInfo['twicecolumn'] = False
                teamInfo['playercount'] = playerCnt
                try:
                    sortedPlayers = sorted(team.players, key=lambda k: k.playerID)
                    for player in sortedPlayers:
                        if player.active == True:
                            playerInfo = dict()
                            playerInfo['name'] = player.name
                            playerInfo['number'] = player.playerID
                            playerInfo['score'] = player.score
                            playerInfo['badge'] = player.badge
                            players.append(playerInfo)
                except:
                    print('sorting error')
                teamInfo['players'] = players
                teams.append(teamInfo)
        elif teamCount == 3:
            twiceCount = 0
            for team in activeTeams:
                teamInfo = dict()
                teamInfo['name'] = team.name
                teamInfo['score'] = team.score
                teamInfo['forecolor'] = '{0:06x}'.format(team.foreColor)
                teamInfo['backcolor'] = '{0:06x}'.format(team.backColor)
                teamInfo['lead'] = team.lead
                players = []
                playerCnt = len(team.players)
                if playerCnt > 20 and twiceCount < 1:
                    teamInfo['twicecolumn'] = True
                    twiceCount = twiceCount + 1
                else:
                    teamInfo['twicecolumn'] = False
                teamInfo['playercount'] = playerCnt
                try:
                    sortedPlayers = sorted(team.players, key=lambda k: k.playerID)
                    for player in sortedPlayers:
                        if player.active == True:
                            playerInfo = dict()
                            playerInfo['name'] = player.name
                            playerInfo['number'] = player.playerID
                            playerInfo['score'] = player.score
                            playerInfo['badge'] = player.badge
                            players.append(playerInfo)
                except:
                    print('sorting error')
                teamInfo['players'] = players
                teams.append(teamInfo)
        elif teamCount == 4:
            twiceCount = 0
            for team in activeTeams:
                teamInfo = dict()
                teamInfo['name'] = team.name
                teamInfo['score'] = team.score
                teamInfo['forecolor'] = '{0:06x}'.format(team.foreColor)
                teamInfo['backcolor'] = '{0:06x}'.format(team.backColor)
                teamInfo['lead'] = team.lead
                players = []
                teamInfo['twicecolumn'] = False
                playerCnt = len(team.players)
                teamInfo['playercount'] = playerCnt
                try:
                    sortedPlayers = sorted(team.players, key=lambda k: k.playerID)
                    for player in sortedPlayers:
                        if player.active == True:
                            playerInfo = dict()
                            playerInfo['name'] = player.name
                            playerInfo['number'] = player.playerID
                            playerInfo['score'] = player.score
                            playerInfo['badge'] = player.badge
                            players.append(playerInfo)
                except:
                    print('sorting error')
                teamInfo['players'] = players
                teams.append(teamInfo)
        elif teamCount == 5:
            twiceCount = 0
            column = 0
            for team in activeTeams:
                teamInfo = dict()
                teamInfo['name'] = team.name
                teamInfo['score'] = team.score
                teamInfo['forecolor'] = '{0:06x}'.format(team.foreColor)
                teamInfo['backcolor'] = '{0:06x}'.format(team.backColor)
                teamInfo['lead'] = team.lead

                players = []
                playerCnt = len(team.players)
                teamInfo['playercount'] = playerCnt

                if playerCnt > 10 and twiceCount < 3:
                    if column == 3:
                        column = column + 1
                        teamInfo['twicecolumn'] = False
                    else:
                        column = column + 2
                        teamInfo['twicecolumn'] = True
                        twiceCount = twiceCount + 1
                else:
                    column = column + 1
                    teamInfo['twicecolumn'] = False

                try:
                    sortedPlayers = sorted(team.players, key=lambda k: k.playerID)
                    for player in sortedPlayers:
                        if player.active == True:
                            playerInfo = dict()
                            playerInfo['name'] = player.name
                            playerInfo['number'] = player.playerID
                            playerInfo['score'] = player.score
                            playerInfo['badge'] = player.badge
                            players.append(playerInfo)
                except:
                    print('sorting error')
                teamInfo['players'] = players
                teams.append(teamInfo)
        elif teamCount == 6:
            twiceCount = 0
            column = 0
            for team in activeTeams:
                teamInfo = dict()
                teamInfo['name'] = team.name
                teamInfo['score'] = team.score
                teamInfo['forecolor'] = '{0:06x}'.format(team.foreColor)
                teamInfo['backcolor'] = '{0:06x}'.format(team.backColor)
                teamInfo['lead'] = team.lead

                players = []
                playerCnt = len(team.players)
                teamInfo['playercount'] = playerCnt
                if playerCnt > 10 and twiceCount < 2:
                    if column == 3:
                        column = column + 1
                        teamInfo['twicecolumn'] = False
                    else:
                        column = column + 2
                        teamInfo['twicecolumn'] = True
                        twiceCount = twiceCount + 1
                else:
                    column = column + 1
                    teamInfo['twicecolumn'] = False

                try:
                    sortedPlayers = sorted(team.players, key=lambda k: k.playerID)
                    for player in sortedPlayers:
                        if player.active == True:
                            playerInfo = dict()
                            playerInfo['name'] = player.name
                            playerInfo['number'] = player.playerID
                            playerInfo['score'] = player.score
                            playerInfo['badge'] = player.badge
                            players.append(playerInfo)
                except:
                    print('sorting error')
                teamInfo['players'] = players
                teams.append(teamInfo)
        elif teamCount == 7:
            twiceCount = 0
            for team in activeTeams:
                teamInfo = dict()
                teamInfo['name'] = team.name
                teamInfo['score'] = team.score
                teamInfo['forecolor'] = '{0:06x}'.format(team.foreColor)
                teamInfo['backcolor'] = '{0:06x}'.format(team.backColor)
                teamInfo['lead'] = team.lead

                players = []
                playerCnt = len(team.players)
                teamInfo['playercount'] = playerCnt
                if playerCnt > 10 and twiceCount < 1:
                    teamInfo['twicecolumn'] = True
                    twiceCount = twiceCount + 1
                else:
                    teamInfo['twicecolumn'] = False

                try:
                    sortedPlayers = sorted(team.players, key=lambda k: k.playerID)
                    for player in sortedPlayers:
                        if player.active == True:
                            playerInfo = dict()
                            playerInfo['name'] = player.name
                            playerInfo['number'] = player.playerID
                            playerInfo['score'] = player.score
                            playerInfo['badge'] = player.badge
                            players.append(playerInfo)
                except:
                    print('sorting error')
                teamInfo['players'] = players
                teams.append(teamInfo)
        elif teamCount == 8:
            twiceCount = 0
            for team in activeTeams:
                teamInfo = dict()
                teamInfo['name'] = team.name
                teamInfo['score'] = team.score
                teamInfo['forecolor'] = '{0:06x}'.format(team.foreColor)
                teamInfo['backcolor'] = '{0:06x}'.format(team.backColor)
                teamInfo['lead'] = team.lead

                players = []
                playerCnt = len(team.players)
                teamInfo['playercount'] = playerCnt
                teamInfo['twicecolumn'] = False
                try:
                    sortedPlayers = sorted(team.players, key=lambda k: k.playerID)
                    for player in sortedPlayers:
                        if player.active == True:
                            playerInfo = dict()
                            playerInfo['name'] = player.name
                            playerInfo['number'] = player.playerID
                            playerInfo['score'] = player.score
                            playerInfo['badge'] = player.badge
                            players.append(playerInfo)
                except:
                    print('sorting error')
                teamInfo['players'] = players
                teams.append(teamInfo)
        result['teams'] = teams
        return result

    def checkLead(self):
        try:
            activeTeams = filter(lambda x: x.active == True, self.teams)
            sortlist = sorted(activeTeams, key=lambda k: k.score, reverse=True)
            maxScore = sortlist[0].score
            topScoreList = filter(lambda x: x.score == maxScore, sortlist)
            # reset lead flags
            for team in self.teams:
                team.lead = False
            # set lead to real team
            for leadTeam in topScoreList:
                print(str(leadTeam.name) + ' score is ' + str(leadTeam.score))
                leadTeam.lead = True
        except:
            print('error in checklead')
            pass

    def insertTeam(self, team):
        try:
            self.teams.append(team)
        except:
            print('insert team error')

    def clearTeams(self):
        teamCnt = len(self.teams)
        for index in range(0, teamCnt):
            self.teams.pop(0)
