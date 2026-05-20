#from device import Device
from modules.GameAuto import GameAuto
from modules.ADB import ADBController
from modules.GameDetector import GameDetector
from modules.ImageProcess import find_points_match_template
import cv2

#scrcpy -S --window-title "eatventure_screen" --max-fps 30

if __name__ == '__main__':

    #device = Device()
    #device.connect()
    #device.take_screenshot()
    #device.crop_swipe_max()
    #device.startAuto() 

    #adb = ADBController()

    #adb.connect()
    #adb.save_screenshot()
    #img = cv2.imread("screenshot.png", 0)  
    #template = cv2.imread("templates/boxes/box5.png", 0)

    #find_points_match_template(img, template)
    #adb.save_screenshot()   
    #adb.crop_screen((10, 270, 90, 300))


    auto = GameAuto()

    #auto.crop_swipe()
    auto.start()

