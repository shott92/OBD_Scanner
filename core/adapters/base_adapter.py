from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    """
    Abstract base class for all communication adapters.
    """

    @abstractmethod
    def connect(self):
        """
        Establish a connection to the vehicle interface.

        Returns:
            bool: True if connection was successful, False otherwise.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect from the vehicle interface.
        """
        pass

    @property
    @abstractmethod
    def is_connected(self):
        """
        Check the current connection status.

        Returns:
            bool: True if connected, False otherwise.
        """
        pass

    @abstractmethod
    def send_receive(self, command_name, command_obj, command_hex):
        """
        Send a command and receive a response.

        Args:
            command_name (str): The name of the command being sent.
            command_obj (object): The command object (e.g., for OBD).
            command_hex (str): The command payload as a hex string (e.g., for UDS).

        Returns:
            str: The formatted response from the vehicle.
        """
        pass

    @abstractmethod
    def get_type_string(self):
        """
        Returns a string representing the adapter type.

        Returns:
            str: The adapter type name.
        """
        pass
