import re
from core.ingestion.vehicle_mapper import VehicleArchitecture

class JLRConfigParser:
    def parse(self, path):
        """
        Parses a JLR .cfg file (similar to C-structs).
        Returns a VehicleArchitecture object.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            veh = VehicleArchitecture()
            
            # 1. Header Info
            name_match = re.search(r'ConfigName\s*=\s*"(.*?)";', content)
            if name_match:
                veh.name = name_match.group(1)
            
            # 2. Find Node Blocks
            # The format is node { ... }
            # We can regex for `node\s*\{(.*?)\};` with DOTALL
            
            # Simple iterator for safer parsing than regex on nested structures
            # But here nodes seem flat.
            
            node_blocks = re.findall(r'node\s*\{(.*?)\};', content, re.DOTALL)
            
            for block in node_blocks:
                self._parse_node(veh, block)
                
            return veh
            
        except Exception as e:
            print(f"Error parsing JLR CFG: {e}")
            return None

    def _parse_node(self, veh, block_content):
        # Extract ECU properties
        props = {}
        # Matches: key = "value"; or key = 0x123; or key = 10;
        # Handle string values
        str_matches = re.finditer(r'([a-z_0-9]+)\s*=\s*"(.*?)";', block_content)
        for m in str_matches:
            props[m.group(1)] = m.group(2)
            
        # Handle hex/int values
        int_matches = re.finditer(r'([a-z_0-9]+)\s*=\s*(0x[0-9A-Fa-f]+|\d+);', block_content)
        for m in int_matches:
            val_str = m.group(2)
            val = int(val_str, 16) if val_str.startswith('0x') else int(val_str)
            props[m.group(1)] = val
            
        # Validate essential fields
        if 'ecu_address' not in props or 'ecu_name' not in props:
            return # Skip invalid/empty node
            
        ecu = veh.add_ecu(
            name=props['ecu_name'],
            address=props['ecu_address'],
            description=props.get('ecu_info', ''),
            network=props.get('ecu_network', '')
        )
        
        # Parse DIDs within the node block
        # did_readX = 0xAA 0xBB;
        # did_infoX = "String";
        # did_tagX = "TAG";
        
        # We need to group them by index.
        # Find all keys starting with did_read
        
        did_indices = set()
        for key in props.keys():
            # Int keys won't be in match group 1 of str_matches?
            # Actually, my regex separated int and strings.
            # But the did_read has multiple bytes separated by space: 0xE1 0x03
            pass
            
        # Regex for DID Reads specifically: did_read(\d+)\s*=\s*((?:0x[0-9A-Fa-f]+\s*)+);
        did_read_matches = re.finditer(r'did_read(\d+)\s*=\s*((?:0x[0-9A-Fa-f]+\s*)+);', block_content)
        
        dids = {} # {index: {bytes: []}}
        
        for m in did_read_matches:
            idx = int(m.group(1))
            byte_strs = m.group(2).strip().split()
            bytes_val = [int(b, 16) for b in byte_strs]
            dids[idx] = {'cmd': bytes_val}
            
        # Now find infos and tags using string regex again or simple search
        # Note: did_info is string, did_tag is string
        info_matches = re.finditer(r'did_info(\d+)\s*=\s*"(.*?)";', block_content)
        for m in info_matches:
            idx = int(m.group(1))
            if idx in dids:
                dids[idx]['info'] = m.group(2)
                
        tag_matches = re.finditer(r'did_tag(\d+)\s*=\s*"(.*?)";', block_content)
        for m in tag_matches:
            idx = int(m.group(1))
            if idx in dids:
                dids[idx]['tag'] = m.group(2)
                
        # Register DIDs to ECU
        for idx, did_data in dids.items():
            cmd = did_data['cmd']
            # Assume ReadDID (0x22) is standard, so the DID ID is usually the last 2 bytes of the read cmd if it starts with 0x22?
            # OR the config defines the *entire* payload to send.
            # e.g. did_read0 = 0xE1 0x03; -> This looks like the DID ID itself if the service 0x22 is implicit?
            # Wait, 0xE1 0x03 is 2 bytes. 
            # Another example: did_read22 = 0xF1 0x71; -> 2 bytes.
            # Another: did_read1 = 0xD0 0x20;
            # JLR tool likely sends 22 <byte1> <byte2>.
            
            did_id = 0
            if len(cmd) >= 2:
                did_id = (cmd[0] << 8) | cmd[1]
            elif len(cmd) == 1:
                did_id = cmd[0]
                
            veh.add_did_to_ecu(
                ecu_addr=props['ecu_address'],
                did_id=did_id,
                name=did_data.get('info', f"DID 0x{did_id:X}"),
                read_cmd_bytes=cmd,
                tag=did_data.get('tag', '')
            )
