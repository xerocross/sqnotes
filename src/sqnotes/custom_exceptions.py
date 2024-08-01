class NotesDirNotConfiguredException(Exception):
    """Exception raised if the user notes directory is not configured."""
    pass

class NotesDirNotSelectedException(Exception):
    """Exception raised if user notes directory not specified."""

class NoteNotFoundException(Exception):
    """Exception raised if attempt to open a note that is not found."""
    
class TextEditorNotConfiguredException(Exception):
    """Raise if attempted to use text editor but not configured."""
    
class DatabaseException(Exception):
    """Raise if an error occurs while interacting with the database."""

class DecryptionFailedException(Exception):
    """Raise if the GPG decryption process is not successful."""



class TextEditorSubprocessException(Exception):
    """Raise when an exception occurs in calling the text editor in a subprocess."""
    
  
class CouldNotRunGPG(Exception):
    """Raise when a command is called that requires GPG and GPG is not available."""

class CouldNotOpenDatabaseException(Exception):
    """Raise if error encountered while attempting to open the database."""

