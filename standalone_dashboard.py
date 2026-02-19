"""
ARES AI Dashboard - Standalone UI Demo
Shows what the AI interface looks like without pandas dependency
"""

import streamlit as st
import cv2
import numpy as np
import os
from src.model.healing import VisualHealer

def main():
    # Page Config
    st.set_page_config(page_title="ARES AI Dashboard", layout="wide")

    st.title("ARES: AI-Augmented QA Command Center")
    st.markdown("---")

    # Sidebar for Control
    st.sidebar.header("Execution Control")
    env = st.sidebar.selectbox("Environment", ["Staging", "Production", "UAT"])
    
    st.sidebar.markdown("### AI Controls")
    threshold = st.sidebar.slider("AI Confidence Threshold", 0.5, 1.0, 0.8, 0.05)
    healing_mode = st.sidebar.selectbox("Healing Mode", ["Visual Only", "DOM + Visual", "Multi-Modal"])

    if st.sidebar.button("Run AI Healing Demo"):
        st.sidebar.info("Executing AI Vision Recovery...")
        
        # Run the demo
        try:
            # Create demo scene
            scene = np.ones((400, 600, 3), dtype=np.uint8) * 240
            cv2.rectangle(scene, (50, 50), (550, 350), (255, 255, 255), -1)
            cv2.rectangle(scene, (50, 50), (550, 350), (200, 200, 200), 2)
            
            button_x, button_y = 250, 200
            button_w, button_h = 100, 40
            cv2.rectangle(scene, (button_x, button_y), (button_x + button_w, button_y + button_h), (66, 133, 244), -1)
            cv2.putText(scene, "Login", (button_x + 25, button_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imwrite("demo_scene_ui.png", scene)
            
            # Test AI healing
            healer = VisualHealer(threshold=threshold)
            coords = healer.find_element_visually("demo_scene_ui.png", "assets/templates/login_button.png")
            
            if coords:
                st.sidebar.success(f"AI found element at: {coords}")
                # Draw result
                cv2.circle(scene, coords, 20, (0, 255, 0), 3)
                cv2.putText(scene, "AI Found Here!", (coords[0]-60, coords[1]-30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.imwrite("demo_result_ui.png", scene)
            else:
                st.sidebar.error("AI could not locate element")
                
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")

    # Main Dashboard Content
    st.header("AI Vision Analytics")

    # Predictive Analytics Section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Predictive Defect Analytics")
        
        # Simple chart data
        modules = ['Login', 'Payments', 'User Profile', 'Search']
        failure_rates = [12, 85, 5, 22]
        
        # Display as a simple bar chart
        for module, rate in zip(modules, failure_rates):
            color = "HIGH" if rate > 50 else "MEDIUM" if rate > 20 else "LOW"
            st.write(f"{color} **{module}**: {rate}% failure risk")
            
            # Progress bar
            st.progress(rate/100, text=f"{rate}%")

    with col2:
        st.subheader("System Health Metrics")
        
        # Metrics
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            st.metric(label="System Health", value="88%", delta="-2%")
            st.metric(label="Healing Success", value="95%", delta="+5%")
        with col2_2:
            st.metric(label="Avg Healing Time", value="180ms", delta="-20ms")
            st.metric(label="Elements Healed", value="127", delta="+12")
        
        st.write("**AI Vision Insights:**")
        st.success("Last run: 4 locators healed automatically")
        st.info("OpenCV template matching active")
        st.warning("High risk area: Payments module")

    # Visual Evidence Section
    st.markdown("---")
    st.subheader("AI Visual Recovery Evidence")

    if os.path.exists("demo_scene_ui.png"):
        st.image("demo_scene_ui.png", caption="AI Visual Input - What the AI Sees", width=600)
    else:
        st.info("Run the demo to see AI visual input")

    if os.path.exists("demo_result_ui.png"):
        st.image("demo_result_ui.png", caption="AI Healing Result - Element Located", width=600)
    else:
        st.info("Run the demo to see AI healing results")

    # AI Engine Status
    st.markdown("---")
    st.subheader("AI Engine Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Core AI")
        st.info("OpenCV: Active")
        st.info("Template Matching: Ready")
        st.info("Confidence: 0.8")

    with col2:
        st.markdown("### Healing System")
        st.success("VisualHealer: Operational")
        st.success("Coordinate Mapping: Working")
        st.success("Pixel Accuracy: 100%")

    with col3:
        st.markdown("### Reliability")
        st.warning("Self-Healing: Enabled")
        st.warning("Fallback Mode: Active")
        st.warning("Recovery Speed: <200ms")

    # Performance Metrics Table
    st.markdown("---")
    st.subheader("Performance Metrics")

    # Create metrics table
    metrics = [
        ("Healing Success Rate", "95%", "↑ 5% from baseline"),
        ("Execution Speed", "180ms", "↓ 20ms optimized"),
        ("False Positive Rate", "5%", "↓ 3% improvement"),
        ("Coverage Accuracy", "95%", "↑ 15% with AI"),
        ("Test Maintenance", "15%", "↓ 25% time saved"),
        ("Flaky Test Rate", "3%", "↓ 15% reduction")
    ]

    for metric, value, change in metrics:
        col1, col2, col3 = st.columns([3, 1, 2])
        with col1:
            st.write(f"**{metric}**")
        with col2:
            st.write(f"`{value}`")
        with col3:
            st.write(f"{change}")

    # Real-time Log Section
    st.markdown("---")
    st.subheader("AI Activity Log")

    log_entries = [
        ("2024-02-19 14:30:15", "INFO", "AI VisualHealer initialized with threshold 0.8"),
        ("2024-02-19 14:30:16", "INFO", "Template matching started for login_button.png"),
        ("2024-02-19 14:30:16", "SUCCESS", "Element located at coordinates (300, 220)"),
        ("2024-02-19 14:30:17", "INFO", "Coordinate mapping completed successfully"),
        ("2024-02-19 14:30:17", "SUCCESS", "Self-healing completed in 180ms")
    ]

    for timestamp, level, message in log_entries:
        if level == "SUCCESS":
            st.success(f"`{timestamp}` - {message}")
        elif level == "INFO":
            st.info(f"`{timestamp}` - {message}")
        else:
            st.error(f"`{timestamp}` - {message}")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        **ARES AI-Augmented QA Engine** - Next-Generation Test Automation with Computer Vision
        
        *Transforming Test Automation from Manual Scripting to Intelligent Autonomous Systems*
        """
    )

if __name__ == "__main__":
    main()
