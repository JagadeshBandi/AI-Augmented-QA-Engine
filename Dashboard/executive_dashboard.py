"""
ARES Executive Dashboard
Advanced QualityOps dashboard with AI insights, robotic logs, and real-time monitoring
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio
import threading

# Set page config
st.set_page_config(
    page_title="ARES Executive Dashboard",
    page_icon="brain",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import ARES components
try:
    from src.model.predictor import get_defect_predictor
    from src.model.vision_healer import get_vision_healer
    from src.utils.metrics_collector import get_metrics_collector
    ARES_AVAILABLE = True
except ImportError:
    ARES_AVAILABLE = False
    st.warning("ARES components not available. Running in demo mode.")

# Custom CSS for terminal-style logs
st.markdown("""
<style>
.terminal {
    background-color: #1e1e1e;
    color: #00ff00;
    font-family: 'Courier New', monospace;
    padding: 15px;
    border-radius: 5px;
    font-size: 12px;
    line-height: 1.4;
    overflow-y: auto;
    max-height: 400px;
    white-space: pre-wrap;
}
.terminal .error { color: #ff4444; }
.terminal .warning { color: #ffaa00; }
.terminal .success { color: #44ff44; }
.terminal .info { color: #4444ff; }
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.metric-card h3 {
    margin: 0;
    font-size: 2.5em;
    font-weight: bold;
}
.metric-card p {
    margin: 5px 0 0 0;
    font-size: 1.1em;
    opacity: 0.9;
}
.ai-confidence-bar {
    height: 30px;
    background: #e0e0e0;
    border-radius: 15px;
    overflow: hidden;
    position: relative;
}
.ai-confidence-fill {
    height: 100%;
    background: linear-gradient(90deg, #ff4444, #ffaa00, #44ff44);
    transition: width 0.5s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
}
.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
}
.status-online { background-color: #44ff44; }
.status-offline { background-color: #ff4444; }
.status-warning { background-color: #ffaa00; }
</style>
""", unsafe_allow_html=True)


class ExecutiveDashboard:
    """Advanced Executive Dashboard with AI insights and robotic logs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.robotic_logs = []
        self.ai_predictions = []
        self.vision_healing_events = []
        self.system_metrics = {}
        
        # Initialize ARES components
        if ARES_AVAILABLE:
            self.predictor = get_defect_predictor()
            self.healer = get_vision_healer()
            self.metrics_collector = get_metrics_collector()
        
        # Dashboard state
        self.last_update = datetime.now()
        self.auto_refresh = True
        self.refresh_interval = 5  # seconds
    
    def render_header(self):
        """Render dashboard header with system status"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 10px; margin-bottom: 2rem; color: white;'>
            <h1 style='margin: 0; font-size: 2.5em; text-align: center;'>ARES Executive Dashboard</h1>
            <p style='margin: 10px 0 0 0; text-align: center; opacity: 0.9;'>
                AI-Augmented Quality Operations Platform | Real-time Monitoring & Predictive Analytics
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # System status indicators
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class='status-indicator status-online'></span>
            <span>AI Brain Online</span>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='status-indicator status-online'></span>
            <span>Vision System Active</span>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class='status-indicator status-online'></span>
            <span>Metrics Pipeline</span>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class='status-indicator status-warning'></span>
            <span>CI/CD Running</span>
            """, unsafe_allow_html=True)
    
    def render_ai_confidence_score(self):
        """Render AI confidence score with visual indicators"""
        st.subheader("AI Confidence Score")
        
        # Simulate AI confidence data
        ai_confidence = np.random.uniform(0.75, 0.98)
        confidence_level = "High" if ai_confidence > 0.9 else "Medium" if ai_confidence > 0.8 else "Low"
        
        # Confidence bar
        st.markdown(f"""
        <div class='ai-confidence-bar'>
            <div class='ai-confidence-fill' style='width: {ai_confidence * 100}%'>
                {ai_confidence:.1%} Confidence
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Confidence details
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Overall Confidence", f"{ai_confidence:.1%}")
        
        with col2:
            st.metric("Confidence Level", confidence_level)
        
        with col3:
            st.metric("Model Accuracy", f"{np.random.uniform(0.85, 0.95):.1%}")
        
        # AI Model Performance
        st.subheader("Model Performance Metrics")
        
        performance_data = {
            'Model': ['Random Forest', 'Gradient Boosting', 'Neural Network', 'Ensemble'],
            'Accuracy': [0.92, 0.89, 0.94, 0.96],
            'Precision': [0.91, 0.88, 0.93, 0.95],
            'Recall': [0.90, 0.87, 0.92, 0.94],
            'F1-Score': [0.90, 0.87, 0.92, 0.94]
        }
        
        df = pd.DataFrame(performance_data)
        st.dataframe(df, use_container_width=True)
        
        # Model comparison chart
        fig = go.Figure()
        
        for metric in ['Accuracy', 'Precision', 'Recall', 'F1-Score']:
            fig.add_trace(go.Bar(
                name=metric,
                x=df['Model'],
                y=df[metric],
                yaxis='y'
            ))
        
        fig.update_layout(
            title="AI Model Performance Comparison",
            xaxis_title="Model",
            yaxis_title="Score",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_robotic_logs(self):
        """Render terminal-style robotic interaction logs"""
        st.subheader("Robotic Interaction Logs")
        
        # Log controls
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("Clear Logs"):
                self.robotic_logs.clear()
        
        with col2:
            auto_scroll = st.checkbox("Auto Scroll", value=True)
        
        with col3:
            log_level = st.selectbox("Log Level", ["All", "Info", "Warning", "Error"])
        
        # Generate sample robotic logs
        if not self.robotic_logs or st.button("Generate Sample Logs"):
            self.generate_sample_logs()
        
        # Filter logs based on level
        filtered_logs = self.robotic_logs
        if log_level != "All":
            filtered_logs = [log for log in self.robotic_logs if log['level'].lower() == log_level.lower()]
        
        # Display logs in terminal style
        log_content = ""
        for log in filtered_logs[-50:]:  # Show last 50 logs
            timestamp = log['timestamp'].strftime("%H:%M:%S.%f")[:-3]
            level = log['level']
            message = log['message']
            
            css_class = level.lower()
            log_content += f'<span class="{css_class}">[{timestamp}] [{level}] {message}</span>\n'
        
        st.markdown(f"""
        <div class='terminal'>
            {log_content}
        </div>
        """, unsafe_allow_html=True)
        
        # Log statistics
        if self.robotic_logs:
            log_stats = {
                'Total': len(self.robotic_logs),
                'Info': len([l for l in self.robotic_logs if l['level'] == 'INFO']),
                'Warning': len([l for l in self.robotic_logs if l['level'] == 'WARNING']),
                'Error': len([l for l in self.robotic_logs if l['level'] == 'ERROR'])
            }
            
            st.write("**Log Statistics:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total", log_stats['Total'])
            with col2:
                st.metric("Info", log_stats['Info'])
            with col3:
                st.metric("Warnings", log_stats['Warning'])
            with col4:
                st.metric("Errors", log_stats['Error'])
    
    def generate_sample_logs(self):
        """Generate sample robotic interaction logs"""
        import random
        
        sample_messages = [
            ("INFO", "AI Brain initialized with 4 predictive models"),
            ("INFO", "Vision system calibrated - 15 templates loaded"),
            ("INFO", "Starting test execution pipeline"),
            ("INFO", "Analyzing git commits for risk prediction"),
            ("WARNING", "High risk detected in payment processing tests"),
            ("INFO", "Template matching initiated for login_button"),
            ("INFO", "Found login button at coordinates (245, 189) with 0.94 confidence"),
            ("INFO", "Executing click action using computer vision"),
            ("SUCCESS", "Login button clicked successfully"),
            ("INFO", "Typing credentials into healed input field"),
            ("WARNING", "Element selector failed, switching to vision healing"),
            ("INFO", "Edge detection algorithm applied"),
            ("INFO", "Element recovered using ORB feature matching"),
            ("SUCCESS", "Self-healing completed in 1.2s"),
            ("ERROR", "Template matching failed - threshold not met"),
            ("WARNING", "Fallback to traditional selectors"),
            ("INFO", "Metrics pushed to InfluxDB"),
            ("INFO", "AI prediction updated - risk score: 0.78"),
            ("SUCCESS", "Test session completed - 85% pass rate"),
            ("INFO", "Generating executive report"),
            ("INFO", "Quality score calculated: 87.3/100"),
            ("WARNING", "Flakiness detected in test_search_functionality"),
            ("INFO", "Performance benchmarks collected"),
            ("SUCCESS", "All systems operational")
        ]
        
        current_time = datetime.now()
        
        for i, (level, message) in enumerate(sample_messages):
            timestamp = current_time - timedelta(seconds=len(sample_messages) - i)
            self.robotic_logs.append({
                'timestamp': timestamp,
                'level': level,
                'message': message
            })
    
    def render_predictive_analytics(self):
        """Render predictive analytics dashboard"""
        st.subheader("Predictive Analytics")
        
        # Risk prediction for test suite
        if ARES_AVAILABLE:
            # Get real predictions
            test_names = [
                "test_login_functionality",
                "test_payment_processing", 
                "test_user_registration",
                "test_search_functionality",
                "test_api_endpoints",
                "test_ui_components"
            ]
            
            predictions = self.predictor.predict_batch_risks(test_names)
            summary = self.predictor.get_risk_summary(predictions)
        else:
            # Demo data
            predictions = self.generate_demo_predictions()
            summary = self.generate_demo_summary()
        
        # Risk summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("High Risk Tests", summary['risk_distribution']['critical'] + summary['risk_distribution']['high'])
        
        with col2:
            st.metric("Average Risk Score", f"{summary['average_risk_score']:.1%}")
        
        with col3:
            st.metric("Risk Trend", summary['risk_trend'].title())
        
        with col4:
            st.metric("Total Tests", summary['total_tests'])
        
        # Risk breakdown chart
        risk_data = summary['risk_distribution']
        fig = go.Figure(data=[
            go.Bar(
                x=list(risk_data.keys()),
                y=list(risk_data.values()),
                marker_color=['#ff4444', '#ffaa00', '#4444ff', '#44ff44']
            )
        ])
        
        fig.update_layout(
            title="Risk Distribution",
            xaxis_title="Risk Level",
            yaxis_title="Number of Tests",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # High risk tests details
        if summary['high_risk_tests']:
            st.subheader("High Risk Tests")
            
            high_risk_df = pd.DataFrame(summary['high_risk_tests'])
            st.dataframe(high_risk_df, use_container_width=True)
        
        # Recommendations
        if summary.get('recommendations'):
            st.subheader("AI Recommendations")
            for rec in summary['recommendations']:
                st.write(f"• {rec}")
    
    def generate_demo_predictions(self):
        """Generate demo predictions for testing"""
        from dataclasses import dataclass
        
        @dataclass
        class DemoPrediction:
            test_name: str
            risk_score: float
            risk_level: str
            confidence: float
            contributing_factors: List[str]
            recommended_actions: List[str]
            prediction_timestamp: datetime
        
        demo_predictions = [
            DemoPrediction(
                "test_login_functionality", 0.25, "low", 0.92,
                ["Recent changes minimal", "Stable history"],
                ["Standard execution", "Monitor performance"],
                datetime.now()
            ),
            DemoPrediction(
                "test_payment_processing", 0.87, "high", 0.89,
                ["Complex payment logic changed", "Multiple files modified"],
                ["Manual review required", "Additional testing"],
                datetime.now()
            ),
            DemoPrediction(
                "test_user_registration", 0.92, "critical", 0.95,
                ["Database schema changes", "Configuration files modified"],
                ["Urgent review needed", "Consider rollback"],
                datetime.now()
            ),
            DemoPrediction(
                "test_search_functionality", 0.34, "medium", 0.88,
                ["Minor UI changes", "Low complexity"],
                ["Standard testing", "Monitor closely"],
                datetime.now()
            ),
            DemoPrediction(
                "test_api_endpoints", 0.45, "medium", 0.91,
                ["API version bump", "Documentation updated"],
                ["Integration testing", "Performance monitoring"],
                datetime.now()
            ),
            DemoPrediction(
                "test_ui_components", 0.18, "low", 0.94,
                ["CSS changes only", "No logic modifications"],
                ["Standard execution", "Visual verification"],
                datetime.now()
            )
        ]
        
        return demo_predictions
    
    def generate_demo_summary(self):
        """Generate demo summary for testing"""
        return {
            "total_tests": 6,
            "risk_distribution": {"low": 2, "medium": 2, "high": 1, "critical": 1},
            "average_risk_score": 0.518,
            "high_risk_tests": [
                {
                    "test_name": "test_user_registration",
                    "risk_score": 0.92,
                    "risk_level": "critical",
                    "top_factors": ["Database schema changes", "Configuration files modified"]
                },
                {
                    "test_name": "test_payment_processing", 
                    "risk_score": 0.87,
                    "risk_level": "high",
                    "top_factors": ["Complex payment logic changed", "Multiple files modified"]
                }
            ],
            "risk_trend": "increasing",
            "recommendations": [
                "URGENT: 1 critical risk tests detected",
                "Consider running tests in priority order",
                "High overall risk - consider additional testing"
            ]
        }
    
    def render_vision_healing_stats(self):
        """Render vision healing statistics"""
        st.subheader("Vision Healing Statistics")
        
        if ARES_AVAILABLE:
            stats = self.healer.get_healing_stats()
        else:
            # Demo stats
            stats = {
                "total_attempts": 47,
                "successful_healings": 42,
                "success_rate": 89.4,
                "average_confidence": 0.87,
                "average_healing_time": 1.2,
                "methods_used": {
                    "template_matching_TM_CCOEFF_NORMED": 25,
                    "grayscale_matching": 8,
                    "fallback_selector": 6,
                    "edge_detection": 4,
                    "feature_matching": 2
                },
                "total_templates": 15,
                "available_methods": 6
            }
        
        # Success metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
        
        with col2:
            st.metric("Avg Confidence", f"{stats['average_confidence']:.1%}")
        
        with col3:
            st.metric("Avg Healing Time", f"{stats['average_healing_time']:.1f}s")
        
        with col4:
            st.metric("Total Attempts", stats['total_attempts'])
        
        # Methods usage chart
        if stats.get('methods_used'):
            methods_df = pd.DataFrame(
                list(stats['methods_used'].items()),
                columns=['Method', 'Usage Count']
            )
            
            fig = px.pie(
                methods_df,
                values='Usage Count',
                names='Method',
                title='Healing Methods Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Healing timeline
        st.subheader("Healing Timeline")
        
        # Generate demo timeline data
        timeline_data = []
        current_time = datetime.now()
        
        for i in range(20):
            timestamp = current_time - timedelta(minutes=i*5)
            success = np.random.choice([True, False], p=[0.85, 0.15])
            confidence = np.random.uniform(0.7, 0.98) if success else np.random.uniform(0.3, 0.7)
            
            timeline_data.append({
                'timestamp': timestamp,
                'success': success,
                'confidence': confidence,
                'method': np.random.choice(['template_matching', 'grayscale', 'fallback', 'edge_detection'])
            })
        
        timeline_df = pd.DataFrame(timeline_data)
        
        fig = go.Figure()
        
        # Add scatter plot for healing events
        fig.add_trace(go.Scatter(
            x=timeline_df['timestamp'],
            y=timeline_df['confidence'],
            mode='markers',
            marker=dict(
                color=timeline_df['success'].map({True: '#44ff44', False: '#ff4444'}),
                size=8,
                symbol=timeline_df['method'].map({
                    'template_matching': 'circle',
                    'grayscale': 'square',
                    'fallback': 'diamond',
                    'edge_detection': 'triangle'
                })
            ),
            text=timeline_df['method'],
            hovertemplate='Time: %{x}<br>Confidence: %{y:.2f}<br>Method: %{text}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Vision Healing Events Timeline",
            xaxis_title="Time",
            yaxis_title="Confidence Score",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_real_time_metrics(self):
        """Render real-time system metrics"""
        st.subheader("Real-time Metrics")
        
        # System metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CPU Usage
            cpu_usage = np.random.uniform(20, 80)
            st.metric("CPU Usage", f"{cpu_usage:.1f}%")
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = cpu_usage,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "CPU"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=200)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Memory Usage
            memory_usage = np.random.uniform(30, 70)
            st.metric("Memory Usage", f"{memory_usage:.1f}%")
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = memory_usage,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Memory"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ]
                }
            ))
            fig.update_layout(height=200)
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Test Execution Rate
            test_rate = np.random.uniform(5, 15)
            st.metric("Test Rate", f"{test_rate:.1f}/min")
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = test_rate,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Tests/min"},
                gauge = {
                    'axis': {'range': [None, 20]},
                    'bar': {'color': "purple"},
                    'steps': [
                        {'range': [0, 10], 'color': "lightgray"},
                        {'range': [10, 15], 'color': "yellow"},
                        {'range': [15, 20], 'color': "red"}
                    ]
                }
            ))
            fig.update_layout(height=200)
            st.plotly_chart(fig, use_container_width=True)
        
        # Real-time metrics timeline
        st.subheader("System Performance Timeline")
        
        # Generate time series data
        time_points = 50
        timestamps = [datetime.now() - timedelta(minutes=i) for i in range(time_points, 0, -1)]
        
        metrics_data = {
            'timestamp': timestamps,
            'cpu_usage': [np.random.uniform(20, 80) for _ in range(time_points)],
            'memory_usage': [np.random.uniform(30, 70) for _ in range(time_points)],
            'test_rate': [np.random.uniform(5, 15) for _ in range(time_points)],
            'error_rate': [np.random.uniform(0, 5) for _ in range(time_points)]
        }
        
        metrics_df = pd.DataFrame(metrics_data)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('CPU Usage', 'Memory Usage', 'Test Rate', 'Error Rate'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        fig.add_trace(go.Scatter(x=metrics_df['timestamp'], y=metrics_df['cpu_usage'], 
                              name='CPU Usage', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=metrics_df['timestamp'], y=metrics_df['memory_usage'], 
                              name='Memory Usage', line=dict(color='green')), row=1, col=2)
        fig.add_trace(go.Scatter(x=metrics_df['timestamp'], y=metrics_df['test_rate'], 
                              name='Test Rate', line=dict(color='purple')), row=2, col=1)
        fig.add_trace(go.Scatter(x=metrics_df['timestamp'], y=metrics_df['error_rate'], 
                              name='Error Rate', line=dict(color='red')), row=2, col=2)
        
        fig.update_layout(height=600, showlegend=False, title_text="Real-time System Metrics")
        st.plotly_chart(fig, use_container_width=True)
    
    def render_quality_score(self):
        """Render overall quality score"""
        st.subheader("Overall Quality Score")
        
        # Calculate quality score
        test_score = np.random.uniform(75, 95)
        security_score = np.random.uniform(80, 98)
        performance_score = np.random.uniform(70, 90)
        reliability_score = np.random.uniform(80, 95)
        
        overall_score = (test_score + security_score + performance_score + reliability_score) / 4
        
        # Main score display
        score_color = "#44ff44" if overall_score >= 90 else "#ffaa00" if overall_score >= 75 else "#ff4444"
        
        st.markdown(f"""
        <div style='text-align: center; padding: 2rem;'>
            <h1 style='font-size: 4em; color: {score_color}; margin: 0;'>{overall_score:.1f}</h1>
            <p style='font-size: 1.5em; color: #666; margin: 0;'>Overall Quality Score</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Component scores
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Test Quality", f"{test_score:.1f}")
        
        with col2:
            st.metric("Security", f"{security_score:.1f}")
        
        with col3:
            st.metric("Performance", f"{performance_score:.1f}")
        
        with col4:
            st.metric("Reliability", f"{reliability_score:.1f}")
        
        # Quality breakdown
        quality_data = {
            'Component': ['Test Quality', 'Security', 'Performance', 'Reliability'],
            'Score': [test_score, security_score, performance_score, reliability_score],
            'Weight': [0.3, 0.25, 0.25, 0.2]
        }
        
        quality_df = pd.DataFrame(quality_data)
        quality_df['Weighted Score'] = quality_df['Score'] * quality_df['Weight']
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=quality_df['Component'],
            y=quality_df['Score'],
            name='Score',
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Scatter(
            x=quality_df['Component'],
            y=quality_df['Weighted Score'],
            name='Weighted Score',
            mode='markers+lines',
            marker=dict(color='red', size=10),
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title="Quality Score Breakdown",
            xaxis_title="Component",
            yaxis_title="Score",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def run(self):
        """Main dashboard execution"""
        # Auto-refresh setup
        if self.auto_refresh:
            st_autorefresh = st.empty()
        
        # Render components
        self.render_header()
        
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "AI Brain", "Vision Healing", "Robotic Logs", 
            "Real-time Metrics", "Predictive Analytics", "Quality Score"
        ])
        
        with tab1:
            self.render_ai_confidence_score()
        
        with tab2:
            self.render_vision_healing_stats()
        
        with tab3:
            self.render_robotic_logs()
        
        with tab4:
            self.render_real_time_metrics()
        
        with tab5:
            self.render_predictive_analytics()
        
        with tab6:
            self.render_quality_score()
        
        # Auto-refresh
        if self.auto_refresh:
            time.sleep(self.refresh_interval)
            st_autorefresh.empty()
            st.rerun()


def st_autorefresh(interval: int = 5000, key: str = None):
    """Auto-refresh component"""
    if key is None:
        key = "autorefresh"
    
    if key not in st.session_state:
        st.session_state[key] = 0
    
    st.session_state[key] += 1
    
    if st.session_state[key] > 0:
        st.rerun()


def main():
    """Main dashboard entry point"""
    dashboard = ExecutiveDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
