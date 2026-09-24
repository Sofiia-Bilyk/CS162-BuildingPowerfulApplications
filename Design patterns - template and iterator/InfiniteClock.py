import time

class ClockIterator:
    def __init__(self):
        self.hours = 0
        self.minutes = 0

    def __iter__(self):
        return self

    def __next__(self):
        current_time = f"{self.hours:02}:{self.minutes:02}" # 1:5 -> 01:05
        self.minutes += 1
        if self.minutes == 60:
            self.minutes = 0
            self.hours += 1
        if self.hours == 24:
            self.hours = 0
        return current_time


clock = ClockIterator()
for time in clock:
    print(time)
