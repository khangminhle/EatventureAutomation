#from device import Device
from modules.GameAuto import GameAuto
from modules.ADB import ADBController
from modules.GameDetector import GameDetector
from modules.ImageProcess import find_points_match_template
import glob
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
    '''
    img = cv2.imread("screenshot.png", 0)  

    print('test')

    templates = ["templates/boxes/box9.png"]#glob.glob("templates/boxes/*.png")

    for tp in templates:

        template = cv2.imread(tp, 0)

        points = find_points_match_template(img, template, threshold=0.8, binary=True)
        if points:
            print("template", tp)
            print(points)
            print("len:", len(points))

            for x, y in points:
                center_x = x
                center_y = y
                cv2.rectangle(img, (center_x-50, center_y-50), (center_x+50, center_y+50), (0, 255, 0), 1)
            cv2.imwrite("test_boxes.png", img)
            break
    '''
    #find_points_match_template(img, template)
    #adb.save_screenshot()   
    #adb.crop_screen((10, 270, 90, 300))


    auto = GameAuto()

    #auto.crop_swipe()
    auto.start()

