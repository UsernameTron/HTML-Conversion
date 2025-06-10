"""
Production health checks and monitoring endpoints.
"""

import time
import psutil
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from utils.cache_manager import get_cache_manager
from utils.performance_monitor import get_performance_monitor
from config.production import config

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health check status."""
    name: str
    status: str  # healthy, degraded, unhealthy
    message: str
    response_time_ms: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class HealthChecker:
    """Comprehensive health checking system."""
    
    def __init__(self):
        self.cache_manager = get_cache_manager()
        self.performance_monitor = get_performance_monitor()
        self.start_time = time.time()
    
    def check_application_health(self) -> HealthStatus:
        """Check overall application health."""
        start_time = time.time()
        
        try:
            # Basic application functionality test
            test_data = {"test": "health_check"}
            self.cache_manager.set("health_check", test_data, ttl=60)
            cached_data = self.cache_manager.get("health_check")
            
            if cached_data == test_data:
                status = "healthy"
                message = "Application is functioning normally"
            else:
                status = "degraded"
                message = "Cache operations are not working correctly"
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                name="application",
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={
                    "uptime_seconds": time.time() - self.start_time,
                    "cache_test": cached_data == test_data
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Application health check failed: {str(e)}")
            
            return HealthStatus(
                name="application",
                status="unhealthy",
                message=f"Application health check failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
    
    def check_memory_health(self) -> HealthStatus:
        """Check memory usage health."""
        start_time = time.time()
        
        try:
            memory = psutil.virtual_memory()
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Define thresholds
            system_memory_warning = 80  # 80%
            system_memory_critical = 90  # 90%
            process_memory_warning = 512  # 512 MB
            process_memory_critical = 1024  # 1 GB
            
            status = "healthy"
            messages = []
            
            if memory.percent > system_memory_critical:
                status = "unhealthy"
                messages.append(f"System memory usage critical: {memory.percent:.1f}%")
            elif memory.percent > system_memory_warning:
                status = "degraded"
                messages.append(f"System memory usage high: {memory.percent:.1f}%")
            
            if process_memory > process_memory_critical:
                status = "unhealthy"
                messages.append(f"Process memory usage critical: {process_memory:.1f} MB")
            elif process_memory > process_memory_warning:
                if status == "healthy":
                    status = "degraded"
                messages.append(f"Process memory usage high: {process_memory:.1f} MB")
            
            if not messages:
                messages.append("Memory usage is within normal limits")
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                name="memory",
                status=status,
                message="; ".join(messages),
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={
                    "system_memory_percent": memory.percent,
                    "system_memory_available_gb": memory.available / 1024 / 1024 / 1024,
                    "process_memory_mb": process_memory,
                    "memory_warning_threshold": system_memory_warning,
                    "memory_critical_threshold": system_memory_critical
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Memory health check failed: {str(e)}")
            
            return HealthStatus(
                name="memory",
                status="unhealthy",
                message=f"Memory health check failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
    
    def check_disk_health(self) -> HealthStatus:
        """Check disk usage health."""
        start_time = time.time()
        
        try:
            disk_usage = psutil.disk_usage('/')
            used_percent = (disk_usage.used / disk_usage.total) * 100
            free_gb = disk_usage.free / 1024 / 1024 / 1024
            
            # Define thresholds
            disk_warning = 80  # 80%
            disk_critical = 90  # 90%
            
            if used_percent > disk_critical:
                status = "unhealthy"
                message = f"Disk usage critical: {used_percent:.1f}%"
            elif used_percent > disk_warning:
                status = "degraded"
                message = f"Disk usage high: {used_percent:.1f}%"
            else:
                status = "healthy"
                message = "Disk usage is within normal limits"
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                name="disk",
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={
                    "disk_used_percent": used_percent,
                    "disk_free_gb": free_gb,
                    "disk_total_gb": disk_usage.total / 1024 / 1024 / 1024,
                    "disk_warning_threshold": disk_warning,
                    "disk_critical_threshold": disk_critical
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Disk health check failed: {str(e)}")
            
            return HealthStatus(
                name="disk",
                status="unhealthy",
                message=f"Disk health check failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
    
    def check_cpu_health(self) -> HealthStatus:
        """Check CPU usage health."""
        start_time = time.time()
        
        try:
            # Get CPU usage over a short period
            cpu_percent = psutil.cpu_percent(interval=1)
            process = psutil.Process()
            process_cpu = process.cpu_percent()
            
            # Define thresholds
            cpu_warning = 70  # 70%
            cpu_critical = 90  # 90%
            
            if cpu_percent > cpu_critical:
                status = "unhealthy"
                message = f"CPU usage critical: {cpu_percent:.1f}%"
            elif cpu_percent > cpu_warning:
                status = "degraded"
                message = f"CPU usage high: {cpu_percent:.1f}%"
            else:
                status = "healthy"
                message = "CPU usage is within normal limits"
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                name="cpu",
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={
                    "system_cpu_percent": cpu_percent,
                    "process_cpu_percent": process_cpu,
                    "cpu_count": psutil.cpu_count(),
                    "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                    "cpu_warning_threshold": cpu_warning,
                    "cpu_critical_threshold": cpu_critical
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"CPU health check failed: {str(e)}")
            
            return HealthStatus(
                name="cpu",
                status="unhealthy",
                message=f"CPU health check failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
    
    def check_cache_health(self) -> HealthStatus:
        """Check cache system health."""
        start_time = time.time()
        
        try:
            # Test cache operations
            test_key = f"health_check_cache_{int(time.time())}"
            test_value = {"timestamp": time.time(), "data": "health_check"}
            
            # Test set operation
            self.cache_manager.set(test_key, test_value, ttl=60)
            
            # Test get operation
            retrieved_value = self.cache_manager.get(test_key)
            
            # Test cache stats
            cache_stats = self.cache_manager.get_stats()
            
            if retrieved_value == test_value:
                status = "healthy"
                message = "Cache operations are functioning normally"
            else:
                status = "degraded"
                message = "Cache read/write operations are not working correctly"
            
            # Check cache hit rate
            if cache_stats.get('hit_rate', 0) < 50:
                if status == "healthy":
                    status = "degraded"
                message += f" (Hit rate: {cache_stats.get('hit_rate', 0):.1f}%)"
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                name="cache",
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={
                    "cache_test_success": retrieved_value == test_value,
                    "cache_stats": cache_stats,
                    "test_key": test_key
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Cache health check failed: {str(e)}")
            
            return HealthStatus(
                name="cache",
                status="unhealthy",
                message=f"Cache health check failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
    
    def check_performance_health(self) -> HealthStatus:
        """Check performance monitoring health."""
        start_time = time.time()
        
        try:
            # Test performance monitoring
            self.performance_monitor.record_request()
            self.performance_monitor.record_operation_time("health_check", 0.1)
            
            # Get performance summary
            summary = self.performance_monitor.get_performance_summary()
            
            # Check error rate
            error_rate = summary['application']['error_rate_percent']
            
            if error_rate > 10:
                status = "unhealthy"
                message = f"High error rate: {error_rate:.1f}%"
            elif error_rate > 5:
                status = "degraded"
                message = f"Elevated error rate: {error_rate:.1f}%"
            else:
                status = "healthy"
                message = "Performance monitoring is functioning normally"
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                name="performance",
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={
                    "error_rate_percent": error_rate,
                    "total_requests": summary['application']['total_requests'],
                    "total_errors": summary['application']['total_errors'],
                    "uptime_seconds": summary['uptime_seconds']
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Performance health check failed: {str(e)}")
            
            return HealthStatus(
                name="performance",
                status="unhealthy",
                message=f"Performance health check failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={"error": str(e)}
            )
    
    def run_all_checks(self) -> Dict[str, HealthStatus]:
        """Run all health checks."""
        checks = {}
        
        check_methods = [
            self.check_application_health,
            self.check_memory_health,
            self.check_disk_health,
            self.check_cpu_health,
            self.check_cache_health,
            self.check_performance_health
        ]
        
        for check_method in check_methods:
            try:
                health_status = check_method()
                checks[health_status.name] = health_status
            except Exception as e:
                logger.error(f"Health check {check_method.__name__} failed: {str(e)}")
                checks[check_method.__name__] = HealthStatus(
                    name=check_method.__name__,
                    status="unhealthy",
                    message=f"Health check failed: {str(e)}",
                    response_time_ms=0,
                    timestamp=datetime.utcnow(),
                    details={"error": str(e)}
                )
        
        return checks
    
    def get_overall_health(self, checks: Dict[str, HealthStatus]) -> str:
        """Determine overall health status."""
        if not checks:
            return "unhealthy"
        
        statuses = [check.status for check in checks.values()]
        
        if "unhealthy" in statuses:
            return "unhealthy"
        elif "degraded" in statuses:
            return "degraded"
        else:
            return "healthy"
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        checks = self.run_all_checks()
        overall_status = self.get_overall_health(checks)
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": overall_status,
            "uptime_seconds": time.time() - self.start_time,
            "environment": config.environment,
            "version": config.app_version,
            "checks": {}
        }
        
        for name, health_status in checks.items():
            report["checks"][name] = {
                "status": health_status.status,
                "message": health_status.message,
                "response_time_ms": health_status.response_time_ms,
                "timestamp": health_status.timestamp.isoformat(),
                "details": health_status.details
            }
        
        return report


# Global health checker instance
health_checker = HealthChecker()


def get_health_status() -> Dict[str, Any]:
    """Get current health status."""
    return health_checker.generate_health_report()


def get_readiness_status() -> Dict[str, Any]:
    """Get readiness status for Kubernetes probes."""
    checks = health_checker.run_all_checks()
    
    # For readiness, we only care about critical services
    critical_checks = ["application", "cache"]
    critical_health = {name: checks[name] for name in critical_checks if name in checks}
    
    overall_status = health_checker.get_overall_health(critical_health)
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            name: {
                "status": health.status,
                "message": health.message
            }
            for name, health in critical_health.items()
        }
    }


def get_liveness_status() -> Dict[str, Any]:
    """Get liveness status for Kubernetes probes."""
    # For liveness, we just check if the application is responsive
    app_health = health_checker.check_application_health()
    
    return {
        "status": app_health.status,
        "timestamp": app_health.timestamp.isoformat(),
        "message": app_health.message,
        "response_time_ms": app_health.response_time_ms
    }