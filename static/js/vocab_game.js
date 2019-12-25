$(document).ready(function(){

    var socket = io.connect('http://127.0.0.1:5000/');

    const username = document.querySelector('#username').innerHTML;

    socket.on('connect', function(){
        //sends to app.py as msg which it prints
        socket.send('User has connected')
    });
    
    
    $('#readyButton').on('click', function() {        
        socket.emit('join', {'username': username}); // def on_join --> set_game
    })  


    //data will be a json automatically
    socket.on('playerReady', function(data){        
        console.log(data)
        //from python --> emit('playerReady', {'player': player, 'room': room, 'qString': qString}, room=room)
        if (data){
            document.querySelector('#ready1').style="color:white;background:green"
            document.querySelector('#readyButton').style="visibility:hidden"
            document.getElementById('qJSON').innerHTML = data.qString
        }
        if (data.player == 'p2'){
             document.querySelector('#ready2').style = "color:white;background:green"  
             document.querySelector('#ready2').innerHTML = data.opponent      
             Wait(1)
        }
        document.getElementById('zone').innerHTML = data.room 
    });

    $('#clicker').on('click', function() {        
        var room = document.getElementById('zone').innerHTML
        socket.emit('choice_made', {'username': username, 'room':room});
    }) 
    
    $('#finish').on('click', function() {
        var room = document.getElementById('zone').innerHTML 
        var ajData = this.value       
        socket.emit('finish', {'username': username, 'ajData':ajData, 'room':room}); // def on_join --> set_game
    })  

    socket.on('turn', function(data){        
        console.log('turn', data)
        //from python --> emit('playerReady', {'player': player, 'room': room, 'qString': qString}, room=room)
        if (data.username == username){
            document.querySelector('#ready1').style="color:white;background:blue"            
        }
        else{
            document.querySelector('#ready2').style="color:white;background:blue" 
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
    document.querySelector('#ready1').style="color:white;background:green"
    document.querySelector('#ready2').style="color:white;background:green"

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

    
    console.log(question, choice, answer, time, point) 
    
    ajData[question] = [point, time]
    console.log(ajData)

    var results = document.createElement("div")
    results.setAttribute('id', 'results')
    container.appendChild(results);

    var result1 = document.createElement("h5")        
        result1.innerHTML = "Question: " + question
        results.appendChild(result1);
    var result2 = document.createElement("h5")        
        result2.innerHTML = "Answer: " + answer
        results.appendChild(result2);
    var result3 = document.createElement("h5")        
        result3.innerHTML = "Point: " + point
        results.appendChild(result3);    
    
    //sends the signal to socket that a choice has been made
    document.getElementById('clicker').click()    
    // send ajData to the html element
    //aj is answer json ...
    document.getElementById('finish').value = JSON.stringify(ajData)

    }



function Start(n){        
        document.getElementById('head').innerHTML = 'Time'
        timer.innerHTML = "10"
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
    timer.innerHTML = '3'
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