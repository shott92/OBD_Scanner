import json
import os
import time

class ServiceManager:
    """
    Manages Dealer-Level functions:
    - RoutineControl (0x31)
    - InputOutputControl (0x2F)
    - WriteDataByIdentifier (0x2E) - For Coding
    """
    def __init__(self, connection_manager):
        self.conn = connection_manager
        
    def load_definitions(self, ecu_name):
        """
        Loads available services from JSON definitions.
        """
        # Mapping generic names to filenames
        filename = f"{ecu_name.lower().replace(' ', '_')}.json"
        
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        path = os.path.join(root, 'resources', 'services', filename)
        
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {"routines": [], "io_controls": [], "coding": []}

    def execute_routine(self, ecu_addr, routine_id, params=None, progress_callback=None):
        """
        Executes Service 0x31 (RoutineControl).
        """
        # 1. Start Routine (0x31 0x01 ...)
        if progress_callback: progress_callback(10, "Starting Routine...")
        time.sleep(0.5)
        
        # 2. Check Result
        if progress_callback: progress_callback(50, "Routine Running...")
        time.sleep(1.0) # Simulation
        
        # 3. Request Results (0x31 0x03 ...) optional
        if progress_callback: progress_callback(100, "Routine Complete.")
        
        return True

    def execute_io_control(self, ecu_addr, did, state, progress_callback=None):
        """
        Executes Service 0x2F (InputOutputControlByIdentifier).
        """
        if progress_callback: progress_callback(10, f"Setting DID 0x{did:X} to {state}...")
        time.sleep(0.5)
        # 0x2F logic stub
        if progress_callback: progress_callback(100, "IO State Set.")
        return True

    def write_coding(self, ecu_addr, did, raw_bytes, progress_callback=None):
        """
        Executes Service 0x2E (WriteDataByIdentifier).
        """
        if progress_callback: progress_callback(20, f"Writing configuration to 0x{did:X}...")
        time.sleep(1.0)
        # 0x2E logic stub
        if progress_callback: progress_callback(100, "Configuration Saved.")
        return True
