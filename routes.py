import sys, boto3, random
import datetime
import ast
import json
from random import randint
from flask import render_template, url_for, flash, redirect, request, abort, jsonify  
from app import app, db, bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms import LoginForm
from pprint import pprint
from models import *
from flask_socketio import SocketIO, join_room, leave_room, send, emit

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

socketio = SocketIO(app, manage_session=False)


@app.route("/login/<string:stid>", methods=['GET', 'POST'])
def login(stid):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=stid).first()
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
    else:
        form.studentID.data = stid
    return render_template('login.html', title='Login', form=form, stid=stid)

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

@app.route("/fight", methods=['GET', 'POST'])
def fight():

    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('home'))

    users = {
        1: [current_user.username, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQHYKxS5kWkgLPasL6-7by-00UWkA4qmh96e5g8m3VfxBpOzPgR&s'],
        2: ['Unknown', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSVh-nPVkZ4hnJXNsFoUOWH2B7o49NLqwN8jr6hefjLDJqWHi83&s']
    }

    numList = [1, 2, 3]
    recordDict = {}
    for key in numList:
        recordDict[key] = {
            't': 0,
            'q': None,
            'a': None,
            'c': None
        }
    pprint(recordDict)    

    return render_template('fight.html', title='Fight', users=users, username=current_user.username)

@app.route("/fightscores/<string:game>", methods=['GET', 'POST'])
def fight_scores(game):

    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('home'))

    data = Games.query.filter_by(id=game).first()
    game_results = ast.literal_eval(data.results)
    game_qs = ast.literal_eval(data.records)   
    
    pprint(game_results)

    opponent = None 
    rDict = {}
    
    
    for key in game_results:
        for user in game_results[key]:
            if user == current_user.username:
                rDict[key] = game_results[key][user]
            else:
                opponent = user
    
    for key in game_results:
        for user in game_results[key]:
            if user != current_user.username:
                rDict[key] += game_results[key][user]
    
    print (rDict)

    for r in rDict:
        # if both answers are correct
        if rDict[r][0] == 1 and rDict[r][2] == 1:            
            if rDict[r][1] > rDict[r][3]:
                rDict[r].append('faster')
            elif rDict[r][1] ==rDict[r][3]:
                rDict[r].append('even')    
            else:
                rDict[r].append('slower')
        else:
            rDict[r].append('-')



    return render_template('fightscores.html', title='Scores', rDict=rDict, user=current_user.username, opponent=opponent)


def add_questions ():
    with open('Questions.json', "r") as f:
        jload = json.load(f)

    # make a list of number as long as the json dictionary
    numbers = list(range(1, len(jload)+1))

    QUESTIONS = 2
    count = 1 

    qDict = {}
    while count < QUESTIONS +1:
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
        
        pDict = {
            'p1' : current_user.username, 
            'p2' : None, 
            'sid1' : request.sid, 
            'sid2' : None
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
        'player': player, 
        'game': game, 
        'qString': qString
        }



@socketio.on('join')
def on_join(data):
    """User joins a room"""
    
    player_game = set_game()
    #return {'player': player, 'game': game 'qString': qString}

    room = player_game['game']
    player = player_game['player']
    qString = player_game['qString']

    print('ROOM TYPE ', type(room))

    
    join_room(room)      
    
    emit('playerReady', {'player': player, 'room': room, 'qString': qString}, room=room)
    
@socketio.on('questions')
def questions(room):  
    #room is the same as saved game      

    with open('Questions.json', "r") as f:
        jload = json.load(f)

    numbers = list(range(1, len(jload)+1))

    qDict = {}
    for i in range(1, 4):
        random.shuffle(numbers)
        print(numbers)
        aList = [
            jload[str(numbers[0])][1],
            jload[str(numbers[1])][1],
            jload[str(numbers[2])][1]
        ]
        random.shuffle(aList)
        qDict[i] = {
            'q': [
                jload[str(numbers[0])][0],
                jload[str(numbers[0])][1]
            ],
            'a': aList
        }

    pprint(qDict)
    qString = json.dumps(qDict)   

    emit('questions', {'qs': qString, 'room': room['room']}, room=room['room'])


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
    db.session.commit()



      
    print ('GAME_RESULTS', game_results)
    
    socketio.emit('end', {'username':username}, room=room)