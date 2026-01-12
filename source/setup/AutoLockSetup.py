from Cryptodome.Protocol.KDF import scrypt
from pywintypes import error as pywterror
from subprocess import run as subRun
from Cryptodome.Hash import SHA256
from shutil import copyfile
from getpass import getuser
from time import sleep
import winreg as wrg
from sys import exit
from sys import argv
import win32file
import pyuac
import os

COMP_NAME_HASH:bytes = SHA256.new(os.environ['COMPUTERNAME'].encode()).digest()
DRIVES:list = []

def getRemovableDrives() -> list:
    list1:list = []
    for d in range(0,26):
        mask=1 << d
        if win32file.GetLogicalDrives() & mask:
            # here if the drive is at least there
            drname='%c:\\' % chr(ord('A')+d)
            t=win32file.GetDriveType(drname)
            if t == win32file.DRIVE_REMOVABLE:
                list1.append(drname.replace('\\',''))
    return(list1)

def shared(masterpass:str='')->None:
    DRIVES = getRemovableDrives()
    #select drive
    selectDrive = input(f'which drive should be used as the security key?\navailible drives are {DRIVES}, \'cancel\' to cancel: ').upper()
    if (selectDrive == 'CANCEL'):
        input('password setting cancelled, press enter to exit...')
        exit()
    elif (selectDrive in DRIVES):
        pass
    else:
        while True:
            DRIVES = getRemovableDrives()
            selectDrive = input(f'input didnt match known drives, input is case sensitive.\nif new drive was plugged in, it should show now, {DRIVES=}: ').upper()
            if (selectDrive == 'CANCEL'):
                input('password setting cancelled, press enter to exit...')
                exit()
            elif (selectDrive in DRIVES):
                break
            
    #set password
    password = input('input a password:')
    
    #check password
    if argv[1]=='fts':
        test = input(f'{masterpass=},\n{selectDrive=},\n{password=},\ndoes these settings look correct? [Y/N]: ').lower()
    else:
        test = input(f'{selectDrive=},\n{password=},\ndoes these settings look correct? [Y/N]: ').lower()
    if ('n' in test):
        input('no entered, press enter to exit...')
        exit()
    elif ('y' in test):
        pass
    
    if argv[1]=='fts':
        #creates the Autolock key in LOCMA\\SOFTWARE
        with wrg.OpenKey(wrg.HKEY_LOCAL_MACHINE,r'SOFTWARE') as soft:
            wrg.CreateKey(soft,'AutoLock')
            
        #uses scrypt to hash password then set as master pass in AutoLock
        setMasterPass:bytes = scrypt(masterpass, COMP_NAME_HASH, 16, N=2**14, r=8, p=1)
        with wrg.OpenKey(wrg.HKEY_LOCAL_MACHINE,r'SOFTWARE\\AutoLock',0,wrg.KEY_WRITE) as AL:
            wrg.SetValueEx(AL,str('MasterPass'),0,wrg.REG_BINARY,setMasterPass)
    
    #sets password for current user
    try:
        with open(f'{selectDrive}\\KEY','w')as key:
            key.write(password)
    except PermissionError:
        input('Perrmission error occurred.\n(likely KEY file already exists on drive, if replacing file, turn on hidden items in explorer and delete the file)\npress enter to exit...')
        exit()
    
    #hides file
    subRun(["attrib","+H",f'{selectDrive}\\KEY'])
    
    setPassword:bytes = scrypt(password, COMP_NAME_HASH, 16, N=2**14, r=8, p=1)
    with wrg.OpenKey(wrg.HKEY_LOCAL_MACHINE,r'SOFTWARE\\AutoLock',0,wrg.KEY_WRITE) as AL:
        wrg.SetValueEx(AL,str(getuser()),0,wrg.REG_BINARY,setPassword)
        
    print('password applied, please rerun AutoLock.')
    sleep(5)



def main():
    if len(argv)>2:
        if argv[1]=='fts':
            try:
                with wrg.OpenKeyEx(wrg.HKEY_LOCAL_MACHINE,'SOFTWARE\\AutoLock') as AL:
                    wrg.QueryValueEx(AL,'MasterPass')
                    input('first time setup already run, not overwriting set master password.\npress enter to exit...')
                    exit()
            except FileNotFoundError:
                pass
            masterPassword:str = input('first time setup detected, please enter master password: ')
            shared(masterPassword)
            copyfile(argv[2],r'C:\AutoLock.py')
            exit()
        
    try:
        with wrg.OpenKeyEx(wrg.HKEY_LOCAL_MACHINE,'SOFTWARE\\AutoLock') as AL:
            masterPassBytes:bytes = wrg.QueryValueEx(AL,'MasterPass')
    except FileNotFoundError:
        input('master password doesnt exist, meaning first time setup hasnt been run.\nrunning AutoLock will trigger this, as running this file by itself puts it in add user mode.\npress enter to exit...')
        exit()    
    checkMasterPass:str = input('master password: ')
    with wrg.OpenKeyEx(wrg.HKEY_LOCAL_MACHINE,r'SOFTWARE\\AutoLock') as winkey:
        savedMasterPass:bytes= wrg.QueryValueEx(winkey,'MasterPass')[0]
    hashCheckMasterPass = scrypt(checkMasterPass, COMP_NAME_HASH, 16, N=2**14, r=8, p=1)
    if (hashCheckMasterPass!=savedMasterPass):
        input('Password is incorrect.\npress enter to exit...')
        exit()
    shared()
    
    
    
    
    """global DRIVES
    DRIVES = getRemovableDrives()
    #select drive
    selectDrive = input(f'which drive should be used as the security key?\navailible drives are {DRIVES}, \'cancel\' to cancel: ')
    if (selectDrive == 'cancel'):
        input('password setting cancelled, press enter to exit...')
        exit()
    elif (selectDrive in DRIVES):
        drive = selectDrive
    else:
        while True:
            DRIVES = getRemovableDrives()
            selectDrive = input(f'input didnt match known drives, input is case sensitive.\nif new drive was plugged in, it should show now, {DRIVES=}: ')
            if (selectDrive == 'cancel'):
                input('password setting cancelled, press enter to exit...')
                exit()
            elif (selectDrive in DRIVES):
                drive = selectDrive
                break
        
    #set password
    try:
        with open(f'{drive}\\KEY','w')as key:
            password = input('input a password:')
            key.write(password)
    except PermissionError:
        input('Perrmission error occurred\n(likely KEY file already exists on drive, if replacing file, turn on hidden items in explorer and delete the file)\npress enter to exit...')
        exit()
    
    #hides file
    subRun(["attrib","+H",f'{selectDrive}\\KEY'])
    #check password
    test = input('does the password look correct? [Y/N]: ').lower()
    if ('n' in test):
        input('no entered, press enter to exit...')
        exit()
    elif ('y' in test):
        key = scrypt(password, SHA256.new(COMP_NAME).digest(), 16, N=2**14, r=8, p=1)
        with wrg.OpenKey(wrg.HKEY_LOCAL_MACHINE,r'SOFTWARE') as soft:
            wrg.CreateKey(soft,'AutoLock')
        with wrg.OpenKey(wrg.HKEY_LOCAL_MACHINE,r'SOFTWARE\\AutoLock',0,wrg.KEY_WRITE) as AL:
            wrg.SetValueEx(AL,str(getuser()),0,wrg.REG_BINARY,key)
        print('password applied, please rerun AutoLock.')
        sleep(5)
    else:
        input('input wasnt yes or no, press enter to exit...')
        exit()"""
    

        
if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        try:
            pyuac.runAsAdmin()
        except pywterror:
            input('admin not granted, please run with admin permissions.\npress enter to exit...')
    else:      
        main()
