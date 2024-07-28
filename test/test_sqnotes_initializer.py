
from sqnotes import SQNotes
from encrypted_note_helper import EncryptedNoteHelper


def get_test_sqnotes():
    encrypted_note_helper = EncryptedNoteHelper
    sqnotes_obj = SQNotes(encrypted_note_helper = encrypted_note_helper)
    return sqnotes_obj