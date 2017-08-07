#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os, re, time, sys
from subprocess import check_output
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


infrm = '''
===============================================================================================================================================================
Port      RemoteIP            PID       Executable Name                    User                              Title
==============================================================================================================================================================='''
	

def id_netstat_processes():
 
    # First Run netstat to get network connections
    # Options
    # a Displays all active TCP connections and the TCP and UDP ports on which the computer is listening.
    # o Displays active TCP connections and includes the process ID (PID) for each
    #   connection. You can find the application based on the PID on the Processes
    #   tab inWindows Task Manager. This parameter can be combined with -a, -n, and -p.
    # n Displays active TCP connections, however, addresses and port numbers are
    #   expressed numerically and no attempt is made to determine names.
    result = check_output("netstat -aon", shell=True)
 
    # Now make an array of terms to remove from the data obtained from netstat 
    clean_up_array = [
        ("Active Connections", ""),
        ("Proto", ""),
        ("Local Address", ""),
        ("Foreign Address", ""),
        ("State", ""),
        ("PID", ""),
        ("\r", ""),
        ("\t", " ")
    ]
 
    # Remove terms from the netstat data
    for find, replace in clean_up_array:
        result = result.replace(find, replace)
 
    # * Because I am feeling feisty, I will utilize an evil regular expression to extract the
    #   netstat information via regex groups via the () command
    #   
    # * Likewise Because terminal output is space padded rather than tabbed we need to account
    #   for variable spacing via the regex (space)* or ' *' expression
    #   
    # * Becuase the 1st group is either UDP or TCP use (UDP|TCP) to find either or
    #   
    # * Because the 2ed group is either a IPV4 xxx.xxx.xxx.xxx or IPV6 XXXX::XXXX::XXXX::XXXX::XXXX%xx address or [::]
    #   Use [0-9]*\\.[0-9]*\\.[0-9]*\\.[0-9]* for any or none number length with dots or
    #   [ *[a-z0-9]*:* *[a-z0-9]*:* *[a-z0-9]*:* *[a-z0-9]*:* *[a-z0-9%]*\\] for any or none letters or numbers of : until the port :
    #   
    # * Because the 3ed group is the port use any number [0-9]*
    # 
    # * Because the 4th group is remote ip (i only had ipv4) or *:* use [0-9]*\\.[0-9]*\\.[0-9]*\\.[0-9]*|\\[:*\\] or \\*
    # 
    # * Because the 5th group is the remote ip use any number [0-9]* 
    # 
    # * Because the 6th group is the status use LISTENING|ESTABLISHED|TIME_WAIT|CLOSE_WAIT with any or none group find
    # 
    # * Becuase the 7th group is pid use any number [0-9]* 
    # a ugly regex string that extracts the required information into groups... does not support IPV6 remote address atm but supports local IPV6
    reexstring = " *(UDP|TCP) *([0-9]*\\.[0-9]*\\.[0-9]*\\.[0-9]*|\\[ *[a-z0-9]*:* *[a-z0-9]*:* *[a-z0-9]*:* *[a-z0-9]*:* *[a-z0-9%]*\\]):([0-9]*) *([0-9]*\\.[0-9]*\\.[0-9]*\\.[0-9]*|\\[:*\\]|\\*):(\\*|[0-9]*) *(LISTENING|ESTABLISHED|TIME_WAIT|CLOSE_WAIT)* *([0-9]*)"
 
    # Build the regex string
    regexcompiled = re.compile(reexstring)
 
    # Process the input
    items = regexcompiled.finditer(result)
 
    networkitems = []
 
    # Loop thru the results
    for match in items:
        # we could just do data.append((match.groups())) but do this for user Configurability
        # Extract and trim the data obtained
        networktype = match.group(1).strip()
        localip = match.group(2).strip()
        localport = match.group(3).strip()
        remoteip = match.group(4).strip()
        remoteport = match.group(5).strip()
 
        # Because status can be None we need to check for None
        if not match.group(6) is None:
            status = match.group(6).strip()
        else:
            status = ""
        pid = match.group(7).strip()
 
        # Append items to an array for future processing
        networkitems.append(( localip, localport, remoteip, remoteport, status, pid))
 
    # At this point we are ready to get a list of all PID running
    tasklist = check_output("tasklist /v", shell=True)
 
    # Again our console result needs to be cleaned up prior to processing 
    clean_up_array = [
        ("Image Name", "" ),
        ("PID", "" ),
        ("Session Name", "" ),
        ("Session#", "" ),
        ("Mem Usage", "" ),
        ("Status", "" ),
        ("User Name", "" ),
        ("CPU Time", "" ),
        ("Window Title", "" ),
        ("=",""),
        ("\r", ""),
        ("\t", " ")
    ]
 
    # Remove terms from the tasklist data
    for find, replace in clean_up_array:
        tasklist = tasklist.replace(find, replace)
 
 
    # Because application names can have spaces in them , our regex becomes a touch more complex and requires look aheads via ?
    # Likewise, because the terminal is heavily space padded we can safely assuming two spaces will end each segment
    # thus, '  *' (or space space *) and '   *' (space space space *) are used in the look ahead as group stoppers
    # Beyond this, wildcard (.*) for any characters are used for group extraction
    regexstring2 = "^(.*?)   *([0-9]*) *(.*?)  *([0-9]*) *([0-9,]* .) *(.*?)  *(.*?)   *([0-9:]*) *(.*?)  "
 
    # To make life easier, a dictionary will be utilized to lookup the pid
    tasks = {}
 
    # Build the regex string And allow for multiline processing
    regexcompiled2 = re.compile(regexstring2, re.MULTILINE)
 
    # Process the input
    items = regexcompiled2.finditer(tasklist)
 
    # Loop thru the results
    for match in items:
        # Extract and trim the data obtained
        imagename = match.group(1).strip()
        pid = match.group(2).strip()
 
        # Sometimes this approach yields an empty string at the start check for this and continue if found
        if pid == '':
            continue
 
        sessionname = match.group(3).strip()
        sessionnumber = match.group(4).strip()
        memory = match.group(5).strip()
        status = match.group(6).strip()
        user = match.group(7).strip()
        cputime = match.group(8).strip()
        title = match.group(9).strip()
 
        # Populate our dictionary with information
        tasks[pid] = (imagename,sessionname,sessionnumber,memory,status,user,cputime,title)
 
    # Create a variable to hold our output
    output = ""
    # Loop thru all netstat items
    for item in networkitems:
        # Extract our array object
        localip, localport, remoteip, remoteport, status, pid = item
 
        # See if the PID exists within our PID array
        if pid in tasks.keys():
            # If so extract the PID information and add it to the output
            imagename,sessionname,sessionnumber,memory,status,user,cputime,title = tasks[pid]
            output += localport.ljust(10) + remoteip.ljust(20) + pid.ljust(10) + imagename.ljust(35)  + user.ljust(35) + title + "\n"
        else:
            # If not report the error in the output, if this happens then the application is likely something hidden deep in
            # administrative privileges and googling will be required to attempt to access it. This is the domain of viruses!
            output += localport.ljust(10) + remoteip.ljust(20) + "PID "+ pid +" Missing" + "\n"
 
# Print output, resize Dos screen size
	os.system('mode 160')
	os.system('title Python netstat v.0.0.7')
	print green(infrm)
	print cyan(output)
# This is our application entry point
if __name__ == "__main__":
    # Run our extraction function
    id_netstat_processes()