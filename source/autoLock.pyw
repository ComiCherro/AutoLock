from urllib.request import urlretrieve
from urllib.error import URLError
from sys import exit
import subprocess
import ctypes
import backend

#glo. vars
UsersLocked:list = []
DRIVES:list = []
key:str = ""

#setup
def setup(firstTimeSetup:bool)->None:
    try:
        with open(rf"C:\users\{backend.getuser()}\Downloads\autoLockSetup.py") as a:
            pass
    except FileNotFoundError:
        try:
            urlretrieve("https://raw.githubusercontent.com/ComiCherro/AutoLock/refs/heads/main/source/setup/autoLockSetup.py", rf"C:\users\{backend.getuser()}\Downloads\autoLockSetup.py")
        except URLError:
            input('setup not accessible from internet, please goto\n\nhttps://github.com/ComiCherro/AutoLock/blob/main/source/setup/autoLockSetup.py\n\nand download + run the file, then rerun AutoLock.\npress enter to exit...')
            exit() 
    if firstTimeSetup:
        doc = subprocess.Popen(fr'start /WAIT C:\Users\{backend.getuser()}\Downloads\autoLockSetup.py fts {backend.os.path.realpath(__file__)}', shell=True)
    else:
        doc = subprocess.Popen(fr'start /WAIT C:\Users\{backend.getuser()}\Downloads\autoLockSetup.py', shell=True)
    doc.wait()
    backend.os.remove(rf"C:\users\{backend.getuser()}\Downloads\autoLockSetup.py")
    exit()


def main()->None:
    while True:
        backend.sleep(.1)
        key = backend.checkDrives()
        savedKey = backend.checkIfSavedKey()
        if (savedKey==None):
            continue
        elif (key==None):
            ctypes.windll.user32.LockWorkStation()
        else:
            if not backend.keyCheck(key[0],savedKey):
                ctypes.windll.user32.LockWorkStation()
                continue
            backend.waitForDriveRemoval(key[1])
            ctypes.windll.user32.LockWorkStation()
            
if (__name__=='__main__'):
    #attempt to open reg. key
    try:
        with backend.wrg.OpenKeyEx(backend.wrg.HKEY_LOCAL_MACHINE,r'SOFTWARE\AutoLock',0,backend.wrg.KEY_READ) as a:
            pass
    except FileNotFoundError:
        setup(True)
    main()