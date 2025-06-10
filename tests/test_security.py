"""
Security tests for HTML sanitization and input validation.
"""

import pytest
from utils.sanitizers import HTMLSanitizer, ContentValidator
from utils.validators import FileValidator, TextValidator
from models.style_models import SecurityConfig


class TestHTMLSanitization:
    """Test HTML sanitization for XSS protection."""
    
    def test_sanitizer_initialization(self, html_sanitizer):
        """Test HTML sanitizer initialization."""
        assert html_sanitizer is not None
        assert hasattr(html_sanitizer, 'sanitize')
    
    def test_safe_html_passthrough(self, html_sanitizer):
        """Test that safe HTML passes through unchanged."""
        safe_html = "<p>This is <strong>safe</strong> content.</p>"
        sanitized = html_sanitizer.sanitize(safe_html)
        assert "<p>" in sanitized
        assert "<strong>" in sanitized
        assert "safe" in sanitized
    
    def test_script_tag_removal(self, html_sanitizer):
        """Test that script tags are removed."""
        malicious_html = '<p>Safe content</p><script>alert("XSS")</script>'
        sanitized = html_sanitizer.sanitize(malicious_html)
        assert "<script>" not in sanitized
        assert "alert" not in sanitized
        assert "Safe content" in sanitized
    
    def test_event_handler_removal(self, html_sanitizer):
        """Test that event handlers are removed."""
        malicious_html = '<p onclick="maliciousFunction()">Click me</p>'
        sanitized = html_sanitizer.sanitize(malicious_html)
        assert "onclick" not in sanitized
        assert "maliciousFunction" not in sanitized
        assert "Click me" in sanitized
    
    def test_iframe_removal(self, html_sanitizer):
        """Test that iframe tags are removed."""
        malicious_html = '<p>Content</p><iframe src="javascript:alert(1)"></iframe>'
        sanitized = html_sanitizer.sanitize(malicious_html)
        assert "<iframe>" not in sanitized
        assert "javascript:" not in sanitized
        assert "Content" in sanitized
    
    def test_javascript_url_removal(self, html_sanitizer):
        """Test that javascript: URLs are removed."""
        malicious_html = '<a href="javascript:alert(1)">Click</a>'
        sanitized = html_sanitizer.sanitize(malicious_html)
        assert "javascript:" not in sanitized
        assert "Click" in sanitized
    
    def test_style_attribute_sanitization(self, html_sanitizer):
        """Test that malicious CSS in style attributes is sanitized."""
        malicious_html = '<p style="background: url(javascript:alert(1))">Content</p>'
        sanitized = html_sanitizer.sanitize(malicious_html)
        assert "javascript:" not in sanitized
        assert "Content" in sanitized
    
    def test_comprehensive_xss_protection(self, html_sanitizer, malicious_html):
        """Test comprehensive XSS protection with complex malicious HTML."""
        sanitized = html_sanitizer.sanitize(malicious_html)
        
        # Ensure all malicious elements are removed
        dangerous_patterns = [
            "<script>", "javascript:", "onclick", "onerror", 
            "alert", "XSS", "<iframe>"
        ]
        
        for pattern in dangerous_patterns:
            assert pattern not in sanitized.lower()
        
        # Ensure safe content remains
        assert "Test Heading" in sanitized
    
    def test_empty_input_handling(self, html_sanitizer):
        """Test handling of empty and None inputs."""
        assert html_sanitizer.sanitize("") == ""
        assert html_sanitizer.sanitize(None) == ""
        assert html_sanitizer.sanitize("   ") == "   "
    
    def test_nested_attack_prevention(self, html_sanitizer):
        """Test prevention of nested XSS attacks."""
        nested_attack = '<p><<script>script>alert("XSS")<</script>/script></p>'
        sanitized = html_sanitizer.sanitize(nested_attack)
        assert "<script>" not in sanitized
        assert "alert" not in sanitized


class TestContentValidation:
    """Test content validation and filtering."""
    
    def test_content_validator_initialization(self):
        """Test ContentValidator initialization."""
        security_config = SecurityConfig()
        validator = ContentValidator(security_config)
        assert validator is not None
    
    def test_content_length_validation(self):
        """Test content length validation."""
        security_config = SecurityConfig(max_text_length=100)
        validator = ContentValidator(security_config)
        
        # Valid length
        short_content = "A" * 50
        is_valid, error = validator.validate_content_length(short_content)
        assert is_valid
        assert error is None
        
        # Invalid length
        long_content = "A" * 200
        is_valid, error = validator.validate_content_length(long_content)
        assert not is_valid
        assert "too long" in error.lower()
    
    def test_suspicious_pattern_detection(self):
        """Test detection of suspicious patterns."""
        security_config = SecurityConfig()
        validator = ContentValidator(security_config)
        
        suspicious_patterns = [
            '<script>alert("test")</script>',
            'javascript:alert(1)',
            'onclick="malicious()"',
            'onerror="attack()"'
        ]
        
        for pattern in suspicious_patterns:
            has_suspicious, detected = validator.detect_suspicious_patterns(pattern)
            assert has_suspicious
            assert len(detected) > 0


class TestInputValidation:
    """Test input validation utilities."""
    
    def test_text_validator_initialization(self):
        """Test TextValidator initialization."""
        validator = TextValidator()
        assert validator is not None
    
    def test_text_input_validation(self):
        """Test text input validation."""
        validator = TextValidator()
        
        # Valid text
        valid_text = "This is normal text content."
        is_valid, error = validator.validate_text_input(valid_text)
        assert is_valid
        assert error is None
        
        # Empty text
        is_valid, error = validator.validate_text_input("")
        assert not is_valid
        assert "empty" in error.lower()
        
        # Text too long
        long_text = "A" * 2000000  # 2MB
        is_valid, error = validator.validate_text_input(long_text)
        assert not is_valid
        assert "too long" in error.lower()
    
    def test_file_validator_initialization(self):
        """Test FileValidator initialization."""
        validator = FileValidator()
        assert validator is not None
    
    def test_file_extension_validation(self):
        """Test file extension validation."""
        validator = FileValidator()
        
        # Valid extensions
        valid_files = ["document.txt", "file.pdf", "content.docx"]
        for filename in valid_files:
            is_valid, error = validator.validate_file_extension(filename)
            assert is_valid
            assert error is None
        
        # Invalid extensions
        invalid_files = ["malware.exe", "script.js", "style.css"]
        for filename in invalid_files:
            is_valid, error = validator.validate_file_extension(filename)
            assert not is_valid
            assert "not allowed" in error.lower()
    
    def test_file_size_validation(self, temp_file):
        """Test file size validation."""
        validator = FileValidator()
        
        # Test with temporary file (should be small and valid)
        is_valid, error = validator.validate_file_size(temp_file)
        assert is_valid
        assert error is None
    
    def test_path_traversal_protection(self):
        """Test protection against path traversal attacks."""
        validator = FileValidator()
        
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "/etc/passwd",
            "C:\\Windows\\System32\\cmd.exe"
        ]
        
        for path in malicious_paths:
            is_valid, error = validator.validate_file_path(path)
            assert not is_valid
            assert "path" in error.lower()


class TestSecurityConfiguration:
    """Test security configuration and settings."""
    
    def test_security_config_defaults(self):
        """Test SecurityConfig default values."""
        config = SecurityConfig()
        assert config.max_file_size_mb > 0
        assert config.max_text_length > 0
        assert len(config.allowed_file_types) > 0
        assert len(config.blocked_patterns) > 0
    
    def test_security_config_customization(self):
        """Test SecurityConfig customization."""
        config = SecurityConfig(
            max_file_size_mb=5,
            max_text_length=50000,
            allowed_file_types=['txt', 'md']
        )
        assert config.max_file_size_mb == 5
        assert config.max_text_length == 50000
        assert 'txt' in config.allowed_file_types
        assert 'pdf' not in config.allowed_file_types
    
    def test_blocked_patterns_configuration(self):
        """Test blocked patterns in security configuration."""
        config = SecurityConfig()
        
        # Check that common attack patterns are blocked
        expected_patterns = ['<script', 'javascript:', 'onclick=', 'onerror=']
        for pattern in expected_patterns:
            assert any(pattern.lower() in blocked.lower() for blocked in config.blocked_patterns)


class TestSecurityIntegration:
    """Test integration of security components."""
    
    def test_end_to_end_sanitization(self, html_sanitizer):
        """Test end-to-end HTML sanitization process."""
        # Complex malicious input
        malicious_input = """
        <div>
            <h1>Legitimate Title</h1>
            <script>
                // Malicious script
                fetch('/steal-data', {
                    method: 'POST',
                    body: document.cookie
                });
            </script>
            <p onclick="stealData()">Click here</p>
            <img src="x" onerror="maliciousFunction()">
            <iframe src="javascript:alert('XSS')"></iframe>
            <a href="javascript:void(0)" onclick="attack()">Link</a>
            <style>
                body { background: url('javascript:alert(1)'); }
            </style>
        </div>
        """
        
        sanitized = html_sanitizer.sanitize(malicious_input)
        
        # Verify malicious content is removed
        malicious_elements = [
            '<script>', 'fetch(', 'document.cookie', 'onclick=', 'onerror=',
            'javascript:', '<iframe>', 'maliciousFunction', 'stealData'
        ]
        
        for element in malicious_elements:
            assert element not in sanitized
        
        # Verify legitimate content remains
        assert "Legitimate Title" in sanitized
        assert "<h1>" in sanitized
        assert "<div>" in sanitized
    
    def test_security_performance(self, html_sanitizer):
        """Test security processing performance."""
        import time
        
        # Large document with mixed content
        large_content = """
        <div class="document">
            <h1>Large Document Test</h1>
            """ + "<p>Safe paragraph content. " * 1000 + """</p>
            <script>alert('Should be removed');</script>
            """ + "<div>More safe content. " * 500 + """</div>
        </div>
        """
        
        start_time = time.time()
        sanitized = html_sanitizer.sanitize(large_content)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should process within reasonable time (< 1 second for this size)
        assert processing_time < 1.0
        
        # Should still remove malicious content
        assert "<script>" not in sanitized
        assert "alert" not in sanitized
        
        # Should preserve safe content
        assert "Large Document Test" in sanitized
        assert "Safe paragraph content" in sanitized