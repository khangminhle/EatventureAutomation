"""ADB (Android Debug Bridge) controller for device interaction."""

import logging
import adbutils
import cv2
from modules.ImageProcess import resize_image
import numpy as np
from typing import Optional, Tuple
from .Constants import DEFAULT_PROJECT_DEVICE_HEIGHT, DEFAULT_PROJECT_DEVICE_WIDTH, TemplateConfig
from .Constants import SwipeConfig
from .Constants import ImageColor

logger = logging.getLogger(__name__)


class ADBController:
    """
    Controls ADB device connections and interactions.
    Handles screenshots, clicks, swipes, and image cropping/saving.
    """
    
    def __init__(self):
        """Initialize ADB controller with default values."""
        self.__core = None
        self.screen_center_x = 0
        self.screen_center_y = 0
        self.new_device_scale_x = 1.0
        self.new_device_scale_y = 1.0
        self.scale_x = 1.0
        self.scale_y = 1.0
        #self.upper_bound_y = 2120
        self.max_screen_x = 0
        self.max_screen_y = 0
        self.distanceToSwipe = 0

    def is_ready(self) -> bool:
        """
        Check if device is connected and ready.
        
        Returns:
            True if connected, False otherwise
        """
        return self.__core is not None

    def connect(self) -> bool:
        """
        Connect to Android device via ADB.
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.is_ready():
            logger.info("Device already connected")
            return True
        
        try:
            adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
            self.__core = adb.device()
            logger.info(f"Connected to device: {self.__core}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to device: {e}")
            return False

    def config(self) -> bool:
        """
        Configure device screen parameters (scaling, center, etc).
        
        Returns:
            True if configuration successful, False otherwise
        """
        if not self.is_ready():
            logger.error("Device not connected")
            return False
        
        try:
            if not self.__core:
                return False

            info = self.__core.window_size()
            self.screen_center_x = info.width // 2
            self.screen_center_y = info.height // 2
            self.distanceToSwipe = -self.screen_center_y * SwipeConfig.SWIPE_DISTANCE_RATIO
            self.new_device_scale_x = info.width / DEFAULT_PROJECT_DEVICE_WIDTH
            self.new_device_scale_y = info.height / DEFAULT_PROJECT_DEVICE_HEIGHT
            self.scale_x = info.width / TemplateConfig.DEFAULT_TEMPLATE_WIDTH
            self.scale_y = info.height / TemplateConfig.DEFAULT_TEMPLATE_HEIGHT
            self.max_screen_x = info.width
            self.max_screen_y = info.height
            
            logger.info(f"Device configured: {info.width}x{info.height}")
            return True
        except Exception as e:
            logger.error(f"Failed to configure device: {e}")
            return False

    def click(self, x: int, y: int, mode=None) -> None:
        """
        Click at scaled coordinates on device.
        
        Args:
            x: X coordinate (template-relative)
            y: Y coordinate (template-relative)
        """
        if self.__core:
            if mode == "scaled":
                scaled_x = int(x * self.scale_x)
                scaled_y = int(y * self.scale_y)
            else:
                scaled_x = int(x * self.new_device_scale_x)
                scaled_y = int(y * self.new_device_scale_y)

            self.__core.click(scaled_x, scaled_y)

    def swipe(self, fx: int, fy: int, tx: int, ty: int, duration: float = 3.0, mode: str = None) -> None:
        """
        Swipe from one point to another on device.
        
        Args:
            fx: From X coordinate (template-relative)
            fy: From Y coordinate (template-relative)
            tx: To X coordinate (template-relative)
            ty: To Y coordinate (template-relative)
            duration: Swipe duration in seconds
        """
        if not self.__core:
            return

        if mode == "scaled":
            fx = int(fx * self.scale_x)
            fy = int(fy * self.scale_y)
            tx = int(tx * self.scale_x)
            ty = int(ty * self.scale_y)
        else:
            fx = int(fx * self.new_device_scale_x)
            fy = int(fy * self.new_device_scale_y)
            tx = int(tx * self.new_device_scale_x)
            ty = int(ty * self.new_device_scale_y)

        self.__core.swipe(fx, fy, tx, ty, duration)

    def crop_screen(
        self,
        position: Tuple[int|float, int|float, int|float, int|float]
    ) -> Optional[np.ndarray]:
        """
        Crop a region from the screen.
        
        Args:
            position: Tuple of (left, top, right, bottom) coordinates
        
        Returns:
            Cropped RGBA image, or None on error
        """
        if len(position) != 4:
            logger.error(f"Invalid position: expected 4 values, got {len(position)}")
            return None
        
        try:
            left, top, right, bottom = [coord for coord in position]
            
            # Validate coordinates
            if any(coord < 0 for coord in [left, top, right, bottom]):
                logger.error("Coordinates cannot be negative")
                return None
            
            if left >= right or top >= bottom:
                logger.error("Invalid crop region: left >= right or top >= bottom")
                return None
            
            screenshot = self.__core.screenshot()

            #self.__screencap()
            if screenshot is None:
                return None
            
            # Scale for current device resolution

            left *= self.new_device_scale_x
            top *= self.new_device_scale_y
            right *= self.new_device_scale_x
            bottom *= self.new_device_scale_y

            screenshot = np.array(screenshot)

            img = screenshot[int(top):int(bottom), int(left):int(right)]
            return img
        
        except Exception as e:
            logger.error(f"Crop screen error: {e}")
            return None

    def screenshot(self, mode: ImageColor = ImageColor.BGR) -> Optional[np.ndarray]:
        """
        Get full screenshot in specified color mode.
        
        Args:
            mode: Color mode (ImageColor.BGR or ImageColor.GRAYSCALE)
        
        Returns:
            Image as numpy array, or None on error
        """
        if not self.__core:
            logger.error("Device not connected")
            return None
        
        try:
            #screenshot = self.__screencap()
            screenshot = self.__core.screenshot()

            if (1/self.scale_x) > 1:
                print("THIET BI KHONG DU DO PHAN GIAI DE CHAY BOT")
                return None

            screenshot = resize_image(np.array(screenshot), 1/self.scale_x, 1/self.scale_y)

            if screenshot is None:
                return None
            
            if mode == ImageColor.BGR:
                return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            elif mode == ImageColor.GRAYSCALE:
                return cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
            else:
                logger.warning(f"Unknown mode: {mode}, defaulting to BGR")
                return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None

    def save_image(
        self,
        image: np.ndarray,
        name: str,
        mode: ImageColor = ImageColor.BGR
    ) -> bool:
        """
        Save image to file.
        
        Args:
            image: Image as numpy array
            name: Filename without extension
            mode: Color mode for conversion
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not isinstance(image, np.ndarray):
                logger.error("Input must be numpy array")
                return False
            
            if mode == ImageColor.BGR:
                new_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            elif mode == ImageColor.GRAYSCALE:
                new_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                logger.warning(f"Unknown mode: {mode}, defaulting to BGR")
                new_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            cv2.imwrite(f'{name}.png', new_image)
            logger.info(f"Saved image: {name}.png")
            return True
        
        except Exception as e:
            logger.error(f"Save image error: {e}")
            return False

    def save_screenshot(self, mode: ImageColor = ImageColor.BGR) -> bool:
        """
        Save current screenshot to file.
        
        Args:
            mode: Color mode for conversion
        
        Returns:
            True if successful, False otherwise
        """
        if not self.__core:
            logger.error("Device not connected")
            return False
        
        try:
            image = self.screenshot(mode)
            
            if image is not None:
                cv2.imwrite("screenshot.png", image)
                logger.info("Saved screenshot.png")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Save screenshot error: {e}")
            return False

    def crop_swipe(self):

        if not self.__core:
            logger.error("Device not connected")
            return False

        try:
            # Top region
            left = SwipeConfig.SWIPE_TOP_REGION['left'] 
            top = SwipeConfig.SWIPE_TOP_REGION['top'] 
            right = SwipeConfig.SWIPE_TOP_REGION['right']
            bottom = SwipeConfig.SWIPE_TOP_REGION['bottom'] 

            # Bottom region
            new_top = SwipeConfig.SWIPE_BOTTOM_REGION['top'] 
            new_bottom = SwipeConfig.SWIPE_BOTTOM_REGION['bottom']

            cropped_img = self.crop_screen((left, top, right, bottom))#screenshot.crop((left, top, right, bottom))
            
            crops = {}

            if cropped_img is not None:
                crops['top'] = cropped_img
                #self.save_image(cropped_img, name="check_swipe")
            else:
                print("Loi crop swipe top")
                return None

            cropped_img = self.crop_screen((left, new_top, right, new_bottom))#screenshot.crop((left, new_top, right, new_bottom))
        
            if cropped_img is not None:
                crops['bottom'] = cropped_img
                #self.save_image(cropped_img, name="check_swipe_bottom")
            else:
                print("Loi crop swipe bottom")
                return None

            if len(crops) == 2:
                return crops

        except Exception as e:
            print("Error ADB - crop_swipe:", e)
            return None
