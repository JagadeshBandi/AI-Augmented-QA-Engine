"""
Performance tests for generating metrics traffic
"""

import pytest
import time
import random


@pytest.mark.performance
def test_page_load_performance():
    """Test page load performance metrics"""
    start_time = time.time()
    
    # Simulate page load operations
    time.sleep(random.uniform(0.1, 0.5))
    
    # Simulate some work
    result = sum(i * i for i in range(100))
    
    duration = time.time() - start_time
    assert duration < 1.0, f"Page load took too long: {duration}s"
    assert result == 328350, "Calculation failed"


@pytest.mark.performance
@pytest.mark.parametrize("user_count", [1, 10, 100])
def test_concurrent_users_simulation(user_count):
    """Simulate concurrent user load"""
    start_time = time.time()
    
    # Simulate concurrent user processing
    for i in range(user_count):
        time.sleep(0.01)  # Simulate user processing time
        assert i < user_count, "User count mismatch"
    
    duration = time.time() - start_time
    assert duration < user_count * 0.02, f"Concurrent processing too slow: {duration}s"


@pytest.mark.slow
def test_api_response_time():
    """Test API response time simulation"""
    start_time = time.time()
    
    # Simulate API call with variable response time
    response_time = random.uniform(0.05, 0.3)
    time.sleep(response_time)
    
    duration = time.time() - start_time
    assert duration < 0.5, f"API response too slow: {duration}s"


@pytest.mark.flaky
def test_occasionally_failing_test():
    """Test that occasionally fails to generate flakiness metrics"""
    import random
    
    # 30% chance of failure to create flakiness
    if random.random() < 0.3:
        pytest.fail("Random failure for flakiness testing")
    
    # Test logic when it passes
    assert True, "Test passed"
