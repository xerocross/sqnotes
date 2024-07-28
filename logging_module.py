
from injector import Module, inject, Injector, singleton
from sqnotes_logger import SQNotesLogger

class LoggingModule(Module):
    def configure(self, binder):
        binder.bind(SQNotesLogger, to=SQNotesLogger(), scope=singleton)