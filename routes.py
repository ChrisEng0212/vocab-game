import sys, boto3, random
from random import shuffle
from datetime import datetime, timedelta
import ast
import json
from random import randint
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt, socketio, login
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms import LoginForm
from pprint import pprint
from models import *
from flask_socketio import SocketIO, join_room, leave_room, send, emit




@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()

    if form.validate_on_submit():
        new_user = User(username=form.username.data, studentID=form.studentID.data)
        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user)
        flash(f'Logged In', 'secondary')
        return redirect(url_for('home'))
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(
                f'Login Successful. Welcome back {current_user.username}.', 'success')
            return redirect(url_for('home'))
        elif True:
            login_user(user)
            flash(
                f'Login Successful. Welcome back {current_user.username}.', 'success')
        else:
            flash(
                f'Login Unsuccessful. Please check your password.', 'danger')
            return redirect(url_for('login', stid=current_user.username))
    
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

    return render_template("home.html")

@app.route('/waiting', methods=['POST'])
def waiting():  

    count = Games.query.filter_by(gameSet=0).count()
    print ('Waiting', count)
    games = Games.query.filter_by(gameSet=1).count()
    game_records = Games.query.filter_by(gameSet=1).all()
    for game in game_records:
        if game.date_posted < datetime.now() - timedelta(minutes=2):
            game.gameSet == 3
            print ('game stopped')
            db.session.commit()

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

    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('home'))

    data = Games.query.filter_by(id=game).first()
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
        winner = player
    elif scores[opponent] > scores[player]:
        winner = opponent
    else:
        winner = 'EVENS'

    # add winner to games data base
    data.winner = winner
    db.session.commit()   

    return render_template('fightscores.html', title='Scores', player=player, opponent=opponent, game_results=game_results, winner=winner)





def add_questions ():
    with open('FRDQs.json', "r") as f:
        jload = json.load(f)

    # make a list of number as long as the json dictionary
    numbers = list(range(1, len(jload)+1))

    QUESTIONS = 6
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

def set_game():
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
    
    games = Games.query.all()

    # assume no games are set
    gameSet = None    
    gameID = 0
    for game in games:
        # check if game is available
        if game.gameSet == 0:
            # no partner yet
            gameID = game.id
            gameSet = 1            

    # no game ready to join, so make new game
    if gameSet == None: 

        random.shuffle(avatars)

        pDict = {
            'p1' : current_user.username, 
            'p2' : 'Waiting', 
            'sid1' : request.sid, 
            'sid2' : None, 
            'avatar1' : avatars[0],
            'avatar2' : avatars[1]
        }

        qString = add_questions() # random questions function

        newGame = Games(players=str(pDict), gameSet=0, records=qString)
        db.session.add(newGame)
        db.session.commit()
        print (newGame.id)
        player = 'p1'
        game = newGame.id

    # game is available to join
    elif gameSet == 1: 
        challenge = Games.query.filter_by(id=gameID).first()
        pDict = ast.literal_eval(challenge.players)
        qDict = ast.literal_eval(challenge.records)
        pDict['p2'] = current_user.username
        pDict['sid2'] = request.sid 
        pDict['gameID'] = gameID
        print (pDict) 

        ## create results dictionary for score tally later
        rDict = {}        
        for number in qDict:
            rDict[qDict[number]['q'][0]] = { pDict['p1'] : [0,0], pDict['p2'] : [0,0] }

        print ('RDICT', rDict)
        rString = json.dumps(rDict)  
        challenge.results = rString
        challenge.players = str(pDict)
        challenge.gameSet = 1        
        db.session.commit()                         
        player = 'p2'  
        game = gameID 
        qString = challenge.records

    return {
        # this will be joining as p1 or as p2
        'player': player, 
        'game': game, 
        'qString': qString, 
        'pDict' : pDict
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
    player_game = set_game()
    #return {'player': player, 'game': game 'qString': qString}
    print (player_game)
    room = player_game['game']
    player = player_game['player']
    qString = player_game['qString']
    pDict = player_game['pDict']
    
    join_room(room)      
    
    emit('playerReady', {'player': player, 'room': room, 'qString': qString, 'pDict': pDict}, room=room)


@socketio.on('choice_made')
def choice_made(data):
    print (data)  

    room = int(data['room'])
    username = data['username']   
    
    socketio.emit('turn', {'username':username}, room=room)

@socketio.on('finish')
def finish(data):
    print (data)  

    room = int(data['room'])
    username = data['username']
    ajData = json.loads(data['ajData'])
    

    print('AJDATA', ajData)
    #{'username': 'Chris', 'ajData': '{"valuable":[0,1],"present":[1,4]}', 'room': '112'}
    game = Games.query.filter_by(id=room).first()
    game_results = ast.literal_eval(game.results)
    
    for q in ajData:
        game_results[q][username][0] = ajData[q][0]
        game_results[q][username][1] = ajData[q][1]
    
    game.results = str(game_results)
    game.gameSet = 2
    db.session.commit()
      
    print ('GAME_RESULTS', game_results)
    
    socketio.emit('end', {'username':username}, room=room)

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')