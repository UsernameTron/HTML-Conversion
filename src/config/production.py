"""
Production configuration and environment management.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration for production."""
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '5432'))
    name: str = os.getenv('DB_NAME', 'html_formatter')
    user: str = os.getenv('DB_USER', 'app_user')
    password: str = os.getenv('DB_PASSWORD', '')
    ssl_mode: str = os.getenv('DB_SSL_MODE', 'require')
    pool_size: int = int(os.getenv('DB_POOL_SIZE', '10'))
    max_overflow: int = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    
    @property
    def connection_string(self) -> str:
        """Get database connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}?sslmode={self.ssl_mode}"


@dataclass
class RedisConfig:
    """Redis configuration for caching and sessions."""
    host: str = os.getenv('REDIS_HOST', 'localhost')
    port: int = int(os.getenv('REDIS_PORT', '6379'))
    db: int = int(os.getenv('REDIS_DB', '0'))
    password: str = os.getenv('REDIS_PASSWORD', '')
    ssl: bool = os.getenv('REDIS_SSL', 'False').lower() == 'true'
    max_connections: int = int(os.getenv('REDIS_MAX_CONNECTIONS', '50'))
    
    @property
    def connection_params(self) -> Dict[str, Any]:
        """Get Redis connection parameters."""
        params = {
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'max_connections': self.max_connections,
            'decode_responses': True
        }
        
        if self.password:
            params['password'] = self.password
        
        if self.ssl:
            params['ssl'] = True
            params['ssl_cert_reqs'] = None
        
        return params


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    # Prometheus metrics
    prometheus_enabled: bool = os.getenv('PROMETHEUS_ENABLED', 'True').lower() == 'true'
    prometheus_port: int = int(os.getenv('PROMETHEUS_PORT', '9090'))
    
    # Health checks
    health_check_enabled: bool = os.getenv('HEALTH_CHECK_ENABLED', 'True').lower() == 'true'
    health_check_interval: int = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
    
    # Logging
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_format: str = os.getenv('LOG_FORMAT', 'json')
    log_file: Optional[str] = os.getenv('LOG_FILE')
    
    # APM
    apm_enabled: bool = os.getenv('APM_ENABLED', 'False').lower() == 'true'
    apm_service_name: str = os.getenv('APM_SERVICE_NAME', 'html-formatter-pro')
    apm_environment: str = os.getenv('APM_ENVIRONMENT', 'production')
    
    # Alerting
    alert_webhook_url: Optional[str] = os.getenv('ALERT_WEBHOOK_URL')
    alert_email: Optional[str] = os.getenv('ALERT_EMAIL')


@dataclass
class StorageConfig:
    """Storage configuration for file handling."""
    # Local storage
    upload_dir: str = os.getenv('UPLOAD_DIR', '/app/uploads')
    temp_dir: str = os.getenv('TEMP_DIR', '/app/tmp')
    cache_dir: str = os.getenv('CACHE_DIR', '/app/cache')
    
    # Cloud storage (optional)
    s3_bucket: Optional[str] = os.getenv('S3_BUCKET')
    s3_region: str = os.getenv('S3_REGION', 'us-east-1')
    s3_access_key: Optional[str] = os.getenv('S3_ACCESS_KEY')
    s3_secret_key: Optional[str] = os.getenv('S3_SECRET_KEY')
    
    # File retention
    temp_file_retention_hours: int = int(os.getenv('TEMP_FILE_RETENTION_HOURS', '24'))
    upload_file_retention_days: int = int(os.getenv('UPLOAD_FILE_RETENTION_DAYS', '30'))
    
    def __post_init__(self):
        """Create necessary directories."""
        for directory in [self.upload_dir, self.temp_dir, self.cache_dir]:
            Path(directory).mkdir(parents=True, exist_ok=True)


@dataclass
class PerformanceConfig:
    """Performance and scaling configuration."""
    # Worker processes
    worker_processes: int = int(os.getenv('WORKER_PROCESSES', '4'))
    worker_connections: int = int(os.getenv('WORKER_CONNECTIONS', '1000'))
    
    # Request handling
    request_timeout: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    max_request_size: int = int(os.getenv('MAX_REQUEST_SIZE', '10485760'))  # 10MB
    
    # Caching
    cache_enabled: bool = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    cache_ttl_default: int = int(os.getenv('CACHE_TTL_DEFAULT', '3600'))  # 1 hour
    cache_max_size: int = int(os.getenv('CACHE_MAX_SIZE', '1000'))
    
    # Rate limiting
    rate_limit_enabled: bool = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    rate_limit_requests_per_minute: int = int(os.getenv('RATE_LIMIT_RPM', '60'))
    rate_limit_burst: int = int(os.getenv('RATE_LIMIT_BURST', '10'))


@dataclass
class ProductionConfig:
    """Complete production configuration."""
    # Environment
    environment: str = os.getenv('ENVIRONMENT', 'production')
    debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    testing: bool = os.getenv('TESTING', 'False').lower() == 'true'
    
    # Application
    app_name: str = os.getenv('APP_NAME', 'HTML Formatter Pro')
    app_version: str = os.getenv('APP_VERSION', '1.0.0')
    app_host: str = os.getenv('APP_HOST', '0.0.0.0')
    app_port: int = int(os.getenv('APP_PORT', '8501'))
    
    # Secret management
    secret_key: str = os.getenv('SECRET_KEY', os.urandom(32).hex())
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    def __post_init__(self):
        """Validate production configuration."""
        if self.environment == 'production':
            self._validate_production_settings()
    
    def _validate_production_settings(self):
        """Validate critical production settings."""
        errors = []
        
        # Check debug mode
        if self.debug:
            errors.append("Debug mode must be disabled in production")
        
        # Check secret key
        if len(self.secret_key) < 32:
            errors.append("Secret key must be at least 32 characters")
        
        # Check required environment variables
        required_vars = {
            'SECRET_KEY': self.secret_key,
            'APP_HOST': self.app_host,
            'APP_PORT': str(self.app_port)
        }
        
        for var_name, var_value in required_vars.items():
            if not var_value:
                errors.append(f"Required environment variable {var_name} is not set")
        
        if errors:
            raise ValueError(f"Production configuration validation failed: {'; '.join(errors)}")
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'json': {
                    'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
                    'class': 'pythonjsonlogger.jsonlogger.JsonFormatter'
                },
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.monitoring.log_level,
                    'formatter': self.monitoring.log_format,
                    'stream': 'ext://sys.stdout'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['console'],
                    'level': self.monitoring.log_level,
                    'propagate': False
                },
                'security': {
                    'handlers': ['console'],
                    'level': 'WARNING',
                    'propagate': False
                },
                'performance': {
                    'handlers': ['console'],
                    'level': 'INFO',
                    'propagate': False
                }
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'environment': self.environment,
            'debug': self.debug,
            'app_name': self.app_name,
            'app_version': self.app_version,
            'app_host': self.app_host,
            'app_port': self.app_port,
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'name': self.database.name,
                'ssl_mode': self.database.ssl_mode
            },
            'redis': {
                'host': self.redis.host,
                'port': self.redis.port,
                'db': self.redis.db,
                'ssl': self.redis.ssl
            },
            'monitoring': {
                'prometheus_enabled': self.monitoring.prometheus_enabled,
                'health_check_enabled': self.monitoring.health_check_enabled,
                'log_level': self.monitoring.log_level,
                'apm_enabled': self.monitoring.apm_enabled
            },
            'performance': {
                'cache_enabled': self.performance.cache_enabled,
                'rate_limit_enabled': self.performance.rate_limit_enabled,
                'worker_processes': self.performance.worker_processes
            }
        }


# Global production configuration instance
config = ProductionConfig()


def setup_logging():
    """Setup production logging."""
    import logging.config
    
    logging_config = config.get_logging_config()
    
    # Add file handler if log file is specified
    if config.monitoring.log_file:
        logging_config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': config.monitoring.log_level,
            'formatter': config.monitoring.log_format,
            'filename': config.monitoring.log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
        
        # Add file handler to all loggers
        for logger_config in logging_config['loggers'].values():
            if 'file' not in logger_config['handlers']:
                logger_config['handlers'].append('file')
    
    logging.config.dictConfig(logging_config)


def get_environment_info() -> Dict[str, Any]:
    """Get current environment information."""
    return {
        'environment': config.environment,
        'debug': config.debug,
        'app_name': config.app_name,
        'app_version': config.app_version,
        'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        'platform': os.sys.platform,
        'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown',
        'pid': os.getpid(),
        'uid': os.getuid() if hasattr(os, 'getuid') else 'unknown',
        'gid': os.getgid() if hasattr(os, 'getgid') else 'unknown'
    }