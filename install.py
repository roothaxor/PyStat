import os, sys, shutil
from sys import platform as _platform
from termcolor import colored
if _platform == 'win32':
    import colorama
    colorama.init()

def yellow(text):
    return colored(text, 'yellow', attrs=['bold'])

def green(text):
    return colored(text, 'green', attrs=['bold'])

def red(text):
    return colored(text, 'red', attrs=['bold'])

def cyan(text):
    return colored(text, 'cyan', attrs=['bold'])

loc = os.getcwd()
file = loc+'\pystat.bat'
contfile = loc+'\pystat_core.py'
cont = '''@echo off
python %s
pause'''%(contfile)
out = open(file, 'w')
out.write(cont)
out.close()
os.system('cls')
print green("\n\n\n[!] Script Generated pystat.bat file")
dest = os.environ['WINDIR']
full_file_name = file
try:
	shutil.copy(full_file_name, dest)
except IOError:
	print red("\nError:")+cyan(" Permission denied While moving pystat.bat to C:\Windows")
	print green("\n[!] Please copy pystat.bat file to C:\Windows")
	print green("\n[+] For test open CMD and enter pystat\n\n\n")