
import os
import sys
import subprocess
import argparse

project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
print(f"appending {src_path} to path")

if project_root not in sys.path:
    sys.path.append(project_root)

if src_path not in sys.path:
    sys.path.append(src_path)
    


def main():
    parser = argparse.ArgumentParser(
        description='SQNotes test-runner utility.',
        )
    
    subparsers = parser.add_subparsers(dest='command', help='Subcommands.')
    
    subparsers.add_parser('sqnotes-module', help='Run sqnotes module tests.')
    
    subparsers.add_parser('open-database', help='Run tests for opening the database.')
    subparsers.add_parser('init', help='Run tests for SQNotes initialization.')
    subparsers.add_parser('choose-text-editor', help='Run tests for choosing the text editor.')
    subparsers.add_parser('path-input', help='Run tests for PathInputUser')
    
    parser.add_argument('--spec', 
                    action='store_true', 
                    help='Enable spec printout.')

    
    args = parser.parse_args()
    subdirectory = None
    if args.command == 'sqnotes-module':
        
        subdirectory = ['test/test_sqnotes']
    elif args.command == 'open-database':
        subdirectory = ['test/test_sqnotes/test_open_and_setup_database.py']
    elif args.command == 'choose-text-editor':
        subdirectory = ['test/test_sqnotes/test_choose_text_editor_interactive.py']
    elif args.command == 'init':
        subdirectory = ['test/test_sqnotes/test_initialization.py']
    elif args.command == 'path-input':
        subdirectory = ['test/test_path_input_helper.py', 
                        'test/test_sqnotes/test_set_notes_path_interactive.py']
        
    
    test_run_command = [sys.executable, '-m', 'pytest']
    if subdirectory is not None:
        for s in subdirectory:
            test_run_command.append(s)
    
    if args.spec:
        test_run_command.insert(3, '--spec')
    
    
    result = subprocess.run(test_run_command, cwd=project_root)

    # Exit with the same status code as the test runner
    sys.exit(result.returncode)
        
            

if __name__ == '__main__':
    main()