import sys, boto3, random
import random
from datetime import datetime, timedelta
import ast
import json
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt, socketio, login
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms import LoginForm
from pprint import pprint
from models import *
from flask_socketio import SocketIO, join_room, leave_room, send, emit


def set_environment():
    if current_user.is_authenticated:
        course = User.query.filter_by(username=current_user.username).first().test
        
        courseDict ={
            'FRD_2_2': [GamesFRD, 'static\json_files\FRD_defs_02-2.json', '_FRD'],
            'WPE_2_2': [GamesWPE, 'static\json_files\WPE_defs_02-2.json', '_WPE'],
            'FRD_2_1': [GamesFRD, 'static\json_files\FRD_defs_02-1.json', '_FRD'],
            'WPE_2_1': [GamesWPE, 'static\json_files\WPE_defs_02-1.json', '_WPE'],           
            'FRD_1_1': [GamesFRD, 'static\json_files\FRD_defs_01-1.json', '_FRD'],
            'WPE_1_1': [GamesWPE, 'static\json_files\WPE_defs_01-1.json', '_WPE'],           
            'FRD_1_2': [GamesFRD, 'static\json_files\FRD_defs_01-2.json', '_FRD'],
            'WPE_1_2': [GamesWPE, 'static\json_files\WPE_defs_01-2.json', '_WPE'],           
        }
        Games = courseDict[course][0]
        jDict = courseDict[course][1]
        roomTag = courseDict[course][2]
        victories = courseDict[course][0].query.filter_by(winner=current_user.studentID).count()

    return [Games, jDict, roomTag, victories]

    


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(studentID=form.studentID.data).first()
        if user:
            login_user(user)
            user.username = form.username.data
            db.session.commit()
        else:
            new_user = User(username=form.username.data, studentID=form.studentID.data, test=form.vocab.data)
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(username=form.username.data).first()
            login_user(user)        
        flash(f'Logged In', 'secondary')
        return redirect(url_for('home'))        
    
    return render_template('login.html', title='Login', form=form)

@app.route("/logout", methods=['GET'])
def logout():

    # Logout user
    logout_user()
    flash('You have logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():  

    if current_user.is_authenticated: 
        v = set_environment()[3]
    else:
        v = None


    return render_template("home.html", victories = v)

@app.route('/waiting', methods=['POST'])
def waiting(): 
    Games = set_environment()[0] 

    count = Games.query.filter_by(gameSet=0).count()
    print ('Waiting', count)
    games = Games.query.filter_by(gameSet=1).count()
    game_records = Games.query.filter_by(gameSet=1).all()
    
    print ('GAMES', games)

    home = request.form ['home']    
    
    return jsonify({'count' : count , 'games' : games }) 


@app.route("/fight", methods=['GET', 'POST'])
def fight():
     
    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('home'))
        
        
    unknown = 'https://lms-tester.s3-ap-northeast-1.amazonaws.com/avatar/waiting.png'
    

    users = {
        1: ['Waiting', unknown],
        2: ['Waiting', unknown]
    }
      
    return render_template('fight.html', title='Fight', users=users, username=current_user.username)


@app.route("/fightscores/<string:game>", methods=['GET', 'POST'])
def fight_scores(game):
    Games = set_environment()[0] 
    gameID = game.split('_')[0]

    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('home'))

    data = Games.query.filter_by(id=gameID).first()
    game_results = ast.literal_eval(data.results)
    game_qs = ast.literal_eval(data.records)   
    
    print('GAME_RESULTS')
    pprint(game_results)

    opponent = None 
    player = current_user.username

    
    # set opponent name
    for key in game_results:
        for user in game_results[key]:
            if user != current_user.username:
                opponent = user
                print('opponent name found')
        break
    
    for key in game_results:
        if game_results[key][player][0] == 1 and game_results[key][opponent][0] == 1:
            if game_results[key][player][1] > game_results[key][opponent][1]:
                game_results[key][player][1] = 1
                game_results[key][opponent][1] = 0
            elif game_results[key][player][1] < game_results[key][opponent][1]:
                game_results[key][player][1] = 0
                game_results[key][opponent][1] = 1
            else:
                game_results[key][player][1] = 0
                game_results[key][opponent][1] = 0
        else:
            game_results[key][player][1] = 0
            game_results[key][opponent][1] = 0

    print('TIME_RESULTS')
    pprint(game_results)

    scores = {
        player : [0, 0] , 
        opponent : [0, 0] 
    }

    # calculate scores
    for key in game_results:
        scores[player][0] += sum(game_results[key][player])
        scores[opponent][0] += sum(game_results[key][opponent])
    
    print ('SCORES', scores)
    game_results['SCORE'] = scores

    if scores[player] > scores[opponent]:
        user = User.query.filter_by(username=player).first()
        if user:
            winner = player
            winnerID = user.studentID
        else: 
            winner = player
            winnerID = player
    elif scores[opponent] > scores[player]:
        user = User.query.filter_by(username=opponent).first()
        if user:
            winner = opponent
            winnerID = user.studentID
        else: 
            winner = opponent        
            winnerID = opponent        
    else:
        winner = 'EVENS'
        winnerID = 'EVENS'

    # add winner to games data base
    data.winner = winnerID
    db.session.commit()   

    return render_template('fightscores.html', title='Scores', player=player, opponent=opponent, game_results=game_results, winner=winner)


def add_questions (q):
    jDict = set_environment()[1] 
        
    with open(jDict, "r") as f:
        jload = json.load(f)

    # make a list of number as long as the json dictionary
    numbers = list(range(1, len(jload)+1))

    QUESTIONS = q
    count = 1 

    qDict = {}
    while count < QUESTIONS +1:
        # suffle the list before accessing it
        random.shuffle(numbers)
        no_duplicate = False
        for key in qDict:
            if numbers[0] in qDict[key]['q']:
                no_duplicate = True 

        if no_duplicate == False:
            aList = [
                jload[str(numbers[0])][1],
                jload[str(numbers[1])][1],
                jload[str(numbers[2])][1]
            ]
            random.shuffle(aList)
            qDict[count] = {
                'q': [
                    jload[str(numbers[0])]  [0],
                    jload[str(numbers[0])]  [1], 
                    numbers[0]
                ],
                'a': aList
            }
            count +=1
        else:
            pass

    pprint(qDict)    
    qString = json.dumps(qDict) 

    return qString

def set_game(bot):
    Games = set_environment()[0] 
    roomTag = set_environment()[2] 

    number_of_qs = 6
    gameSet = None 

    if bot == None:
        player = current_user.username
    else:
        player = 'Bot'
        gameSet = 1
        room = bot
        gameID = int(room.split('_')[0])
    
    avatars = [
        'https://lms-tester.s3-ap-northeast-1.amazonaws.com/avatar/robot_01.PNG',
        'https://lms-tester.s3-ap-northeast-1.amazonaws.com/avatar/robot_02.PNG', 
        'https://lms-tester.s3-ap-northeast-1.amazonaws.com/avatar/robot_03.PNG',
        'https://lms-tester.s3-ap-northeast-1.amazonaws.com/avatar/robot_04.PNG', 
        'https://lms-tester.s3-ap-northeast-1.amazonaws.com/avatar/robot_05.PNG',
        'https://lms-tester.s3-ap-northeast-1.amazonaws.com/avatar/robot_06.PNG',
        'https://lms-tester.s3-ap-northeast-1.amazonaws.com/avatar/robot_07.PNG', 
        'https://lms-tester.s3-ap-northeast-1.amazonaws.com/avatar/robot_08.PNG', 
        'https://lms-tester.s3-ap-northeast-1.amazonaws.com/avatar/robot_09.PNG',
        'https://lms-tester.s3-ap-northeast-1.amazonaws.com/avatar/robot_10.PNG' 
    ]  

    game = Games.query.filter_by(gameSet=0).first()
    if game:
        print ('FOUND GAME ', game)
        game.gameSet = 1
        room = str(game.id) + roomTag 
        gameID = game.id
        gameSet = 1  # this means we are joining an existing game
        db.session.commit()         
          
    # no game ready to join, so make new game
    if gameSet == None: 
        random.shuffle(avatars)

        # player dict
        pDict = {
            'p1' : player, 
            'p2' : 'Waiting', 
            'sid1' : request.sid, 
            'sid2' : None, 
            'avatar1' : avatars[0],
            'avatar2' : avatars[1]
        }

        qString = add_questions(number_of_qs) # random questions function

        newGame = Games(players=str(pDict), gameSet=0, records=qString)
        db.session.add(newGame)
        db.session.commit()
        print (newGame.id)
        player = 'p1'
        room = str(newGame.id) + roomTag

    # game is available to join
    elif gameSet == 1:         
        challenge = Games.query.filter_by(id=gameID).first()        
        if challenge.gameSet == 1:
            pDict = ast.literal_eval(challenge.players)
            qDict = ast.literal_eval(challenge.records)
            p1 = pDict['p1']
            pDict['p2'] = player
            if p1 == player:
                # cannot play against yourself
                return None
            elif player == 'Bot':
                pDict['avatar2'] = "https://lms-tester.s3-ap-northeast-1.amazonaws.com/avatar/bot_01.png"                
           
            pDict['sid2'] = request.sid 
            pDict['gameID'] = room
            print (pDict) 

            ## create results dictionary for score tally later
            rDict = {}  
            botPoints = [0,1,1]      
            for number in qDict: 
                if player == 'Bot':  
                    botScore = random.choice(botPoints)
                    botTime = random.randint(20,70)
                else:
                    # no bot so....
                    botScore = 0
                    botTime = 0                              
                rDict[qDict[number]['q'][0]] = { pDict['p1'] : [0,0], pDict['p2'] : [botScore, botTime] }

            print ('RDICT')
            pprint(rDict)
            rString = json.dumps(rDict)  
            challenge.results = rString
            challenge.players = str(pDict)
            challenge.gameSet = 1        
            db.session.commit()                         
            player = 'p2'  
            room = room
            qString = challenge.records        
        else:
            # bot is too late to join 
            print('too late to join')
            return None
        

    return {
        # this will be joining as p1 or as p2
        'player': player, 
        'room': room, 
        'qString': qString, 
        'pDict' : pDict, 
        'qs' : number_of_qs
        }

@socketio.on('connect')
def on_connect():
    """User connects"""
    print('connect_python')
    send({"username": current_user.username})


@socketio.on('join')
def on_join(data):
    """User joins a room"""
    print('join started')
    player_game = set_game(None)    
    if player_game == None:
        return 'ERROR - No Game Set'
    print (player_game)
    room = player_game['room']
    player = player_game['player']
    qString = player_game['qString']
    pDict = player_game['pDict']
    qs = player_game['qs']
    
    join_room(room)      
    
    emit('playerReady', {'player': player, 'room': room, 'qString': qString, 'pDict': pDict, 'qs': qs}, room=room)

@socketio.on('bot')
def bot_mode(data):
    Games = set_environment()[0] 

    room = data['room']
    gameID = int(room.split('_')[0])
    #using 'room' as an argument means the bot will be loaded
    player_game = set_game(room)  
    qs = player_game['qs'] 
    pDict = player_game['pDict']      

    game = Games.query.filter_by(id=gameID).first()
    results = ast.literal_eval(game.results)
    
    botDict = {}
    count = 1
    for vocab in results:
        botDict[count] = results[vocab]['Bot'][1]        
        count += 1
    print ('botDict ', botDict)

    emit('botReady', {'pDict': pDict, 'botDict': botDict, 'qs':qs}, room=room)


@socketio.on('choice_made')
def choice_made(data):
    print ('choice', data)  

    room = data['room']
    username = data['username'] 
    player = data['player']  
    
    socketio.emit('turn', {'player' : player}, room=room)

@socketio.on('finish')
def finish(data): 
    Games = set_environment()[0]    

    room = data['room']
    gameID = int(room.split('_')[0])
    username = data['username']
    ajData = json.loads(data['ajData'])    

    print('AJDATA', ajData)    
    game = Games.query.filter_by(id=gameID).first()
    game_results = ast.literal_eval(game.results)
    
    for q in ajData:
        game_results[q][username][0] = ajData[q][0]
        game_results[q][username][1] = ajData[q][1]
    
    game.results = str(game_results)
    game.gameSet = 2
    db.session.commit()
      
    print ('GAME_RESULTS', game_results)
    
    socketio.emit('end', {'username':username}, room=room)
    leave_room(room)

@socketio.on('lost_player')
def lost(data): 
    Games = set_environment()[0] 

    room = data['room']
    try:
        gameID = int(room.split('_')[0])
    except:
        print('No Room Found')
        return False
    username = data['username'] 

    game = Games.query.filter_by(id=gameID).first()
    pDict = ast.literal_eval(game.players)
    if username == pDict['p1']: 
        game.gameSet = 3
        game.winner = pDict['p2']
        db.session.commit()
    elif username == pDict['p2']:  
        game.gameSet = 3
        game.winner = pDict['p1']
        db.session.commit()
    else:
        print('No Match Found')
        return False 

    print ('lost_player', data, room ) 
    socketio.emit('lost', {'username':username, 'room':room}, room=room)

@socketio.on('disconnect')
def test_disconnect():
    print('Client Disconnected')