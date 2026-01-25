import time

class PerformanceMonitor:
    def __init__(self):
        self.active_timers = {}
        self.state = "READY" # READY, ARMED, RUNNING, FINISHED
        self.start_time = 0
        self.end_time = 0
        self.result = 0.0

    def update_speed(self, speed_mph):
        """
        Update state based on current speed.
        Logic for 0-60 MPH timer.
        """
        if self.state == "READY" and speed_mph < 1.0:
            self.state = "ARMED"
        
        elif self.state == "ARMED" and speed_mph > 1.0:
            self.state = "RUNNING"
            self.start_time = time.time()
        
        elif self.state == "RUNNING":
            if speed_mph >= 60.0:
                self.end_time = time.time()
                self.result = self.end_time - self.start_time
                self.state = "FINISHED"
            # Reset if stopped early? 
            # Simplified logic: just keep running until 60 or manual reset
            if speed_mph < 0.1:
                self.state = "ARMED" # Reset if stopped

    def reset(self):
        self.state = "READY"
        self.result = 0.0

    def get_status(self):
        if self.state == "RUNNING":
            return f"Timer: {time.time() - self.start_time:.2f}s"
        elif self.state == "FINISHED":
            return f"0-60: {self.result:.2f}s"
        else:
            return self.state
