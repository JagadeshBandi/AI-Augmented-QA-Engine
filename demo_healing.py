#!/usr/bin/env python3
"""
Demo of AI-Powered Test Healing without browser dependencies
Shows the core logic of visual element recovery
"""

import cv2
import numpy as np
import os
from src.model.healing import VisualHealer

def create_demo_images():
    """Create demo images to simulate the healing process"""
    
    # Create a simple "scene" (what the AI sees)
    scene = np.ones((400, 600, 3), dtype=np.uint8) * 240  # Light gray background
    
    # Add some UI elements
    cv2.rectangle(scene, (50, 50), (550, 350), (255, 255, 255), -1)  # White panel
    cv2.rectangle(scene, (50, 50), (550, 350), (200, 200, 200), 2)   # Border
    
    # Add a "Login Button" 
    button_x, button_y = 250, 200
    button_w, button_h = 100, 40
    cv2.rectangle(scene, (button_x, button_y), (button_x + button_w, button_y + button_h), (66, 133, 244), -1)
    cv2.putText(scene, "Login", (button_x + 25, button_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Save the scene
    cv2.imwrite("demo_scene.png", scene)
    
    # Create the template (what we're looking for)
    template = scene[button_y:button_y+button_h, button_x:button_x+button_w]
    cv2.imwrite("assets/templates/login_button.png", template)
    
    print("   Demo images created:")
    print("   - demo_scene.png (what AI sees)")
    print("   - assets/templates/login_button.png (what AI looks for)")

def demo_ai_healing():
    """Demonstrate the AI healing process"""
    
    print("\n AI-Augmented QA Engine Demo")
    print("=" * 50)
    
    # Create demo images
    create_demo_images()
    
    # Initialize the AI healer
    healer = VisualHealer(threshold=0.8)
    
    print("\n Step 1: Simulating failed selector")
    print("   Selector '#broken-id-123' not found on page")
    print("   Triggering AI Vision Recovery...")
    
    print("\n Step 2: Taking screenshot of current state")
    print("   Screenshot saved as: demo_scene.png")
    
    print("\n Step 3: AI Visual Analysis")
    print("   Loading template: assets/templates/login_button.png")
    print("   Running OpenCV template matching...")
    
    # Run the visual healing
    coords = healer.find_element_visually("demo_scene.png", "assets/templates/login_button.png")
    
    if coords:
        print(f"\n SUCCESS! AI found the element at coordinates: {coords}")
        print(f"   Element center: X={coords[0]}, Y={coords[1]}")
        print("   AI would click at these coordinates")
        
        # Visual verification - draw a circle where found
        scene = cv2.imread("demo_scene.png")
        cv2.circle(scene, coords, 20, (0, 255, 0), 3)  # Green circle
        cv2.putText(scene, "AI Found Here!", (coords[0]-60, coords[1]-30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imwrite("demo_result.png", scene)
        print("    Result saved as: demo_result.png")
        
    else:
        print("\n AI could not find the element")
        print("   Manual intervention required")
    
    print("\n Demo Summary:")
    print("   - Framework attempted normal selector first")
    print("   - Failed selector triggered AI recovery")
    print("   - OpenCV template matching found the element")
    print("   - Test automation continues successfully")
    
    # Cleanup
    if os.path.exists("demo_scene.png"):
        os.remove("demo_scene.png")
    if os.path.exists("demo_result.png"):
        os.remove("demo_result.png")

if __name__ == "__main__":
    demo_ai_healing()
