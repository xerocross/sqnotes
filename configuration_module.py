
import os
import configparser

CONFIG_FILENAME = "config.ini"

class ConfigFileReadingException(Exception):
    """Raise if encounter an error trying to parse the config file."""

class ConfigModuleNotInitializedException(Exception):
    """Raise if get/set method called on ConfigurationModule before initialized."""

class ConfigurationModule:
    
    def __init__(self):
        self.CONFIG_DIR = None
        self.is_initialized = False
        self.user_config = None
        
    def _set_config_dir(self, config_dir):
        self.CONFIG_DIR = config_dir
        
    def _get_config_file(self):
        return os.path.join(self.CONFIG_DIR, CONFIG_FILENAME)
        
    def _get_config_dir(self):
        if self.CONFIG_DIR is None:
            raise Exception("CONFIG_DIR not set")
        else:
            return self.CONFIG_DIR

    def get_setting_from_user_config(self, key):
        if not self.is_initialized:
            raise ConfigModuleNotInitializedException()
        
        if 'settings' in self.user_config and key in self.user_config['settings']:
            return self.user_config['settings'][key]
        else:
            return None
        
    def get_global_from_user_config(self, key):
        if not self.is_initialized:
            raise ConfigModuleNotInitializedException()
        if 'global' in self.user_config and key in self.user_config['global']:
            return self.user_config['global'][key]
        else:
            return None
        
    def _save_config(self):
        with open(self.CONFIG_FILE, 'w') as open_file:
            self.user_config.write(open_file)

    def set_global_to_user_config(self, key, value):
        if not self.is_initialized:
            raise ConfigModuleNotInitializedException()
        if 'global' not in self.user_config:
            self.user_config['global'] = {}
        self.user_config['global'][key]= value
        self._save_config()

    def set_setting_to_user_config(self, key, value):
        if not self.is_initialized:
            raise ConfigModuleNotInitializedException()
        if 'settings' not in self.user_config:
            self.user_config['settings'] = {}
        self.user_config['settings'][key]= value
        self._save_config()
    
    def _is_config_dir_exists(self):
        return os.path.exists(self._get_config_dir())
    
    def _is_config_file_exists(self):
        return os.path.exists(self._get_config_file())
    
    def _create_configuration_groups(self):
        if 'global' not in self.user_config:
            self.user_config['global'] = {}
        if 'settings' not in self.user_config:
            self.user_config['settings'] = {}
    
    def _set_is_initialized(self):
        self.is_initialized = True
        
    def open_or_create_and_open_user_config_file(self):
        # Ensure the configuration directory exists
        CONFIG_DIR = self._get_config_dir()
        self.CONFIG_FILE = self._get_config_file()
        
        if not self._is_config_dir_exists():
            print(f"creating new user_config directory {self._get_config_dir()}")
            os.makedirs(CONFIG_DIR)
            
        user_config = configparser.ConfigParser()
        self.user_config = user_config
        
        if self._is_config_file_exists():
            try:
                user_config.read(self.CONFIG_FILE)
            except Exception:
                raise ConfigFileReadingException()
        else:
            self._create_configuration_groups()
            self._save_config()
            self._set_is_initialized()
        return user_config
            
            
            
            
            
            
            
            
            
    