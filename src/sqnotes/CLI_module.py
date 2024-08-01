
import argparse
from injector import Injector
from sqnotes.sqnotes_module import SQNotes, SET_NOTES_PATH_INTERACTIVE_FLAG,\
    SET_TEXT_EDITOR_INTERACTIVE_FLAG
from sqnotes.manual import Manual
from sqnotes.injection_configuration_module import InjectionConfigurationModule

class SQNotesCLI:
    
    def __get_sqnotes(self):
        injector = Injector([InjectionConfigurationModule()])
    
        sqnotes = injector.get(SQNotes)
        return sqnotes

    def main(self):
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
    
        sqnotes = self.__get_sqnotes()
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
            initialized = sqnotes._get_is_initialized()
            if not initialized:
                print(interface_copy.SQNOTES_NOT_INITIALIZED_MESSAGE)
                return
            else:
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