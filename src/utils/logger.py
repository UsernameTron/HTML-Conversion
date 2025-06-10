"""Enhanced logging system with structured logging and correlation IDs."""

import logging
import json
import time
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
import streamlit as st

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


class CorrelationIDProcessor:
    """Add correlation IDs to log entries."""
    
    def __call__(self, logger, method_name, event_dict):
        # Get correlation ID from Streamlit session state or create new one
        if hasattr(st, 'session_state') and 'correlation_id' in st.session_state:
            correlation_id = st.session_state.correlation_id
        else:
            correlation_id = str(uuid.uuid4())[:8]
            if hasattr(st, 'session_state'):
                st.session_state.correlation_id = correlation_id
        
        event_dict['correlation_id'] = correlation_id
        return event_dict


class TimestampProcessor:
    """Add high-precision timestamps to log entries."""
    
    def __call__(self, logger, method_name, event_dict):
        event_dict['timestamp'] = time.time()
        event_dict['iso_timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%S.%fZ', time.gmtime())
        return event_dict


class SecurityEventProcessor:
    """Mark security-related events for special handling."""
    
    SECURITY_KEYWORDS = [
        'security', 'xss', 'injection', 'malicious', 'dangerous', 
        'blocked', 'sanitized', 'validation', 'unauthorized'
    ]
    
    def __call__(self, logger, method_name, event_dict):
        event_text = str(event_dict.get('event', '')).lower()
        
        if any(keyword in event_text for keyword in self.SECURITY_KEYWORDS):
            event_dict['security_event'] = True
            event_dict['alert_level'] = 'high' if method_name in ['error', 'critical'] else 'medium'
        
        return event_dict


class PerformanceProcessor:
    """Add performance metrics to log entries."""
    
    def __call__(self, logger, method_name, event_dict):
        # Add execution context if available
        if 'duration' in event_dict:
            duration = event_dict['duration']
            if duration > 1.0:
                event_dict['performance_alert'] = 'slow_operation'
            elif duration > 5.0:
                event_dict['performance_alert'] = 'very_slow_operation'
        
        return event_dict


class EnhancedLogger:
    """Enhanced logger with structured logging and security features."""
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        """Initialize enhanced logger."""
        self.name = name
        self.log_file = log_file or "app_enhanced.log"
        
        if STRUCTLOG_AVAILABLE:
            self._setup_structlog()
        else:
            self._setup_standard_logging()
    
    def _setup_structlog(self):
        """Setup structured logging with processors."""
        # Configure structlog
        structlog.configure(
            processors=[
                CorrelationIDProcessor(),
                TimestampProcessor(),
                SecurityEventProcessor(),
                PerformanceProcessor(),
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Create logger
        self.logger = structlog.get_logger(self.name)
        
        # Setup file handler for structured logs
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler],
            format='%(message)s'  # structlog handles formatting
        )
    
    def _setup_standard_logging(self):
        """Setup standard logging as fallback."""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        if STRUCTLOG_AVAILABLE:
            self.logger.info(message, **kwargs)
        else:
            context = self._format_context(kwargs)
            self.logger.info(f"{message} {context}")
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        if STRUCTLOG_AVAILABLE:
            self.logger.warning(message, **kwargs)
        else:
            context = self._format_context(kwargs)
            self.logger.warning(f"{message} {context}")
    
    def error(self, message: str, **kwargs):
        """Log error message with context."""
        if STRUCTLOG_AVAILABLE:
            self.logger.error(message, **kwargs)
        else:
            context = self._format_context(kwargs)
            self.logger.error(f"{message} {context}")
    
    def security_event(self, message: str, event_type: str, **kwargs):
        """Log security event with special marking."""
        kwargs.update({
            'security_event': True,
            'event_type': event_type,
            'alert_level': 'high'
        })
        self.error(message, **kwargs)
    
    def performance_event(self, message: str, duration: float, operation: str, **kwargs):
        """Log performance event with metrics."""
        kwargs.update({
            'performance_event': True,
            'duration': duration,
            'operation': operation
        })
        
        if duration > 5.0:
            self.warning(message, **kwargs)
        else:
            self.info(message, **kwargs)
    
    def user_action(self, action: str, details: Dict[str, Any]):
        """Log user action for audit trail."""
        self.info(
            f"User action: {action}",
            action=action,
            user_event=True,
            **details
        )
    
    def file_processing_event(self, filename: str, operation: str, result: str, **kwargs):
        """Log file processing events."""
        self.info(
            f"File processing: {operation} - {result}",
            filename=filename,
            operation=operation,
            result=result,
            file_processing=True,
            **kwargs
        )
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for standard logging."""
        if not context:
            return ""
        return f"[{', '.join(f'{k}={v}' for k, v in context.items())}]"


class ApplicationMetrics:
    """Application metrics collector."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            'requests_total': 0,
            'errors_total': 0,
            'files_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'processing_times': [],
            'file_sizes': [],
            'security_events': 0
        }
        
        self.start_time = time.time()
    
    def increment_requests(self):
        """Increment total requests."""
        self.metrics['requests_total'] += 1
    
    def increment_errors(self):
        """Increment error count."""
        self.metrics['errors_total'] += 1
    
    def record_file_processing(self, file_size: int, processing_time: float):
        """Record file processing metrics."""
        self.metrics['files_processed'] += 1
        self.metrics['file_sizes'].append(file_size)
        self.metrics['processing_times'].append(processing_time)
    
    def record_cache_hit(self):
        """Record cache hit."""
        self.metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        """Record cache miss."""
        self.metrics['cache_misses'] += 1
    
    def record_security_event(self):
        """Record security event."""
        self.metrics['security_events'] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        uptime = time.time() - self.start_time
        
        return {
            'uptime_seconds': round(uptime, 2),
            'requests_total': self.metrics['requests_total'],
            'errors_total': self.metrics['errors_total'],
            'error_rate': round(
                (self.metrics['errors_total'] / max(self.metrics['requests_total'], 1)) * 100, 2
            ),
            'files_processed': self.metrics['files_processed'],
            'avg_processing_time': round(
                sum(self.metrics['processing_times']) / max(len(self.metrics['processing_times']), 1), 2
            ),
            'avg_file_size': round(
                sum(self.metrics['file_sizes']) / max(len(self.metrics['file_sizes']), 1), 2
            ),
            'cache_hit_rate': round(
                (self.metrics['cache_hits'] / max(self.metrics['cache_hits'] + self.metrics['cache_misses'], 1)) * 100, 2
            ),
            'security_events': self.metrics['security_events']
        }


# Global instances
@st.cache_resource
def get_enhanced_logger(name: str) -> EnhancedLogger:
    """Get enhanced logger instance."""
    return EnhancedLogger(name)


@st.cache_resource
def get_application_metrics() -> ApplicationMetrics:
    """Get application metrics instance."""
    return ApplicationMetrics()


# Timing decorator
def log_performance(operation_name: str):
    """Decorator to log performance metrics."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_enhanced_logger(func.__module__)
            metrics = get_application_metrics()
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.performance_event(
                    f"Operation completed: {operation_name}",
                    duration=duration,
                    operation=operation_name,
                    function=func.__name__
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                metrics.increment_errors()
                
                logger.error(
                    f"Operation failed: {operation_name}",
                    duration=duration,
                    operation=operation_name,
                    function=func.__name__,
                    error=str(e)
                )
                raise
        
        return wrapper
    return decorator