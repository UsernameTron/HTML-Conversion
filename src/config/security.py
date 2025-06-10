"""
Production security configuration and hardening.
"""

import os
import secrets
from typing import Dict, List, Optional
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class SecurityConfig:
    """Production security configuration."""
    
    # Environment
    environment: str = os.getenv('ENVIRONMENT', 'development')
    debug_mode: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Session security
    session_timeout: int = int(os.getenv('SESSION_TIMEOUT', '3600'))  # 1 hour
    secret_key: str = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
    
    # CSRF protection
    csrf_token_expiry: int = int(os.getenv('CSRF_TOKEN_EXPIRY', '1800'))  # 30 minutes
    
    # Rate limiting
    rate_limit_requests: int = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
    rate_limit_window: int = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))  # 1 hour
    
    # File upload security
    max_file_size: int = int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB
    allowed_file_types: List[str] = os.getenv(
        'ALLOWED_FILE_TYPES', 
        'txt,pdf,docx,md,rtf'
    ).split(',')
    
    # Content security
    max_content_length: int = int(os.getenv('MAX_CONTENT_LENGTH', '1000000'))  # 1MB
    html_sanitization: bool = os.getenv('HTML_SANITIZATION', 'True').lower() == 'true'
    
    # Network security
    allowed_hosts: List[str] = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    cors_origins: List[str] = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
    
    # SSL/TLS
    force_https: bool = os.getenv('FORCE_HTTPS', 'False').lower() == 'true'
    hsts_max_age: int = int(os.getenv('HSTS_MAX_AGE', '31536000'))  # 1 year
    
    # Content Security Policy
    csp_default_src: List[str] = ["'self'"]
    csp_script_src: List[str] = ["'self'", "'unsafe-inline'", "'unsafe-eval'", "https://cdn.jsdelivr.net"]
    csp_style_src: List[str] = ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"]
    csp_font_src: List[str] = ["'self'", "https://fonts.gstatic.com"]
    csp_img_src: List[str] = ["'self'", "data:", "https:"]
    csp_connect_src: List[str] = ["'self'", "ws:", "wss:"]
    
    # Logging and monitoring
    log_security_events: bool = os.getenv('LOG_SECURITY_EVENTS', 'True').lower() == 'true'
    alert_on_security_events: bool = os.getenv('ALERT_ON_SECURITY_EVENTS', 'False').lower() == 'true'
    
    def __post_init__(self):
        """Validate security configuration."""
        if self.environment == 'production':
            self._validate_production_config()
    
    def _validate_production_config(self):
        """Validate production security requirements."""
        errors = []
        
        # Check secret key strength
        if len(self.secret_key) < 32:
            errors.append("Secret key must be at least 32 characters in production")
        
        # Check HTTPS enforcement
        if not self.force_https:
            errors.append("HTTPS must be enforced in production")
        
        # Check debug mode
        if self.debug_mode:
            errors.append("Debug mode must be disabled in production")
        
        # Check allowed hosts
        if 'localhost' in self.allowed_hosts or '127.0.0.1' in self.allowed_hosts:
            errors.append("Localhost should not be in allowed hosts for production")
        
        if errors:
            raise ValueError(f"Production security validation failed: {'; '.join(errors)}")
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses."""
        headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=()',
        }
        
        if self.force_https:
            headers['Strict-Transport-Security'] = f'max-age={self.hsts_max_age}; includeSubDomains'
        
        # Content Security Policy
        csp_directives = [
            f"default-src {' '.join(self.csp_default_src)}",
            f"script-src {' '.join(self.csp_script_src)}",
            f"style-src {' '.join(self.csp_style_src)}",
            f"font-src {' '.join(self.csp_font_src)}",
            f"img-src {' '.join(self.csp_img_src)}",
            f"connect-src {' '.join(self.csp_connect_src)}",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        headers['Content-Security-Policy'] = '; '.join(csp_directives)
        
        return headers
    
    def is_allowed_host(self, host: str) -> bool:
        """Check if host is allowed."""
        if not host:
            return False
        
        # Extract hostname from URL if full URL is provided
        try:
            parsed = urlparse(f"http://{host}")
            hostname = parsed.hostname or host
        except:
            hostname = host
        
        return hostname in self.allowed_hosts
    
    def is_allowed_file_type(self, filename: str) -> bool:
        """Check if file type is allowed."""
        if not filename:
            return False
        
        extension = filename.lower().split('.')[-1]
        return extension in self.allowed_file_types
    
    def get_rate_limit_key(self, identifier: str) -> str:
        """Get rate limit key for identifier."""
        return f"rate_limit:{identifier}"


class SecurityMiddleware:
    """Security middleware for request processing."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self._failed_attempts = {}
    
    def validate_request(self, request_data: Dict) -> tuple[bool, Optional[str]]:
        """Validate incoming request for security."""
        # Check content length
        content = request_data.get('content', '')
        if len(content) > self.config.max_content_length:
            return False, f"Content exceeds maximum length of {self.config.max_content_length} characters"
        
        # Check for suspicious patterns
        suspicious_patterns = [
            '<script>', 'javascript:', 'eval(', 'document.cookie',
            'window.location', 'document.write', 'innerHTML',
            '../', '..\\', '/etc/passwd', 'cmd.exe'
        ]
        
        content_lower = content.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                return False, f"Suspicious pattern detected: {pattern}"
        
        return True, None
    
    def log_security_event(self, event_type: str, details: Dict):
        """Log security event."""
        if not self.config.log_security_events:
            return
        
        import logging
        security_logger = logging.getLogger('security')
        security_logger.warning(
            f"Security event: {event_type}",
            extra={
                'event_type': event_type,
                'details': details,
                'timestamp': __import__('datetime').datetime.utcnow().isoformat()
            }
        )


class InputSanitizer:
    """Advanced input sanitization for production."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security."""
        if not filename:
            return ""
        
        # Remove path traversal attempts
        filename = filename.replace('../', '').replace('..\\', '')
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove null bytes and control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)
        
        # Limit length
        filename = filename[:255]
        
        # Ensure safe characters only
        safe_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_'
        filename = ''.join(char if char in safe_chars else '_' for char in filename)
        
        return filename
    
    def sanitize_text_input(self, text: str) -> str:
        """Sanitize text input."""
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Limit length
        if len(text) > self.config.max_content_length:
            text = text[:self.config.max_content_length]
        
        # Remove control characters (except common whitespace)
        allowed_controls = {'\t', '\n', '\r'}
        text = ''.join(
            char for char in text 
            if ord(char) >= 32 or char in allowed_controls
        )
        
        return text
    
    def sanitize_html_content(self, html: str) -> str:
        """Sanitize HTML content using production settings."""
        if not self.config.html_sanitization:
            return html
        
        try:
            import bleach
            from bleach.css_sanitizer import CSSSanitizer
            
            # Production-safe HTML tags
            allowed_tags = [
                'p', 'br', 'strong', 'em', 'u', 'i', 'b',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'ul', 'ol', 'li', 'blockquote',
                'div', 'span', 'a', 'img',
                'table', 'thead', 'tbody', 'tr', 'th', 'td',
                'code', 'pre'
            ]
            
            # Production-safe attributes
            allowed_attributes = {
                'a': ['href', 'title'],
                'img': ['src', 'alt', 'width', 'height'],
                'div': ['class'],
                'span': ['class'],
                'p': ['class'],
                'h1': ['class'], 'h2': ['class'], 'h3': ['class'],
                'h4': ['class'], 'h5': ['class'], 'h6': ['class'],
                'table': ['class'],
                'th': ['class'], 'td': ['class'],
                'code': ['class'], 'pre': ['class']
            }
            
            # CSS sanitizer with restricted properties
            css_sanitizer = CSSSanitizer(
                allowed_css_properties=[
                    'color', 'background-color', 'font-size', 'font-weight',
                    'text-align', 'margin', 'padding', 'border',
                    'width', 'height', 'display'
                ]
            )
            
            # Sanitize HTML
            clean_html = bleach.clean(
                html,
                tags=allowed_tags,
                attributes=allowed_attributes,
                css_sanitizer=css_sanitizer,
                strip=True
            )
            
            return clean_html
            
        except ImportError:
            # Fallback if bleach is not available
            import re
            
            # Remove script tags and their content
            clean_html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove dangerous attributes
            dangerous_attrs = ['onclick', 'onload', 'onerror', 'onmouseover', 'onfocus', 'onblur']
            for attr in dangerous_attrs:
                clean_html = re.sub(f'{attr}=["\'][^"\']*["\']', '', clean_html, flags=re.IGNORECASE)
            
            # Remove javascript: URLs
            clean_html = re.sub(r'href=["\']javascript:[^"\']*["\']', '', clean_html, flags=re.IGNORECASE)
            
            return clean_html


# Production security configuration instance
production_security = SecurityConfig()

# Security middleware instance
security_middleware = SecurityMiddleware(production_security)

# Input sanitizer instance
input_sanitizer = InputSanitizer(production_security)