import time
from datetime import datetime


class FunctionTimer:
    def __init__(self, name):
        self.name = name
        self.active_sub_timer = None
        self.actions = []
        self.stopwatch = Stopwatch()
        self.return_time = None

    def reset(self, name):
        self.name = name
        self.active_sub_timer = None
        self.actions = []
        self.stopwatch = Stopwatch()
        self.return_time = None

    def start_function(self, name):
        if self.active_sub_timer is None:
            function_timer = FunctionTimer(name)
            self.active_sub_timer = function_timer
            self.actions.append(function_timer)
        else:
            self.active_sub_timer.start_function(name)

    def function_return(self):
        if self.active_sub_timer is None:
            self.return_time = self.stopwatch.lap()
            return False

        if not self.active_sub_timer.function_return():
            self.stopwatch.lap()  # Lap for time_action
            self.active_sub_timer = None

        return True

    def time_action(self, action_name):
        if self.active_sub_timer is None:
            timing = self.stopwatch.lap()
            self.actions.append(ActionTiming(action_name, timing))
        else:
            self.active_sub_timer.time_action(action_name)

    def timings_string(self):
        return '\n'.join(self.timings_string_pieces())

    def timings_string_pieces(self):
        this_function_time = self.return_time
        if this_function_time is None:  # Maybe we aren't returned yet.
            this_function_time = time.time() - self.stopwatch.start

        pieces = ['{}() [{}]'.format(self.name, self.format_time(this_function_time))]
        for action in self.actions:
            if type(action) is FunctionTimer:
                for piece in action.timings_string_pieces():
                    pieces.append('\t{}'.format(piece))
            elif type(action) is ActionTiming:
                pieces.append('\t{}: [{}]'.format(action.name, self.format_time(action.timing)))
        return pieces

    def format_time(self, t):
        return datetime.utcfromtimestamp(t).strftime("%H:%M:%S.%f")


class ActionTiming:
    def __init__(self, name, timing):
        self.name = name
        self.timing = timing


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


default = FunctionTimer('init')
