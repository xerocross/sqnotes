epilog_text = """
SQNotes is intended to help you by keeping bits 
of text information at your fingertips for easy recall.
It uses GPG to encrypt your notes and for displaying
the contents to you on-the-fly it decrypts them into
temporary files. To help you find your notes again
more quickly, there is a built-in keyword search. 
Simply include tags in your notes by adding #hashtags
to the note content anywhere in the note, like '#apple'.
Then to find all notes containing that keyword later
use the keywords command as in `sqnotes keywords -k apple`.

Note that keywords are stored in a plaintext data-
base. This is intentional and necessary. The purpose
of the keywords is to allow for fast searching. Text
content other than keywords will not be stored in the
database. The content is only stored in the note files.
"""