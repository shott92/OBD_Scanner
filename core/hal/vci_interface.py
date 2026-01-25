from abc import ABC, abstractmethod

class VCIInterface(ABC):
    """
    Abstract Base Class for Vehicle Communication Interfaces (VCI).
    Enforces a standard API for all hardware adapters (J2534, ELM327, DoIP, etc.).
    """

    def __init__(self, config=None):
        self.config = config or {}
        self._is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the hardware."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the hardware."""
        pass

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @abstractmethod
    def send_frame(self, data: bytes, protocol: str = "CAN", **kwargs):
        """Send a raw frame/message."""
        pass

    @abstractmethod
    def read_frame(self, timeout: float = 0.1):
        """Read a frame/message."""
        pass
        
    def get_name(self) -> str:
        return self.__class__.__name__
