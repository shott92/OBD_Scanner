from abc import ABC, abstractmethod

class FirmwareFile(ABC):
    """
    Abstract Base Class for ECU Firmware Files.
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.header = {} # logical metadata (version, part number)
        self.blocks = [] # list of (address, data_bytes)

    @abstractmethod
    def parse(self):
        """
        Parse the file and populate self.blocks and self.header.
        Returns: True if success, False otherwise.
        """
        pass
