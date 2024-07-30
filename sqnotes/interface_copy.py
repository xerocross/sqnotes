
SQNOTES_NOT_INITIALIZED_MESSAGE = "SQNotes is not initialized; please initialize now. (Run py with -h to see the help menu.)"
DATABASE_EXCEPTION_MESSAGE = lambda : "SQNotes encountered an unexpected database error."
SETTING_UP_DATABASE_MESSAGE = lambda : 'SQNotes is setting up your notes database for keeping track of keywords.'
UNKNOWN_ERROR = lambda : 'Sorry. An unknown error has occurred.'
DATA_NOT_SAVED = lambda : 'Data may not have been saved correctly'
EXITING = lambda : 'Exiting now'
COULD_NOT_OPEN_DATABASE = lambda : 'SQNotes could not open the database.'
NOTE_ADDED = lambda : "Note added: {}"
TEXT_EDITOR_SUBPROCESS_ERROR = lambda : "Encountered an error attempting to open the configured text editor: '{}'."
GPG_SUBPROCESS_ERROR_MESSAGE = lambda : "Encountered an error while attempting to call GPG."
SOME_DELAY_FOR_DECRYPTION = lambda : "This may take some time as search requires decrypting your notes."
GPG_VERIFIED = lambda : "Ran GPG successfully."
GPG_NOT_RUN = lambda : "Could not run GPG."
NEED_TO_INSTALL_GPG = lambda : "Was not able to run GPG on this device. It may not be installed. SQNotes cannot function without GPG."
CALLING_GPG_VERSION = lambda : "Attempting to get GPG version...\n\n"
SUPPORTED_TEXT_EDITORS = lambda : "Supported text editors include these: {}"
NOTE_NOT_FOUND_ERROR = lambda : "Could not find the selected note: {}"
