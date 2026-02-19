"""
Computer Vision Self-Healing System for ARES QA Engine
Advanced robotic vision layer for UI element recovery using OpenCV
"""

import os
import cv2
import numpy as np
import logging
import time
from typing import Tuple, Optional, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import json

from playwright.sync_api import Page, Locator


@dataclass
class VisionHealingResult:
    """Result of vision healing operation"""
    success: bool
    coordinates: Optional[Tuple[int, int]]
    confidence: float
    method_used: str
    healing_time: float
    element_type: str
    error_message: Optional[str] = None
    fallback_used: bool = False


@dataclass
class ElementTemplate:
    """Template for visual element matching"""
    name: str
    template_path: str
    threshold: float
    element_type: str
    fallback_selectors: List[str]
    description: str


class VisionHealer:
    """
    Advanced Computer Vision healing system
    Uses OpenCV for template matching and visual element recovery
    """
    
    def __init__(self, template_dir: str = "assets/templates", threshold: float = 0.8):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        self.threshold = threshold
        self.logger = logging.getLogger(__name__)
        
        # Healing statistics
        self.healing_stats = {
            "total_attempts": 0,
            "successful_healings": 0,
            "methods_used": {},
            "average_confidence": 0.0,
            "average_healing_time": 0.0
        }
        
        # Element templates
        self.templates = self._load_templates()
        
        # OpenCV methods for template matching
        self.matching_methods = {
            'TM_CCOEFF': cv2.TM_CCOEFF,
            'TM_CCOEFF_NORMED': cv2.TM_CCOEFF_NORMED,
            'TM_CCORR': cv2.TM_CCORR,
            'TM_CCORR_NORMED': cv2.TM_CCORR_NORMED,
            'TM_SQDIFF': cv2.TM_SQDIFF,
            'TM_SQDIFF_NORMED': cv2.TM_SQDIFF_NORMED
        }
        
        # Best methods for different element types
        self.preferred_methods = {
            'button': ['TM_CCOEFF_NORMED', 'TM_CCORR_NORMED'],
            'input': ['TM_SQDIFF_NORMED', 'TM_CCOEFF_NORMED'],
            'link': ['TM_CCOEFF_NORMED', 'TM_CCORR_NORMED'],
            'image': ['TM_CCORR_NORMED', 'TM_CCOEFF_NORMED'],
            'default': ['TM_CCOEFF_NORMED']
        }
        
        # Initialize default templates if they don't exist
        self._create_default_templates()
    
    def _load_templates(self) -> Dict[str, ElementTemplate]:
        """Load element templates from configuration"""
        templates = {}
        
        # Default template configuration
        default_templates = {
            'login_button': ElementTemplate(
                name='login_button',
                template_path='login_button.png',
                threshold=0.8,
                element_type='button',
                fallback_selectors=[
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Login")',
                    'button:has-text("Sign In")',
                    '[data-testid="login-button"]'
                ],
                description='Login/Sign In button'
            ),
            'username_field': ElementTemplate(
                name='username_field',
                template_path='username_field.png',
                threshold=0.7,
                element_type='input',
                fallback_selectors=[
                    'input[name="username"]',
                    'input[type="email"]',
                    'input[placeholder*="email"]',
                    'input[placeholder*="username"]',
                    '[data-testid="username"]'
                ],
                description='Username/Email input field'
            ),
            'password_field': ElementTemplate(
                name='password_field',
                template_path='password_field.png',
                threshold=0.7,
                element_type='input',
                fallback_selectors=[
                    'input[name="password"]',
                    'input[type="password"]',
                    '[data-testid="password"]'
                ],
                description='Password input field'
            ),
            'submit_button': ElementTemplate(
                name='submit_button',
                template_path='submit_button.png',
                threshold=0.8,
                element_type='button',
                fallback_selectors=[
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Submit")',
                    'button:has-text("Continue")'
                ],
                description='Generic submit button'
            ),
            'search_button': ElementTemplate(
                name='search_button',
                template_path='search_button.png',
                threshold=0.75,
                element_type='button',
                fallback_selectors=[
                    'button:has-text("Search")',
                    'input[type="search"]',
                    '[data-testid="search"]'
                ],
                description='Search button/field'
            )
        }
        
        # Try to load custom templates from file
        template_config_file = self.template_dir / "templates.json"
        if template_config_file.exists():
            try:
                with open(template_config_file, 'r') as f:
                    custom_templates = json.load(f)
                
                for name, config in custom_templates.items():
                    templates[name] = ElementTemplate(**config)
                
                self.logger.info(f"Loaded {len(custom_templates)} custom templates")
            except Exception as e:
                self.logger.error(f"Failed to load custom templates: {e}")
        
        # Use default templates as fallback
        templates.update(default_templates)
        
        return templates
    
    def _create_default_templates(self):
        """Create placeholder templates if they don't exist"""
        for template_name, template in self.templates.items():
            template_path = self.template_dir / template.template_path
            
            if not template_path.exists():
                # Create a simple placeholder template
                placeholder = np.ones((100, 200, 3), dtype=np.uint8) * 255
                
                # Add some basic patterns based on element type
                if template.element_type == 'button':
                    cv2.rectangle(placeholder, (10, 10), (190, 90), (100, 100, 200), -1)
                    cv2.putText(placeholder, template.name, (20, 55), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                elif template.element_type == 'input':
                    cv2.rectangle(placeholder, (10, 30), (190, 70), (200, 200, 200), -1)
                    cv2.rectangle(placeholder, (10, 30), (190, 70), (100, 100, 100), 2)
                
                cv2.imwrite(str(template_path), placeholder)
                self.logger.info(f"Created placeholder template: {template_path}")
    
    def heal_element(self, page: Page, element_name: str, 
                     screenshot_path: Optional[str] = None) -> VisionHealingResult:
        """
        Main healing function - attempts to find and heal a failed element
        """
        start_time = time.time()
        self.healing_stats["total_attempts"] += 1
        
        try:
            # Get template for this element
            template = self.templates.get(element_name)
            if not template:
                return VisionHealingResult(
                    success=False,
                    coordinates=None,
                    confidence=0.0,
                    method_used="none",
                    healing_time=time.time() - start_time,
                    element_type="unknown",
                    error_message=f"No template found for element: {element_name}"
                )
            
            # Take screenshot if not provided
            if not screenshot_path:
                screenshot_path = f"temp_screenshot_{int(time.time())}.png"
                page.screenshot(path=screenshot_path)
            
            # Try template matching first
            result = self._template_matching_healing(screenshot_path, template, start_time)
            
            if result.success:
                self._update_stats(result)
                return result
            
            # Try advanced healing methods
            result = self._advanced_healing(screenshot_path, template, start_time)
            
            if result.success:
                self._update_stats(result)
                return result
            
            # Try fallback selectors
            result = self._fallback_selector_healing(page, template, start_time)
            
            self._update_stats(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Vision healing failed for {element_name}: {e}")
            return VisionHealingResult(
                success=False,
                coordinates=None,
                confidence=0.0,
                method_used="error",
                healing_time=time.time() - start_time,
                element_type="unknown",
                error_message=str(e)
            )
    
    def _template_matching_healing(self, screenshot_path: str, template: ElementTemplate, 
                                 start_time: float) -> VisionHealingResult:
        """Try to find element using template matching"""
        try:
            # Load screenshot and template
            screenshot = cv2.imread(screenshot_path)
            template_img = cv2.imread(str(self.template_dir / template.template_path))
            
            if screenshot is None or template_img is None:
                return VisionHealingResult(
                    success=False,
                    coordinates=None,
                    confidence=0.0,
                    method_used="template_matching",
                    healing_time=time.time() - start_time,
                    element_type=template.element_type,
                    error_message="Failed to load images"
                )
            
            # Get preferred methods for this element type
            methods = self.preferred_methods.get(template.element_type, self.preferred_methods['default'])
            
            best_match = None
            best_confidence = 0.0
            best_method = None
            
            # Try different template matching methods
            for method_name in methods:
                if method_name not in self.matching_methods:
                    continue
                
                try:
                    # Apply template matching
                    result = cv2.matchTemplate(screenshot, template_img, self.matching_methods[method_name])
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    # For SQDIFF and SQDIFF_NORMED, lower values are better
                    if method_name in ['TM_SQDIFF', 'TM_SQDIFF_NORMED']:
                        confidence = 1.0 - (min_val / 255.0) if min_val < 255 else 0.0
                        location = min_loc
                    else:
                        confidence = max_val / 255.0
                        location = max_loc
                    
                    # Check if this is the best match so far
                    if confidence > best_confidence and confidence >= template.threshold:
                        best_confidence = confidence
                        best_match = location
                        best_method = method_name
                
                except Exception as e:
                    self.logger.warning(f"Template matching method {method_name} failed: {e}")
                    continue
            
            if best_match:
                # Calculate center coordinates
                template_h, template_w = template_img.shape[:2]
                center_x = best_match[0] + template_w // 2
                center_y = best_match[1] + template_h // 2
                
                return VisionHealingResult(
                    success=True,
                    coordinates=(center_x, center_y),
                    confidence=best_confidence,
                    method_used=f"template_matching_{best_method}",
                    healing_time=time.time() - start_time,
                    element_type=template.element_type
                )
            
            return VisionHealingResult(
                success=False,
                coordinates=None,
                confidence=best_confidence,
                method_used="template_matching",
                healing_time=time.time() - start_time,
                element_type=template.element_type,
                error_message=f"No match found above threshold {template.threshold}"
            )
            
        except Exception as e:
            self.logger.error(f"Template matching healing failed: {e}")
            return VisionHealingResult(
                success=False,
                coordinates=None,
                confidence=0.0,
                method_used="template_matching",
                healing_time=time.time() - start_time,
                element_type=template.element_type,
                error_message=str(e)
            )
    
    def _advanced_healing(self, screenshot_path: str, template: ElementTemplate, 
                         start_time: float) -> VisionHealingResult:
        """Advanced healing using multiple computer vision techniques"""
        try:
            screenshot = cv2.imread(screenshot_path)
            if screenshot is None:
                return VisionHealingResult(
                    success=False,
                    coordinates=None,
                    confidence=0.0,
                    method_used="advanced",
                    healing_time=time.time() - start_time,
                    element_type=template.element_type,
                    error_message="Failed to load screenshot"
                )
            
            # Convert to different color spaces for better matching
            methods_tried = []
            
            # Try grayscale matching
            gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template_img = cv2.imread(str(self.template_dir / template.template_path), cv2.IMREAD_GRAYSCALE)
            
            if template_img is not None:
                try:
                    result = cv2.matchTemplate(gray_screenshot, template_img, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val >= template.threshold * 0.9:  # Slightly lower threshold for grayscale
                        template_h, template_w = template_img.shape[:2]
                        center_x = max_loc[0] + template_w // 2
                        center_y = max_loc[1] + template_h // 2
                        
                        return VisionHealingResult(
                            success=True,
                            coordinates=(center_x, center_y),
                            confidence=max_val,
                            method_used="grayscale_matching",
                            healing_time=time.time() - start_time,
                            element_type=template.element_type
                        )
                
                except Exception as e:
                    methods_tried.append(f"grayscale: {e}")
            
            # Try edge detection based matching
            try:
                edges = cv2.Canny(gray_screenshot, 50, 150)
                template_edges = cv2.Canny(template_img, 50, 150) if template_img is not None else None
                
                if template_edges is not None:
                    result = cv2.matchTemplate(edges, template_edges, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val >= template.threshold * 0.8:
                        template_h, template_w = template_edges.shape[:2]
                        center_x = max_loc[0] + template_w // 2
                        center_y = max_loc[1] + template_h // 2
                        
                        return VisionHealingResult(
                            success=True,
                            coordinates=(center_x, center_y),
                            confidence=max_val,
                            method_used="edge_detection",
                            healing_time=time.time() - start_time,
                            element_type=template.element_type
                        )
                
                methods_tried.append("edge_detection: no match")
            
            except Exception as e:
                methods_tried.append(f"edge_detection: {e}")
            
            # Try feature matching (ORB)
            try:
                orb = cv2.ORB_create()
                kp1, des1 = orb.detectAndCompute(gray_screenshot, None)
                kp2, des2 = orb.detectAndCompute(template_img, None)
                
                if des1 is not None and des2 is not None:
                    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                    matches = bf.match(des1, des2)
                    matches = sorted(matches, key=lambda x: x.distance)
                    
                    if len(matches) > 10:  # Need enough good matches
                        # Get coordinates of good matches
                        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches[:10]]).reshape(-1, 1, 2)
                        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches[:10]]).reshape(-1, 1, 2)
                        
                        # Calculate center of template matches
                        center_x = int(np.mean(dst_pts[:, 0, 0]))
                        center_y = int(np.mean(dst_pts[:, 0, 1]))
                        
                        confidence = len(matches) / min(len(kp1), len(kp2))
                        
                        return VisionHealingResult(
                            success=True,
                            coordinates=(center_x, center_y),
                            confidence=confidence,
                            method_used="feature_matching",
                            healing_time=time.time() - start_time,
                            element_type=template.element_type
                        )
                
                methods_tried.append("feature_matching: insufficient features")
            
            except Exception as e:
                methods_tried.append(f"feature_matching: {e}")
            
            return VisionHealingResult(
                success=False,
                coordinates=None,
                confidence=0.0,
                method_used="advanced",
                healing_time=time.time() - start_time,
                element_type=template.element_type,
                error_message=f"Advanced methods failed: {'; '.join(methods_tried)}"
            )
            
        except Exception as e:
            self.logger.error(f"Advanced healing failed: {e}")
            return VisionHealingResult(
                success=False,
                coordinates=None,
                confidence=0.0,
                method_used="advanced",
                healing_time=time.time() - start_time,
                element_type=template.element_type,
                error_message=str(e)
            )
    
    def _fallback_selector_healing(self, page: Page, template: ElementTemplate, 
                                 start_time: float) -> VisionHealingResult:
        """Fallback to traditional selectors with visual verification"""
        try:
            for selector in template.fallback_selectors:
                try:
                    element = page.locator(selector).first
                    
                    if element.count() > 0:
                        # Verify element is visible
                        if element.is_visible():
                            # Get bounding box
                            box = element.bounding_box()
                            if box:
                                center_x = box['x'] + box['width'] // 2
                                center_y = box['y'] + box['height'] // 2
                                
                                return VisionHealingResult(
                                    success=True,
                                    coordinates=(center_x, center_y),
                                    confidence=0.9,  # High confidence for visible elements
                                    method_used="fallback_selector",
                                    healing_time=time.time() - start_time,
                                    element_type=template.element_type,
                                    fallback_used=True
                                )
                
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            return VisionHealingResult(
                success=False,
                coordinates=None,
                confidence=0.0,
                method_used="fallback_selector",
                healing_time=time.time() - start_time,
                element_type=template.element_type,
                error_message="All fallback selectors failed",
                fallback_used=True
            )
            
        except Exception as e:
            self.logger.error(f"Fallback selector healing failed: {e}")
            return VisionHealingResult(
                success=False,
                coordinates=None,
                confidence=0.0,
                method_used="fallback_selector",
                healing_time=time.time() - start_time,
                element_type=template.element_type,
                error_message=str(e),
                fallback_used=True
            )
    
    def click_healed_element(self, page: Page, result: VisionHealingResult) -> bool:
        """Click on the healed element using coordinates"""
        if not result.success or result.coordinates is None:
            return False
        
        try:
            x, y = result.coordinates
            
            # Add some visual feedback (optional)
            page.mouse.move(x, y)
            page.wait_for_timeout(100)  # Small delay for visual feedback
            
            # Click the element
            page.mouse.click(x, y)
            
            self.logger.info(f"Successfully clicked healed element at ({x}, {y}) with confidence {result.confidence:.2f}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to click healed element: {e}")
            return False
    
    def type_healed_element(self, page: Page, result: VisionHealingResult, text: str) -> bool:
        """Type text into the healed element"""
        if not result.success or result.coordinates is None:
            return False
        
        try:
            x, y = result.coordinates
            
            # Click first to focus
            page.mouse.click(x, y)
            page.wait_for_timeout(100)
            
            # Type the text
            page.keyboard.type(text)
            
            self.logger.info(f"Successfully typed into healed element at ({x}, {y})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to type into healed element: {e}")
            return False
    
    def create_template_from_screenshot(self, page: Page, element_name: str, 
                                      selector: str, template_name: Optional[str] = None) -> bool:
        """Create a new template from a screenshot of an element"""
        try:
            # Find the element
            element = page.locator(selector).first
            if element.count() == 0:
                self.logger.error(f"Element not found for template creation: {selector}")
                return False
            
            # Get bounding box
            box = element.bounding_box()
            if not box:
                self.logger.error("Could not get element bounding box")
                return False
            
            # Take full page screenshot
            screenshot_path = f"temp_template_creation_{int(time.time())}.png"
            page.screenshot(path=screenshot_path)
            
            # Crop the element from the screenshot
            screenshot = cv2.imread(screenshot_path)
            if screenshot is None:
                self.logger.error("Failed to load screenshot")
                return False
            
            # Crop the element area
            element_img = screenshot[
                int(box['y']):int(box['y'] + box['height']),
                int(box['x']):int(box['x'] + box['width'])
            ]
            
            # Save the template
            final_template_name = template_name or element_name
            template_path = self.template_dir / f"{final_template_name}.png"
            cv2.imwrite(str(template_path), element_img)
            
            # Add to templates
            self.templates[final_template_name] = ElementTemplate(
                name=final_template_name,
                template_path=f"{final_template_name}.png",
                threshold=0.8,
                element_type="custom",
                fallback_selectors=[selector],
                description=f"Custom template created from {selector}"
            )
            
            # Clean up temporary screenshot
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            
            self.logger.info(f"Created template: {template_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create template: {e}")
            return False
    
    def _update_stats(self, result: VisionHealingResult):
        """Update healing statistics"""
        if result.success:
            self.healing_stats["successful_healings"] += 1
        
        method = result.method_used
        self.healing_stats["methods_used"][method] = self.healing_stats["methods_used"].get(method, 0) + 1
        
        # Update averages
        total_attempts = self.healing_stats["total_attempts"]
        successful = self.healing_stats["successful_healings"]
        
        if total_attempts > 0:
            self.healing_stats["average_confidence"] = (
                (self.healing_stats["average_confidence"] * (total_attempts - 1) + result.confidence) / total_attempts
            )
            self.healing_stats["average_healing_time"] = (
                (self.healing_stats["average_healing_time"] * (total_attempts - 1) + result.healing_time) / total_attempts
            )
    
    def get_healing_stats(self) -> Dict[str, Any]:
        """Get current healing statistics"""
        total_attempts = self.healing_stats["total_attempts"]
        
        return {
            **self.healing_stats,
            "success_rate": (self.healing_stats["successful_healings"] / total_attempts * 100) if total_attempts > 0 else 0,
            "total_templates": len(self.templates),
            "available_methods": list(self.matching_methods.keys())
        }
    
    def reset_stats(self):
        """Reset healing statistics"""
        self.healing_stats = {
            "total_attempts": 0,
            "successful_healings": 0,
            "methods_used": {},
            "average_confidence": 0.0,
            "average_healing_time": 0.0
        }
    
    def save_templates_config(self):
        """Save current templates configuration to file"""
        try:
            templates_config = {}
            for name, template in self.templates.items():
                templates_config[name] = {
                    'name': template.name,
                    'template_path': template.template_path,
                    'threshold': template.threshold,
                    'element_type': template.element_type,
                    'fallback_selectors': template.fallback_selectors,
                    'description': template.description
                }
            
            config_path = self.template_dir / "templates.json"
            with open(config_path, 'w') as f:
                json.dump(templates_config, f, indent=2)
            
            self.logger.info(f"Saved templates configuration to {config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save templates configuration: {e}")


# Global vision healer instance
_vision_healer_instance = None


def get_vision_healer() -> VisionHealer:
    """Get or create the global vision healer instance"""
    global _vision_healer_instance
    if _vision_healer_instance is None:
        _vision_healer_instance = VisionHealer()
    return _vision_healer_instance
