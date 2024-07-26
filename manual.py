
import textwrap
import shutil

basic_usage = """\
SQNotes Basic Usage\


SQNotes is a note-keeping utility for helping you keep useful \
text-based data at your fingertips at the command line. Your notes \
will be stored as files on your computer, not within the app. \
Notes are also encrypted using GPG with your own key pair \
according to your configuration.

Note: all encryption/decryption is done by GPG outside the scope \
of SQNotes.

To aid with searchability, SQNotes indexes your notes by keywords. \
To attach keywords to your notes, simply include hashtags directly \
in your notes when you create them using SQNotes. SQNotes scans \
your notes for hashtags upon creating or editing the note and \
stores these keywords in a plaintext database locally on your \
computer.

Run `sqnotes new` to create a new note. This will open the configured \
text editor ('vim' by default). Write your new note, then save \
and close the editor, and SQNotes will index, encrypt, and save your note.

Find your note later using either full text search (`search`) or \
keyword search (`keyword`).

"""


encryption_info = """\
Encryption \


SQNotes uses GPG and your existing key pair for local encryption \
of your notes.

When you write a note, the plaintext information is \
originally stored in a temporary file on your system. SQNotes then \
calls GPG to encrypt the contents into a new file, which is then \
registered with the SQNotes database. At this point the temporary file \
is deleted.

When reading a note (as in when you search your notes by text or \
by keyword, notes are decrypted in-memory.

When editing a note, the encrypted note file is decrypted into a \
temporary file which is then opened in your text editor. After editing, \
the contents are encrypted and saved back to the original note file \
and the temporary file is deleted.
"""

class Manual:
    
    def _get_wrapped_text(self, input_text, width):
        wrapper = textwrap.TextWrapper(width=width, expand_tabs=False, replace_whitespace=False)
        paragraphs = input_text.split('\n\n')
        # print("paragraphs:")
        # print(paragraphs)
        wrapped_text = ''
        for paragraph in paragraphs:
            wrapped_text += '\n'.join(wrapper.wrap(paragraph))
            wrapped_text += '\n\n'
        return wrapped_text
    
    def print_main_page(self):
        wrapped_text = self._get_wrapped_text(input_text=basic_usage, width=self.width)
        print(wrapped_text)
        
        
    def print_encryption_info(self, ):
        wrapped_text = self._get_wrapped_text(input_text=encryption_info, width=self.width)
        print(wrapped_text)
        
    def __init__(self):
        self.MAX_WIDTH = 70
        self.width =  min(shutil.get_terminal_size().columns, self.MAX_WIDTH)
        
        