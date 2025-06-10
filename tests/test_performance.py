"""
Performance tests for monitoring and optimization.
"""

import pytest
import time
import threading
from utils.performance_monitor import get_performance_monitor
from utils.cache_manager import get_cache_manager
from utils.logger import get_enhanced_logger


class TestPerformanceMonitoring:
    """Test performance monitoring functionality."""
    
    def test_performance_monitor_initialization(self, performance_monitor):
        """Test performance monitor initialization."""
        assert performance_monitor is not None
        assert hasattr(performance_monitor, 'record_request')
        assert hasattr(performance_monitor, 'record_operation_time')
    
    def test_request_tracking(self, performance_monitor):
        """Test request tracking functionality."""
        initial_summary = performance_monitor.get_performance_summary()
        initial_requests = initial_summary['application']['total_requests']
        
        # Record some requests
        for i in range(5):
            performance_monitor.record_request()
        
        updated_summary = performance_monitor.get_performance_summary()
        updated_requests = updated_summary['application']['total_requests']
        
        assert updated_requests >= initial_requests + 5
    
    def test_operation_timing(self, performance_monitor):
        """Test operation timing functionality."""
        operation_name = "test_operation"
        operation_time = 0.1  # 100ms
        
        performance_monitor.record_operation_time(operation_name, operation_time)
        
        summary = performance_monitor.get_performance_summary()
        
        # Check if operation is recorded
        assert 'operations' in summary
        if operation_name in summary['operations']:
            assert summary['operations'][operation_name]['count'] > 0
            assert summary['operations'][operation_name]['total_time'] >= operation_time
    
    def test_error_tracking(self, performance_monitor):
        """Test error tracking functionality."""
        initial_summary = performance_monitor.get_performance_summary()
        initial_errors = initial_summary['application']['total_errors']
        
        # Record some errors
        for i in range(3):
            performance_monitor.record_error("Test error")
        
        updated_summary = performance_monitor.get_performance_summary()
        updated_errors = updated_summary['application']['total_errors']
        
        assert updated_errors >= initial_errors + 3
    
    def test_system_metrics_collection(self, performance_monitor):
        """Test system metrics collection."""
        summary = performance_monitor.get_performance_summary()
        
        # Check system metrics are present
        assert 'system' in summary
        assert 'memory' in summary['system']
        assert 'cpu' in summary['system']
        assert 'disk' in summary['system']
        
        # Check memory metrics
        memory = summary['system']['memory']
        assert 'process_memory_mb' in memory
        assert 'system_memory_percent' in memory
        assert memory['process_memory_mb'] > 0
        
        # Check CPU metrics
        cpu = summary['system']['cpu']
        assert 'process_cpu_percent' in cpu
        assert 'system_cpu_percent' in cpu
        assert cpu['process_cpu_percent'] >= 0
    
    def test_performance_summary_structure(self, performance_monitor):
        """Test performance summary structure."""
        summary = performance_monitor.get_performance_summary()
        
        required_keys = [
            'timestamp', 'uptime_seconds', 'system', 'application', 'operations'
        ]
        
        for key in required_keys:
            assert key in summary
        
        # Check application metrics structure
        app_metrics = summary['application']
        app_required_keys = [
            'total_requests', 'total_errors', 'error_rate_percent',
            'recent_requests', 'recent_errors'
        ]
        
        for key in app_required_keys:
            assert key in app_metrics


class TestCacheManager:
    """Test cache management and performance."""
    
    def test_cache_manager_initialization(self, cache_manager):
        """Test cache manager initialization."""
        assert cache_manager is not None
        assert hasattr(cache_manager, 'get')
        assert hasattr(cache_manager, 'set')
    
    def test_cache_basic_operations(self, cache_manager):
        """Test basic cache operations."""
        key = "test_key"
        value = "test_value"
        
        # Test set and get
        cache_manager.set(key, value, ttl=300)
        retrieved_value = cache_manager.get(key)
        
        assert retrieved_value == value
    
    def test_cache_expiration(self, cache_manager):
        """Test cache expiration functionality."""
        key = "expiring_key"
        value = "expiring_value"
        
        # Set with very short TTL
        cache_manager.set(key, value, ttl=1)
        
        # Should be available immediately
        assert cache_manager.get(key) == value
        
        # Wait for expiration
        time.sleep(2)
        
        # Should be expired
        assert cache_manager.get(key) is None
    
    def test_cache_statistics(self, cache_manager):
        """Test cache statistics collection."""
        # Perform some cache operations
        cache_manager.set("stat_key1", "value1", ttl=300)
        cache_manager.set("stat_key2", "value2", ttl=300)
        
        # Test hits
        cache_manager.get("stat_key1")
        cache_manager.get("stat_key1")  # Hit
        
        # Test miss
        cache_manager.get("nonexistent_key")  # Miss
        
        stats = cache_manager.get_stats()
        
        assert 'total_requests' in stats
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'hit_rate' in stats
        
        assert stats['total_requests'] > 0
        assert stats['hits'] >= 0
        assert stats['misses'] >= 0
    
    def test_cache_performance(self, cache_manager):
        """Test cache performance with multiple operations."""
        num_operations = 100
        
        # Set operations
        start_time = time.time()
        for i in range(num_operations):
            cache_manager.set(f"perf_key_{i}", f"value_{i}", ttl=300)
        set_time = time.time() - start_time
        
        # Get operations
        start_time = time.time()
        for i in range(num_operations):
            cache_manager.get(f"perf_key_{i}")
        get_time = time.time() - start_time
        
        # Performance assertions (should be fast)
        assert set_time < 1.0  # 100 sets in less than 1 second
        assert get_time < 0.5  # 100 gets in less than 0.5 seconds
        
        # Calculate operations per second
        set_ops_per_sec = num_operations / set_time
        get_ops_per_sec = num_operations / get_time
        
        assert set_ops_per_sec > 100  # At least 100 sets per second
        assert get_ops_per_sec > 200  # At least 200 gets per second
    
    def test_concurrent_cache_access(self, cache_manager):
        """Test concurrent cache access."""
        num_threads = 5
        operations_per_thread = 20
        
        def cache_worker(thread_id):
            for i in range(operations_per_thread):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                
                # Set value
                cache_manager.set(key, value, ttl=300)
                
                # Get value
                retrieved = cache_manager.get(key)
                assert retrieved == value
        
        # Create and start threads
        threads = []
        start_time = time.time()
        
        for thread_id in range(num_threads):
            thread = threading.Thread(target=cache_worker, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time
        assert total_time < 5.0
        
        # Verify cache statistics
        stats = cache_manager.get_stats()
        total_operations = num_threads * operations_per_thread * 2  # set + get
        assert stats['total_requests'] >= total_operations


class TestLoggingPerformance:
    """Test logging system performance."""
    
    def test_logger_initialization(self):
        """Test logger initialization performance."""
        start_time = time.time()
        logger = get_enhanced_logger("test_logger")
        end_time = time.time()
        
        initialization_time = end_time - start_time
        
        # Should initialize quickly
        assert initialization_time < 0.1
        assert logger is not None
    
    def test_logging_performance(self):
        """Test logging operation performance."""
        logger = get_enhanced_logger("performance_test")
        
        num_logs = 1000
        
        start_time = time.time()
        for i in range(num_logs):
            logger.info(f"Performance test log message {i}", test_id=i)
        end_time = time.time()
        
        logging_time = end_time - start_time
        
        # Should log 1000 messages quickly (< 1 second)
        assert logging_time < 1.0
        
        # Calculate logs per second
        logs_per_sec = num_logs / logging_time
        assert logs_per_sec > 1000  # At least 1000 logs per second
    
    def test_concurrent_logging(self):
        """Test concurrent logging performance."""
        num_threads = 5
        logs_per_thread = 100
        
        def logging_worker(thread_id):
            logger = get_enhanced_logger(f"thread_{thread_id}")
            for i in range(logs_per_thread):
                logger.info(f"Thread {thread_id} log {i}", thread_id=thread_id, log_id=i)
        
        # Create and start threads
        threads = []
        start_time = time.time()
        
        for thread_id in range(num_threads):
            thread = threading.Thread(target=logging_worker, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time
        assert total_time < 2.0


class TestIntegratedPerformance:
    """Test integrated performance of multiple components."""
    
    def test_full_pipeline_performance(self, template_service, performance_monitor, cache_manager):
        """Test performance of full processing pipeline."""
        # Get template
        template = template_service.get_template('business_letter')
        if not template:
            pytest.skip("Business letter template not available")
        
        # Prepare content
        content_data = {}
        for placeholder in template.placeholders:
            content_data[placeholder.key] = placeholder.placeholder_text
        
        num_iterations = 10
        
        start_time = time.time()
        
        for i in range(num_iterations):
            # Record request
            performance_monitor.record_request()
            
            # Render template
            rendered = template_service.render_template('business_letter', content_data)
            assert rendered is not None
            
            # Cache result
            cache_key = f"test_render_{i}"
            cache_manager.set(cache_key, rendered, ttl=300)
            
            # Retrieve from cache
            cached_result = cache_manager.get(cache_key)
            assert cached_result == rendered
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should process 10 iterations quickly
        assert total_time < 5.0
        
        # Check performance metrics
        summary = performance_monitor.get_performance_summary()
        assert summary['application']['total_requests'] >= num_iterations
        
        # Check cache performance
        stats = cache_manager.get_stats()
        assert stats['total_requests'] >= num_iterations
    
    def test_memory_usage_stability(self, template_service, cache_manager):
        """Test memory usage stability under load."""
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many operations
        for i in range(100):
            # Template operations
            template = template_service.get_template('business_letter')
            if template:
                content_data = {placeholder.key: placeholder.placeholder_text 
                              for placeholder in template.placeholders}
                rendered = template_service.render_template('business_letter', content_data)
                
                # Cache operations
                cache_manager.set(f"memory_test_{i}", rendered, ttl=60)
                cache_manager.get(f"memory_test_{i}")
            
            # Force garbage collection every 10 iterations
            if i % 10 == 0:
                gc.collect()
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 50MB for 100 operations)
        assert memory_increase < 50, f"Memory increased by {memory_increase:.2f}MB"
    
    def test_error_handling_performance(self, template_service, performance_monitor):
        """Test performance impact of error handling."""
        start_time = time.time()
        
        # Test various error conditions
        for i in range(50):
            # Try to get non-existent template
            result = template_service.get_template(f'nonexistent_template_{i}')
            assert result is None
            
            # Try to render with invalid data
            result = template_service.render_template('business_letter', {})
            assert result is None
            
            # Record error
            performance_monitor.record_error(f"Test error {i}")
        
        end_time = time.time()
        error_handling_time = end_time - start_time
        
        # Error handling should not significantly impact performance
        assert error_handling_time < 2.0
        
        # Check error tracking
        summary = performance_monitor.get_performance_summary()
        assert summary['application']['total_errors'] >= 50