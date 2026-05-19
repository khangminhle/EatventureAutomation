"""Image processing utilities for template matching and image comparison."""

import cv2
import numpy as np
from sklearn.cluster import DBSCAN


def resize_template(img: np.ndarray, scale_x: float = 1.0, scale_y: float = 1.0) -> np.ndarray:
    """
    Resize template image based on scale factors.
    
    Args:
        img: Input image
        scale_x: X-axis scale factor
        scale_y: Y-axis scale factor
    
    Returns:
        Resized image, or original if scale is 1.0
    """
    if scale_x == 1.0 and scale_y == 1.0:
        return img
    
    return cv2.resize(img, None, fx=scale_x, fy=scale_y, interpolation=cv2.INTER_AREA)


def check_same_images(img1: np.ndarray, img2: np.ndarray) -> bool:
    """
    Compare two images for exact similarity.
    
    Args:
        img1: First image (BGR)
        img2: Second image (BGR)
    
    Returns:
        True if images are identical, False otherwise
    """
    try:
        if img1.shape != img2.shape:
            return False
        
        diff = cv2.absdiff(img1, img2)
        non_zero_count = np.count_nonzero(diff)
        
        if non_zero_count == 0:
            print("Images are identical")
            return True
        else:
            print("Images are different")
            return False
    except Exception as e:
        print(f"Error in check_same_images: {e}")
        return False


def find_points_match_template(
    img: np.ndarray,
    template: np.ndarray,
    threshold: float = 0.8,
    check: bool = False
) -> bool | list[tuple[int, int]]:
    """
    Find matching template locations in image using template matching.
    
    Args:
        img: Input screenshot image
        template: Template image to match
        threshold: Matching confidence threshold (0.0-1.0)
        check: If True, return boolean; if False, return list of points
    
    Returns:
        Boolean if check=True, or list of (x, y) center coordinates
    """
    try:
        if template is None or img is None:
            return False if check else []
        
        w, h = template.shape[1], template.shape[0]
        
        # Perform template matching
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        
        # Find all locations matching threshold
        loc = np.where(res >= threshold)
        
        # Return check result
        if check:
            return len(loc[0]) > 0
        
        # Calculate center points
        points = []
        for pt in zip(*loc[::-1]):
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            points.append((center_x, center_y))
        
        # Cluster nearby points
        if len(points) > 0:
            points = clustering_centers(points)
        
        return points
    
    except Exception as e:
        print(f"Error in find_points_match_template: {e}")
        return False if check else []


def clustering_centers(raw_points: list[tuple[int, int]], distance: int = 20) -> list[tuple[int, int]]:
    """
    Cluster nearby points to reduce duplicates using DBSCAN.
    
    Args:
        raw_points: Raw coordinate list from template matching
        distance: Cluster radius in pixels (default 20)
    
    Returns:
        List of clustered center coordinates
    """
    if not raw_points:
        return []
    
    try:
        # Convert to numpy array
        data = np.array(raw_points)
        
        # DBSCAN clustering
        # eps: maximum distance between points in cluster
        # min_samples: 1 to avoid missing any buttons
        model = DBSCAN(eps=distance, min_samples=1).fit(data)
        labels = model.labels_
        
        centers = []
        
        # Calculate center of each cluster
        for label in set(labels):
            if label == -1:
                continue  # Skip noise
            
            cluster_points = data[labels == label]
            center_x = int(np.mean(cluster_points[:, 0]))
            center_y = int(np.mean(cluster_points[:, 1]))
            centers.append((center_x, center_y))
        
        return centers
    
    except Exception as e:
        print(f"Error in clustering_centers: {e}")
        return raw_points
