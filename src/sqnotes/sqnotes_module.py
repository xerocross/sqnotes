import argparse
import os
import glob
import subprocess
import tempfile
from datetime import datetime
import sqlite3
import re
import sys

from dotenv import load_dotenv
from sqnotes import interface_copy
from sqnotes.printer_helper import PrinterHelper

from sqnotes.manual import Manual
from sqnotes.command_validator import CommandValidator
from sqnotes.encrypted_note_helper import EncryptedNoteHelper, GPGSubprocessException
from injector import inject, Injector
from sqnotes.injection_configuration_module import InjectionConfigurationModule
from sqnotes.sqnotes_logger import SQNotesLogger
from sqnotes.user_configuration_helper import UserConfigurationHelper
from sqnotes.database_service import DatabaseService
from sqnotes.choose_text_editor import ChooseTextEditor, MaxInputAttemptsException
from sqnotes.path_input_helper import PathInputHelper
from sqnotes.fileinfo import FileInfo
from sqnotes.sqnotes_config_module import SQNotesConfig

from sqnotes.custom_exceptions import (
    TextEditorSubprocessException,
    DatabaseException,
    TextEditorNotConfiguredException,
    NotesDirNotConfiguredException,
    NotesDirNotSelectedException,
    CouldNotOpenDatabaseException,
    CouldNotRunGPG,
)


VERSION = "0.2"
DEBUGGING = "--debug" in sys.argv
ASCII_ARMOR_CONFIG_KEY = "armor"
GPG_VERIFIED_KEY = "gpg_verified"
SET_TEXT_EDITOR_INTERACTIVE_FLAG = True

VIM = "vim"
NANO = "nano"
GPG = "gpg"
INITIALIZED = "initialized"
DATABASE_IS_SET_UP_KEY = "database_is_set_up"
NO = "no"
NOTES_PATH_KEY = "notes_path"
GPG_KEY_EMAIL_KEY = "gpg_key_email"
TEXT_EDITOR_KEY = "text_editor"

SUPPORTED_TEXT_EDITORS = [VIM, NANO]


class EnvironmentConfigurationNotFound(Exception):
    """Raise if the environment configuration file is not found."""


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
env_file_path = os.path.join(project_root, ".production.env")
if os.getenv("TESTING") == "true":
    env_file_path = os.path.join(project_root, ".test.env")
else:
    env_file_path = os.path.join(project_root, ".env.production")
if not os.path.exists(env_file_path):
    raise EnvironmentConfigurationNotFound()
else:
    load_dotenv(env_file_path)


SET_NOTES_PATH_INTERACTIVE_FLAG = (os.getenv("SET_NOTES_PATH_INTERACTIVE") == 'yes')
IS_INITIALIZATION_GATE_REFACTORED_INSIDE_SQNOTES = (os.getenv("IS_INITIALIZATION_GATE_REFACTORED_INSIDE_SQNOTES") == 'yes')


class SQNotes:

    NOT_INITIALIZED = 18
    GPG_ERROR = 12
    DEFAULT_NOTES_DIR_KEY = 'DEFAULT_NOTES_DIR'
    USER_CONFIG_DIR_KEY = 'USER_CONFIG_DIR'
    INIT_GLOBALS_KEY = 'INIT_GLOBALS'
    INIT_USER_SETTINGS_KEY = 'INIT_USER_SETTINGS'
    DB_FILE_PATH_KEY = 'DB_FILE_PATH'
    DATABASE_FILE_NAME_KEY = 'DATABASE_FILE_NAME'
    DATABASE_IS_SET_UP_KEY = 'DATABASE_IS_SET_UP'
    @inject
    def __init__(
        self,
        encrypted_note_helper: EncryptedNoteHelper,
        sqnotes_logger: SQNotesLogger,
        user_configuration_helper: UserConfigurationHelper,
        database_service: DatabaseService,
        choose_text_editor: ChooseTextEditor,
        printer_helper: PrinterHelper,
        path_input_helper: PathInputHelper,
        sqnotes_config : SQNotesConfig
    ):

        self.encrypted_note_helper = encrypted_note_helper
        self.sqnotes_logger = sqnotes_logger
        sqnotes_logger.configure(debug=DEBUGGING)
        self.logger = sqnotes_logger.get_logger("SQNotes")
        self.user_configuration_helper = user_configuration_helper
        self.database_service = database_service
        self.choose_text_editor = choose_text_editor
        self.printer_helper = printer_helper
        self.path_input_helper = path_input_helper
        self.sqnotes_config = sqnotes_config


    def new_note(self):
        initialization_gate_toggle = self.sqnotes_config.get("IS_INITIALIZATION_GATE_REFACTORED_INSIDE_SQNOTES") == "yes"
        if initialization_gate_toggle and not self._get_is_initialized():
            print(interface_copy.SQNOTES_NOT_INITIALIZED_MESSAGE())
            exit(self.NOT_INITIALIZED)
        
        self._check_gpg_verified()
        self.GPG_KEY_EMAIL = self.get_gpg_key_email()
        self.check_gpg_key_email()
        NOTES_DIR = self.get_notes_dir_from_config()
        self.check_text_editor_is_configured()
        TEXT_EDITOR = self._get_configured_text_editor()

        try:
            self.open_database()
        except Exception:
            message = (
                interface_copy.COULD_NOT_OPEN_DATABASE()
                + " "
                + interface_copy.EXITING()
            )
            print(message)
            exit(1)

        try:
            note_content = self._get_input_from_text_editor(TEXT_EDITOR=TEXT_EDITOR)
        except TextEditorSubprocessException:
            message = interface_copy.TEXT_EDITOR_SUBPROCESS_ERROR().format(
                self._get_configured_text_editor()
            )
            self.logger.error(message)
            print(message)
            exit(1)

        self._insert_new_note(note_content=note_content, notes_dir=NOTES_DIR)

    def directly_insert_note(self, text):
        self._check_gpg_verified()
        self.GPG_KEY_EMAIL = self.get_gpg_key_email()
        self.check_gpg_key_email()
        NOTES_DIR = self.get_notes_dir_from_config()
        try:
            self.open_database()
        except Exception as e:
            message = (
                interface_copy.COULD_NOT_OPEN_DATABASE()
                + " "
                + interface_copy.EXITING()
            )
            print(message)
            exit(1)

        self._insert_new_note(note_content=text, notes_dir=NOTES_DIR)

    def search_keywords(self, keywords):
        NOTES_DIR = self.get_notes_dir_from_config()
        self.open_database()
        results = self.database_service.query_notes_by_keywords(keywords=keywords)
        if results:
            print("")  # blank line
            for result in results:
                note_path = os.path.join(NOTES_DIR, result[0])
                try:
                    decrypted_content = (
                        self.encrypted_note_helper.get_decrypted_content_in_memory(
                            note_path=note_path
                        )
                    )
                except GPGSubprocessException:
                    message = (
                        interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE()
                        + "\n"
                        + interface_copy.EXITING()
                    )
                    print(message)
                    self.logger.error(message)
                    exit(1)

                self._print_note(
                    note_path=note_path, decrypted_content=decrypted_content
                )
                print("")  # blank line

        else:
            print(f"No notes found with keywords: {keywords}")

    def edit_note(self, filename):
        initialization_gate_toggle = self.sqnotes_config.get("IS_INITIALIZATION_GATE_REFACTORED_INSIDE_SQNOTES") == "yes"
        if initialization_gate_toggle and not self._get_is_initialized():
            print(interface_copy.SQNOTES_NOT_INITIALIZED_MESSAGE())
            exit(self.NOT_INITIALIZED)

        self.GPG_KEY_EMAIL = self.get_gpg_key_email()
        self.check_gpg_key_email()
        NOTES_DIR = self.get_notes_dir_from_config()
        self.check_text_editor_is_configured
        self.TEXT_EDITOR = self._get_configured_text_editor()
        self.open_database()
        self.logger.debug(f"editing note: {NOTES_DIR} / {filename}")
        note_path = os.path.join(NOTES_DIR, filename)
        if not os.path.exists(note_path):
            message = (
                interface_copy.NOTE_NOT_FOUND_ERROR().format(note_path)
                + "\n"
                + interface_copy.EXITING()
            )
            print(message)
            self.logger.error(message)
            exit(1)

        config = {
            "GPG_KEY_EMAIL": self.GPG_KEY_EMAIL,
            "USE_ASCII_ARMOR": self._is_use_ascii_armor(),
        }

        temp_dec_filename = ""
        try:
            temp_dec_filename = self.encrypted_note_helper.decrypt_note_into_temp_file(
                note_path=note_path
            )
            edited_content = self._get_edited_note_from_text_editor(
                temp_filename=temp_dec_filename
            )

            self.logger.debug("edited note content:")
            self.logger.debug(edited_content)
            self.encrypted_note_helper.write_encrypted_note(
                note_file_path=note_path, note_content=edited_content, config=config
            )

        except GPGSubprocessException as e:
            self.logger.error(e)
            message = (
                interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE()
                + "\n"
                + interface_copy.EXITING()
            )
            print(message)
            self.logger.error(message)
            self._delete_temp_file(temp_file=temp_dec_filename)
            exit(1)
        finally:
            self._delete_temp_file(temp_file=temp_dec_filename)

        try:
            note_id = self.database_service.get_note_id_from_database_or_raise(
                filename=filename
            )
            self.database_service.delete_keywords_from_database_for_note(
                note_id=note_id
            )
            self._extract_and_save_keywords(
                note_id=note_id, note_content=edited_content
            )
            self.database_service.commit_transaction()

        except Exception:
            raise DatabaseException()

        print(f"Note edited: {filename}")

    def search_notes(self, search_queries):
        print(interface_copy.SOME_DELAY_FOR_DECRYPTION())
        is_found_any_matches = False
        notes_dir = self.get_notes_dir_from_config()

        note_paths = self._get_all_note_paths()
        queries_in_lower_case = [query.lower() for query in search_queries]
        for note_path in note_paths:
            try:
                decrypted_content = (
                    self.encrypted_note_helper.get_decrypted_content_in_memory(
                        note_path=note_path
                    )
                )
            except GPGSubprocessException as e:
                self.logger.error(e)
                message = (
                    interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE()
                    + " "
                    + interface_copy.EXITING()
                )
                self.printer_helper.print_to_so(message)
                exit(self.GPG_ERROR)

            content_in_lower_case = decrypted_content.lower()
            if all(
                lowercase_query in content_in_lower_case
                for lowercase_query in queries_in_lower_case
            ):
                print(f"\n{note_path}:\n{decrypted_content}")
                is_found_any_matches = True

        if not is_found_any_matches:
            print("no notes match search query")


    def rescan_for_database(self):
        NOTES_DIR = self.get_notes_dir_from_config()
        self.open_database()
        files = self._get_all_note_paths()
        files_info = [
            FileInfo(path=file, base_name=os.path.basename(file)) for file in files
        ]

        for file_info in files_info:
            content = self.encrypted_note_helper.get_decrypted_content_in_memory(
                note_path=file_info.path
            )
            try:
                note_id = self.database_service.get_note_id_from_database_or_none(
                    filename=file_info
                )

                if note_id is None:
                    note_id = self.database_service.insert_new_note_into_database(
                        note_filename_base=file_info.base_name
                    )

                self.database_service.delete_keywords_from_database_for_note(
                    note_id=note_id
                )
                self._extract_and_save_keywords(note_id=note_id, note_content=content)
                self.database_service.commit_transaction()

            except Exception:
                raise DatabaseException()
        print("rescan complete")

    def print_all_keywords(self):
        self.open_database()
        keywords = self.database_service.get_all_keywords()
        for kw in keywords:
            print(kw)
        if len(keywords) == 0:
            message = interface_copy.NO_KEYWORDS_IN_DATABASE()
            self.printer_helper.print_to_so(message)

    def notes_list(self):
        self.logger.debug("printing notes list")
        notes_dir = self.get_notes_dir_from_config()
        files = self._get_all_note_paths()
        filenames = [os.path.basename(file) for file in files]
        for file in filenames:
            self.logger.debug(f"note found: {file}")
            print(file)

    def check_available_text_editors(self):
        available_editors = self._get_available_text_editors()
        if len(available_editors) > 0:
            print("supported text editors installed:")
            print(available_editors)
        else:
            print("No supported text editors installed.")
            print(
                f"Supported text editors include these: {', '.join(SUPPORTED_TEXT_EDITORS)}."
            )

    def run_git_command(self, args):
        subprocess.call(["git"] + args, cwd=self.NOTES_DIR)

    def open_database(self):
        notes_dir = self.get_notes_dir_from_config()
        if notes_dir is None:
            raise NotesDirNotSelectedException()
        configured_db_path = self._get_db_path_from_user_config()
        
        self.logger.debug(f"opening database at {configured_db_path}")

        try:
            self.database_service.connect(
                db_file_path=configured_db_path
            )
        except Exception as e:
            self.logger.error(e)
            raise CouldNotOpenDatabaseException()

        is_database_set_up = self._get_is_database_set_up()
        if not is_database_set_up:
            self.logger.debug("found database not set up")
            self.setup_database()

    def _get_input_from_text_editor(self, TEXT_EDITOR):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
        try:
            response = subprocess.call([TEXT_EDITOR, temp_filename])
            if response != 0:
                raise TextEditorSubprocessException()
        except Exception as e:
            self.logger.error(
                "an exception occurred while attempting the text editor subprocess"
            )
            self.logger.error(e)
            raise TextEditorSubprocessException()
        try:
            with open(temp_filename, "r") as file:
                note_content = file.read().strip()
        finally:
            self._delete_temp_file(temp_file=temp_filename)
        return note_content

    def _get_new_note_name(self):
        is_use_armor = self._is_use_ascii_armor()
        extension = "txt" if is_use_armor else "txt.gpg"
        datetime_string = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{datetime_string}.{extension}"

    def _insert_new_note(self, note_content, notes_dir):

        base_filename = self._get_new_note_name()
        note_file_path = os.path.join(notes_dir, base_filename)
        try:
            enh_config = {
                "GPG_KEY_EMAIL": self.GPG_KEY_EMAIL,
                "USE_ASCII_ARMOR": self._is_use_ascii_armor(),
            }

            self.encrypted_note_helper.write_encrypted_note(
                note_file_path=note_file_path,
                note_content=note_content,
                config=enh_config,
            )

        except GPGSubprocessException as e:
            self.logger.error(e)
            message = (
                interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE()
                + " "
                + interface_copy.EXITING()
            )
            self.logger.error(message)
            self.printer_helper.print_to_so(message)
            exit(self.GPG_ERROR)

        
        note_added_message = interface_copy.NOTE_ADDED().format(base_filename)
        print(note_added_message)

        try:
            note_id = self.database_service.insert_new_note_into_database(
                note_filename_base=base_filename
            )

            self._extract_and_save_keywords(note_id=note_id, note_content=note_content)

            self.database_service.commit_transaction()
            return note_id
        except Exception as e:
            is_database_exception = self._check_for_database_exception(e)
            if is_database_exception:
                message = (
                    interface_copy.DATABASE_EXCEPTION_MESSAGE()
                    + "\n"
                    + interface_copy.DATA_NOT_SAVED()
                )
                self.logger.error(message)
                self.logger.error(e)
                print(message)
                exit(1)
            else:
                message = (
                    interface_copy.UNKNOWN_ERROR()
                    + "\n"
                    + interface_copy.DATA_NOT_SAVED()
                )
                self.logger.error(message)
                self.logger.error(e)
                print(
                    interface_copy.UNKNOWN_ERROR()
                    + "\n"
                    + interface_copy.DATA_NOT_SAVED()
                )
                exit(1)

    def _extract_and_save_keywords(self, note_id, note_content):
        keywords = self._extract_keywords(note_content)
        keyword_ids = []
        for keyword in keywords:
            keyword_id = self.database_service.insert_keyword_into_database(
                keyword=keyword
            )
            keyword_ids.append(keyword_id)

        for keyword_id in keyword_ids:
            self.database_service.insert_note_keyword_into_database(note_id, keyword_id)

    def _get_is_initialized(self):
        value = self.user_configuration_helper.get_global_from_user_config(INITIALIZED)
        self.logger.debug(f"checking initialized: {value}")
        return self.user_configuration_helper.get_global_from_user_config(INITIALIZED) == "yes"

    

    def _delete_temp_file(self, temp_file):
        if os.path.exists(temp_file):
            os.remove(temp_file)

    def _get_edited_note_from_text_editor(self, temp_filename):
        TEXT_EDITOR = self._get_configured_text_editor()
        edit_process = subprocess.run([TEXT_EDITOR, temp_filename], check=True)

        # Ensure Vim exited properly before proceeding
        if edit_process.returncode != 0:
            raise Exception("Editing failed")
        with open(temp_filename, "r") as file:
            edited_content = file.read().strip()
        return edited_content

    def _get_available_text_editors(self):
        available_editors = []
        for editor in SUPPORTED_TEXT_EDITORS:
            validator_function = CommandValidator.get_validator_by_command(
                command_string=editor
            )
            if validator_function is None:
                continue
            editor_is_supported = validator_function()
            if editor_is_supported:
                available_editors.append(editor)
        return available_editors
    
    def _check_for_database_exception(self, e):
        return (
            isinstance(e, sqlite3.IntegrityError)
            or isinstance(e, sqlite3.OperationalError)
            or isinstance(e, sqlite3.ProgrammingError)
            or isinstance(e, sqlite3.DataError)
            or isinstance(e, sqlite3.InternalError)
            or isinstance(e, sqlite3.InterfaceError)
            or isinstance(e, sqlite3.DatabaseError)
            or isinstance(e, sqlite3.NotSupportedError)
        )

    def _extract_keywords(self, content):
        tags = [match[1:] for match in re.findall(r"\B#\w+\b", content)]
        unique_tags = set(tags)
        return unique_tags

    def _get_db_path_from_user_config(self):
        return self.user_configuration_helper.get_setting_from_user_config(key = self.DB_FILE_PATH_KEY)

    def _set_user_db_path(self, user_specified_directory = None):
        db_file_name = self.sqnotes_config.get(key = self.DATABASE_FILE_NAME_KEY)
        if user_specified_directory is not None:
            full_file_path = os.path.join(user_specified_directory, db_file_name)
        else:
            default_db_path = self._get_default_db_file_path()
            full_file_path = os.path.join(default_db_path, db_file_name)
        self.user_configuration_helper.set_setting_to_user_config(key=self.DB_FILE_PATH_KEY, value = full_file_path)

    
    def _get_default_db_file_path(self):
        DATABASE_PATH = self.sqnotes_config.get(key = 'DATABASE_PATH')
        database_path = DATABASE_PATH.replace('[notes_dir]', self.get_notes_dir_from_config())
        expanded_path = os.path.expanduser(database_path)
        return expanded_path
        

    def get_notes_dir_from_config(self):
        self.logger.debug(f"about to call to get notes dir from config")
        notes_dir_path = self.user_configuration_helper.get_setting_from_user_config(
            key=NOTES_PATH_KEY
        )
        self.logger.debug(f"found {notes_dir_path}")
        if notes_dir_path is None:
            raise NotesDirNotConfiguredException()
        else:
            return notes_dir_path

    def _get_configured_text_editor(self):
        text_editor = self.user_configuration_helper.get_setting_from_user_config("text_editor")

        if text_editor is None:
            raise TextEditorNotConfiguredException()
        return text_editor

    def _is_text_editor_configured(self):
        text_editor = self.user_configuration_helper.get_setting_from_user_config("text_editor")
        return text_editor is not None and text_editor != ""

    def _get_all_note_paths(self):
        notes_dir = self.get_notes_dir_from_config()
        print(f"looking for notes in {notes_dir}")
        extensions = ["txt.gpg", "txt"]
        all_notes = []
        for ex in extensions:
            pattern = os.path.join(notes_dir, f"*.{ex}")
            files = glob.glob(pattern)
            all_notes.extend(files)
        return all_notes

    def _get_user_config_dir(self):
        configured_path =  self.sqnotes_config.get(key = self.USER_CONFIG_DIR_KEY)
        expanded_path = os.path.expanduser(configured_path)
        return expanded_path

    def _get_default_notes_dir(self):
        return self.sqnotes_config.get(key = self.DEFAULT_NOTES_DIR_KEY)

    def prompt_for_user_notes_path(self):
        user_input_notes_path = None
        attempt_num = 0
        max_attempts = 2
        default_notes_dir = self._get_default_notes_dir()
        while user_input_notes_path is None:
            prompt = "Please enter a path for saving your notes \nin the format '[full_path_to_parent]/[note_directory]'. \nPress enter to use default '{}'.".format(
                default_notes_dir
            )
            user_input_notes_path = input(prompt + ">")

            if user_input_notes_path == "":
                selected_path = default_notes_dir
                return selected_path
            else:
                selected_path = user_input_notes_path
                success = self._try_to_make_path(selected_path)

                if success is False:
                    if attempt_num < max_attempts:
                        attempt_num += 1
                        print("Please try again.")
                        user_input_notes_path = None
                    else:
                        print(
                            "Failed multiple times; you can try running this command again."
                        )
                        exit(1)
                else:
                    return selected_path

    def prompt_to_initialize(self):
        print("sqnotes not initialized; please run initialization")

    def _print_note(self, note_path, decrypted_content):
        print(f"{note_path}:\n{decrypted_content}")


    def _try_to_make_path(self, selected_path):
        if os.path.exists(selected_path):
            return True
        else:
            directory = os.path.dirname(selected_path)
            user_expanded_directory = os.path.expanduser(directory)

            directory_exists = os.path.exists(user_expanded_directory)
            if directory_exists:
                try:
                    os.mkdir(selected_path)
                    return True
                except FileExistsError:
                    # logically this shouldn't happen
                    print(f"directory '{selected_path}' already exists")
                    return False
                except Exception as e:
                    self.logger.error(e)
                    print("encountered an error attempting to make this directory")
                    return False
            else:
                print(f"parent directory {directory} does not exist")
                return False

    def _check_gpg_verified(self):
        is_gpg_verified = self._get_gpg_verified()
        if not is_gpg_verified:
            is_gpg_available = CommandValidator.verify_command(command_string=GPG)
            if is_gpg_available:
                self._set_gpg_verified()
            else:
                raise CouldNotRunGPG()

    def _set_gpg_verified(self):
        self.user_configuration_helper.set_setting_to_user_config(key=GPG_VERIFIED_KEY, value="yes")

    def _get_gpg_verified(self):
        return (
            self.user_configuration_helper.get_setting_from_user_config(key=GPG_VERIFIED_KEY)
            == "yes"
        )

    def initialize(self):
        selected_path = self.prompt_for_user_notes_path()

        self.user_configuration_helper.set_setting_to_user_config(
            key=NOTES_PATH_KEY, value=selected_path
        )
        self.user_configuration_helper.set_setting_to_user_config(
            key=ASCII_ARMOR_CONFIG_KEY, value="yes"
        )

        gpg_verified = CommandValidator.verify_command(command_string=GPG)
        if not gpg_verified:
            print(interface_copy.NEED_TO_INSTALL_GPG)
        else:
            self._set_gpg_verified()

        self.choose_text_editor_interactive()

        self.printer_helper.print_to_so(interface_copy.INITIALIZATION_COMPLETE())
        self.user_configuration_helper.set_global_to_user_config(key=INITIALIZED, value="yes")

    def _get_is_database_set_up(self):
        is_set_up = (
            self.user_configuration_helper.get_global_from_user_config(self.DATABASE_IS_SET_UP_KEY)
            == "yes"
        )
        return is_set_up

    def _set_database_is_set_up(self):
        self.user_configuration_helper.set_global_to_user_config(key=self.DATABASE_IS_SET_UP_KEY, value="yes")

    def setup_database(self):
        print(interface_copy.SETTING_UP_DATABASE_MESSAGE())
        self.logger.debug("setting up the database tables")
        self.database_service.setup_database()
        self._set_database_is_set_up()

    def set_notes_path_interactive(self):
        self.printer_helper.print_to_so(interface_copy.SETTING_THE_NOTES_PATH())
        self.path_input_helper.get_path_interactive()

    def _is_use_ascii_armor(self):
        return (
            self.user_configuration_helper.get_setting_from_user_config(key=ASCII_ARMOR_CONFIG_KEY)
            == "yes"
        )

    def _set_use_ascii_armor(self, isUseArmor):
        value = "yes" if isUseArmor else "no"
        self.user_configuration_helper.set_setting_to_user_config(
            key=ASCII_ARMOR_CONFIG_KEY, value=value
        )
        self.logger.debug(f"set {ASCII_ARMOR_CONFIG_KEY}=yes")

    def check_gpg_key_email(self):
        self.GPG_KEY_EMAIL = self.get_gpg_key_email()
        if self.GPG_KEY_EMAIL is None:
            print(interface_copy.GPG_KEY_NOT_SET_MESSAGE())
            exit(1)

    def get_gpg_key_email(self):
        return self.user_configuration_helper.get_setting_from_user_config(key=GPG_KEY_EMAIL_KEY)

    def set_gpg_key_email(self, new_gpg_key_email):
        self.GPG_KEY_EMAIL = new_gpg_key_email
        self.user_configuration_helper.set_setting_to_user_config(
            key=GPG_KEY_EMAIL_KEY, value=new_gpg_key_email
        )
        print(f"GPG Key set to: {self.GPG_KEY_EMAIL}")

    def check_gpg_installed(self):
        is_can_run_gpg_version = CommandValidator.verify_command(command_string=GPG)
        message = (
            interface_copy.GPG_VERIFIED()
            if is_can_run_gpg_version
            else interface_copy.GPG_NOT_RUN()
        )
        print(message)

    def startup(self):
        self._setup_user_configuration()

    def _setup_user_configuration(self):
        user_config_dir = self._get_user_config_dir()
        self.user_configuration_helper._set_config_dir(config_dir=user_config_dir)
        
        init_globals = self._get_initial_globals_from_config()
        init_user_settings = self._get_initial_user_settings_from_config()
        
        self.user_configuration_helper.open_or_create_and_open_user_config_file(
            initial_globals=init_globals,
            initial_settings=init_user_settings
        )
        
    def _get_initial_globals_from_config(self):
        return self.sqnotes_config.get(key = self.INIT_GLOBALS_KEY)
    
    def _get_initial_user_settings_from_config(self):
        return self.sqnotes_config.get(key = self.INIT_USER_SETTINGS_KEY)

    def _set_configured_text_editor(self, editor):
        if editor in self._get_supported_text_editors():
            self.user_configuration_helper.set_setting_to_user_config(
                key=TEXT_EDITOR_KEY, value=editor
            )

    def _get_input_until_condition_satisfied(self, prompt, condition):
        response = None
        while response == None:
            user_input = input(prompt)
            if condition(user_input):
                return user_input
            else:
                continue

    def _get_supported_text_editors(self):
        return SUPPORTED_TEXT_EDITORS

    def choose_text_editor_interactive(self):
        available_editors = self._get_available_text_editors()

        self.choose_text_editor.set_available_editors(
            available_editors=available_editors
        )
        self.choose_text_editor.set_supported_editors(
            supported_editors=self._get_supported_text_editors()
        )

        try:
            selected_editor = self.choose_text_editor.choose_text_editor_interactive()
            self._set_configured_text_editor(editor=selected_editor)
            confirm_message = interface_copy.TEXT_EDITOR_WAS_CONFIGURED().format(
                selected_editor
            )
            self.printer_helper.print_to_so(confirm_message)
        except MaxInputAttemptsException:
            message = interface_copy.DID_NOT_SET_TEXT_EDITOR_TRY_AGAIN()
            print(message)

    def check_text_editor_is_configured(self):
        # Check if a text editor is configured, prompt to select one if not
        is_configured = self._is_text_editor_configured()
        if not is_configured:
            TEXT_EDITOR = input(
                "No text editor configured. Please enter the path to your preferred terminal text editor (e.g. 'vim', 'nano')> "
            )
            self.user_configuration_helper.set_setting_to_user_config("text_editor", TEXT_EDITOR)


def __get_sqnotes():
    injector = Injector([InjectionConfigurationModule()])

    sqnotes = injector.get(SQNotes)
    return sqnotes


def main():
    parser = argparse.ArgumentParser(
        description="SQNote: Secure note-taking command-line utility.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debugging mode with detailed log messages",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-k", "--keywords", nargs="+", help="Keywords for keyword search"
    )
    group.add_argument(
        "-s", "--search", nargs="+", help="Search term for full text search."
    )
    group.add_argument("-n", "--new", help="Text for new note.", type=str)

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    subparsers.add_parser("new", help="Add a new note.")
    subparsers.add_parser("init", help="Initialize app.")

    subparsers.add_parser(
        "text-editors", help="Show supported text editors available on your system."
    )

    SET_NOTES_PATH_COMMAND = "set-notes-path"
    if SET_NOTES_PATH_INTERACTIVE_FLAG:
        subparsers.add_parser(
            "set-notes-path", help="Set the directory path for storing your note files."
        )

    if SET_TEXT_EDITOR_INTERACTIVE_FLAG:
        subparsers.add_parser(
            "config-text-editor", help="Choose your text editor (interactive)."
        )

    man_command = subparsers.add_parser("man", help="Show manual.")
    manual_subcommands = man_command.add_subparsers(
        dest="man_subcommand", help="Manual subcommands."
    )
    manual_subcommands.add_parser("encryption", help="Show manual page for encryption.")
    manual_subcommands.add_parser("main", help="Show main manual page.")

    search_subparser = subparsers.add_parser(
        "search",
        help="Find notes by full text search. (Slow because requires full decryption.)",
    )
    search_subparser.add_argument("-t", "--text", nargs="+", help="Search strings.")

    set_gpg_key_subparser = subparsers.add_parser(
        "set-gpg-key", help="Set the GPG key."
    )
    set_gpg_key_subparser.add_argument(
        "-i", "--id", help="GPG key email/identifier.", type=str
    )

    use_armor_subparser = subparsers.add_parser(
        "use-ascii-armor", help="Configure use of ASCII armor for encryption"
    )
    group = use_armor_subparser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-y", "--yes", action="store_true", help="Set to use ASCII armor for encryption"
    )
    group.add_argument(
        "-n",
        "--no",
        action="store_true",
        help="Set not to use ASCII armor for encryption",
    )

    keyword_search_subparser = subparsers.add_parser(
        "keywords",
        help="Find notes keyword. (Fast because searches plaintext database.)",
    )
    keyword_search_subparser.add_argument(
        "-k", "--keywords", nargs="+", help="Keywords to search for.", required=True
    )

    subparsers.add_parser(
        "rescan",
        help="Rescan notes to populate database (useful for troubleshooting certain errors)",
    )
    subparsers.add_parser(
        "notes-list", help="Show a list of all notes (scans notes directory)"
    )
    subparsers.add_parser("print-keywords", help="Print all keywords from database.")

    subparsers.add_parser(
        "verify-gpg", help="Verify that SQNotes can run GPG for encryption/decryption"
    )

    git_parser = subparsers.add_parser("git", help="Passthrough git commands.")
    git_parser.add_argument(
        "git_args", nargs=argparse.REMAINDER, help="Arguments for git command"
    )

    edit_parser = subparsers.add_parser("edit", help="Edit a note.")
    edit_parser.add_argument("-n", "--note", help="Note base filename.", type=str)

    args = parser.parse_args()

    sqnotes = __get_sqnotes()
    sqnotes.startup()

    if args.command == "init":
        sqnotes.initialize()
    elif args.command == "man":
        manual = Manual()
        if args.man_subcommand == "encryption":
            manual.print_encryption_page()
        else:
            manual.print_main_page()
    else:
        if not IS_INITIALIZATION_GATE_REFACTORED_INSIDE_SQNOTES:
            is_initialized = sqnotes._get_is_initialized()
            if not is_initialized:
                print(interface_copy.SQNOTES_NOT_INITIALIZED_MESSAGE())
                exit(0)
            
        if args.command == "new":
            sqnotes.new_note()
        elif args.new:
            sqnotes.directly_insert_note(text=args.new)
        elif args.search:
            sqnotes.search_notes(search_queries=args.search)
        elif args.keywords:
            sqnotes.search_keywords(keywords=args.keywords)
        elif args.command == "notes-list":
            sqnotes.notes_list()
        elif args.command == "verify-gpg":
            sqnotes.check_gpg_installed()

        elif (
            SET_TEXT_EDITOR_INTERACTIVE_FLAG
            and args.command == "config-text-editor"
        ):
            sqnotes.choose_text_editor_interactive()
        elif (
            SET_NOTES_PATH_INTERACTIVE_FLAG
            and args.command == SET_NOTES_PATH_COMMAND
        ):
            sqnotes.set_notes_path_interactive()
        elif args.command == "text-editors":
            sqnotes.check_available_text_editors()
        elif args.command == "set-gpg-key":
            sqnotes.set_gpg_key_email(args.id)
        elif args.command == "use-ascii-armor":
            if args.yes:
                sqnotes._set_use_ascii_armor(isUseArmor=True)
            elif args.no:
                sqnotes._set_use_ascii_armor(isUseArmor=False)
        elif args.command == "search":
            sqnotes.search_notes(args.text)
        elif args.command == "keywords":
            sqnotes.search_keywords(args.keywords)
        elif args.command == "edit":
            sqnotes.edit_note(args.note)
        elif args.command == "git":
            sqnotes.run_git_command(args.git_args)
        elif args.command == "print-keywords":
            sqnotes.print_all_keywords()
        elif args.command == "rescan":
            sqnotes.rescan_for_database()

        else:
            parser.print_help()


if __name__ == "__main__":
    main()
