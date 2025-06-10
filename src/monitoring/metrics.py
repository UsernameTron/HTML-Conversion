"""
Production metrics collection and Prometheus integration.
"""

import time
import logging
from typing import Dict, Any, Optional
from functools import wraps
from collections import defaultdict, deque
from threading import Lock
from datetime import datetime, timedelta

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from config.production import config

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Production metrics collector with Prometheus integration."""
    
    def __init__(self):
        self._lock = Lock()
        self._start_time = time.time()
        
        # Internal metrics storage (fallback if Prometheus not available)
        self._counters = defaultdict(int)
        self._histograms = defaultdict(list)
        self._gauges = defaultdict(float)
        self._request_history = deque(maxlen=1000)
        
        # Initialize Prometheus metrics if available
        if PROMETHEUS_AVAILABLE and config.monitoring.prometheus_enabled:
            self._setup_prometheus_metrics()
        else:
            logger.warning("Prometheus client not available or disabled, using internal metrics only")
            self._prometheus_metrics = None
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        self._registry = CollectorRegistry()
        
        # Request metrics
        self.request_counter = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self._registry
        )
        
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            registry=self._registry
        )
        
        # Application metrics
        self.template_render_counter = Counter(
            'template_renders_total',
            'Total template renders',
            ['template_id', 'status'],
            registry=self._registry
        )
        
        self.template_render_duration = Histogram(
            'template_render_duration_seconds',
            'Template render duration',
            ['template_id'],
            registry=self._registry
        )
        
        self.file_upload_counter = Counter(
            'file_uploads_total',
            'Total file uploads',
            ['file_type', 'status'],
            registry=self._registry
        )
        
        self.file_upload_size = Histogram(
            'file_upload_size_bytes',
            'File upload size in bytes',
            ['file_type'],
            registry=self._registry
        )
        
        # Cache metrics
        self.cache_operations = Counter(
            'cache_operations_total',
            'Cache operations',
            ['operation', 'result'],
            registry=self._registry
        )
        
        self.cache_hit_rate = Gauge(
            'cache_hit_rate',
            'Cache hit rate percentage',
            registry=self._registry
        )
        
        # System metrics
        self.memory_usage = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            ['type'],
            registry=self._registry
        )
        
        self.cpu_usage = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            ['type'],
            registry=self._registry
        )
        
        # Error metrics
        self.error_counter = Counter(
            'errors_total',
            'Total errors',
            ['error_type', 'component'],
            registry=self._registry
        )
        
        # Security metrics
        self.security_events = Counter(
            'security_events_total',
            'Security events',
            ['event_type', 'severity'],
            registry=self._registry
        )
        
        # Performance metrics
        self.active_users = Gauge(
            'active_users',
            'Number of active users',
            registry=self._registry
        )
        
        self.concurrent_requests = Gauge(
            'concurrent_requests',
            'Number of concurrent requests',
            registry=self._registry
        )
        
        self._prometheus_metrics = True
        logger.info("Prometheus metrics initialized successfully")
    
    def record_request(self, method: str = "GET", endpoint: str = "/", status: int = 200, duration: float = 0):
        """Record HTTP request metrics."""
        with self._lock:
            # Internal metrics
            self._counters[f"requests_{status}"] += 1
            self._counters["requests_total"] += 1
            
            # Request history for rate calculation
            self._request_history.append({
                "timestamp": time.time(),
                "method": method,
                "endpoint": endpoint,
                "status": status,
                "duration": duration
            })
            
            # Prometheus metrics
            if self._prometheus_metrics:
                self.request_counter.labels(method=method, endpoint=endpoint, status=str(status)).inc()
                if duration > 0:
                    self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_template_render(self, template_id: str, status: str = "success", duration: float = 0):
        """Record template rendering metrics."""
        with self._lock:
            # Internal metrics
            self._counters[f"template_renders_{status}"] += 1
            self._counters["template_renders_total"] += 1
            
            if duration > 0:
                self._histograms[f"template_render_duration_{template_id}"].append(duration)
            
            # Prometheus metrics
            if self._prometheus_metrics:
                self.template_render_counter.labels(template_id=template_id, status=status).inc()
                if duration > 0:
                    self.template_render_duration.labels(template_id=template_id).observe(duration)
    
    def record_file_upload(self, file_type: str, status: str = "success", size_bytes: int = 0):
        """Record file upload metrics."""
        with self._lock:
            # Internal metrics
            self._counters[f"file_uploads_{status}"] += 1
            self._counters["file_uploads_total"] += 1
            
            if size_bytes > 0:
                self._histograms[f"file_upload_size_{file_type}"].append(size_bytes)
            
            # Prometheus metrics
            if self._prometheus_metrics:
                self.file_upload_counter.labels(file_type=file_type, status=status).inc()
                if size_bytes > 0:
                    self.file_upload_size.labels(file_type=file_type).observe(size_bytes)
    
    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation metrics."""
        with self._lock:
            # Internal metrics
            self._counters[f"cache_{operation}_{result}"] += 1
            self._counters[f"cache_{operation}_total"] += 1
            
            # Prometheus metrics
            if self._prometheus_metrics:
                self.cache_operations.labels(operation=operation, result=result).inc()
    
    def update_cache_hit_rate(self, hit_rate: float):
        """Update cache hit rate metric."""
        with self._lock:
            self._gauges["cache_hit_rate"] = hit_rate
            
            if self._prometheus_metrics:
                self.cache_hit_rate.set(hit_rate)
    
    def update_system_metrics(self, memory_bytes: int, cpu_percent: float):
        """Update system resource metrics."""
        with self._lock:
            self._gauges["memory_usage_bytes"] = memory_bytes
            self._gauges["cpu_usage_percent"] = cpu_percent
            
            if self._prometheus_metrics:
                self.memory_usage.labels(type="process").set(memory_bytes)
                self.cpu_usage.labels(type="process").set(cpu_percent)
    
    def record_error(self, error_type: str, component: str = "application"):
        """Record error metrics."""
        with self._lock:
            # Internal metrics
            self._counters[f"errors_{error_type}"] += 1
            self._counters["errors_total"] += 1
            
            # Prometheus metrics
            if self._prometheus_metrics:
                self.error_counter.labels(error_type=error_type, component=component).inc()
    
    def record_security_event(self, event_type: str, severity: str = "medium"):
        """Record security event metrics."""
        with self._lock:
            # Internal metrics
            self._counters[f"security_{event_type}_{severity}"] += 1
            self._counters["security_events_total"] += 1
            
            # Prometheus metrics
            if self._prometheus_metrics:
                self.security_events.labels(event_type=event_type, severity=severity).inc()
    
    def update_concurrent_users(self, user_count: int):
        """Update active user count."""
        with self._lock:
            self._gauges["active_users"] = user_count
            
            if self._prometheus_metrics:
                self.active_users.set(user_count)
    
    def update_concurrent_requests(self, request_count: int):
        """Update concurrent request count."""
        with self._lock:
            self._gauges["concurrent_requests"] = request_count
            
            if self._prometheus_metrics:
                self.concurrent_requests.set(request_count)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        with self._lock:
            now = time.time()
            uptime = now - self._start_time
            
            # Calculate request rate over last 5 minutes
            recent_requests = [
                req for req in self._request_history
                if now - req["timestamp"] < 300  # 5 minutes
            ]
            request_rate = len(recent_requests) / 5.0 if recent_requests else 0
            
            # Calculate error rate
            total_requests = self._counters.get("requests_total", 0)
            total_errors = self._counters.get("errors_total", 0)
            error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": uptime,
                "requests": {
                    "total": total_requests,
                    "rate_per_minute": request_rate * 60,
                    "recent_5min": len(recent_requests)
                },
                "templates": {
                    "total_renders": self._counters.get("template_renders_total", 0),
                    "successful_renders": self._counters.get("template_renders_success", 0),
                    "failed_renders": self._counters.get("template_renders_error", 0)
                },
                "files": {
                    "total_uploads": self._counters.get("file_uploads_total", 0),
                    "successful_uploads": self._counters.get("file_uploads_success", 0),
                    "failed_uploads": self._counters.get("file_uploads_error", 0)
                },
                "cache": {
                    "hit_rate": self._gauges.get("cache_hit_rate", 0),
                    "total_operations": self._counters.get("cache_get_total", 0) + self._counters.get("cache_set_total", 0)
                },
                "system": {
                    "memory_usage_bytes": self._gauges.get("memory_usage_bytes", 0),
                    "cpu_usage_percent": self._gauges.get("cpu_usage_percent", 0)
                },
                "errors": {
                    "total": total_errors,
                    "rate_percent": error_rate
                },
                "security": {
                    "total_events": self._counters.get("security_events_total", 0)
                },
                "performance": {
                    "active_users": self._gauges.get("active_users", 0),
                    "concurrent_requests": self._gauges.get("concurrent_requests", 0)
                }
            }
    
    def get_prometheus_metrics(self) -> Optional[str]:
        """Get Prometheus metrics in text format."""
        if not self._prometheus_metrics:
            return None
        
        try:
            return generate_latest(self._registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Error generating Prometheus metrics: {str(e)}")
            return None
    
    def reset_metrics(self):
        """Reset all metrics (for testing)."""
        with self._lock:
            self._counters.clear()
            self._histograms.clear()
            self._gauges.clear()
            self._request_history.clear()


# Global metrics collector instance
metrics_collector = MetricsCollector()


def track_request(method: str = "GET", endpoint: str = "/"):
    """Decorator to track request metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 200
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 500
                metrics_collector.record_error("request_error", "application")
                raise
            finally:
                duration = time.time() - start_time
                metrics_collector.record_request(method, endpoint, status, duration)
        
        return wrapper
    return decorator


def track_template_render(template_id: str):
    """Decorator to track template rendering metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                metrics_collector.record_error("template_render_error", "template_service")
                raise
            finally:
                duration = time.time() - start_time
                metrics_collector.record_template_render(template_id, status, duration)
        
        return wrapper
    return decorator


def track_file_upload(file_type: str):
    """Decorator to track file upload metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            status = "success"
            size_bytes = 0
            
            try:
                result = func(*args, **kwargs)
                if isinstance(result, dict) and 'size' in result:
                    size_bytes = result['size']
                return result
            except Exception as e:
                status = "error"
                metrics_collector.record_error("file_upload_error", "file_processor")
                raise
            finally:
                metrics_collector.record_file_upload(file_type, status, size_bytes)
        
        return wrapper
    return decorator


def get_metrics() -> Dict[str, Any]:
    """Get current metrics summary."""
    return metrics_collector.get_metrics_summary()


def get_prometheus_metrics() -> Optional[str]:
    """Get Prometheus metrics."""
    return metrics_collector.get_prometheus_metrics()