document.addEventListener('DOMContentLoaded', () =>{
    
    var link = location.protocol + '//' + document.domain + ':' + location.port
    console.log(link)
    
    var socket = io.connect(link);
    //var socket = io.connect('http://' + document.domain + ':' + location.port, {transports: ['websocket']});

    console.log(socket)

    const username = document.querySelector('#username').innerHTML;

    socket.on('connect', function(){
        //sends to app.py as msg which it prints
        console.log('connect_js')
        socket.send('User has connected')
    });
    
    
    $('#readyButton').on('click', function() {
        console.log('readyButton Activated')
        document.querySelector('#readyButton').style="visibility:hidden"   
        alert('if your game does not load in one min, please fresh')
        socket.emit('join', {'username': username}); // def on_join --> set_game
    })  

      
    //data will be a json automatically
    socket.on('playerReady', function(data){        
        console.log(data)
        //from python --> emit('playerReady', {'player': player, 'room': room, 'qString': qString}, room=room)
        if (data){            
                     
            document.getElementById('qJSON').innerHTML = data.qString
            if (data.player == 'p1'){
                document.getElementById('player').innerHTML = 'p1'
                document.querySelector('#name1').style="color:purple; background:white" 
                console.log('p1 set')
                document.getElementById('img1').src = data.pDict['avatar1']
                document.querySelector('#name1').innerHTML = data.pDict['p1']            
            }
            else if (data.player == 'p2'){                
                document.getElementById('img1').src = data.pDict['avatar1']
                document.querySelector('#name1').innerHTML = data.pDict['p1'] 
                document.getElementById('img2').src = data.pDict['avatar2']
                document.querySelector('#name2').innerHTML = data.pDict['p2']
                if (username == data.pDict['p2']){ 
                    document.querySelector('#name2').style = "color:purple; background:white" 
                }
                console.log('p2 set')
                Wait(1)
            }           
            
        }
        document.getElementById('zone').innerHTML = data.room 
    });

    $('#clicker').on('click', function() {        
        var room = document.getElementById('zone').innerHTML
        var player = document.getElementById('player').innerHTML
        socket.emit('choice_made', {'username': username, 'room':room, 'player':player});
    }) 
    
    $('#finish').on('click', function() {
        var room = document.getElementById('zone').innerHTML 
        var ajData = this.value       
        socket.emit('finish', {'username': username, 'ajData':ajData, 'room':room}); // def on_join --> set_game
    })  

    socket.on('turn', function(data){        
        console.log('turn', data)
        //from python --> emit('playerReady', {'player': player, 'room': room, 'qString': qString}, room=room)
        if (data.player == 'p1'){
            document.querySelector('#ready1').style="background:darkturquoise"                        
        }
        else{
            document.querySelector('#ready2').style="background:darkturquoise" 
                 
        }        
    });
    
    socket.on('end', function(data){        
        console.log('end', data)     
    });

});//end of connect sesssion

function checkScore(game){
    window.open(window.location.href + 'scores/' + game)
}

function create_inputs(q){ 
    //set player bars back to green
    document.querySelector('#ready1').style="color:white;background:hotpink"
    document.querySelector('#ready2').style="color:white;background:hotpink"

    var container = document.getElementById("qBox");

    // remove results before next question appears
    if (document.getElementById("results")) {
        container.removeChild(document.getElementById("results"))
    }

    var obj = JSON.parse(document.getElementById('qJSON').innerHTML) 
    console.log(obj)
    console.log(q)   
    qNum = Object.keys(obj).length
    console.log(qNum)
    
    //add div for question and inputs to be created    
    var parent = document.createElement("div")
        parent.setAttribute('id', 'parent');
        container.appendChild(parent);

    if (q > qNum){  
        document.getElementById('stop').innerHTML = 'stop'     
        game = document.getElementById('zone').innerHTML    
        var end = document.createElement("button");        
        end.setAttribute('class' , "btn btn-warning" );           
        end.innerHTML = 'CHECK SCORE'        
        end.setAttribute('value' , game );                
        end.setAttribute('onclick', 'checkScore(this.value)')
        parent.appendChild(end)  

        document.getElementById('finish').click()   
                
        return false
    }

    var header = document.createElement("h1");        
        let question = obj[q]['q'][0]
        let answer = obj[q]['q'][1]
        header.style = "color:purple";
        header.innerHTML = question
        parent.appendChild(header);
    
    

    for (i = 0; i < 3 ; i++) {   

        let choice = obj[q]['a'][i]
        console.log(choice)

        var input = document.createElement("input");
        input.setAttribute('type', 'radio');
        input.setAttribute('id' , choice );
        input.setAttribute('name' , answer );
        input.setAttribute('value' , question );
        input.setAttribute('onclick', 'send_result(this.id, this.name, this.value)');
        parent.appendChild(input);

        var label = document.createElement("label");
        label.setAttribute('for' , choice);
        label.setAttribute('class' , 'choice');
        label.innerHTML = choice
        
        parent.appendChild(label);

        var br = document.createElement("br");        
        parent.appendChild(br);
        
    }

}


function remove_inputs(){
    var container = document.getElementById("qBox")

    var element = document.getElementById('parent');
    console.log(element)
    if (element){        
        var question = element.firstElementChild.textContent
        container.removeChild(element);
        send_result('NoChoice', 'None', question )        
    }
}



//keep json object active in the DOM
var ajData = {}

function send_result(choice, answer, question){
    var container = document.getElementById("qBox");

    // may have been removed by remove_inputs function
    var element = document.getElementById('parent');
    if (element){     
        container.removeChild(element);
    }

    var time = parseInt(document.getElementById('timer').innerHTML);    

    
    if (choice == answer){         
        var point = 1
    } else {
         var point = 0
    }

    
    console.log('CHECK', question, choice, answer, time, point) 
    
    ajData[question] = [point, time]
    console.log(ajData)

    var results = document.createElement("div")
    results.setAttribute('id', 'results')
    container.appendChild(results);

    var result1 = document.createElement("h5")        
        result1.innerHTML = "Vocab: " + question
        result1.style = "color:purple"
        results.appendChild(result1);
    var result2 = document.createElement("h5")        
        result2.innerHTML = "Answer: " + answer
        result2.style = "color:blue"
        results.appendChild(result2);
    var result3 = document.createElement("h5")        
        result3.innerHTML = "point + " + point        
        results.appendChild(result3);    
    
    //sends the signal to socket that a choice has been made
    document.getElementById('clicker').click()    
    // send ajData to the html element
    //aj is answer json ...
    document.getElementById('finish').value = JSON.stringify(ajData)

    }



function Start(n){        
        document.getElementById('head').innerHTML = 'Time'
        timer.innerHTML = "9"
        var x = setInterval(function() {            
            var timer = document.getElementById('timer')
            var count = Number(timer.innerHTML)            
            var newCount = count - 1              
            
            if (newCount == 0){
                clearInterval(x);
                remove_inputs() 
                Wait(n+1)                
            } 
            else {
                timer.innerHTML = newCount 
            }
        }, 1000)
}

function Wait(n) {    
    // when stops comes in at 1 instead of zero the timer should stop
    if (n == 1){
        timer.innerHTML = '8'
    }
    else {
        timer.innerHTML = '3'
    }    
    document.getElementById('head').innerHTML = 'Next Q in..';
      
        var y = setInterval(function() {              
            var timer = document.getElementById('timer')        
            var count = Number(timer.innerHTML)        
            var newCount = count - 1  

            
            if (newCount == 0){
                clearInterval(y);            
                create_inputs(n)
                if (document.getElementById('stop').innerHTML == 'go'){
                    Start(n)
                    }             
            } else {
                timer.innerHTML = newCount 
            }
        }, 1000)
    
}