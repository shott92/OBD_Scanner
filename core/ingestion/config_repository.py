import os
import glob

class ConfigRepository:
    """
    Manages the 3-layer configuration storage (Local, Internal, Public).
    Structure: [Layer]/[Make]/[Model]/[Year]/[ConfigName].cfg
    """
    def __init__(self, base_dir=None):
        if base_dir is None:
            # Default to repo root/resources
            root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.base_dir = os.path.join(root, 'resources', 'configs')
        else:
            self.base_dir = base_dir
            
        self.layers = ['local', 'internal', 'public']
        self._cache = {} # Nested dict: {Make: {Model: {Year: {Layer: Path}}}}

    def scan(self):
        """
        Scans the repository and builds the index.
        """
        self._cache = {}
        
        for layer in self.layers:
            layer_path = os.path.join(self.base_dir, layer)
            if not os.path.exists(layer_path):
                continue
                
            # Walk directory: Make/Model/Year
            # We assume depth 3.
            for make in os.listdir(layer_path):
                make_path = os.path.join(layer_path, make)
                if not os.path.isdir(make_path): continue
                
                if make not in self._cache: self._cache[make] = {}
                
                for model in os.listdir(make_path):
                    model_path = os.path.join(make_path, model)
                    if not os.path.isdir(model_path): continue
                    
                    if model not in self._cache[make]: self._cache[make][model] = {}
                    
                    for year in os.listdir(model_path):
                        year_path = os.path.join(model_path, year)
                        if not os.path.isdir(year_path): continue
                        
                        # Find .cfg or .json files
                        configs = glob.glob(os.path.join(year_path, "*.cfg")) + glob.glob(os.path.join(year_path, "*.json"))
                        
                        if configs:
                            if year not in self._cache[make][model]:
                                self._cache[make][model][year] = {}
                            
                            # Store the first valid config found in this layer
                            # (We could support multiple, but for now 1 per year slot per layer)
                            self._cache[make][model][year][layer] = configs[0]

    def get_makes(self):
        return sorted(list(self._cache.keys()))

    def get_models(self, make):
        if make in self._cache:
            return sorted(list(self._cache[make].keys()))
        return []

    def get_years(self, make, model):
        if make in self._cache and model in self._cache[make]:
            return sorted(list(self._cache[make][model].keys()), reverse=True)
        return []

    def get_config_path(self, make, model, year):
        """
        Returns the path to the config file, prioritizing Local > Internal > Public.
        """
        if make in self._cache and model in self._cache[make] and year in self._cache[make][model]:
            options = self._cache[make][model][year]
            for layer in self.layers:
                if layer in options:
                    return options[layer]
        return None
