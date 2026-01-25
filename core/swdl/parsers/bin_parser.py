import os
from ..firmware import FirmwareFile

class BinParser(FirmwareFile):
    """
    Parses Raw Binary Files.
    Assumes a fixed start address (default 0x0000_8000) for prototype.
    """
    def parse(self):
        if not os.path.exists(self.filepath): return False
        
        try:
            with open(self.filepath, 'rb') as f:
                data = f.read()
            
            self.header['file_type'] = "Raw Binary"
            self.header['size'] = len(data)
            
            # For RAW binaries, we don't know the address unless user specifies or we guess.
            # We'll default to 0x8000 for demo
            self.blocks.append((0x8000, data))
            
            return True
        except:
            return False
