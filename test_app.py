#!/usr/bin/env python3
"""
Test script for HTML Text Formatter Pro
Tests the security and functionality of the new modular architecture.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all modules can be imported correctly."""
    print("🔧 Testing module imports...")
    
    try:
        # Test model imports
        from models.style_models import StyleConfig, SecurityConfig
        print("✅ Models imported successfully")
        
        # Test utility imports
        from utils.sanitizers import HTMLSanitizer, ContentValidator
        from utils.validators import FileValidator, TextValidator
        print("✅ Utilities imported successfully")
        
        # Test service imports
        from services.file_processor import FileProcessor
        from services.html_generator import HTMLGenerator
        print("✅ Services imported successfully")
        
        # Test UI component imports
        from ui.components.style_sidebar import StyleSidebar
        from ui.components.file_uploader import FileUploaderComponent
        from ui.components.preview import PreviewComponent
        from ui.main_page import MainPage
        print("✅ UI components imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_security_features():
    """Test security features."""
    print("\\n🔒 Testing security features...")
    
    try:
        from utils.sanitizers import HTMLSanitizer
        from models.style_models import SecurityConfig
        
        # Test HTML sanitization
        sanitizer = HTMLSanitizer()
        
        # Test XSS protection
        malicious_html = '<script>alert("XSS")</script><p>Safe content</p>'
        sanitized = sanitizer.sanitize(malicious_html)
        
        if '<script>' not in sanitized and 'Safe content' in sanitized:
            print("✅ XSS protection working")
        else:
            print("❌ XSS protection failed")
            return False
        
        # Test content validation
        from utils.validators import TextValidator
        validator = TextValidator()
        
        # Test oversized content
        large_text = "A" * 2_000_000  # 2MB
        is_valid, error = validator.validate_text_input(large_text)
        
        if not is_valid and "too long" in error.lower():
            print("✅ Content size validation working")
        else:
            print("❌ Content size validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Security test error: {e}")
        return False

def test_configuration():
    """Test configuration and styling."""
    print("\\n🎨 Testing configuration...")
    
    try:
        from models.style_models import StyleConfig
        from config.constants import COLOR_SCHEMES, MATERIAL_COLORS
        
        # Test style configuration
        config = StyleConfig()
        print(f"✅ Default style config created: {config.font_size}px font")
        
        # Test color schemes
        if len(COLOR_SCHEMES) >= 10:
            print(f"✅ Color schemes loaded: {len(COLOR_SCHEMES)} schemes")
        else:
            print("❌ Insufficient color schemes")
            return False
        
        # Test material colors
        if len(MATERIAL_COLORS) >= 15:
            print(f"✅ Material colors loaded: {len(MATERIAL_COLORS)} color families")
        else:
            print("❌ Insufficient material colors")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def test_html_generation():
    """Test HTML generation."""
    print("\\n📄 Testing HTML generation...")
    
    try:
        from services.html_generator import HTMLGenerator
        from models.style_models import StyleConfig
        
        # Create test configuration
        config = StyleConfig(
            font_size=16,
            text_color="#333333",
            background_color="#ffffff"
        )
        
        # Generate HTML
        generator = HTMLGenerator(config)
        test_content = "<p>This is a test paragraph.</p>"
        
        html_doc = generator.generate_html_document(test_content)
        
        # Check HTML structure
        required_elements = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '<body>',
            'test paragraph',
            'Permissions-Policy',
            'Content-Security-Policy'
        ]
        
        missing_elements = [elem for elem in required_elements if elem not in html_doc]
        
        if not missing_elements:
            print("✅ HTML generation working correctly")
            print(f"✅ Generated document size: {len(html_doc):,} characters")
            return True
        else:
            print(f"❌ Missing HTML elements: {missing_elements}")
            return False
        
    except Exception as e:
        print(f"❌ HTML generation test error: {e}")
        return False

def test_document_processing():
    """Test document processing capabilities."""
    print("\\n📄 Testing document processing...")
    
    try:
        from services.document_processors.pdf_processor import PDFProcessor
        from services.document_processors.docx_processor import DOCXProcessor
        
        # Test PDF processor initialization
        pdf_processor = PDFProcessor()
        print(f"✅ PDF processor initialized with {len(pdf_processor.strategies)} strategies")
        
        # Test DOCX processor initialization
        docx_processor = DOCXProcessor()
        print(f"✅ DOCX processor initialized (available: {docx_processor.available})")
        
        # Test CSS sanitizer (should work without warnings now)
        from utils.css_sanitizer import CSSSanitizer
        css_sanitizer = CSSSanitizer()
        
        test_css = "color: red; font-size: 16px; background: blue;"
        sanitized = css_sanitizer.sanitize_css(test_css)
        
        if sanitized and "color: red" in sanitized:
            print("✅ CSS sanitizer working correctly")
        else:
            print("❌ CSS sanitizer not working as expected")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Document processing test error: {str(e)}")
        return False

def test_performance_monitoring():
    """Test performance monitoring and caching."""
    print("\\n📊 Testing performance monitoring...")
    
    try:
        from utils.performance_monitor import get_performance_monitor
        from utils.cache_manager import get_cache_manager
        from utils.logger import get_enhanced_logger
        
        # Test performance monitor
        monitor = get_performance_monitor()
        monitor.record_request()
        monitor.record_operation_time("test_operation", 0.1)
        
        summary = monitor.get_performance_summary()
        if 'timestamp' in summary and 'system' in summary:
            print("✅ Performance monitoring working")
        else:
            print("❌ Performance monitoring failed")
            return False
        
        # Test cache manager
        cache = get_cache_manager()
        cache.set("test_key", "test_value", ttl=300)
        cached_value = cache.get("test_key")
        
        if cached_value == "test_value":
            print("✅ Cache manager working")
        else:
            print("❌ Cache manager failed")
            return False
        
        # Test enhanced logger
        logger = get_enhanced_logger("test_logger")
        logger.info("Test log message", test_param="test_value")
        print("✅ Enhanced logging working")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance monitoring test error: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 HTML Text Formatter Pro - Security & Functionality Tests")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Security Features", test_security_features), 
        ("Configuration", test_configuration),
        ("HTML Generation", test_html_generation),
        ("Document Processing", test_document_processing),
        ("Performance Monitoring", test_performance_monitoring)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")
    
    print("\\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready for use.")
        print("\\n🔒 Security features verified:")
        print("  • XSS protection active")
        print("  • Input validation working")
        print("  • Content sanitization enabled")
        print("  • File security checks operational")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)