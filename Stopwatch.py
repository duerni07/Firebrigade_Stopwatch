from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Stopwatch:
    def __init__(self):
        logger.info("Initializing Stopwatch")
        time = datetime.now()
        self.start_time = time
        self.end_time = time
        self.isRunning = False
        self.isResetted = True
        self.lap_times = []
        self.last_stop_times = []

    def can_be_started(self) -> bool:
        return not self.isRunning and self.isResetted
    
    def can_be_stopped(self) -> bool:
        return self.isRunning
    
    def can_be_resetted(self) -> bool:
        return not self.isRunning

    def start(self, offset_milliseconds: int = 0) -> str:
        if self.can_be_started():
            current_time = datetime.now()
            offset_delta = timedelta(milliseconds=offset_milliseconds)
            self.start_time = current_time - offset_delta
            self.isRunning = True
            self.isResetted = False
            status = "Stopwatch started at: " + str(self.start_time)
            logger.info(status)
            return status
        elif self.isRunning:
            return "Stopwatch is already running"
        else:
            return "Stopwatch is not resetted. Reset it first"
        
    def lap(self) -> str:
        if self.isRunning:
            self.lap_times.append(self.get_elapsed_time_formatted())
            status = "New Lap: " + self.lap_times[-1]
            logger.info(status)
            return status
        else:
            return "Stopwatch is not running. Start it to record a lap"
        
    def get_lap_times(self) -> list:
        return self.lap_times

    def stop(self) -> None:
        if self.can_be_stopped():
            self.end_time = datetime.now()
            self.isRunning = False
            self.last_stop_times.append(self.get_elapsed_time_formatted())
            status = "Stopwatch stopped at: " + str(self.end_time)
            logger.info(status)
            return status
        else:
            return "Stopwatch is not running"

    def reset(self) -> None:
        if self.can_be_resetted():
            now = datetime.now()
            self.start_time = now
            self.end_time = now
            self.isRunning = False
            self.lap_times = []
            self.isResetted = True
            status = "Stopwatch resetted"
            logger.info(status)
            return status
        else:
            return "Cannot reset. Stopwatch is running. Stop it first"

    def get_elapsed_time(self):
        if self.isRunning:
            return datetime.now() - self.start_time
        else:
            return self.end_time - self.start_time
        
    def get_elapsed_time_formatted(self) -> str:
        # Format the elapsed time to be in the format of SS:MS
        elapsed_time = self.get_elapsed_time().total_seconds()
        return str('{:6.3f}'.format(elapsed_time))
    
    def is_running(self) -> bool:
        return self.isRunning
    

stopwatch = Stopwatch()