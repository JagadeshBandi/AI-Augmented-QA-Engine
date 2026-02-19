"""
ARES Complete Repository Dashboard
Shows entire repo structure, real-time activity, and system status
"""

import streamlit as st
import os
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np

# Page config
st.set_page_config(
    page_title="ARES Complete Repository Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("ARES: Complete Repository Dashboard")
st.markdown("---")

# Sidebar controls
st.sidebar.header("Repository Controls")

# Real-time refresh
auto_refresh = st.sidebar.checkbox("Auto Refresh (5s)", value=True)
refresh_interval = 5 if auto_refresh else 0

# Action buttons
if st.sidebar.button("Run AI Demo"):
    st.sidebar.info("Running AI Healing Demo...")
    try:
        result = subprocess.run(['python3', 'demo_healing.py'], 
                              capture_output=True, text=True, cwd='.')
        st.sidebar.success("Demo completed!")
        st.session_state.demo_output = result.stdout
        st.session_state.demo_error = result.stderr
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")

if st.sidebar.button("Run Tests"):
    st.sidebar.info("Running test suite...")
    try:
        result = subprocess.run(['python3', '-m', 'pytest', 'tests/', '-v'], 
                              capture_output=True, text=True, cwd='.')
        st.session_state.test_output = result.stdout
        st.session_state.test_error = result.stderr
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")

if st.sidebar.button("Generate Visual Evidence"):
    st.sidebar.info("Generating visual evidence...")
    try:
        # Create demo scene
        scene = np.ones((400, 600, 3), dtype=np.uint8) * 240
        cv2.rectangle(scene, (50, 50), (550, 350), (255, 255, 255), -1)
        cv2.rectangle(scene, (50, 50), (550, 350), (200, 200, 200), 2)
        
        button_x, button_y = 250, 200
        button_w, button_h = 100, 40
        cv2.rectangle(scene, (button_x, button_y), (button_x + button_w, button_y + button_h), (66, 133, 244), -1)
        cv2.putText(scene, "Login", (button_x + 25, button_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imwrite("repo_demo_scene.png", scene)
        
        # Test AI healing
        from src.model.healing import VisualHealer
        healer = VisualHealer(threshold=0.8)
        coords = healer.find_element_visually("repo_demo_scene.png", "assets/templates/login_button.png")
        
        if coords:
            cv2.circle(scene, coords, 20, (0, 255, 0), 3)
            cv2.putText(scene, "AI Found Here!", (coords[0]-60, coords[1]-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imwrite("repo_demo_result.png", scene)
            st.sidebar.success(f"AI found element at: {coords}")
        else:
            st.sidebar.error("AI could not locate element")
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Repository Structure")
    
    def get_repo_tree():
        """Get complete repository structure"""
        repo_path = "."
        tree = {}
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and cache
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            level = root.replace(repo_path, '').count(os.sep)
            indent = ' ' * 2 * level
            rel_path = os.path.relpath(root, repo_path)
            
            if rel_path != '.':
                tree[rel_path] = {
                    'type': 'directory',
                    'files': [f for f in files if not f.startswith('.') and not f.endswith('.pyc')]
                }
            else:
                tree['root'] = {
                    'type': 'directory',
                    'files': [f for f in files if not f.startswith('.') and not f.endswith('.pyc')]
                }
        
        return tree
    
    repo_tree = get_repo_tree()
    
    # Display repository structure
    for path, info in sorted(repo_tree.items()):
        if path == 'root':
            st.write(f"Directory: **ARES Root Directory**")
        else:
            st.write(f"Directory: **{path}/**")
        
        if info['files']:
            for file in sorted(info['files']):
                file_path = os.path.join(path, file) if path != 'root' else file
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                st.write(f"   File: {file} ({file_size:,} bytes)")
        st.write("")
    
    # Repository statistics
    st.header("Repository Statistics")
    
    def get_repo_stats():
        """Get comprehensive repository statistics"""
        stats = {
            'total_files': 0,
            'python_files': 0,
            'markdown_files': 0,
            'yaml_files': 0,
            'total_lines': 0,
            'total_size': 0
        }
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if not file.startswith('.') and not file.endswith('.pyc'):
                    file_path = os.path.join(root, file)
                    stats['total_files'] += 1
                    stats['total_size'] += os.path.getsize(file_path)
                    
                    if file.endswith('.py'):
                        stats['python_files'] += 1
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                stats['total_lines'] += len(f.readlines())
                        except:
                            pass
                    elif file.endswith('.md'):
                        stats['markdown_files'] += 1
                    elif file.endswith(('.yaml', '.yml')):
                        stats['yaml_files'] += 1
        
        return stats
    
    repo_stats = get_repo_stats()
    
    col1_1, col1_2, col1_3 = st.columns(3)
    with col1_1:
        st.metric("Total Files", repo_stats['total_files'])
        st.metric("Python Files", repo_stats['python_files'])
    with col1_2:
        st.metric("Total Lines", f"{repo_stats['total_lines']:,}")
        st.metric("Markdown Files", repo_stats['markdown_files'])
    with col1_3:
        st.metric("Total Size", f"{repo_stats['total_size']//1024:,} KB")
        st.metric("Config Files", repo_stats['yaml_files'])

with col2:
    st.header("Real-time Activity")
    
    # System status
    st.subheader("System Status")
    
    def check_component_status():
        """Check status of all ARES components"""
        components = {}
        
        # Check AI components
        try:
            from src.model.healing import VisualHealer
            components['VisualHealer'] = 'Active'
        except:
            components['VisualHealer'] = 'Error'
        
        try:
            from src.pages.base_page import BasePage
            components['BasePage'] = 'Active'
        except:
            components['BasePage'] = 'Error'
        
        try:
            from src.model.advanced_vision_healer import AdvancedVisionHealer
            components['AdvancedVisionHealer'] = 'Active'
        except:
            components['AdvancedVisionHealer'] = 'Error'
        
        try:
            from src.model.risk_predictor import RiskPredictor
            components['RiskPredictor'] = 'Active'
        except:
            components['RiskPredictor'] = 'Error'
        
        return components
    
    component_status = check_component_status()
    
    for component, status in component_status.items():
        st.write(f"{status} {component}")
    
    # Recent activity log
    st.subheader("Activity Log")
    
    if 'demo_output' in st.session_state:
        st.success("AI Demo Completed")
        with st.expander("View Demo Output"):
            st.code(st.session_state.demo_output)
    
    if 'test_output' in st.session_state:
        st.info("Test Suite Completed")
        with st.expander("View Test Results"):
            st.code(st.session_state.test_output)
    
    # Current time
    st.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Visual Evidence Section
st.markdown("---")
st.header("Visual Evidence")

col2_1, col2_2 = st.columns(2)

with col2_1:
    st.subheader("AI Visual Input")
    if os.path.exists("repo_demo_scene.png"):
        st.image("repo_demo_scene.png", caption="AI Visual Input - What AI Sees", width=400)
    else:
        st.info("Click 'Generate Visual Evidence' to see AI input")

with col2_2:
    st.subheader("AI Healing Result")
    if os.path.exists("repo_demo_result.png"):
        st.image("repo_demo_result.png", caption="AI Healing Result - Element Found", width=400)
    else:
        st.info("Click 'Generate Visual Evidence' to see AI results")

# File Content Viewer
st.markdown("---")
st.header("File Content Viewer")

# File selector
all_files = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    for file in files:
        if not file.startswith('.') and not file.endswith('.pyc'):
            file_path = os.path.join(root, file)
            all_files.append(file_path)

selected_file = st.selectbox("Select file to view:", sorted(all_files))

if selected_file:
    try:
        with open(selected_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        st.subheader(f"Content: {selected_file}")
        
        # Show first 50 lines by default
        lines = content.split('\n')
        show_all = st.checkbox("Show all lines", value=False)
        
        if show_all:
            st.code(content, language='python' if selected_file.endswith('.py') else None)
        else:
            preview_lines = 50
            st.code('\n'.join(lines[:preview_lines]), 
                   language='python' if selected_file.endswith('.py') else None)
            
            if len(lines) > preview_lines:
                st.info(f"Showing first {preview_lines} of {len(lines)} lines. Check 'Show all lines' to see complete file.")
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")

# Auto refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("**ARES Complete Repository Dashboard** - Real-time repository monitoring and AI system status")
