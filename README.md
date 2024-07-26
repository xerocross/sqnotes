# SQNotes (A Secure Note-Taking Terminal Utility)

The idea here was to have a highly portable way to take
down any sort of text data and make it available at
your fingertips at the terminal. Thus what I call "quick
notes" was born. Add to that a desire to encrypt the data
before saving it and you get "secure quick notes": sqnotes.

Sqnotes uses gpg to encrypt and decrypt using your gpg key
pair.

Right now, **this script is only designed to work on Linux** 
as yours truly uses Ubuntu. But it is a Python script, and 
all the component parts have variants available on Windows.
Making this script work on Windows is a future goal.



## Installation

### Prerequisites

This script is aimed at Linux, but with some minor adjustments it can
probably be made to work on Windows too. Be sure to look at the dependencies,
including especially python3, vim and gpg.

Before running the script, ensure you have Python 3.x installed on your system.

### Dependencies

This script requires the following dependencies:

- `gpg` (GNU Privacy Guard) for encryption
- `vim` for text editing (optional, can be replaced with another editor)
- Other Python modules as listed in `requirements.txt`

### Installation Steps

1. **Install Python 3.x**: If not already installed, download and install Python 3.x from [python.org](https://www.python.org).

2. **Install `gpg` and `vim`**:
- On Debian-based systems (Ubuntu):
     ```bash
     sudo apt-get update
     sudo apt-get install gnupg vim
     ```
- On macOS using Homebrew:
     ```bash
     brew install gnupg vim
     ```

3. **Make executable**:

	- Make the script executable. (For example, on Linux use the command
	`chmox +x sqnotes.py`.)
	
	- Place this script somewhere in your PATH. On Linux, you might put
	it in `/usr/local/bin`.
	
	- Optionally, you can program a bash alias to be able to conveniently
	access this script without needing to explicitly call python or type
	the `.py` ending. On Linux, also if you want to drop the `.py` ending
	you can simply rename the file (not sure if Windows can handle that).

4. **Set up a gpg key pair**:
	For encryption, you will have to configure this script to use an
	existing gpg key pair. It will ask for the email address of your
	key. It will not help you set that up. Check any reference for
	your system on how to set up the key pair.
	
5. **(Optional) Install git**:
	Consult any reference on how to install git on your 
	device. Git is useful for keeping track of your notes
	across several devices or among various users.
	

## Usage

Run SQNotes with the `-h` command to see the help page. Note that manual
pages are included in the app.





