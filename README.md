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
	

### Usage

Run `sqnotes -h` to see the help menu.

To create a new note, run `sqnotes -n`. This will launch the configured text editor. I use Vim. You can use, for example, nano if you prefer (I think; hasn't been tested yet). Use a terminal editor. I don't know what will happen if you try configuring a GUI-based editor. No promises there.

In your notes, add hashtags to index them. A hashtag starts with a hashtag symbol (#), has one or more word characters (no special characters, symbols, or spaces), and is terminated by any non-word character like a space or a period.

Do not put anything private or confidential inside a hashtag in a note. The purpose of the hashtags is to be indexable and, thus, quickly searchable. They are stored in a database as plaintext. Apart from the hashtags, the content is encrypted and stored in encrypted format.

The index is stored as an SQLite database that, by default, is stored in the same directory as your note files. There is a reason for that. You are encouraged to keep all semantic data in the same place. This allows you to, for example, easily back everything up or check everything into a git repo, which is supported by using the git passthrough command `--git``.

To search your notes, you can use the -f command as in `sqnotes -f 'apple'`, which will decrypt all your notes on-the-fly, search for your query in all of them, and display the content of all the notes that contain your search query. This of course can be **very slow**, and it will depend on how many notes you have.

A quicker alternative to full text search is to search the keywords. To do a keyword search, use the command -k like so `sqnotes -k '#apple'`.

Both the `-f` and `-k` commands are designed to accept multiple argument strings. If you enter two search terms, the script will find notes containing **both** of them, not just either one.






