#from device import Device
from modules.Constants import ImageColor
from modules.GameAuto import GameAuto
from modules.ADB import ADBController
from modules.GameDetector import GameDetector
from modules.ImageProcess import find_points_match_template
import glob
import cv2

#scrcpy -S --window-title "eatventure_screen" --max-fps 30

if __name__ == '__main__':
    auto = GameAuto()
    auto.start()
    
    '''
    adb = ADBController()

    adb.connect()

    adb.save_screenshot(ImageColor.GRAYSCALE)

    img = cv2.imread("screenshot.png")

    thresh_value = 180
    _, img = cv2.threshold(img, thresh_value, 255, cv2.THRESH_BINARY_INV)

    cv2.imwrite("test.png", img)
    #cv2.imshow("show:", img)
    
    '''