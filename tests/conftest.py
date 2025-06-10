"""
Pytest configuration and fixtures for HTML Text Formatter Pro tests.
"""

import pytest
import sys
from pathlib import Path
import tempfile
import os

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test content for file processing")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <html>
        <head><title>Test Document</title></head>
        <body>
            <h1>Test Heading</h1>
            <p>This is a test paragraph.</p>
            <div class="content">
                <p>More content here.</p>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def malicious_html():
    """Malicious HTML content for security testing."""
    return """
    <html>
        <head><title>Malicious Document</title></head>
        <body>
            <h1>Test Heading</h1>
            <script>alert('XSS Attack!');</script>
            <p onclick="maliciousFunction()">Click me</p>
            <iframe src="javascript:alert('XSS')"></iframe>
            <img src="x" onerror="alert('XSS')">
        </body>
    </html>
    """


@pytest.fixture
def style_config():
    """Sample style configuration for testing."""
    from models.style_models import StyleConfig
    return StyleConfig(
        font_size=16,
        text_color="#333333",
        background_color="#ffffff",
        font_family="Arial, sans-serif",
        line_height=1.6,
        max_width=800
    )


@pytest.fixture
def template_service():
    """Template service instance for testing."""
    from services.template_service import TemplateService
    return TemplateService()


@pytest.fixture
def html_sanitizer():
    """HTML sanitizer instance for testing."""
    from utils.sanitizers import HTMLSanitizer
    from models.style_models import SecurityConfig
    return HTMLSanitizer(SecurityConfig())


@pytest.fixture
def performance_monitor():
    """Performance monitor instance for testing."""
    from utils.performance_monitor import get_performance_monitor
    return get_performance_monitor()


@pytest.fixture
def cache_manager():
    """Cache manager instance for testing."""
    from utils.cache_manager import get_cache_manager
    return get_cache_manager()


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables and state before each test."""
    # Store original environment
    original_env = dict(os.environ)
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)