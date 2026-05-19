"""Game detector for template matching and game state detection."""

import os
import logging
from typing import Optional, List
import cv2
import glob
import numpy as np

from .ImageProcess import find_points_match_template, check_same_images
from .Constants import (
    BASE_DIR,
    GameMode,
    TemplateConfig,
    ValidZones,
    SwipeConfig
)
from .ADB import ADBController

logger = logging.getLogger(__name__)


class GameDetector:
    """
    Detects game elements and state through template matching.
    Validates points against valid game zones.
    """
    
    def __init__(self, adb: ADBController, map_game: str = "NORMAL"):
        """
        Initialize game detector.
        
        Args:
            adb: ADB controller instance
            map_game: Game map type ("NORMAL" or "POTION")
        """
        self.__adb = adb
        self.__map = map_game
        logger.info(f"GameDetector initialized with map: {map_game}")

    def _check_valid_points(self, x: int, y: int) -> bool:
        """
        Check if point is within valid game zones.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            True if point is in valid zone, False otherwise
        """
        if x < 0 or y < 0:
            return False
        
        if x > self.__adb.max_screen_x or y > self.__adb.max_screen_y:
            return False
        
        # Check center zone
        if ValidZones.CENTER["x_min"] <= x <= ValidZones.CENTER["x_max"]:
            return ValidZones.CENTER["y_min"] <= y <= ValidZones.CENTER["y_max"]
        
        # Check left zone
        if x < ValidZones.LEFT["x_max"]:
            return ValidZones.LEFT["y_min"] <= y <= ValidZones.LEFT["y_max"]
        
        # Check right zone
        if x > ValidZones.RIGHT["x_min"]:
            return ValidZones.RIGHT["y_min"] <= y <= ValidZones.RIGHT["y_max"]
        
        return False

    def _match_template_helper(
        self,
        template_paths: List[str],
        mode: str = "GRAY",
        **kwargs
    ) -> Optional[bool | List[tuple]]:
        """
        Generic template matching helper.
        
        Args:
            template_paths: Path components to template file
            mode: Color mode ("GRAY" or "BGR")
            **kwargs: Additional arguments for find_points_match_template
        
        Returns:
            Matching points or boolean, or None on error
        """
        if not self.__adb:
            logger.error("ADB not connected")
            return None
        
        try:
            img = self.__adb.screenshot(mode=mode)
            
            if img is None:
                logger.warning("Failed to capture screenshot")
                return None
            
            template_path = os.path.join(BASE_DIR, *template_paths)
            
            if mode == "GRAY":
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            else:
                template = cv2.imread(template_path)
            
            if template is None:
                logger.warning(f"Template not found: {template_path}")
                return None
            
            return find_points_match_template(img, template, **kwargs)
        
        except Exception as e:
            logger.error(f"Template matching error: {e}")
            return None

    def check_nothing_upgrade(self) -> bool:
        """
        Check if there are any upgradeable items left.
        
        Returns:
            True if upgradeable items exist, False otherwise
        """
        try:
            # Check upgrade food availability
            if self.find_upgrade_food():
                return True
            return False
        except Exception as e:
            logger.error(f"Error in check_nothing_upgrade: {e}")
            return False

    def find_upgrade_food(self) -> List[tuple]:
        """
        Find food upgrade buttons on screen.
        
        Returns:
            List of valid (x, y) coordinates for food upgrades
        """
        try:
            points = self._match_template_helper(
                ['templates', TemplateConfig.TEMPLATES["upgrade_food"]]
            )
            
            if points is None or isinstance(points, bool):
                return []
            
            # Offset y by 20 and validate
            valid_points = [
                (x, y + 20) for x, y in points
                if self._check_valid_points(x, y + 20)
            ]
            
            logger.debug(f"Found {len(valid_points)} food upgrades")
            return valid_points
        
        except Exception as e:
            logger.error(f"Error finding upgrade food: {e}")
            return []

    def find_button_coin(self) -> List[tuple]:
        """
        Find coin button based on game map type.
        
        Returns:
            List of (x, y) coordinates for coin buttons
        """
        try:
            if self.__map == "POTION":
                template_name = TemplateConfig.TEMPLATES["coin_potion_ingredients"]
            else:
                template_name = TemplateConfig.TEMPLATES["button_coin"]
            
            points = self._match_template_helper(['templates', template_name])
            
            if points is None or isinstance(points, bool):
                return []
            
            logger.debug(f"Found {len(points)} coin buttons")
            return points
        
        except Exception as e:
            logger.error(f"Error finding button coin: {e}")
            return []

    def find_boxes(self) -> List[tuple]:
        """
        Find collectible boxes on screen.
        
        Returns:
            List of (x, y) coordinates for boxes
        """
        try:
            template_dir = os.path.join(
                BASE_DIR,
                'templates',
                'boxes',
                '*.png'
            )
            templates = glob.glob(template_dir)
            
            if not templates:
                logger.warning("No box templates found")
                return []
            
            for template_path in templates:
                points = self._match_template_helper([template_path])
                
                if points is None or isinstance(points, bool):
                    continue
                
                if len(points) > 0:
                    logger.debug(f"Found {len(points)} boxes using {template_path}")
                    return points
            
            logger.debug("No boxes found on screen")
            return []
        
        except Exception as e:
            logger.error(f"Error finding boxes: {e}")
            return []

    def find_upgrade_shop(self) -> bool:
        """
        Detect if upgrade shop button is visible.
        
        Returns:
            True if upgrade shop button found, False otherwise
        """
        try:
            flag = self._match_template_helper(
                ['templates', TemplateConfig.TEMPLATES["upgrade_shop"]],
                mode="BGR",
                check=True
            )
            
            result = flag is True if isinstance(flag, bool) else False
            logger.debug(f"Upgrade shop found: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error finding upgrade shop: {e}")
            return False

    def find_upgrade_shop_elements(self) -> bool:
        """
        Detect shop elements based on game map type.
        
        Returns:
            True if shop elements found, False otherwise
        """
        try:
            if self.__map == "POTION":
                template_name = TemplateConfig.TEMPLATES["coin_potion_shop"]
            else:
                template_name = TemplateConfig.TEMPLATES["coin_shop"]
            
            flag = self._match_template_helper(
                ['templates', template_name],
                mode="BGR",
                threshold=TemplateConfig.THRESHOLDS["coin_shop"],
                check=True
            )
            
            result = flag is True if isinstance(flag, bool) else False
            logger.debug(f"Shop elements found: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error finding shop elements: {e}")
            return False

    def find_open_button(self) -> bool:
        """
        Detect open map button.
        
        Returns:
            True if open button found, False otherwise
        """
        try:
            flag = self._match_template_helper(
                ['templates', TemplateConfig.TEMPLATES["open_button"]],
                check=True
            )
            
            result = flag is True if isinstance(flag, bool) else False
            logger.debug(f"Open button found: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error finding open button: {e}")
            return False

    def find_finish_button(self) -> bool:
        """
        Detect level finish button.
        
        Returns:
            True if finish button found, False otherwise
        """
        try:
            flag = self._match_template_helper(
                ['templates', TemplateConfig.TEMPLATES["finish_button"]],
                mode="BGR",
                check=True
            )
            
            result = flag is True if isinstance(flag, bool) else False
            logger.debug(f"Finish button found: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error finding finish button: {e}")
            return False

    def check_max_swipe(self, mode: str = "top") -> Optional[bool]:
        """
        Check if screen has reached maximum swipe boundary.
        
        Args:
            mode: "top" or "bottom" region to check
        
        Returns:
            True if at boundary, False if not, None on error
        """
        try:
            # Get crop region coordinates
            left = SwipeConfig.SWIPE_TOP_REGION["left"] * self.__adb.scale_x
            top = SwipeConfig.SWIPE_TOP_REGION["top"] * self.__adb.scale_y
            right = SwipeConfig.SWIPE_TOP_REGION["right"] * self.__adb.scale_x
            bottom = SwipeConfig.SWIPE_TOP_REGION["bottom"] * self.__adb.scale_y
            
            # Load reference image
            if mode == "top":
                img1_path = os.path.join(BASE_DIR, 'check_swipe.png')
            else:
                top = SwipeConfig.SWIPE_BOTTOM_REGION["top"] * self.__adb.scale_y
                bottom = SwipeConfig.SWIPE_BOTTOM_REGION["bottom"] * self.__adb.scale_y
                img1_path = os.path.join(BASE_DIR, 'check_swipe_bottom.png')
            
            img1 = cv2.imread(img1_path)
            
            if img1 is None:
                logger.warning(f"Reference image not found: {img1_path}")
                return None
            
            # Crop current screen
            cropped_img = self.__adb.crop_screen((left, top, right, bottom))
            
            if cropped_img is not None:
                img2 = cv2.cvtColor(cropped_img, cv2.COLOR_RGBA2BGR)
                
                if check_same_images(img1, img2):
                    logger.debug(f"Max swipe reached ({mode})")
                    return True
                else:
                    return False
            else:
                logger.error("Failed to crop screen for swipe check")
                return None
        
        except Exception as e:
            logger.error(f"Error checking max swipe: {e}")
            return None
