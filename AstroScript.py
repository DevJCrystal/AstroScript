import os
import time
import pyautogui
from PIL import Image
from datetime import datetime as dt

startTime = None
shutterImgDir = 'ShutterButtons'

# If window (nt) then cls else clear (mac / linux)
def clear():
    _ = os.system('cls' if os.name == 'nt' else 'clear')

# Check for connected device
def ADBCheck():

    listOfDevices = []

    # First check if device is connected
    os.system(f'adb devices > temp.txt')
    temp = open('temp.txt').readlines()
    for device in temp:
        try:
            int(device[0])
            # Orginally I was going to remove anything after the \t
            # but it is useful to see if a device is offline
            tempDevice = device.split('\n')[0]
            tempDevice2 = tempDevice.split('\t')
            if tempDevice2[1] == 'offline':
                # Connect the device and then add it. 
                ConnectDeviceMenu(tempDevice2[0])
            else:
                listOfDevices.append(device.split('\n')[0])

        except ValueError:
            pass

    return listOfDevices

def ConnectDeviceMenu(ip = None):
    print('1. Connect to a known device')
    print('2. Pair a new device (Only needed for Android 11+)')

    if ip == None:
        choice = int(input('Select an option: '))
    else:
        choice == int(1)

    if choice == 1 or choice == 2:

        if (choice == 1):
            if ip == None:
                ip = input('IP: ')
            newPort = input('What is the connect port? ')
            os.system(f'adb connect {ip}:{newPort}')
            MainMenu()

        if (choice == 2):
            ip = input('IP: ')
            port = input('Port: ')
            os.system(f'adb pair {ip}:{port}')
            newPort = input('What is the connect port? ')
            os.system(f'adb connect {ip}:{newPort}')
            MainMenu()
    else:
        print('Please enter an option fromt the menu.')
        ConnectDeviceMenu()

def AstroCapture(sX = None, sY = None):

    count = 0
    noCap = 0

    lastCapture = None

    astroCap = os.listdir(shutterImgDir)

    while True:
        clear()
        dt_string = startTime.strftime("%m/%d/%Y %H:%M:%S")
        print("  Start Time: ", dt_string)
        if lastCapture == None:
            print('  Last Capture: No Photos taken yet.')
        else:
            dt_string = lastCapture.strftime("%m/%d/%Y %H:%M:%S")
            print("  Last Capture: ", dt_string)
        os.system("adb shell dumpsys battery | grep level")
        os.system("adb shell dumpsys battery | grep temperature")
        print(f'  Current Capture Count: {count}')
        os.system("adb exec-out screencap -p > temp.png")
        os.system('mv temp.png phoneScreen.png')

        # Look for Astro Button
        phoneScreen = Image.open('phoneScreen.png')
        w,h = phoneScreen.size

        astroLoc = None

        for cap in astroCap:

            if astroLoc == None:
                # Might need to adjust this for different res
                astroLoc = pyautogui.locate(f'{shutterImgDir}/{cap}', phoneScreen, grayscale=False, confidence=0.7)
            else:
                pass

        # If not null click
        if not astroLoc == None:
            astroLocCenter = pyautogui.center(astroLoc)
            locX, locY = astroLocCenter

            os.system(f"adb shell input tap {locX} {locY}")
            lastCapture = dt.now()
            count+=1
            print('Starting capture!')
        else:
            print('Not ready to capture.')
        
        if lastCapture == None:
            noCap += 1
            if noCap == 60:
                noCap = 0
                input('It seems we cannot find the shutter. Please add it to the ShutterButtons directory and press enter')
                astroCap = os.listdir(shutterImgDir)

        time.sleep(1)

    MainMenu()

def MainMenu():
    global startTime

    listOfDevices = ADBCheck()

    if len(listOfDevices) == 0:
        print('Need to add a device')
        ConnectDeviceMenu()
    else:
        input('Press enter when your phone is set to Night Sight and mounted where you want.')
        startTime = dt.now()
        AstroCapture()

MainMenu()