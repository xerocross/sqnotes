
from injector import Module, inject, Injector, singleton
from sqnotes.sqnotes_logger import SQNotesLogger
from sqnotes.user_configuration_helper import UserConfigurationHelper
import os
from dotenv import load_dotenv



class InjectionConfigurationModule(Module):
    def configure(self, binder):
        binder.bind(SQNotesLogger, to=SQNotesLogger(), scope=singleton)
        binder.bind(UserConfigurationHelper, to=UserConfigurationHelper(), scope=singleton)