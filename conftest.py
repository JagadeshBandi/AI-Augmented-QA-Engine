"""
Pytest configuration for ARES QA Engine
Integrates with metrics collection for Grafana visualization
"""

import os
import time
import uuid
from datetime import datetime
from typing import Dict, Any
import pytest

from src.utils.metrics_collector import get_metrics_collector, is_enabled


# Global session tracking
session_id = str(uuid.uuid4())
session_start_time = None
test_results = []
test_start_times = {}


def pytest_sessionstart(session):
    """Called after the Session object has been created"""
    global session_start_time
    session_start_time = time.time()
    
    if is_enabled():
        collector = get_metrics_collector()
        print(f"\nARES QA Engine - Session {session_id[:8]} started")
        print(f"Metrics collection enabled - InfluxDB: {collector.url}")


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished"""
    global session_start_time, test_results
    
    if session_start_time and is_enabled():
        total_duration = time.time() - session_start_time
        
        # Calculate session statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.get('status') == 'passed')
        failed_tests = sum(1 for r in test_results if r.get('status') == 'failed')
        skipped_tests = sum(1 for r in test_results if r.get('status') == 'skipped')
        
        # Push session metrics
        collector = get_metrics_collector()
        collector.push_test_session_metrics(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            total_duration=total_duration,
            session_id=session_id
        )
        
        print(f"\nSession Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)" if total_tests > 0 else "   Passed: 0")
        print(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)" if total_tests > 0 else "   Failed: 0")
        print(f"   Skipped: {skipped_tests}")
        print(f"   Duration: {total_duration:.2f}s")
        print(f"   Metrics pushed to Grafana dashboard")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results and push metrics"""
    global test_results, test_start_times
    
    # Execute all other hooks to obtain the report object
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":  # Only consider the main test call
        test_name = f"{item.parent.name}::{item.name}" if item.parent else item.name
        test_file = str(item.fspath)
        
        if report.when == "setup":
            test_start_times[test_name] = time.time()
        
        elif report.when == "call":
            # Calculate test duration
            start_time = test_start_times.get(test_name, time.time())
            duration = time.time() - start_time
            
            # Determine test status
            if report.passed:
                status = "passed"
                error_message = ""
            elif report.failed:
                status = "failed"
                error_message = str(report.longrepr) if report.longrepr else ""
            elif report.skipped:
                status = "skipped"
                error_message = ""
            else:
                status = "error"
                error_message = str(report.longrepr) if report.longrepr else ""
            
            # Store result for session summary
            test_result = {
                'test_name': test_name,
                'status': status,
                'duration': duration,
                'test_file': test_file,
                'error_message': error_message,
                'timestamp': datetime.utcnow()
            }
            test_results.append(test_result)
            
            # Extract test tags/parameters
            test_tags = {}
            if hasattr(item, 'callspec'):
                # Extract pytest parametrize parameters
                for key, value in item.callspec.params.items():
                    test_tags[f"param_{key}"] = str(value)
            
            # Extract markers as tags
            for marker in item.iter_markers():
                if marker.name not in ['parametrize', 'skip', 'skipif']:
                    test_tags[f"marker_{marker.name}"] = "true"
                    if marker.args:
                        test_tags[f"{marker.name}_args"] = str(marker.args)
            
            # Push metrics to InfluxDB
            if is_enabled():
                collector = get_metrics_collector()
                collector.push_test_result(
                    test_name=test_name,
                    status=status,
                    duration=duration,
                    test_file=test_file,
                    error_message=error_message,
                    test_tags=test_tags
                )
                
                # Calculate and push flakiness metrics for tests with history
                if len(test_results) > 1:
                    recent_same_tests = [r for r in test_results[-10:] if r['test_name'] == test_name]
                    if len(recent_same_tests) > 1:
                        recent_results = [1 if r['status'] == 'passed' else 0 for r in recent_same_tests]
                        flakiness_score = 1 - (sum(recent_results) / len(recent_results))
                        
                        collector.push_flakiness_metrics(
                            test_name=test_name,
                            flakiness_score=flakiness_score,
                            recent_results=recent_results
                        )


def pytest_collection_finish(session):
    """Called after collection has been completed"""
    if is_enabled():
        print(f"\nCollected {len(session.items)} test items")


# Custom pytest markers for better categorization
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "ui: mark test as UI test")
    config.addinivalue_line("markers", "api: mark test as API test")
    config.addinivalue_line("markers", "critical: mark test as critical path")
    config.addinivalue_line("markers", "flaky: mark test as known to be flaky")


@pytest.fixture(scope="session")
def metrics_session():
    """Fixture to provide access to metrics collector in tests"""
    if is_enabled():
        return get_metrics_collector()
    return None


# Environment configuration helper
@pytest.fixture(scope="session")
def test_environment():
    """Fixture to provide test environment information"""
    return {
        'session_id': session_id,
        'start_time': session_start_time,
        'metrics_enabled': is_enabled(),
        'ci_environment': os.getenv('CI', 'false') == 'true',
        'branch': os.getenv('GIT_BRANCH', 'unknown'),
        'commit_sha': os.getenv('GIT_COMMIT', 'unknown')
    }
