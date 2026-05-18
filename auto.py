#from device import Device
from modules.GameAuto import GameAuto
from modules.ADB import ADBController
#scrcpy -S --window-title "eatventure_screen" --max-fps 30

if __name__ == '__main__':

    #device = Device()
    #device.connect()
    #device.take_screenshot()
    #device.crop_swipe_max()
    #device.startAuto()

    auto = GameAuto()

    auto.start()   