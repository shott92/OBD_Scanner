import os
import json
import shutil

class ProtocolManager:
    """
    Manages Vehicle Protocol Packages.
    Path: ~/.candy/protocols/
    """
    def __init__(self):
        self.base_path = os.path.join(os.path.expanduser("~"), ".candy", "protocols")
        self.ensure_directory()

    def ensure_directory(self):
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def list_packages(self):
        """Returns list of local package names (folders)."""
        return [d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))]

    def create_package(self, name, description=""):
        """Creates a new empty protocol package."""
        pkg_path = os.path.join(self.base_path, name)
        if os.path.exists(pkg_path):
            raise FileExistsError(f"Package '{name}' already exists.")
        
        os.makedirs(pkg_path)
        manifest = {
            "name": name,
            "description": description,
            "version": "1.0.0",
            "ecus": {}, # Logical Addr -> Name
            "commands": [] # List of {name: str, payload: hex_str}
        }
        
        with open(os.path.join(pkg_path, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=4)
        return pkg_path

    def load_package(self, name):
        """Loads manifest.json from a package."""
        pkg_path = os.path.join(self.base_path, name)
        manifest_path = os.path.join(pkg_path, "manifest.json")
        
        if not os.path.exists(manifest_path):
            return None
            
        with open(manifest_path, "r") as f:
            return json.load(f)

    def save_package(self, name, data):
        """Saves data to manifest.json."""
        pkg_path = os.path.join(self.base_path, name)
        manifest_path = os.path.join(pkg_path, "manifest.json")
        
        with open(manifest_path, "w") as f:
            json.dump(data, f, indent=4)
