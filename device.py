import adbutils
import cv2
import numpy as np
import time
from sklearn.cluster import DBSCAN
from modules.imageProcess import *
from constants import Constants
from adb import ADBController
import subprocess
import glob


class Device: 
    def __init__(self):
        self.adb = ADBController()
        self.__screen_center_x = 0
        self.__screen_center_y = 0
        self.__scale_x = 0
        self.__scale_y = 0
        self.__game_finish = False

        self.__core = None
        self.__mode = "NORMAL"
        self.__upper_bound_y = 2120
        self.__max_swipe_turn = 2
        self.__swipe_turn = 0
        self.__swipe_times = 0
        self.__distanceToSwipe = 0
    

    def isReadyToStart(self):
        if(self.__core == None):
            return False
        return True

    def setScreenCenterX(self, x):
        self.__screen_center_x = x
    def setScreenCenterY(self, y):
        self.__screen_center_y = y
    def setScaleX(self, x):
        self.__scale_x = x
    def setScaleY(self, y):
        self.__scale_y = y 

    def connect(self):
        try:
            adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
            print('Connect to device', adb.device())
            self.__core = adb.device()
        except Exception as e:
            print('Error connect:', e)
            return False

    def config(self):
        print('test')
        if(self.__core):
            info = self.__core.window_size()
            const = Constants()
            print(info)
            default_x = const.DEFAULT_TEMPLATE_WIDTH()
            default_y = const.DEFAULT_TEMPLATE_HEIGHT()
            self.setScaleX(info.width/default_x)
            self.setScaleY(info.height/default_y)
            self.setScreenCenterX(info.width//2)
            self.setScreenCenterY(info.height//2)
            self.__distanceToSwipe = -self.__screen_center_y * 1/4
            self.__swipe_turn = 0
            self.__swipe_times = 0
            self.__game_finish = False

    def take_screenshot(self):
        screenshot = self.__core.screenshot()
        screenshot.save("screenshot.png")

    def screenshot(self, mode="BGR"):

        # Không dùng -p để tránh Android phải nén ảnh thành PNG
        cmd = ["adb", "exec-out", "screencap"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        stdout, _ = process.communicate()

        # 12 byte đầu tiên của screencap chứa thông tin: Width (4 byte), Height (4 byte), Format (4 byte)
        width = int.from_bytes(stdout[0:4], byteorder='little')
        height = int.from_bytes(stdout[4:8], byteorder='little')

        # Tính toán chính xác số lượng byte cần thiết cho ảnh RGBA
        expected_size = width * height * 4
        
        # Lấy đúng lượng byte cần thiết, bắt đầu từ byte thứ 12
        # Sử dụng offset trong frombuffer để tối ưu bộ nhớ (không cần slice stdout[12:])
        frame = np.frombuffer(stdout, dtype=np.uint8, count=expected_size, offset=12)
        
        # Reshape về đúng kích thước màn hình
        frame = frame.reshape((height, width, 4))

        if mode == "BGR":
            return cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

        if mode == "GRAY":
            return cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)

    def startAuto(self):
        print('Auto started!')
        self.config()
        self.crop_swipe_max()
        while(True):
            try:
                print("START!!!!!")
                
                if(self.findNoMultiply()):
                    self.__mode = "AD"
                    self.clickAds()
                    time.sleep(30)

                if(self.__mode == "AD"):
                    action6 = self.clickFinishAds()
                    action7 = self.clickCollectButton()
                    continue
                
                action0 = self.clickFoodUpdate()

                while not action0:

                    self.findBoxes()

                    #self.findFinishButton()
                    #self.findOpenButton()
                    self.__core.click(550, 400)
                    #self.swipe_screen(distanceToSwipe)
                    #self.setTimeSwipe(self.__times_swipe+1)

                    self.swipe_screen(self.__distanceToSwipe)
                    self.__swipe_times += 1
                    print("So lan swipe:", self.__swipe_times)

                    flag = None

                    if(self.__distanceToSwipe < 0):
                        print("Swipe Down")
                        flag =  self.check_swipe_max("bottom")
                    else:
                        flag = self.check_swipe_max()
                        print("Swpipe Up")

                    if flag:
                        self.__distanceToSwipe = self.__distanceToSwipe * -1
                        self.__swipe_turn += 1
                    else:
                        self.crop_swipe_max()

                    if(self.__swipe_turn == self.__max_swipe_turn):
                        print("Da swipe xong 1 turn")
                        action4 = self.findFinishButton()
                        time.sleep(7)
                        if self.__game_finish:
                            action5 = self.findOpenButton()
                        else:
                            action5 = None

                        if not any([action4, action5]):
                            self.__swipe_turn = 0
                        break


      
                    print("Khong co food upgrade")
                    action0 = self.clickFoodUpdate()

                action1 = self.findUpgradeButton()
                
            except Exception as e:
                print('Error:', e)
                break

    def swipe_screen(self, distance, duration=0.5):
        new_y = self.__screen_center_y + distance # + distance means you swipe down to go up

        self.__core.swipe(self.__screen_center_x, self.__screen_center_y, self.__screen_center_x, new_y, duration)

    def click_points(self, points, duration=0.1, callback={}):


        for pt in points:
            x, y = pt[0], pt[1]
            self.__core.click(x, y)

            if callback:
                #action0 = callback['findBoxes']()
                #if not action0:
                callback['clickButtonCoin']()
                callback['findBoxes']()

                #callback['clickButtonCoin']()
            #else:
            #    continue
            time.sleep(duration)

    def clickAds(self):
        x = 550
        y = 2200
        # Default location to click watching Ad
        self.__core.click(x,y)

    def swipe_points(self, points, duration=3.0):
        for pt in points:
            x, y = pt[0], pt[1]
            
            self.__core.click(x, y)
            self.__core.swipe(x, y, x, y, duration)
            print(f"Dang long press toa do {x} {y}")
            time.sleep(0.1)
            break

    def findNoMultiply(self):
        img = self.screenshot(mode="GRAY")
        template = cv2.imread('templates/nomultiply.png', cv2.IMREAD_GRAYSCALE)

        points = find_points_match_template(img, template)

        #print(points)

        if(len(points) <= 0):
            print("Da Multiply")
            return False

        print("Hien dang Multiply Normal")
        return True

    def clickButtonCoin(self):
        

        img = self.screenshot(mode="GRAY")#cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        template = cv2.imread('templates/button_coin.png', cv2.IMREAD_GRAYSCALE)

        points = find_points_match_template(img, template)

        if(len(points) <= 0):
            print("Khong tim thay nut upgrade food")
            self.__core.click(550, 400)
            return False

        print("Dang upgrade button coin")
        self.swipe_points(points)
        time.sleep(0.1)
        self.clickButtonCoin()

        return True

    def clickFoodUpdate(self):
        try:
            img = self.screenshot(mode="GRAY")#self.__core.screenshot()

            #cv2.imwrite("test_screen_shot.png", img)
            #img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
            template = cv2.imread('templates/button_test.png', cv2.IMREAD_GRAYSCALE)

            template = resize_template(template, self.__scale_x, self.__scale_y)

            points = find_points_match_template(img, template, threshold=0.8)

            #Khong lay mui ten ngay goc phai (cho upgrade shop)
            new_points = [(x, y+20) for x,y in points if y+20 < self.__upper_bound_y]
            #if(len(new_points) > 0):
            #    first_point = [new_points[-1]]
            #else:
            #    first_point = []

            #print(first_point)

            if(len(new_points) <= 0):
                print("Khong tim thay nut upgrade food")
                return False

            callback = {
                'findBoxes': self.findBoxes,
                'clickButtonCoin': self.clickButtonCoin
            }

            print("Da tim thay nut upgrade food")
            print(new_points)
            self.click_points(new_points, callback=callback)
            
            return True
        except Exception as e:
            print('Error clickFoodUpdate:', e)

    def findFinishButton(self):
        screenshot = self.__core.screenshot()

        left = 20
        top = 2120
        right = 181
        bottom = 2278


        screenshot = screenshot.crop((left, top, right, bottom))

        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        template = cv2.imread('templates/finished_button.png')

        points = find_points_match_template(img, template, check=True)

        #print(points)

        #if(len(points) <= 0):
        #    print("Khong tim thay nut finish")
        #    return False

        if not points:
            print("Khong tim thay nut finish")
            return False

        print('FINISHED FOUND!')
        print(points)

        x = (left+right)//2
        y = (top+bottom)//2
        self.__core.click(x, y)

        time.sleep(1)
        self.clickToFinish()

        self.__game_finish = True

    def findOpenButton(self):
        screenshot = self.__core.screenshot()

        left = 344
        top = 1304
        right = 733
        bottom = 1462


        screenshot = screenshot.crop((left, top, right, bottom))

        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        template = cv2.imread('templates/open_button.png', cv2.IMREAD_GRAYSCALE)

        points = find_points_match_template(img, template, check=True)

        #print(points)

        #if(len(points) <= 0):
        #    print("Khong tim thay nut open")
        #    return False

        if not points:
            print("Khong tim thay nut open")
            return False

        print('OPEN FOUND!')
        print(points)

        x = (left+right)//2
        y = (top+bottom)//2

        self.__core.click(x, y)

        #self.click_points(points)

        #time.sleep(2)

        self.config()
        time.sleep(3)

    def clickToFinish(self):
        x = 550
        y = 1650

        self.__core.click(x,y)

    def findUpgradeButton(self):
        screenshot = self.__core.screenshot()

        left = 871
        top = 2089
        right = 1063
        bottom = 2272


        screenshot = screenshot.crop((left, top, right, bottom))


        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        template = cv2.imread('templates/upgrade_button.png')

        points = find_points_match_template(img, template, check=True)

        #print(points)

        '''
        if(len(points) <= 0):
            print("Khong tim thay nut upgrade shop")
            return False

        self.click_points(points)
        '''

        if not points:
            print("Khong tim thay nut upgrade shop")
            return False

        x = (left+right)//2
        y = (top+bottom)//2

        print("Da tim thay nut upgrade shop")
        self.__core.click(x, y)

        self.clickUpgradeShop()

    def clickUpgradeShop(self):

        img = self.screenshot(mode="BGR")
        template = cv2.imread('templates/coinshop.png')

        #flag = check_if_match_template(img, template, threshold=0.9)
        flag = find_points_match_template(img, template, threshold=0.9,check=True)

        while(flag):
            x = 850
            y = 950

            for _ in range(10):
                self.__core.click(x,y)

            img = self.screenshot(mode="BGR")
            flag = find_points_match_template(img, template, threshold=0.9,check=True)

        # Default (x,y) button close upgrade shop
        self.__core.click(920, 800)

    def clickCollectButton(self):
        img = self.screenshot(mode="GRAY")
        templates = ["collect_button.png"]

        for temp in templates:
            template = cv2.imread(f'templates/{temp}', cv2.IMREAD_GRAYSCALE)

            points = find_points_match_template(img, template)

            if(len(points) > 0):
                self.click_points(points)
                print("Da click collect")
                return True

        print("Dang tim nut collect")

        return False

    def clickFinishAds(self):
        img = self.screenshot(mode="GRAY")
        templates = glob.glob("templates/ads/*.png")


        for temp in templates:
            template = cv2.imread(temp, cv2.IMREAD_GRAYSCALE)

            points = find_points_match_template(img, template)

            if(len(points) > 0):
                self.click_points(points)
                print("Da click finish ads")
                self.__mode = "NORMAL"
                return True

        print("Dang tim nut finish ads")

        self.__core.click(1011, 150)
        #self.__mode = "NORMAL"
        return False

    def findBoxes(self):
        #template = cv2.imread('templates/box3.png')

        templates = glob.glob("templates/boxes/*.png")
        img = self.screenshot(mode="GRAY")
    

        #templates = ["box.png", "box1.png", "box2.png", "box3.png", "boxes.png"]
        flag = False
        for temp in templates:
            template = cv2.imread(temp, cv2.IMREAD_GRAYSCALE)
            points = find_points_match_template(img, template)

            if(len(points) > 0):
                self.click_points(points)
                print("Da tim thay boxes!")
                print('Da tim thay template', temp)
                flag = True

        if(flag == True):
            return True

        print("Khong tim thay boxes!")
        return False
        #template2 = cv2.imread('box2.png')

        #points = find_points_match_template(img, template)
        #points2 = find_points_match_template(img, template2)

        #if(len(points) <= 0): #and len(points2) <= 0):
        #    print("Khong tim thay boxes")
        #    return False

        #print("Da tim thay boxes")
        #self.click_points(points)
        #click_points(points2)


        #draw_test(points, img)

        #draw_test(img, points)

        #print(points)

        #print(points2)

        #return True
        #print(points)

        #draw_test(points, img)
    
    def crop_swipe_max(self):

        # Top region
        left = 10
        top = 270
        right = 90
        bottom = 300

        # Bottom region
        new_top = 2080
        new_bottom = 2110

        screenshot = self.__core.screenshot()

        cropped_img = screenshot.crop((left, top, right, bottom))

        cropped_img.save("check_swipe.png")

        cropped_img = screenshot.crop((left, new_top, right, new_bottom))

        cropped_img.save("check_swipe_bottom.png")

    def check_swipe_max(self, mode="top"):

        # Top region
        left = 10
        top = 270
        right = 90
        bottom = 300

        if mode == "top":
            img1 = cv2.imread("check_swipe.png")
        else:
            # Bottom region
            top = 2080
            bottom = 2110
            img1 = cv2.imread("check_swipe_bottom.png")

        #img2 = cv2.imread("check_swipe_bottom.png")

        if img1 is None:
            return None

        screenshot = self.__core.screenshot()

        cropped_img = screenshot.crop((left, top, right, bottom))

        img2 = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_RGB2BGR)


        if check_same_images(img1, img2):
            return True
        else:
            return False