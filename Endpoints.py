from flask import Flask, render_template, jsonify, request
import json, os, signal
from flask_sock import Sock
import time
from Stopwatch import stopwatch
from Audioplayer import audioplayer
from datetime import datetime
from SerialToWebsocketBridge import getESP32Port, SerialToWebsocketBridge
from threading import Thread
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def getStatusFromStopwatchAsJson():
    status_dict = {
        "is_running": str(stopwatch.isRunning),
        "is_resetted": str(stopwatch.isResetted),
        "can_be_started": str(stopwatch.can_be_started()),
        "can_be_stopped": str(stopwatch.can_be_stopped()),
        "can_be_resetted": str(stopwatch.can_be_resetted()),
        "can_be_lapped": str(stopwatch.is_running())
    }
    return {"?status": status_dict}

app = Flask(__name__)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}
sock = Sock(app)

flask_logger = logging.getLogger('werkzeug')
flask_logger.setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

esp32Port = getESP32Port()
bridge = SerialToWebsocketBridge(esp32Port)
bridge_thread = Thread(target=bridge.start)
bridge_thread.start()


@app.route('/')
def index():
    return render_template('stopwatch.html')

@sock.route('/websocket/control_watch')
def control_watch_sock(ws):
    while True:
        message = ws.receive()
        logger.debug(f"Got a message on websocket on /websocket/control_watch: {message}")
        if message.startswith("?status"):
            #this means that the message is a request for the status of the stopwatch. we need to return the status as json
            res = getStatusFromStopwatchAsJson()
            logger.debug(f"Returning the status response on websocket: ?{res}")
            ws.send(res)
        elif message.startswith("$"):
            #this means this is just an information message. We don't need to do anything with it, just log it
            logger.debug(f"Got an information message on websocket on /websocket/control_watch: {message}")
        elif message == "start":
            res = stopwatch.start()
            ws.send(res)
        elif message == "stop":
            res = stopwatch.stop()
            ws.send(res)
        elif message == "lap":
            res = stopwatch.lap()
            ws.send(res)
        elif message == "reset":
            res = stopwatch.reset()
            ws.send(res)
        elif message == "buzzer":
            if stopwatch.isRunning:
                res = stopwatch.stop()
                ws.send(res)
            else:
                res = stopwatch.start()
                ws.send(res)
        elif message == "buzzer_longpress":
            res = stopwatch.reset()
            ws.send(res)
        elif message == "stop_longpress":
            res = stopwatch.reset()
            ws.send(res)
        else:
            logger.debug(f"Got an unkown command on websocket on /websocket/control_watch: {message}")
            ws.send("Unknown command")

#This is used to display the lap times in the frontend
@app.route('/http/get_lap_times')
def get_laps():
    def generate():
        while True:
            lap_times = stopwatch.get_lap_times()
            yield f"data:{lap_times}\n\n"
            time.sleep(0.5)
    return app.response_class(generate(), mimetype='text/event-stream')

@app.route('/http/get_last_stop_times')
def get_last_stop_times():
    def generate():
        while True:
            last_stop_times = stopwatch.last_stop_times
            yield f"data:{last_stop_times}\n\n"
            time.sleep(1)
    return app.response_class(generate(), mimetype='text/event-stream')

#This is used to display the elapsed time in the frontend
@app.route('/http/time')
def get_time():
    def generate():
        while True:
            elapsed_time = stopwatch.get_elapsed_time_formatted()
            yield f"data:{elapsed_time}\n\n"
            time.sleep(0.1)  # Update every 0.1 second
    return app.response_class(generate(), mimetype='text/event-stream')

@app.route('/http/play_audio_with_stopwatch')
def start_audio_with_stopwatch():
    if stopwatch.is_running():
        return "Stop the stopwatch first"
    if not stopwatch.isResetted:
        return "Reset the stopwatch first"
    if audioplayer.is_playing:
        return "Audio is already playing"
    if stopwatch.can_be_started():
        #start a new thread to play the audio. So the stopwatch can be started exactly when the audio says "Vor"
        thread = Thread(target=audioplayer.play)
        thread.start()
        threading.Event().wait(16.6) #start the stopwatch 16.6s after the audio starts playing
        return stopwatch.start()

@app.route('/http/play_only_audio')
def play_only_audio():
    if audioplayer.is_playing:
        return "Audio is already playing"
    thread = Thread(target=audioplayer.play)
    thread.start()
    audioplayer.play()
    return "Audio successfully played"

