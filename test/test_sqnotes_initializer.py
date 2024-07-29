
from sqnotes.sqnotes_module import SQNotes
from injector import Injector


def get_test_sqnotes():
    injector = Injector()
    return injector.get(SQNotes)