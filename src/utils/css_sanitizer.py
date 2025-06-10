"""CSS sanitization utilities for secure style processing."""

import logging
import re
from typing import Dict, List, Optional, Set
import tinycss2
from tinycss2.ast import QualifiedRule, AtRule, Declaration

logger = logging.getLogger(__name__)


class CSSSanitizer:
    """Secure CSS sanitizer for style attributes and stylesheets."""
    
    def __init__(self):
        """Initialize CSS sanitizer with security rules."""
        # Allowed CSS properties (whitelist approach)
        self.allowed_properties = {
            # Typography
            'color', 'font-family', 'font-size', 'font-weight', 'font-style',
            'line-height', 'letter-spacing', 'text-align', 'text-decoration',
            'text-transform', 'text-indent', 'word-spacing',
            
            # Layout and positioning
            'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
            'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
            'border', 'border-radius', 'width', 'height', 'max-width', 'max-height',
            'min-width', 'min-height', 'display', 'overflow', 'overflow-x', 'overflow-y',
            
            # Visual effects
            'background', 'background-color', 'background-image', 'background-size',
            'background-position', 'background-repeat', 'opacity', 'box-shadow',
            'border-color', 'border-style', 'border-width',
            
            # Flexbox and grid (safe subset)
            'flex', 'flex-direction', 'justify-content', 'align-items', 'align-content',
            'flex-wrap', 'gap',
            
            # Transitions and animations (limited)
            'transition', 'transform'
        }
        
        # Dangerous CSS patterns to block
        self.dangerous_patterns = [
            r'javascript\s*:',
            r'expression\s*\(',
            r'@import',
            r'@media\s+.*\(\s*device',
            r'behavior\s*:',
            r'-moz-binding',
            r'data\s*:.*script',
            r'vbscript\s*:',
            r'mocha\s*:',
            r'livescript\s*:',
            r'url\s*\(\s*["\']?\s*data\s*:.*script'
        ]
        
        # Compile patterns for performance
        self.dangerous_regex = re.compile('|'.join(self.dangerous_patterns), re.IGNORECASE)
        
        # URL validation pattern
        self.safe_url_pattern = re.compile(r'^https?://[^\s<>"\']+$|^data:image/[^;]+;base64,[A-Za-z0-9+/=]+$')
    
    def sanitize_css(self, css_content: str) -> str:
        """
        Sanitize CSS content with comprehensive security filtering.
        
        Args:
            css_content: Raw CSS content to sanitize
            
        Returns:
            Sanitized CSS content safe for use
        """
        if not css_content or not isinstance(css_content, str):
            return ""
        
        try:
            # Quick security scan
            if self.dangerous_regex.search(css_content):
                logger.warning("Dangerous CSS pattern detected and blocked")
                return ""
            
            # Check if this looks like a full stylesheet or inline styles
            if '{' in css_content and '}' in css_content:
                # This is a full stylesheet, parse as such
                return self._sanitize_stylesheet(css_content)
            else:
                # This looks like inline styles, parse as declarations
                return self._sanitize_inline_styles(css_content)
            
        except Exception as e:
            logger.warning(f"CSS parsing error: {str(e)}")
            return ""
    
    def _sanitize_stylesheet(self, css_content: str) -> str:
        """Sanitize a full CSS stylesheet."""
        try:
            parsed = tinycss2.parse_stylesheet(css_content)
            sanitized_rules = []
            
            for rule in parsed:
                if isinstance(rule, QualifiedRule):
                    # Process CSS rule with selector
                    selector = self._serialize_selector(rule.prelude)
                    if self._is_safe_selector(selector):
                        declarations = self._sanitize_declarations(rule.content)
                        if declarations:
                            sanitized_rules.append(f"{selector} {{ {declarations} }}")
            
            return '\n'.join(sanitized_rules)
            
        except Exception as e:
            logger.warning(f"Stylesheet parsing error: {str(e)}")
            return ""
    
    def _sanitize_inline_styles(self, css_content: str) -> str:
        """Sanitize inline CSS declarations."""
        try:
            # Parse CSS using tinycss2
            parsed = tinycss2.parse_declaration_list(css_content)
            
            sanitized_declarations = []
            
            for token in parsed:
                if isinstance(token, Declaration):
                    if self._is_safe_declaration(token):
                        sanitized_value = self._sanitize_value(token.value)
                        if sanitized_value:
                            sanitized_declarations.append(f"{token.name}: {sanitized_value}")
                
            return "; ".join(sanitized_declarations)
            
        except Exception as e:
            logger.warning(f"Declaration parsing error: {str(e)}")
            return ""
    
    def _serialize_selector(self, prelude) -> str:
        """Serialize a CSS selector from tokens."""
        return ''.join(token.serialize() for token in prelude).strip()
    
    def _is_safe_selector(self, selector: str) -> bool:
        """Check if a CSS selector is safe."""
        # Basic selector safety - block dangerous patterns
        dangerous_selector_patterns = [
            r'javascript\s*:',
            r'expression\s*\(',
            r'@import',
            r'url\s*\(\s*["\']?\s*javascript'
        ]
        
        for pattern in dangerous_selector_patterns:
            if re.search(pattern, selector, re.IGNORECASE):
                return False
        
        return True
    
    def _sanitize_declarations(self, content) -> str:
        """Sanitize declarations within a CSS rule."""
        try:
            parsed_declarations = tinycss2.parse_declaration_list(content)
            sanitized_declarations = []
            
            for token in parsed_declarations:
                if isinstance(token, Declaration):
                    if self._is_safe_declaration(token):
                        sanitized_value = self._sanitize_value(token.value)
                        if sanitized_value:
                            sanitized_declarations.append(f"{token.name}: {sanitized_value}")
            
            return "; ".join(sanitized_declarations)
            
        except Exception as e:
            logger.warning(f"Declaration sanitization error: {str(e)}")
            return ""
    
    def sanitize_style_attribute(self, style_value: str) -> str:
        """
        Sanitize inline style attribute values.
        
        Args:
            style_value: Inline style attribute value
            
        Returns:
            Sanitized style value
        """
        return self.sanitize_css(style_value)
    
    def _is_safe_declaration(self, declaration: Declaration) -> bool:
        """Check if a CSS declaration is safe to include."""
        property_name = declaration.name.lower().strip()
        
        # Check against whitelist
        if property_name not in self.allowed_properties:
            logger.debug(f"Blocked CSS property: {property_name}")
            return False
        
        return True
    
    def _sanitize_value(self, value_tokens) -> str:
        """Sanitize CSS property values."""
        try:
            # Convert tokens back to string
            value_string = tinycss2.serialize(value_tokens).strip()
            
            # Remove dangerous patterns
            if self.dangerous_regex.search(value_string):
                logger.warning(f"Dangerous CSS value blocked: {value_string}")
                return ""
            
            # Validate URLs in values
            url_pattern = re.compile(r'url\s*\(\s*["\']?([^)]+?)["\']?\s*\)', re.IGNORECASE)
            
            def validate_url(match):
                url = match.group(1).strip().strip('"\'')
                if self.safe_url_pattern.match(url):
                    return match.group(0)  # Keep original if safe
                else:
                    logger.warning(f"Unsafe URL in CSS blocked: {url}")
                    return ""
            
            # Replace URLs with validated versions
            sanitized_value = url_pattern.sub(validate_url, value_string)
            
            # Additional validation for specific properties
            sanitized_value = self._validate_property_specific(sanitized_value)
            
            return sanitized_value
            
        except Exception as e:
            logger.warning(f"CSS value sanitization error: {str(e)}")
            return ""
    
    def _validate_property_specific(self, value: str) -> str:
        """Apply property-specific validation rules."""
        value = value.strip()
        
        # Block excessively large values that could cause issues
        if len(value) > 200:
            logger.warning("CSS value too long, truncating")
            return value[:200]
        
        # Block unusual unicode characters that could be used for attacks
        if re.search(r'[\u0000-\u001f\u007f-\u009f\ufeff]', value):
            logger.warning("Suspicious unicode characters in CSS value")
            return re.sub(r'[\u0000-\u001f\u007f-\u009f\ufeff]', '', value)
        
        return value
    
    def validate_color_value(self, color: str) -> bool:
        """Validate color values specifically."""
        if not color:
            return False
        
        color = color.strip().lower()
        
        # Hex colors
        if re.match(r'^#[0-9a-f]{3}$|^#[0-9a-f]{6}$', color):
            return True
        
        # RGB/RGBA colors
        if re.match(r'^rgba?\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*[0-9.]+)?\s*\)$', color):
            return True
        
        # Named colors (basic set)
        named_colors = {
            'white', 'black', 'red', 'green', 'blue', 'yellow', 'orange', 'purple',
            'pink', 'brown', 'gray', 'grey', 'transparent', 'inherit', 'initial'
        }
        
        if color in named_colors:
            return True
        
        return False


# Bleach CSS sanitizer integration
class BleachCSSSanitizer:
    """CSS sanitizer class for use with bleach."""
    
    def __init__(self):
        self.sanitizer = CSSSanitizer()
    
    def sanitize_css(self, style: str) -> str:
        """CSS sanitizer method for use with bleach."""
        return self.sanitizer.sanitize_css(style)

# Create instance for use with bleach
bleach_css_sanitizer = BleachCSSSanitizer()

# Global instance for convenience
_css_sanitizer = CSSSanitizer()

def sanitize_css(css_content: str) -> str:
    """
    Standalone function to sanitize CSS content.
    
    Args:
        css_content: CSS content to sanitize
        
    Returns:
        Sanitized CSS content
    """
    return _css_sanitizer.sanitize_css(css_content)