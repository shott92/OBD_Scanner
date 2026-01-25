import time
from core.ingestion.vehicle_mapper import VehicleArchitecture

class SnapshotScanner:
    """
    Iterates through a VehicleArchitecture and reads all defined DIDs.
    """
    def __init__(self, connection_manager):
        self.conn = connection_manager
        self.aborted = False

    def shim_read_did(self, ecu_addr, did_id, cmd_bytes):
        """
        Simulate or Perform ReadDID.
        In a real scenario, this would use self.conn.send_and_receive(...)
        """
        # Mock Response for Demo
        # Return random bytes or specific values for known IDs like VIN
        import random
        
        # VIN (0xF190)
        if did_id == 0xF190:
            return b"SAL-MOCK-VIN-123"
            
        # Random data for others
        length = random.randint(1, 4)
        return bytes([random.randint(0, 255) for _ in range(length)])

    def take_snapshot(self, architecture, progress_callback=None):
        """
        Reads all DIDs in the architecture.
        Updates the 'last_value' field in the DID objects in place.
        """
        self.aborted = False
        total_ecus = len(architecture.ecus)
        processed_ecus = 0
        
        for addr, ecu in architecture.ecus.items():
            if self.aborted: break
            
            dids = ecu['dids']
            if not dids:
                processed_ecus += 1
                continue
                
            if progress_callback:
                progress_callback(int((processed_ecus / total_ecus) * 100), f"Reading {ecu['name']}...")
            
            for did_id, did in dids.items():
                if self.aborted: break
                
                # Send Read Command
                # In real app: response = self.conn.send_isotp(addr, did['read_cmd'])
                # Mocking:
                val = self.shim_read_did(addr, did_id, did['read_cmd'])
                
                # Store Value
                # Format as Hex String for display
                did['last_value'] = val.hex().upper()
                did['last_update'] = time.time()
                
                # Small delay to prevent bus flooding (if we were real)
                time.sleep(0.01)
            
            processed_ecus += 1
            
        return architecture

    def abort(self):
        self.aborted = True
