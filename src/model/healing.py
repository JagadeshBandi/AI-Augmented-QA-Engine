import cv2
import numpy as np

class VisualHealer:
    """
    Advanced AI Implementation:
    Uses Template Matching to find UI elements when DOM selectors fail.
    """
    def __init__(self, threshold=0.8):
        self.threshold = threshold

    def find_element_visually(self, scene_path, template_path):
        # Load the screenshot and the 'target' icon/button
        scene = cv2.imread(scene_path)
        template = cv2.imread(template_path)

        # Perform Match Template (Standard Robotic Vision technique)
        result = cv2.matchTemplate(scene, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= self.threshold:
            # Return the center coordinates of the found element
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)

        return None