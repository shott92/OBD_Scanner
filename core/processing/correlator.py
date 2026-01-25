from collections import defaultdict
import statistics

class Correlator:
    """
    Analyzes time-series CAN data to find signals that correlate with a user action.
    Splits data into 'Baseline' (Start -> T+Baseline) and 'Active' (T+Baseline -> End).
    """
    def __init__(self):
        pass

    def analyze_series(self, log_data, baseline_duration=1.5):
        """
        log_data: List of tuples (timestamp, arb_id, data_bytes)
        baseline_duration: Seconds to treat as "idle" at the start.
        
        Returns: List of candidates
        """
        if not log_data:
            return []
            
        start_time = log_data[0][0]
        split_time = start_time + baseline_duration
        
        # Organize by ID
        # { arb_id: {'base': [frame_bytes], 'act': [frame_bytes]} }
        signals = defaultdict(lambda: {'base': [], 'act': []})
        
        for ts, aid, data in log_data:
            if ts < split_time:
                signals[aid]['base'].append(data)
            else:
                signals[aid]['act'].append(data)
                
        candidates = []
        
        for aid, buckets in signals.items():
            base_frames = buckets['base']
            act_frames = buckets['act']
            
            if not base_frames or not act_frames:
                continue
                
            dlc = len(base_frames[0])
            
            # Analyze Bit-wise
            for byte_idx in range(dlc):
                for bit_idx in range(8):
                    mask = 1 << bit_idx
                    
                    # Extract bit streams
                    base_bits = [(b[byte_idx] & mask) > 0 for b in base_frames]
                    act_bits = [(b[byte_idx] & mask) > 0 for b in act_frames]
                    
                    # 1. Stability Check on Baseline
                    # Ideally, baseline should be constant.
                    # Allow minor noise? No, strict for now.
                    base_val = base_bits[0]
                    if not all(b == base_val for b in base_bits):
                        continue # Noisy baseline -> ignore (likely counter/checksum)
                        
                    # 2. Activity Check
                    # Did it change during the Action phase?
                    # - Binary Toggle: It flips to !base_val and stays? Or toggles back?
                    # - Analog Sweep: It toggles frequently?
                    
                    changes = sum(1 for b in act_bits if b != base_val)
                    if changes > 0:
                        # Characterize the change
                        unique_act = set(act_bits)
                        
                        score = 0.0
                        desc_type = "Unknown"
                        
                        if len(unique_act) == 1 and (list(unique_act)[0] != base_val):
                            # Perfect Toggle (0 -> 1 and stayed 1)
                            score = 1.0
                            desc_type = "Binary Switch"
                        elif len(unique_act) > 1:
                            # It varied during action
                            # Check transition count to distinguish random noise from sweep
                            # Simple heuristic: If it was stable in baseline and active in action, it's a candidate
                            score = 0.8
                            desc_type = "Dynamic/Sweep"
                            
                        candidates.append({
                            'id': aid,
                            'byte': byte_idx,
                            'bit': bit_idx,
                            'score': score,
                            'change': desc_type,
                            'desc': f"ID 0x{aid:X} B{byte_idx}.{bit_idx}"
                        })
        
        # Sort by score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates
