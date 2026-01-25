import os
import json
import shutil

class FirmwareRepository:
    """
    Manages storage and retrieval of ECU binaries (.bin, .vbf)
    Structure: resources/firmware/[Make]/[Model]/[ECU]/
    """
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.repo_dir = os.path.join(self.root_dir, 'resources', 'firmware')
        if not os.path.exists(self.repo_dir):
            os.makedirs(self.repo_dir)

    def get_makes(self):
        return [d for d in os.listdir(self.repo_dir) if os.path.isdir(os.path.join(self.repo_dir, d))]

    def get_models(self, make):
        path = os.path.join(self.repo_dir, make)
        if not os.path.exists(path): return []
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    def get_ecus(self, make, model):
        path = os.path.join(self.repo_dir, make, model)
        if not os.path.exists(path): return []
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    def get_files(self, make, model, ecu):
        path = os.path.join(self.repo_dir, make, model, ecu)
        if not os.path.exists(path): return []
        
        # Look for index.json
        index_path = os.path.join(path, 'index.json')
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    return json.load(f)
            except:
                pass
                
        # Fallback: list files
        files = []
        for f in os.listdir(path):
            if f.endswith('.bin') or f.endswith('.vbf'):
                files.append({"filename": f, "type": "Unknown", "version": "1.0", "notes": "Auto-detected"})
        return files

    def get_file_path(self, make, model, ecu, filename):
        return os.path.join(self.repo_dir, make, model, ecu, filename)
