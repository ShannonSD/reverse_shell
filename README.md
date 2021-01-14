# reverse_shell
This is a reverse shell program written entirely in python 3.
The program requires the following modules:

For the server program:
socket,
sys,
os,
time,
smtplib,
threading,
PIL,
email.message

For the client program:
subprocess,
sys,
os,
time,
pyscreenshot,
keyboard

As the program is a reverse shell, it cannot depend on a user downloading the required modules with a setup.py script.
The program is self-contained by importing or installing required modules from within the program.

The reverse shell is able to:
1) run system commands
2) download files from the remote machine
3) upload files to the remote machine
4) capture screenshots
5) capture keystrokes and email them
6) convert itself into an executable to evade detection

*to use the keylogger feature, the script must run with sudo privileges as the keyboard module does not work without it.

This program was built for educational purposes. Do not use it to access systems that you are not authorized to use.
