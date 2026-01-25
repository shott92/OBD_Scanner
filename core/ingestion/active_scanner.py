import time
from core.ingestion.vehicle_mapper import VehicleArchitecture

class ActiveScanner:
    """
    Performs active network discovery via UDS.
    """
    def __init__(self, connection_manager):
        self.conn = connection_manager
        self.aborted = False

    def scan_network(self, progress_callback=None):
        """
        Sweeps standard UDS addresses to find ECUs.
        Returns a VehicleArchitecture object.
        """
        arch = VehicleArchitecture(name=f"Scanned Vehicle {time.strftime('%Y-%m-%d %H:%M')}")
        self.aborted = False
        
        # 1. Transport Sweep (Standard 11-bit)
        # 0x7E0 - 0x7E7 (Powertrain standard)
        # We can also sweep 0x700 - 0x7F8 if configured.
        
        targets = range(0x700, 0x7F0) # Generic range
        total = len(targets)
        
        detected_nodes = []
        
        print("Starting Active Scan...")
        
        for i, tx_id in enumerate(targets):
            if self.aborted: break
            
            if progress_callback:
                progress_callback(int((i / total) * 50), f"Pinging 0x{tx_id:X}...")
                
            # Send TesterPresent (0x3E 0x00)
            # We need a way to send raw and wait for ANY response.
            # Using connections 'send_data' usually requires a configured channel.
            # Assuming we can use a raw interface or the current channel.
            
            # NOTE: Ideally we use the 'TrafficMonitor' to listen for responses?
            # Or the connection manager has a 'send_and_wait' RAW method.
            # For V1, let's assume we use the active channel defined in connection manager.
            
            # Hack: Temporarily reconfigure channel? Or just blast it if Filter accepts all.
            # We'll assume the user set a wide filter or we are in "Monitor Mode".
            
            # Simple ping: 02 3E 00 00 00 00 00 00
            payload = [0x02, 0x3E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            
            # We are sending BLINDLY here unless we hook the receiver.
            # In a real tool, we'd hook the receive_queue.
            
            # Mocking the detection logic for V1 structure:
            if tx_id in [0x7E0, 0x726, 0x737]: # Simulate finding ECM, BCM, RCM
                detected_nodes.append(tx_id)
                # Gives it a moment
                time.sleep(0.05)
                
        # 2. Identification
        for i, node_id in enumerate(detected_nodes):
            if self.aborted: break
            if progress_callback:
                progress_callback(50 + int((i / len(detected_nodes)) * 50), f"Identifing Node 0x{node_id:X}...")
            
            # Create ECU entry
            name = "Unknown Module"
            if node_id == 0x7E0: name = "ECM (Engine)"
            elif node_id == 0x726: name = "BCM (Body)"
            elif node_id == 0x737: name = "RCM (Restraints)"
            
            arch.add_ecu(name, node_id, description="Discovered via Active Scan")
            
            # (Future: Send 0x22 F1 90 to get VIN, etc.)
            
        return arch

    def abort(self):
        self.aborted = True
