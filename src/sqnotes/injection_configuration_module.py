
from injector import Module, inject, Injector, singleton
from sqnotes.sqnotes_logger import SQNotesLogger
from sqnotes.configuration_module import ConfigurationModule
import os
from dotenv import load_dotenv



class InjectionConfigurationModule(Module):
    def configure(self, binder):
        binder.bind(SQNotesLogger, to=SQNotesLogger(), scope=singleton)
        binder.bind(ConfigurationModule, to=ConfigurationModule(), scope=singleton)