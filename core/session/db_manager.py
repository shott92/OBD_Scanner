import os
import cantools
from shutil import copyfile

class DBManager:
    """
    Manages CAN Database (DBC) files.
    Implements the Three-Tier Lookup Strategy:
    1. Local Override (~/.candy/dbc/local)
    2. Team Repo (~/.candy/dbc/team)
    3. Upstream OpenDBC (~/.candy/dbc/opendbc)
    """
    def __init__(self):
        self.base_path = os.path.join(os.path.expanduser("~"), ".candy", "dbc")
        self.tiers = {
            "local": os.path.join(self.base_path, "local"),
            "team": os.path.join(self.base_path, "team"),
            "opendbc": os.path.join(self.base_path, "opendbc")
        }
        self.ensure_directories()
        self.loaded_db = None

    def ensure_directories(self):
        for path in self.tiers.values():
            if not os.path.exists(path):
                os.makedirs(path)

    def load_dbc(self, filename, tier_priority=["local", "team", "opendbc"]):
        """
        Attempts to load a DBC file by checking tiers in order.
        Returns the cantools.db object or None.
        """
        for tier in tier_priority:
            path = os.path.join(self.tiers[tier], filename)
            if os.path.exists(path):
                try:
                    self.loaded_db = cantools.database.load_file(path)
                    return self.loaded_db
                except Exception as e:
                    print(f"Error loading {path}: {e}")
                    return None
        return None

    def import_dbc_file(self, src_path, target_tier="local"):
        """Copies an external DBC file into the proprietary tier."""
        filename = os.path.basename(src_path)
        dest = os.path.join(self.tiers[target_tier], filename)
        copyfile(src_path, dest)
        return dest

    def list_available_dbcs(self):
        """Returns a dict of {tier: [filenames]}."""
        result = {}
        for tier, path in self.tiers.items():
            result[tier] = [f for f in os.listdir(path) if f.endswith(".dbc")]
        return result

    def export_signals_to_dbc(self, signals, filename, tier="local"):
        """
        Export reverse-engineered signals to a new DBC file.
        signals: List of dicts {'name': str, 'start_bit': int, 'length': int, ...}
        """
        db = cantools.database.Database()
        
        # Create a generic message "decoded_feedback" for now, 
        # normally you'd group signals by message ID.
        # This is a placeholder for the logic to convert our internal signal format to cantools objects.
        
        # Example:
        # msg = cantools.database.can.Message(...)
        # db.messages.append(msg)
        
        save_path = os.path.join(self.tiers[tier], filename)
        with open(save_path, 'w') as f:
            f.write(db.as_dbc_string())
        return save_path
