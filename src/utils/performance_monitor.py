"""Performance monitoring and metrics collection system."""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import deque
import streamlit as st

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)


class PerformanceBuffer:
    """Circular buffer for performance metrics."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize performance buffer."""
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self.lock = threading.Lock()
    
    def add_metric(self, metric: PerformanceMetric):
        """Add metric to buffer."""
        with self.lock:
            self.buffer.append(metric)
    
    def get_metrics(self, metric_name: Optional[str] = None, last_n: Optional[int] = None) -> List[PerformanceMetric]:
        """Get metrics from buffer."""
        with self.lock:
            metrics = list(self.buffer)
        
        if metric_name:
            metrics = [m for m in metrics if m.name == metric_name]
        
        if last_n:
            metrics = metrics[-last_n:]
        
        return metrics
    
    def get_summary(self, metric_name: str, time_window: float = 300) -> Dict[str, float]:
        """Get statistical summary of metrics."""
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        with self.lock:
            recent_metrics = [
                m.value for m in self.buffer 
                if m.name == metric_name and m.timestamp >= cutoff_time
            ]
        
        if not recent_metrics:
            return {}
        
        return {
            'count': len(recent_metrics),
            'min': min(recent_metrics),
            'max': max(recent_metrics),
            'avg': sum(recent_metrics) / len(recent_metrics),
            'p50': self._percentile(recent_metrics, 50),
            'p95': self._percentile(recent_metrics, 95),
            'p99': self._percentile(recent_metrics, 99)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile."""
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]


class SystemMetricsCollector:
    """Collect system-level performance metrics."""
    
    def __init__(self):
        """Initialize system metrics collector."""
        self.process = psutil.Process()
        self.start_time = time.time()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage metrics."""
        memory_info = self.process.memory_info()
        system_memory = psutil.virtual_memory()
        
        return {
            'process_memory_mb': memory_info.rss / 1024 / 1024,
            'process_memory_percent': self.process.memory_percent(),
            'system_memory_percent': system_memory.percent,
            'system_memory_available_mb': system_memory.available / 1024 / 1024
        }
    
    def get_cpu_usage(self) -> Dict[str, float]:
        """Get CPU usage metrics."""
        return {
            'process_cpu_percent': self.process.cpu_percent(),
            'system_cpu_percent': psutil.cpu_percent(),
            'load_average_1m': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
        }
    
    def get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage metrics."""
        disk_usage = psutil.disk_usage('.')
        
        return {
            'disk_total_gb': disk_usage.total / 1024 / 1024 / 1024,
            'disk_used_gb': disk_usage.used / 1024 / 1024 / 1024,
            'disk_free_gb': disk_usage.free / 1024 / 1024 / 1024,
            'disk_usage_percent': (disk_usage.used / disk_usage.total) * 100
        }
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds."""
        return time.time() - self.start_time


class PerformanceMonitor:
    """Comprehensive performance monitoring system."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.buffer = PerformanceBuffer()
        self.system_collector = SystemMetricsCollector()
        
        # Prometheus metrics (if available)
        if PROMETHEUS_AVAILABLE:
            self._setup_prometheus_metrics()
        
        # Application-specific metrics
        self.request_counter = 0
        self.error_counter = 0
        self.operation_timings = {}
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        self.prom_request_counter = Counter(
            'html_formatter_requests_total',
            'Total number of requests'
        )
        
        self.prom_error_counter = Counter(
            'html_formatter_errors_total',
            'Total number of errors'
        )
        
        self.prom_processing_time = Histogram(
            'html_formatter_processing_seconds',
            'Time spent processing requests',
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.prom_memory_usage = Gauge(
            'html_formatter_memory_usage_mb',
            'Current memory usage in MB'
        )
        
        self.prom_cpu_usage = Gauge(
            'html_formatter_cpu_usage_percent',
            'Current CPU usage percentage'
        )
    
    def record_request(self):
        """Record a new request."""
        self.request_counter += 1
        
        if PROMETHEUS_AVAILABLE:
            self.prom_request_counter.inc()
        
        metric = PerformanceMetric(
            name='requests',
            value=1,
            timestamp=time.time()
        )
        self.buffer.add_metric(metric)
    
    def record_error(self, error_type: str = 'unknown'):
        """Record an error."""
        self.error_counter += 1
        
        if PROMETHEUS_AVAILABLE:
            self.prom_error_counter.inc()
        
        metric = PerformanceMetric(
            name='errors',
            value=1,
            timestamp=time.time(),
            labels={'error_type': error_type}
        )
        self.buffer.add_metric(metric)
    
    def record_operation_time(self, operation: str, duration: float):
        """Record operation timing."""
        if operation not in self.operation_timings:
            self.operation_timings[operation] = []
        
        self.operation_timings[operation].append(duration)
        
        if PROMETHEUS_AVAILABLE:
            self.prom_processing_time.observe(duration)
        
        metric = PerformanceMetric(
            name='operation_time',
            value=duration,
            timestamp=time.time(),
            labels={'operation': operation}
        )
        self.buffer.add_metric(metric)
    
    def record_file_processing(self, file_type: str, file_size: int, processing_time: float):
        """Record file processing metrics."""
        metric = PerformanceMetric(
            name='file_processing',
            value=processing_time,
            timestamp=time.time(),
            labels={
                'file_type': file_type,
                'file_size_category': self._get_size_category(file_size)
            }
        )
        self.buffer.add_metric(metric)
    
    def start_background_monitoring(self, interval: float = 30.0):
        """Start background system monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._background_monitor,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
    
    def stop_background_monitoring(self):
        """Stop background monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
    
    def _background_monitor(self, interval: float):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect system metrics
                memory_metrics = self.system_collector.get_memory_usage()
                cpu_metrics = self.system_collector.get_cpu_usage()
                
                # Record memory usage
                memory_metric = PerformanceMetric(
                    name='memory_usage',
                    value=memory_metrics['process_memory_mb'],
                    timestamp=time.time()
                )
                self.buffer.add_metric(memory_metric)
                
                # Record CPU usage
                cpu_metric = PerformanceMetric(
                    name='cpu_usage',
                    value=cpu_metrics['process_cpu_percent'],
                    timestamp=time.time()
                )
                self.buffer.add_metric(cpu_metric)
                
                # Update Prometheus metrics
                if PROMETHEUS_AVAILABLE:
                    self.prom_memory_usage.set(memory_metrics['process_memory_mb'])
                    self.prom_cpu_usage.set(cpu_metrics['process_cpu_percent'])
                
                time.sleep(interval)
                
            except Exception as e:
                # Log error but continue monitoring
                print(f"Background monitoring error: {e}")
                time.sleep(interval)
    
    def get_performance_summary(self) -> dict:
        """Get comprehensive performance summary."""
        import time
        system_data = self.system_collector.get_memory_usage() if hasattr(self, 'system_collector') else {}
        cpu_data = self.system_collector.get_cpu_usage() if hasattr(self, 'system_collector') else {}
        disk_data = self.system_collector.get_disk_usage() if hasattr(self, 'system_collector') else {}
        
        # Merge system data
        system_combined = {**system_data, **cpu_data, **disk_data}
        
        summary = {
            'timestamp': time.time(),
            'uptime_seconds': time.time() - self.system_collector.start_time if hasattr(self, 'system_collector') else 0,
            'operations': {},
            'application': {
                'total_requests': getattr(self, 'request_counter', 0),
                'total_errors': getattr(self, 'error_counter', 0),
                'error_rate_percent': 0.0,
                'recent_requests': 0,
                'recent_errors': 0
            },
            'system': system_combined,
        }
        
        # Calculate error rate
        total_requests = summary['application']['total_requests']
        total_errors = summary['application']['total_errors']
        if total_requests > 0:
            summary['application']['error_rate_percent'] = (total_errors / total_requests) * 100
        
        if hasattr(self, 'operation_timings'):
            for op, times in self.operation_timings.items():
                total_time = sum(times)
                summary['operations'][op] = {
                    'count': len(times),
                    'total_time': total_time,
                    'avg_time': total_time / len(times) if times else 0,
                }
        
        # Add memory, cpu, and disk keys for test compatibility (as dictionaries)
        if system_data:
            summary['system']['memory'] = system_data
        if cpu_data:
            summary['system']['cpu'] = cpu_data
        if disk_data:
            summary['system']['disk'] = disk_data
            
        return summary
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus-formatted metrics."""
        if not PROMETHEUS_AVAILABLE:
            return "# Prometheus client not available"
        
        return generate_latest().decode('utf-8')
    
    def _get_size_category(self, size_bytes: int) -> str:
        """Categorize file size."""
        if size_bytes < 1024 * 1024:  # < 1MB
            return 'small'
        elif size_bytes < 10 * 1024 * 1024:  # < 10MB
            return 'medium'
        else:
            return 'large'


# Global performance monitor
@st.cache_resource
def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    monitor = PerformanceMonitor()
    monitor.start_background_monitoring()
    return monitor


# Performance timing decorator
def monitor_performance(operation_name: str):
    """Decorator to monitor operation performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            monitor.record_request()
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_operation_time(operation_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_operation_time(operation_name, duration)
                monitor.record_error(type(e).__name__)
                raise
        
        return wrapper
    return decorator