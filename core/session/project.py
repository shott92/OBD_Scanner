import json
import os

class Project:
    def __init__(self, name="New Project"):
        self.name = name
        self.protocols = {
            "can": {},
            "lin": {},
            "doip": {}
        }
        self.channels = []

    def save(self, filepath):
        data = {
            "name": self.name,
            "protocols": self.protocols,
            "channels": self.channels
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load(filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Project file not found: {filepath}")

        with open(filepath, 'r') as f:
            data = json.load(f)

        proj = Project(data.get("name", "Unnamed"))
        proj.protocols = data.get("protocols", {})
        proj.channels = data.get("channels", [])
        return proj
