"""
Metrics Collector for ARES QA Engine
Integrates with InfluxDB to store test metrics for Grafana visualization
"""

import os
import time
from datetime import datetime
from typing import Optional, Dict, Any
import logging

try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
    INFLUX_AVAILABLE = True
except ImportError:
    INFLUX_AVAILABLE = False
    logging.warning("InfluxDB client not available. Install with: pip install influxdb-client")

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and pushes test metrics to InfluxDB for Grafana visualization
    """
    
    def __init__(self, 
                 url: str = "http://localhost:8086",
                 token: str = "ares-super-secret-token-change-in-production",
                 org: str = "ares_corp",
                 bucket: str = "qa_metrics",
                 enabled: bool = True):
        """
        Initialize the MetricsCollector
        
        Args:
            url: InfluxDB URL
            token: InfluxDB authentication token
            org: InfluxDB organization name
            bucket: InfluxDB bucket name
            enabled: Whether metrics collection is enabled
        """
        self.enabled = enabled and INFLUX_AVAILABLE
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        
        self.client = None
        self.write_api = None
        
        if self.enabled:
            self._connect()
    
    def _connect(self):
        """Establish connection to InfluxDB"""
        try:
            self.client = InfluxDBClient(
                url=self.url,
                token=self.token,
                org=self.org
            )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            logger.info("Connected to InfluxDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            self.enabled = False
    
    def push_test_result(self, 
                        test_name: str,
                        status: str,
                        duration: float,
                        test_file: str = "",
                        error_message: str = "",
                        test_tags: Optional[Dict[str, str]] = None):
        """
        Push test result metrics to InfluxDB
        
        Args:
            test_name: Name of the test
            status: Test status (passed, failed, skipped, error)
            duration: Test execution duration in seconds
            test_file: Test file path
            error_message: Error message if test failed
            test_tags: Additional tags for the test
        """
        if not self.enabled:
            return
        
        try:
            # Create data point
            point = Point("test_results") \
                .tag("test_name", test_name) \
                .tag("status", status) \
                .tag("test_file", test_file) \
                .field("passed", 1 if status == "passed" else 0) \
                .field("failed", 1 if status == "failed" else 0) \
                .field("skipped", 1 if status == "skipped" else 0) \
                .field("error", 1 if status == "error" else 0) \
                .field("duration", duration) \
                .time(datetime.utcnow(), WritePrecision.NS)
            
            # Add custom tags
            if test_tags:
                for tag_key, tag_value in test_tags.items():
                    point = point.tag(tag_key, str(tag_value))
            
            # Add error message as field if present
            if error_message:
                point = point.field("error_message", error_message)
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, record=point)
            logger.debug(f"Pushed metrics for test: {test_name}")
            
        except Exception as e:
            logger.error(f"Failed to push metrics for test {test_name}: {e}")
    
    def push_test_session_metrics(self, 
                                 total_tests: int,
                                 passed_tests: int,
                                 failed_tests: int,
                                 skipped_tests: int,
                                 total_duration: float,
                                 session_id: str = ""):
        """
        Push test session summary metrics
        
        Args:
            total_tests: Total number of tests
            passed_tests: Number of passed tests
            failed_tests: Number of failed tests
            skipped_tests: Number of skipped tests
            total_duration: Total session duration
            session_id: Unique session identifier
        """
        if not self.enabled:
            return
        
        try:
            point = Point("test_session") \
                .tag("session_id", session_id or f"session_{int(time.time())}") \
                .field("total_tests", total_tests) \
                .field("passed_tests", passed_tests) \
                .field("failed_tests", failed_tests) \
                .field("skipped_tests", skipped_tests) \
                .field("pass_rate", passed_tests / total_tests if total_tests > 0 else 0) \
                .field("fail_rate", failed_tests / total_tests if total_tests > 0 else 0) \
                .field("total_duration", total_duration) \
                .time(datetime.utcnow(), WritePrecision.NS)
            
            self.write_api.write(bucket=self.bucket, record=point)
            logger.info(f"Pushed session metrics: {passed_tests}/{total_tests} passed")
            
        except Exception as e:
            logger.error(f"Failed to push session metrics: {e}")
    
    def push_flakiness_metrics(self, 
                              test_name: str,
                              flakiness_score: float,
                              recent_results: list):
        """
        Push test flakiness metrics
        
        Args:
            test_name: Name of the test
            flakiness_score: Flakiness score (0-1)
            recent_results: Recent test results (list of booleans)
        """
        if not self.enabled:
            return
        
        try:
            point = Point("test_flakiness") \
                .tag("test_name", test_name) \
                .field("flakiness_score", flakiness_score) \
                .field("recent_passes", sum(recent_results)) \
                .field("recent_failures", len(recent_results) - sum(recent_results)) \
                .field("sample_size", len(recent_results)) \
                .time(datetime.utcnow(), WritePrecision.NS)
            
            self.write_api.write(bucket=self.bucket, record=point)
            logger.debug(f"Pushed flakiness metrics for test: {test_name}")
            
        except Exception as e:
            logger.error(f"Failed to push flakiness metrics for {test_name}: {e}")
    
    def close(self):
        """Close the InfluxDB connection"""
        if self.client:
            self.client.close()
            logger.info("InfluxDB connection closed")


# Global instance for use across the application
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create the global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def is_enabled() -> bool:
    """Check if metrics collection is enabled and available"""
    return INFLUX_AVAILABLE and os.getenv("ARES_METRICS_ENABLED", "true").lower() == "true"
