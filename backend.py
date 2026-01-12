from Cryptodome.Protocol.KDF import scrypt
from Cryptodome.Hash import SHA256
from getpass import getuser
from time import sleep
import winreg as wrg
import win32file
import os

COMP_NAME:str = os.environ['COMPUTERNAME'].encode()

#gets list of removable drives
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

#checks drives for password
def checkDrives()->list:
    Drives = getRemovableDrives()
    for drive in Drives:
        try:
            with open(fr'{drive}\KEY') as passFile:
                password = passFile.read()
                correctDrive = drive
                break
        except FileNotFoundError:
            password = None
            continue
    if len(Drives)==0:
        return [None]
    elif (password==None):
        return [None]
    else:
        return [password,correctDrive]
    
#check if current user has a saved key
def checkIfSavedKey()->list:
    with wrg.OpenKeyEx(wrg.HKEY_LOCAL_MACHINE,r'SOFTWARE\\AutoLock') as winkey:
        try:
            savedKey:bytes= wrg.QueryValueEx(winkey,getuser())[0]
            return [savedKey]
        except FileNotFoundError:
            return [None]

#check if key is correct
def keyCheck(key:str,savedKey:bytes)->bool:
    keyFromUSB = scrypt(key, SHA256.new(COMP_NAME).digest(), 16, N=2**14, r=8, p=1)
    if (keyFromUSB==savedKey):
        return True
    else:
        return False
    
#waits till drive with key is removed
def waitForDriveRemoval(drive:str)->None:
    while True:
        sleep(.1)
        try:
            with open(fr'{drive}\KEY') as a:
                pass
        except FileNotFoundError:
            break