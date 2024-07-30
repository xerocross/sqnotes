
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
    
    parser.add_argument('--spec', 
                    action='store_true', 
                    help='Enable spec printout.')

    
    args = parser.parse_args()
    subdirectory = None
    if args.command == 'sqnotes-module':
        
        subdirectory = 'test/test_sqnotes'
        
    
    test_run_command = [sys.executable, '-m', 'pytest']
    if subdirectory is not None:
        test_run_command.append(subdirectory)
    
    if args.spec:
        test_run_command.insert(3, '--spec')
    
    
    result = subprocess.run(test_run_command, cwd=project_root)

    # Exit with the same status code as the test runner
    sys.exit(result.returncode)
        
            

if __name__ == '__main__':
    main()