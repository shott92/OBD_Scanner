import time
import cantools
from collections import deque, defaultdict
import statistics

class TrafficMonitor:
    """
    Analyzes CAN/network traffic in real-time.
    Tracks:
    - Message Counts & Frequency (Hz)
    - Jitter / Anomalies
    - Decodes signals relative to loaded DBCs.
    """
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        
        # Stats Storage
        # { arb_id: { 'count': int, 'last_ts': float, 'intervals': deque, 'avg_interval': float, 'data': bytes } }
        self.messages = defaultdict(lambda: {
            'count': 0, 
            'last_ts': 0.0, 
            'intervals': deque(maxlen=50), 
            'avg_interval': 0.0,
            'data': b'',
            'decoded': {},
            'is_known': False
        })
        
        self.start_time = time.time()

    def process_frame(self, arb_id, data, timestamp=None):
        """
        Ingest a new CAN frame.
        arb_id: Integer arbitration ID
        data: bytes
        timestamp: float (optional)
        """
        if timestamp is None:
            timestamp = time.time()
            
        entry = self.messages[arb_id]
        
        # Update Intervals
        if entry['last_ts'] > 0:
            delta = timestamp - entry['last_ts']
            entry['intervals'].append(delta)
            
            # Recalc average every 10 frames to save CPU? Or every time?
            # Keeping it simple: running avg
            if len(entry['intervals']) > 1:
                entry['avg_interval'] = statistics.mean(entry['intervals'])
        
        entry['count'] += 1
        entry['last_ts'] = timestamp
        entry['data'] = data
        
        # decoding
        if self.db_manager:
            # Check all loaded tiers for a matching message
            # For efficiency, we might want to cache which DB has this ID.
            # But for now, iterate.
            db_found = False
            for tier in ['local', 'team', 'opendbc']:
                if tier not in self.db_manager.tiers: continue
                # We need access to the actual 'cantools.db' object.
                # The DBManager needs to expose a method "get_message_by_id(id)"
                pass
            
            # Assuming db_manager has a .decode_message(id, data) helper
            if hasattr(self.db_manager, 'decode_message'):
                decoded = self.db_manager.decode_message(arb_id, data)
                if decoded:
                    entry['decoded'] = decoded
                    entry['is_known'] = True
                    db_found = True
            
            if not db_found:
                 entry['decoded'] = {}
                 entry['is_known'] = False
                 
        return entry

    def get_snapshot(self):
        """Returns a snapshot of the current stats for UI rendering."""
        # Convert to a dict structure suitable for the table
        return dict(self.messages)
