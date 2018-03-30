# set async_mode to 'threading', 'eventlet', 'gevent' or 'gevent_uwsgi' to
# force a mode else, the best mode is selected automatically from what's
# installed
async_mode = None
import random
import time
from flask import Flask, render_template
import socketio
import paho.mqtt.client as mqtt
import json
from team import Team
from team import Game
from team import Player
import team

import os, sys
import threading
import time
import logging
import datetime as dt
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

# topics definition
FEEDTOPIC = 'QNET/SCOREBOARD/LIVEFEED'
CLEARFEEDTOPIC = 'QNET/SCOREBOARD/CLEARFEED'
GAMESTATUSTOPIC = 'QNET/SCOREBOARD/STATUS'
TEAMSCORETOPIC = 'QNET/SCOREBOARD/TEAMS/#'
PLAYERSCORETOPIC = 'QNET/SCOREBOARD/PLAYER'

'''
FEEDTOPIC = 'QNET/SCOREBOARD/LIVEFEED'
CLEARFEEDTOPIC = 'QNET/SCOREBOARD/CLEARFEED'
GAMESTATUSTOPIC = 'QNET/SCOREBOARD/STATUS'
TEAMSCORETOPIC = 'QNET/SCOREBOARD/TEAM/#'
PLAYERSCORETOPIC = 'QNET/SCOREBOARD/PLAYER'
'''


#BROKERADDRESS = 'localhost' # we have to change your local broker after it is ready.
BROKERADDRESS = 'test.mosquitto.org' # we have to change your local broker after it is ready.

currGame = Game(name='testing game', time=1200)
#TEAMCNT = 8
#PLAYERCNT = 24

TEAMCNT = 1
PLAYERCNT = 72

def initTeams():
    try:
        global currGame
        '''
        for feedidx in range(0, 25):
            currGame.appendFeed('feedmessage is received from borker ' + str(feedidx))
        '''
        if TEAMCNT == 1:
            team = Team(name='team0', teamID=0)
            # team.active = True
            team.setInfo(score=1001, active=True, backColor=0x0000FF)
            for index in range(0, PLAYERCNT):
                player = Player(playerID = index, name='player_' + str(index))
                player.setInfo(name='player_' + str(index), score=1500, active=True, flags=0xFF)
                team.insertNewPlayer(player)
            try:
                team.players[random.randint(0, PLAYERCNT - 1)].badge = 1
                team.players[random.randint(0, PLAYERCNT - 1)].badge = 2
                team.players[random.randint(0, PLAYERCNT - 1)].badge = 3
            except:
                print('error')
            currGame.insertTeam(team)

        else:
            for idx in range(0, TEAMCNT):
                team = Team(name='team' + str(idx), teamID=idx)
                # team.active = True
                team.setInfo(score=1000+idx, active=True, backColor=0x0000FF)
                '''
                for index in range(0, PLAYERCNT):
                    player = Player(playerID = idx * 10 + index, name='player_' + str(idx * 10 + index))
                    player.setInfo(name='player_' + str(idx * 10 + index), score=1500, active=True, flags=0xFF)
                    team.insertNewPlayer(player)
                try:
                    team.players[random.randint(0, PLAYERCNT - 1)].badge = 1
                    team.players[random.randint(0, PLAYERCNT - 1)].badge = 2
                    team.players[random.randint(0, PLAYERCNT - 1)].badge = 3
                except:
                    print('error')
                '''
                currGame.insertTeam(team)
            currGame.checkLead()
    except:
        logging.error('it happens error in initializing of teams')

initTeams()


logging.info(json.dumps(currGame.info()))

# currGame.clearTeams()
# print(json.dumps(currGame.info()))

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    print('new message is arrived topic : ' + msg.topic)
    print('message : ' + str(msg.payload))

    if msg.topic == FEEDTOPIC:
        try:
            feed = json.loads(str(msg.payload))
            print(json.dumps(feed))
            if not 'newfeed' in feed:
                logging.info('invalid format from feedback topic.')
            else:
                currGame.appendFeed(feed['newfeed'])
                print(currGame.info())
                triggerScoketEmit()
        except:
            logging.info('invalid json format from feedback topic.')

    elif msg.topic == CLEARFEEDTOPIC:
        try:
            logging.info('clearing feed messages')
            currGame.clearFeed()
            triggerScoketEmit()
        except:
            logging.info('error happened in clearing feed messages')
    elif msg.topic == GAMESTATUSTOPIC:
        try:
            gameStatus = json.loads(str(msg.payload))
            print(gameStatus)
            if not 'GAMESTATUS' in gameStatus:
                logging.info('there is no status on gamestatus payload.')
            else:
                newStatus = gameStatus['GAMESTATUS']
                if(not isinstance(newStatus, int)):
                    logging.error('invalid variable type in status field')
                else:
                    name = gameStatus['GAMENAME']
                    remaining = gameStatus['REMAINING']
                    currGame.setGameStatus(newStatus, name, remaining)
                    triggerScoketEmit()
                '''
                '''
        except:
            logging.info('invalid json format from gamestatus topic.')

    elif TEAMSCORETOPIC[:-1] in msg.topic:
        try:
            # ex: {"TEAMNAME": "Red Team", "SCORE":5000, "POSITION":5, "ACTIVE":1, "RED":200, "GREEN":100, "BLUE":50}
            teamID = int(msg.topic[-1:])
            teamInfo = json.loads(str(msg.payload))
            teamName = teamInfo['TEAMNAME']
            teamScore = teamInfo['SCORE']
            teamPos = teamInfo['POSITION']
            active = teamInfo['ACTIVE']
            backColor = (int(teamInfo['RED']) << 16) + (int(teamInfo['GREEN']) << 8) + int(teamInfo['BLUE'])

            ###
            currGame.reload = True

            ###
            currGame.teams[teamID].setInfo(teamName, teamScore, teamPos, active, backColor)
            currGame.checkLead()
            triggerScoketEmit()
        except:
            logging.info('invalid json format from teamscore topic.')

    elif PLAYERSCORETOPIC == msg.topic:
        try:
            # ex: {"TEAMID":1, "PLAYERID": 24, "PLAYERNAME": "Haw", "SCORE":100, "ACTIVE":1, "POSITION":8, "FLAGS":5}
            playerInfo = json.loads(str(msg.payload))

            teamID = playerInfo['TEAMID']
            if not isinstance(teamID, int):
                logging.error('teamID should be int type in playertopic')
                return

            if teamID < 0 or teamID > 7:
                logging.error('teamID should be range of 0 to 7')
                return

            playerID = playerInfo['PLAYERID']
            if not isinstance(playerID, int):
                logging.error('playerID should be int type in playertopic')
                return

            playerName = playerInfo['PLAYERNAME']

            score = playerInfo['SCORE']
            if not isinstance(score, int):
                logging.error('score should be int type in playertopic')
                return

            active = bool(playerInfo['ACTIVE'])

            flags = playerInfo['FLAGS']
            if not isinstance(flags, int):
                logging.error('flags should be int type in playertopic')
                return

            if not currGame.teams[teamID].setPlayerInfo(playerID, playerName, score, active, flags):
                logging.error('error happens in set player step')
                return
            triggerScoketEmit()

        except:
            logging.info('invalid json format from player score topic.')

def triggerScoketEmit():
    global changedStatus
    changedStatus = True

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKERADDRESS, 1883, 60)
client.loop_start()
client.subscribe(FEEDTOPIC)
client.subscribe(GAMESTATUSTOPIC)
client.subscribe(TEAMSCORETOPIC)
client.subscribe(PLAYERSCORETOPIC)
client.subscribe(CLEARFEEDTOPIC)

# socket io init
sio = socketio.Server(logger=True, async_mode=None)
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)
app.config['SECRET_KEY'] = 'secret!'
thread = None
changedStatus = False

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        sio.sleep(1)
        global changedStatus
        if changedStatus:
            changedStatus = False
            sio.emit('my response', {'data': json.dumps(currGame.info())},
                     namespace='/test')
        if currGame.gameStatus == team.PLAYING:
            if currGame.time > 0:
                currGame.time = currGame.time - 1
        elif currGame.gameStatus == team.ENDOFGAME:
            currGame.time = 0
        else:
            pass

        gametime = dict()
        gametime['gametime'] = currGame.time
        sio.emit('gametime', {'data': json.dumps(gametime)},
                 namespace='/test')

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    return render_template('index.html')

@sio.on('my event', namespace='/test')
def test_message(sid, message):
    sio.emit('my response', {'data': message['data']}, room=sid,
             namespace='/test')

@sio.on('my broadcast event', namespace='/test')
def test_broadcast_message(sid, message):
    sio.emit('my response', {'data': message['data']}, namespace='/test')


@sio.on('join', namespace='/test')
def join(sid, message):
    sio.enter_room(sid, message['room'], namespace='/test')
    sio.emit('my response', {'data': 'Entered room: ' + message['room']},
             room=sid, namespace='/test')


@sio.on('leave', namespace='/test')
def leave(sid, message):
    sio.leave_room(sid, message['room'], namespace='/test')
    sio.emit('my response', {'data': 'Left room: ' + message['room']},
             room=sid, namespace='/test')


@sio.on('close room', namespace='/test')
def close(sid, message):
    sio.emit('my response',
             {'data': 'Room ' + message['room'] + ' is closing.'},
             room=message['room'], namespace='/test')
    sio.close_room(message['room'], namespace='/test')


@sio.on('my room event', namespace='/test')
def send_room_message(sid, message):
    sio.emit('my response', {'data': message['data']}, room=message['room'],
             namespace='/test')


@sio.on('disconnect request', namespace='/test')
def disconnect_request(sid):
    sio.disconnect(sid, namespace='/test')

@sio.on('connect', namespace='/test')
def test_connect(sid, environ):
    global currGame
    sio.emit('my response', {'data': json.dumps(currGame.info())}, room=sid,
             namespace='/test')

@sio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    print('Client disconnected')

if __name__ == '__main__':
    # deploy with eventlet
    import eventlet
    import eventlet.wsgi
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

    '''
    if sio.async_mode == 'threading':
        # deploy with Werkzeug
        app.run(threaded=True)
    elif sio.async_mode == 'eventlet':
        # deploy with eventlet
        import eventlet
        import eventlet.wsgi
        eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
    elif sio.async_mode == 'gevent':
        # deploy with gevent
        from gevent import pywsgi
        try:
            from geventwebsocket.handler import WebSocketHandler
            websocket = True
        except ImportError:
            websocket = False
        if websocket:
            pywsgi.WSGIServer(('', 5000), app,
                              handler_class=WebSocketHandler).serve_forever()
        else:
            pywsgi.WSGIServer(('', 5000), app).serve_forever()
    elif sio.async_mode == 'gevent_uwsgi':
        print('Start the application through the uwsgi server. Example:')
        print('uwsgi --http :5000 --gevent 1000 --http-websockets --master '
              '--wsgi-file app.py --callable app')
    else:
        print('Unknown async_mode: ' + sio.async_mode)
    '''