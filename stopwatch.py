import time


# Stopwatch keeps track of a start date, returns laps, and can be reset. Useful for timing functions.
class Stopwatch:
    def __init__(self):
        self.start = time.time()
        self.last_lap_start = None

    def reset(self):
        self.start = time.time()
        self.last_lap_start = None

    def lap(self):
        t = time.time()
        if self.last_lap_start is not None:
            lap_time = t - self.last_lap_start
        else:
            lap_time = t - self.start
        self.last_lap_start = t
        return lap_time

    def total(self):
        return time.time() - self.start
