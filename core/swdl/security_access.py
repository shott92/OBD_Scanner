class SecurityAccess:
    """
    Handles Seed/Key exchange (Service 0x27).
    """
    def __init__(self):
        self.dll_cache = {}

    def calculate_key(self, seed_bytes, security_level):
        """
        Calculates key from seed.
        In real world, loads a DLL or .sfg file.
        Here we mock a simple algo: Key = Seed ^ 0xFFFF
        """
        if not seed_bytes:
            return b'\x00\x00'
            
        seed_int = int.from_bytes(seed_bytes, 'big')
        key_int = seed_int ^ 0xFFFF
        
        # Return same length as seed (assuming 2 bytes for demo)
        return key_int.to_bytes(len(seed_bytes), 'big')
