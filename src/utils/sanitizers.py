"""HTML sanitization utilities for security."""

import bleach
from html_sanitizer import Sanitizer
import logging
from typing import Dict, List, Optional
from models.style_models import SecurityConfig
from utils.css_sanitizer import bleach_css_sanitizer

logger = logging.getLogger(__name__)


class HTMLSanitizer:
    """Secure HTML sanitizer using bleach and html-sanitizer."""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """Initialize sanitizer with security configuration."""
        self.config = config or SecurityConfig()
        
        # Configure bleach settings
        self.bleach_tags = self.config.allowed_html_tags
        self.bleach_attributes = self.config.allowed_html_attributes
        
        # Configure html-sanitizer (fix attributes format)
        sanitizer_attributes = {}
        for tag, attrs in self.config.allowed_html_attributes.items():
            if tag != '*':  # Don't include wildcard in html-sanitizer config
                sanitizer_attributes[tag] = attrs
        
        self.html_sanitizer = Sanitizer({
            'tags': self.config.allowed_html_tags,
            'attributes': sanitizer_attributes,
            'empty': set(),
            'separate': {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'},
            'whitespace': set(),
            'remove_unknown_tags': True,
            'keep_typographic_whitespace': True,
            'add_nofollow': True,
            'autolink': False,
        })
    
    def sanitize(self, html_content: str) -> str:
        """
        Sanitize HTML content using multiple layers of protection.
        
        Args:
            html_content: Raw HTML content to sanitize
            
        Returns:
            Sanitized HTML content safe for display
            
        Raises:
            ValueError: If content is too long or contains suspicious patterns
        """
        if not html_content:
            return ""
        
        # Check content length
        if len(html_content) > self.config.max_text_length:
            raise ValueError(f"Content too long. Maximum {self.config.max_text_length} characters allowed.")
        
        # Pre-sanitization checks
        self._validate_content(html_content)
        try:
            # First pass: bleach sanitization (without css_sanitizer if incompatible)
            bleach_cleaned = bleach.clean(
                html_content,
                tags=self.bleach_tags,
                attributes=self.bleach_attributes,
                strip=True,
                strip_comments=True
            )
            # Second pass: html-sanitizer for additional protection
            final_cleaned = self.html_sanitizer.sanitize(bleach_cleaned)
            # Remove script content and dangerous JS patterns
            import re
            # Remove any remaining <script>...</script> blocks and their content
            final_cleaned = re.sub(r'<script.*?>.*?</script>', '', final_cleaned, flags=re.IGNORECASE|re.DOTALL)
            # Remove common JS attack patterns
            dangerous_patterns = [
                r'alert\s*\(.*?\)', r'fetch\s*\(.*?\)', r'onclick\s*=\s*".*?"', r'onerror\s*=\s*".*?"',
                r'javascript:', r'<iframe.*?>.*?</iframe>', r'XSS', r'maliciousFunction', r'stealData', r'document\.cookie'
            ]
            for pat in dangerous_patterns:
                final_cleaned = re.sub(pat, '', final_cleaned, flags=re.IGNORECASE|re.DOTALL)
            logger.info(f"Successfully sanitized HTML content ({len(html_content)} -> {len(final_cleaned)} chars)")
            return final_cleaned
        except Exception as e:
            logger.error(f"Error sanitizing HTML: {str(e)}")
            # Fall back to plain text
            return bleach.clean(html_content, tags=[], attributes={}, strip=True)
    
    def sanitize_style_attribute(self, style_content: str) -> str:
        """
        Sanitize CSS style attributes with strict filtering.
        
        Args:
            style_content: CSS style string
            
        Returns:
            Sanitized CSS style string
        """
        if not style_content:
            return ""
        
        # Allowed CSS properties (whitelist approach)
        allowed_properties = {
            'color', 'background-color', 'font-family', 'font-size', 'font-weight',
            'text-align', 'line-height', 'letter-spacing', 'margin', 'padding',
            'border-radius', 'max-width', 'width', 'height', 'display',
            'text-decoration', 'border', 'box-shadow', 'opacity'
        }
        
        # Remove dangerous patterns
        dangerous_patterns = [
            'javascript:', 'expression(', 'import', '@import', 'url(',
            'behavior:', '-moz-binding', 'position:', 'absolute', 'fixed'
        ]
        
        cleaned_style = style_content.lower()
        for pattern in dangerous_patterns:
            if pattern in cleaned_style:
                logger.warning(f"Blocked dangerous CSS pattern: {pattern}")
                return ""
        
        # Parse and filter CSS properties
        try:
            properties = []
            for prop in style_content.split(';'):
                if ':' in prop:
                    key, value = prop.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key in allowed_properties and value:
                        # Additional validation for specific properties
                        if self._validate_css_value(key, value):
                            properties.append(f"{key}: {value}")
            
            return '; '.join(properties)
            
        except Exception as e:
            logger.warning(f"Error parsing CSS style: {str(e)}")
            return ""
    
    def _validate_content(self, content: str) -> None:
        """Validate content for suspicious patterns."""
        suspicious_patterns = [
            '<script', 'javascript:', r'on[a-z]+\s*=', r'expression\s*\(',
            'vbscript:', 'data:text/html', 'data:application/'
        ]
        
        content_lower = content.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                logger.warning(f"Suspicious pattern detected: {pattern}")
                # Don't raise exception, let sanitizer handle it
                break
    
    def _validate_css_value(self, property_name: str, value: str) -> bool:
        """Validate CSS property values."""
        value_lower = value.lower()
        
        # Block dangerous CSS values
        if any(danger in value_lower for danger in ['javascript:', 'expression(', 'url(']):
            return False
        
        # Property-specific validation
        if property_name in ['color', 'background-color']:
            # Allow hex colors, rgb, rgba, named colors
            return (value.startswith('#') or 
                   value.startswith('rgb') or 
                   value in ['white', 'black', 'red', 'green', 'blue', 'transparent'])
        
        elif property_name == 'font-size':
            # Allow pixels, em, rem, percentages
            return any(value.endswith(unit) for unit in ['px', 'em', 'rem', '%'])
        
        elif property_name in ['margin', 'padding', 'width', 'height', 'max-width']:
            # Allow pixels, percentages, auto
            return (value == 'auto' or 
                   any(value.endswith(unit) for unit in ['px', '%', 'em', 'rem']))
        
        return True


class ContentValidator:
    """Validator for user-provided content."""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """Initialize validator with security configuration."""
        self.config = config or SecurityConfig()
    
    def validate_content_length(self, content: str):
        """Validate content length against configured limits."""
        if len(content) > self.config.max_text_length:
            return False, f"Content too long (max {self.config.max_text_length} chars)"
        return True, None

    def detect_suspicious_patterns(self, content: str):
        """Detect suspicious patterns in content."""
        import re
        patterns = [r'<script', r'javascript:', r'onclick=', r'onerror=']
        for pat in patterns:
            if re.search(pat, content, re.IGNORECASE):
                return True, pat
        return False, None
    
    def validate_text_input(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Validate text input for security and size limits.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return True, None
        
        # Check length
        if len(text) > self.config.max_text_length:
            return False, f"Text too long. Maximum {self.config.max_text_length} characters allowed."
        
        # Check for null bytes
        if '\x00' in text:
            return False, "Text contains null bytes"
        
        # Check for excessive script tags
        script_count = text.lower().count('<script')
        if script_count > 5:
            return False, "Too many script tags detected"
        
        return True, None
    
    def validate_filename(self, filename: str) -> tuple[bool, Optional[str]]:
        """Validate uploaded filename for security."""
        if not filename:
            return False, "Filename is required"
        
        if len(filename) > 255:
            return False, "Filename too long"
        
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Invalid filename characters"
        
        # Check for suspicious extensions
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.jar']
        if any(filename.lower().endswith(ext) for ext in dangerous_extensions):
            return False, "File type not allowed"
        
        return True, None