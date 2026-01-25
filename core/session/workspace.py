import json
import os

class Workspace:
    def __init__(self):
        self.name = "Untitled"
        self.settings = {
            "theme": "Dark",
            "font_size": 12
        }
        self.hardware_config = {
            "interface": "Simulated",
            "channel": 1
        }
        self.loaded_projects = []

    def save(self, filepath):
        data = {
            "name": self.name,
            "settings": self.settings,
            "hardware_config": self.hardware_config,
            "loaded_projects": self.loaded_projects
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def load(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Workspace file not found: {filepath}")
            
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        self.name = data.get("name", "Untitled")
        self.settings = data.get("settings", {})
        self.hardware_config = data.get("hardware_config", {})
        self.loaded_projects = data.get("loaded_projects", [])
