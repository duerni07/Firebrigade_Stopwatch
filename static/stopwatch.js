class StopwatchStatus {
    constructor(){
        this.isRunning = false;
        this.isResetted = true;
        this.canBeStarted = true;
        this.canBeStopped = false;
        this.canBeLapped = false;
        this.canBeResetted = false;
    }

    setStatus(statusJson) {
        this.isRunning = statusJson.is_running === 'True';
        this.isResetted = statusJson.is_resetted === 'True';
        this.canBeStarted = statusJson.can_be_started === 'True';
        this.canBeStopped = statusJson.can_be_stopped === 'True';
        this.canBeLapped = statusJson.can_be_lapped === 'True';
        this.canBeResetted = statusJson.can_be_resetted === 'True';
    }
}
let stopwatchStatus = new StopwatchStatus(); //this is used to display which buttons are enabled or disabled

//update the main timer
const timerElement = document.getElementById('timer');
const eventSource = new EventSource('/http/time');
eventSource.onmessage = function(event) {
    timerElement.innerText = event.data;
};

//update the displayed lap times
const eventSource2 = new EventSource('/http/get_lap_times');
eventSource2.onmessage = function(event) {
    const lapTimesElement = document.getElementById('lap-times');
    lapTimesElement.innerHTML = '';
    let lap_times = event.data.replace(/'/g, '"')
    for (let lapTime of JSON.parse(lap_times)){
        const li = document.createElement('li');
        li.innerText = lapTime;
        lapTimesElement.appendChild(li);
    }
};

//update the displayed last stop times
const eventSource3 = new EventSource('/http/get_last_stop_times');
eventSource3.onmessage = function(event) {
    const lastStopTimesElement = document.getElementById('last_stoptimes');
    lastStopTimesElement.innerHTML = '';
    let last_stop_times = event.data.replace(/'/g, '"')
    for (let lastStopTime of JSON.parse(last_stop_times)){
        const li = document.createElement('li');
        li.innerText = lastStopTime;
        lastStopTimesElement.appendChild(li);
    }
};

let websocket_url = 'ws://' + location.host + '/websocket/control_watch';
let socket = null;

function connect_websocket(){
    socket = new WebSocket(websocket_url);

    socket.onopen = function(event) {
        console.log('WebSocket of Browser successfully connected to the backend!');
    };
    
    socket.onmessage = function(event) {
        console.log('Websocket message from backend: ', event.data);
        if (event.data.includes('?status')){
            const json = JSON.parse(event.data.replace(/'/g, '"'));
            const status = json['?status'];
            stopwatchStatus.setStatus(status);
        }
    };
    
    socket.onclose = function(event) {
        console.log('WebSocket connection closed');
        alert('Websocket connection to the backend got closed. Trying to refresh the page to reconnect the websocket.');
        location.reload(true);
    };
    
    socket.onerror = function(event) {
        console.log('WebSocket error: ', event);
        alert('Websocket error occurred. Trying to refresh the page to reconnect the websocket.');
        location.reload(true);
    };  

}

connect_websocket();

const startButton = document.getElementById('start');
const stopButton = document.getElementById('stop');
const resetButton = document.getElementById('reset');
const lapButton = document.getElementById('lap');
const audioWithStopwatchButton = document.getElementById('start_audio_with_stopwatch');
const audioOnlyButton = document.getElementById('play_audio_only');

startButton.addEventListener('click', function() {
    console.log('Start button clicked in frontend:', get_browser_time());
    socket.send('start');
});
stopButton.addEventListener('click', function() {
    console.log('Stop button clicked in frontend:', get_browser_time());
    socket.send('stop');
});
resetButton.addEventListener('click', function() {
    socket.send('reset');
});
lapButton.addEventListener('click', function() {
    socket.send('lap');
});
audioWithStopwatchButton.addEventListener('click', async function() {
    const response = await fetch('/http/play_audio_with_stopwatch')
    const text = await response.text();
    console.log(text);
});
audioOnlyButton.addEventListener('click', function() {
    fetch('/http/play_only_audio');
});


function get_browser_time(offset=1) {
    const now = new Date();
    now.setHours(now.getHours() + offset); // Adding one hour for my timezone
    const isoString = now.toISOString();
    return isoString;
}




//every 100ms, ask the backend for the status of the stopwatch (to update the buttons)
setInterval(function(){
    //check if websocket is connected
    if (socket.readyState == WebSocket.OPEN){
        socket.send('?status');
    }
}, 100);

//finally, update the buttons based on the status of the stopwatch we got from the backend
setInterval(function(){
    if (stopwatchStatus.canBeStarted){
        startButton.disabled = false;
        audioWithStopwatchButton.disabled = false;
        audioOnlyButton.disabled = false;
    }
    else {
        startButton.disabled = true;
        audioWithStopwatchButton.disabled = true;
        audioOnlyButton.disabled = true;
    }
    if (stopwatchStatus.canBeStopped){
        stopButton.disabled = false;
    }
    else {
        stopButton.disabled = true;
    }

    if (stopwatchStatus.canBeResetted){
        resetButton.disabled = false;
    }
    else {
        resetButton.disabled = true;
    }

    if (stopwatchStatus.canBeLapped){
        lapButton.disabled = false;
    }
    else {
        lapButton.disabled = true;
    }
}, 100);