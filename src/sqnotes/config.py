
import yaml
from injector import inject

class SQNotesConfig:
    @inject
    def __init__(self, config_file_path : str):
        with open(config_file_path, 'r') as file:
            self.data = yaml.safe_load(file)
            print("loaded data:", self.data)
            
    def get(self, key):
        if key in self.data:
            return self.data[key]
        else: 
            return None