import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import time
import logging

AUDIO_FILE_PATH = "./media/Angriffsbefehl.wav"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Audioplayer:
    def __init__(self, audio_file_path) -> None:
        self.audio_file_path = audio_file_path
        try:
            with open(audio_file_path, "r") as f:
                pass
        except FileNotFoundError:
            logger.error(f"File {audio_file_path} not found")
            exit()
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file_path)
        self.is_playing = False

    def play(self) -> None:
        if self.is_playing:
            logger.debug("Cannot play audio because it is already playing")
            return
        logger.debug("Start playing audio")
        self.is_playing = True
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
        self.is_playing = False

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self.is_playing = False
    
    def __del__(self):
        pygame.mixer.quit()

audioplayer = Audioplayer(AUDIO_FILE_PATH)


