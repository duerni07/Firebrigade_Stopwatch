from Stopwatch import stopwatch, Stopwatch
import Camera
from flask import Flask
from Endpoints import app
from Audioplayer import audioplayer, Audioplayer
import logging
from wakepy import keep

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Bewerbstimer:
    def __init__(self, name: str, stopwatch: Stopwatch, cameras: list, audioplayer: Audioplayer, app: Flask):
        self.name = name
        self.stopwatch = stopwatch
        self.cameras = []
        self.audioplayer = audioplayer
        self.webserver = app
        #check if port is available

        self.webserver.run(host="0.0.0.0", port=5000)
    
    def add_camera(self, camera_path: str):
        self.cameras.append(Camera(camera_path))


if __name__ == "__main__":
        with keep.presenting():
            logger.info("Starting Bewerbstimer")
            logger.info("Open the stopwatch in the browser on http://localhost:5000")
            bewerbstimer = Bewerbstimer("Bewerbstimer FF Stallhofen", stopwatch, [], audioplayer, app)
    

        