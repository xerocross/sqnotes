
from injector import Module, inject, Injector, singleton, provider
from sqnotes.sqnotes_logger import SQNotesLogger
from sqnotes.user_configuration_helper import UserConfigurationHelper
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sqnotes_dir = os.path.abspath(os.path.join(current_dir, "../"))
config_file_path = os.path.join(sqnotes_dir, 'sqnotes/config.yaml')


class InjectionConfigurationModule(Module):
    
    @provider
    def provide_config_file_path(self) -> str:
        return config_file_path
    
    def configure(self, binder):
        binder.bind(SQNotesLogger, to=SQNotesLogger(), scope=singleton)
        binder.bind(UserConfigurationHelper, to=UserConfigurationHelper(), scope=singleton)