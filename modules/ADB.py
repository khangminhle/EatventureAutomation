"""ADB (Android Debug Bridge) controller for device interaction."""

import logging
import adbutils
import subprocess
import cv2
import numpy as np
from typing import Optional, Tuple
from .Constants import DEFAULT_TEMPLATE_WIDTH, DEFAULT_TEMPLATE_HEIGHT

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
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.upper_bound_y = 2120
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
            info = self.__core.window_size()
            self.screen_center_x = info.width // 2
            self.screen_center_y = info.height // 2
            self.distanceToSwipe = -self.screen_center_y / 5
            self.scale_x = info.width / DEFAULT_TEMPLATE_WIDTH
            self.scale_y = info.height / DEFAULT_TEMPLATE_HEIGHT
            self.max_screen_x = info.width
            self.max_screen_y = info.height
            
            logger.info(f"Device configured: {info.width}x{info.height}")
            return True
        except Exception as e:
            logger.error(f"Failed to configure device: {e}")
            return False

    def click(self, x: int, y: int) -> None:
        """
        Click at scaled coordinates on device.
        
        Args:
            x: X coordinate (template-relative)
            y: Y coordinate (template-relative)
        """
        if self.__core:
            scaled_x = int(x * self.scale_x)
            scaled_y = int(y * self.scale_y)
            self.__core.click(scaled_x, scaled_y)

    def swipe(self, fx: int, fy: int, tx: int, ty: int, duration: float = 3.0) -> None:
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
        
        fx = int(fx * self.scale_x)
        fy = int(fy * self.scale_y)
        tx = int(tx * self.scale_x)
        ty = int(ty * self.scale_y)
        self.__core.swipe(fx, fy, tx, ty, duration)

    def __screencap(self) -> Optional[np.ndarray]:
        """
        Capture screen from device using optimized screencap.
        
        Returns:
            RGBA image as numpy array, or None on error
        """
        if not self.__core:
            logger.error("Device not connected")
            return None
        
        try:
            cmd = ["adb", "exec-out", "screencap"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            stdout, _ = process.communicate()
            
            # Parse header (12 bytes: width, height, format)
            width = int.from_bytes(stdout[0:4], byteorder='little')
            height = int.from_bytes(stdout[4:8], byteorder='little')
            expected_size = width * height * 4
            
            if len(stdout) < expected_size + 12:
                logger.warning("Incomplete screenshot data")
                return None
            
            # Extract frame data
            frame = np.frombuffer(
                stdout,
                dtype=np.uint8,
                count=expected_size,
                offset=12
            )
            frame = frame.reshape((height, width, 4))
            
            return frame
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None

    def crop_screen(
        self,
        position: Tuple[int, int, int, int]
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
            left, top, right, bottom = [int(coord) for coord in position]
            
            # Validate coordinates
            if any(coord < 0 for coord in [left, top, right, bottom]):
                logger.error("Coordinates cannot be negative")
                return None
            
            if left >= right or top >= bottom:
                logger.error("Invalid crop region: left >= right or top >= bottom")
                return None
            
            screenshot = self.__screencap()
            if screenshot is None:
                return None
            
            img = screenshot[int(top):int(bottom), int(left):int(right)]
            return img
        
        except Exception as e:
            logger.error(f"Crop screen error: {e}")
            return None

    def screenshot(self, mode: str = "BGR") -> Optional[np.ndarray]:
        """
        Get full screenshot in specified color mode.
        
        Args:
            mode: Color mode ("BGR" or "GRAY")
        
        Returns:
            Image as numpy array, or None on error
        """
        if not self.__core:
            logger.error("Device not connected")
            return None
        
        try:
            screenshot = self.__screencap()
            
            if screenshot is None:
                return None
            
            if mode == "BGR":
                return cv2.cvtColor(screenshot, cv2.COLOR_RGBA2BGR)
            elif mode == "GRAY":
                return cv2.cvtColor(screenshot, cv2.COLOR_RGBA2GRAY)
            else:
                logger.warning(f"Unknown mode: {mode}, defaulting to BGR")
                return cv2.cvtColor(screenshot, cv2.COLOR_RGBA2BGR)
        
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None

    def save_image(
        self,
        image: np.ndarray,
        name: str,
        mode: str = "BGR"
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
            
            if mode == "BGR":
                new_image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
            elif mode == "GRAY":
                new_image = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
            else:
                logger.warning(f"Unknown mode: {mode}, defaulting to BGR")
                new_image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
            
            cv2.imwrite(f'{name}.png', new_image)
            logger.info(f"Saved image: {name}.png")
            return True
        
        except Exception as e:
            logger.error(f"Save image error: {e}")
            return False

    def save_screenshot(self, mode: str = "BGR") -> bool:
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
