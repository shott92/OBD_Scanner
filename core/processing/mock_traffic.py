import time
import random

class MockTrafficGenerator:
    """
    Generates fake CAN traffic to test the analysis widget.
    """
    def __init__(self, traffic_monitor):
        self.monitor = traffic_monitor
        self.running = False

    def start(self):
        import threading
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.running = False

    def _run(self):
        # ID 0x123: Engine Data (Fake 20Hz)
        # ID 0x456: Body Data (Unknown, 1Hz)
        
        while self.running:
            # 0x123
            if random.random() < 0.2: # High freq
                data = bytes([random.randint(0, 255) for _ in range(8)])
                self.monitor.process_frame(0x123, data)
            
            # 0x456
            if random.random() < 0.01: # Low freq
                data = b'\xAA\xBB\xCC\xDD'
                self.monitor.process_frame(0x456, data)
                
            time.sleep(0.01) # 100Hz loop
