
import os
import configparser

CONFIG_FILENAME = "config.ini"

class ConfigFileReadingException(Exception):
    """Raise if encounter an error trying to parse the config file."""

class ConfigModuleNotInitializedException(Exception):
    """Raise if get/set method called on ConfigurationModule before initialized."""

SETTINGS_KEY = 'settings'
GLOBAL_KEY = 'global'

class ConfigurationModule:
    
    
    
    def __init__(self):
        self.CONFIG_DIR = None
        self.is_initialized = False
        self.user_config = None
        
    def _set_config_dir(self, config_dir):
        self.CONFIG_DIR = config_dir
        
    def _get_config_file(self):
        return os.path.join(self._get_config_dir(), CONFIG_FILENAME)
        
    def _get_config_dir(self):
        if self.CONFIG_DIR is None:
            raise Exception("CONFIG_DIR not set")
        else:
            return self.CONFIG_DIR

    def get_setting_from_user_config(self, key):
        if not self.is_initialized:
            raise ConfigModuleNotInitializedException()
        
        if SETTINGS_KEY in self.user_config and key in self.user_config[SETTINGS_KEY]:
            return self.user_config[SETTINGS_KEY][key]
        else:
            return None
        
    def get_global_from_user_config(self, key):
        if not self.is_initialized:
            raise ConfigModuleNotInitializedException()
        if GLOBAL_KEY in self.user_config and key in self.user_config[GLOBAL_KEY]:
            return self.user_config[GLOBAL_KEY][key]
        else:
            return None
        
    def _save_config(self):
        with open(self.CONFIG_FILE, 'w') as open_file:
            self.user_config.write(open_file)

    def set_global_to_user_config(self, key, value):
        if not self.is_initialized:
            raise ConfigModuleNotInitializedException()
        if GLOBAL_KEY not in self.user_config:
            self.user_config[GLOBAL_KEY] = {}
        self.user_config[GLOBAL_KEY][key]= value
        self._save_config()

    def set_setting_to_user_config(self, key, value):
        if not self.is_initialized:
            raise ConfigModuleNotInitializedException()
        if SETTINGS_KEY not in self.user_config:
            self.user_config[SETTINGS_KEY] = {}
        self.user_config[SETTINGS_KEY][key]= value
        self._save_config()
    
    def _is_config_dir_exists(self):
        return os.path.exists(self._get_config_dir())
    
    def is_config_file_exists(self):
        return os.path.exists(self._get_config_file())
    
    def _create_configuration_groups(self):
        if GLOBAL_KEY not in self.user_config:
            self.user_config[GLOBAL_KEY] = {}
        if SETTINGS_KEY not in self.user_config:
            self.user_config[SETTINGS_KEY] = {}
    
    def _set_is_initialized(self):
        self.is_initialized = True
        
    def _set_all_settings(self, initial_settings):
        if initial_settings is None:
            return
        
        for key in initial_settings:
            self.user_config[SETTINGS_KEY][key] = initial_settings[key]
            
    
    def _set_all_globals(self, initial_globals):
        if initial_globals is None:
            return
        for key in initial_globals:
            self.user_config[GLOBAL_KEY][key] = initial_globals[key]
    
        
    def _create_and_set_user_config(self):
        user_config = configparser.ConfigParser()
        self.user_config = user_config
        
    def open_or_create_and_open_user_config_file(self, 
                                                 initial_settings : dict = None,
                                                 initial_globals : dict = None):
        # Ensure the configuration directory exists
        CONFIG_DIR = self._get_config_dir()
        self.CONFIG_FILE = self._get_config_file()
        
        if not self._is_config_dir_exists():
            print(f"creating new user_config directory {self._get_config_dir()}")
            os.makedirs(CONFIG_DIR)
            
        self._create_and_set_user_config()
        
        if self.is_config_file_exists():
            try:
                self.user_config.read(self.CONFIG_FILE)
            except Exception:
                raise ConfigFileReadingException()
        else:
            self._create_configuration_groups()
            self._set_all_settings(initial_settings = initial_settings)
            self._set_all_globals(initial_globals = initial_globals)
            self._save_config()
        self._set_is_initialized()
        return self.user_config
            
            
            
            
            
            
            
            
            
    