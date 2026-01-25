import json
import time

class VehicleExporter:
    """
    Exports VehicleArchitecture models to file.
    """
    @staticmethod
    def to_json(arch, filepath):
        """
        Exports the architecture to a JSON file.
        """
        data = {
            "meta": {
                "name": arch.name,
                "exported_at": time.time(),
                "tool": "CANdy_Diag_Pro"
            },
            "ecus": []
        }
        
        for addr, ecu in arch.ecus.items():
            ecu_data = {
                "name": ecu['name'],
                "address_hex": f"0x{addr:X}",
                "description": ecu['description'],
                "dids": []
            }
            
            for did_id, did in ecu['dids'].items():
                ecu_data['dids'].append({
                    "id_hex": f"0x{did_id:X}",
                    "name": did['name'],
                    "tag": did['tag']
                })
            
            data['ecus'].append(ecu_data)
            
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Export Error: {e}")
            return False
